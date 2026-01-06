#!/usr/bin/env python3
"""
HTTP to HTTPS Relay Server
Accepts HTTP requests and relays them to HTTPS endpoints with domain whitelisting.
"""

import os
import sys
import logging
import fnmatch
from urllib.parse import urlparse
from datetime import datetime

import requests
from flask import Flask, request, Response, jsonify

# Configuration
PORT = int(os.getenv('PORT', 8080))
ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS', '').split(',')
ALLOWED_DOMAINS = [d.strip() for d in ALLOWED_DOMAINS if d.strip()]
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/relay.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def is_domain_allowed(domain):
    """Check if domain is in the whitelist (supports wildcards)."""
    if not ALLOWED_DOMAINS:
        logger.warning("No allowed domains configured - blocking all requests")
        return False
    
    for allowed in ALLOWED_DOMAINS:
        # Support wildcard matching
        if fnmatch.fnmatch(domain.lower(), allowed.lower()):
            return True
    return False


def validate_target_url(target_url):
    """Validate and parse the target URL."""
    if not target_url:
        return None, "Missing target URL"
    
    try:
        parsed = urlparse(target_url)
        
        # Must be HTTPS
        if parsed.scheme != 'https':
            return None, f"Target URL must use HTTPS protocol, got: {parsed.scheme}"
        
        # Must have a valid domain
        if not parsed.netloc:
            return None, "Invalid target URL: missing domain"
        
        # Extract domain (without port)
        domain = parsed.netloc.split(':')[0]
        
        # Check whitelist
        if not is_domain_allowed(domain):
            return None, f"Domain not allowed: {domain}"
        
        return target_url, None
    
    except Exception as e:
        return None, f"Invalid target URL: {str(e)}"


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'http-to-https-relay',
        'timestamp': datetime.utcnow().isoformat(),
        'allowed_domains': ALLOWED_DOMAINS
    })


@app.route('/relay', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def relay():
    """
    Relay endpoint. Expects target URL in X-Target-URL header.
    Example: X-Target-URL: https://api.example.com/endpoint
    """
    # Get target URL from header
    target_url = request.headers.get('X-Target-URL')
    
    # Validate target URL
    validated_url, error = validate_target_url(target_url)
    if error:
        logger.warning(f"Request rejected: {error}")
        return jsonify({'error': error}), 400
    
    # Log the request
    logger.info(f"Relaying {request.method} request to {validated_url}")
    
    try:
        # Prepare headers (remove hop-by-hop headers)
        relay_headers = {
            key: value for key, value in request.headers.items()
            if key.lower() not in [
                'host', 'connection', 'keep-alive', 'proxy-authenticate',
                'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
                'upgrade', 'x-target-url'
            ]
        }
        
        # Make the HTTPS request
        response = requests.request(
            method=request.method,
            url=validated_url,
            headers=relay_headers,
            data=request.get_data(),
            params=request.args,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
            verify=True  # Verify SSL certificates
        )
        
        # Prepare response headers
        response_headers = {
            key: value for key, value in response.headers.items()
            if key.lower() not in [
                'connection', 'keep-alive', 'proxy-authenticate',
                'proxy-authorization', 'te', 'trailers', 'transfer-encoding',
                'upgrade', 'content-encoding', 'content-length'
            ]
        }
        
        # Log success
        logger.info(f"Successfully relayed to {validated_url} - Status: {response.status_code}")
        
        # Return the response
        return Response(
            response.content,
            status=response.status_code,
            headers=response_headers,
            content_type=response.headers.get('content-type')
        )
    
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout for {validated_url}")
        return jsonify({'error': 'Request timeout'}), 504
    
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL error for {validated_url}: {str(e)}")
        return jsonify({'error': 'SSL certificate verification failed'}), 502
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {validated_url}: {str(e)}")
        return jsonify({'error': f'Failed to relay request: {str(e)}'}), 502
    
    except Exception as e:
        logger.exception(f"Unexpected error relaying to {validated_url}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/', methods=['GET'])
def index():
    """Info endpoint."""
    return jsonify({
        'service': 'HTTP to HTTPS Relay Server',
        'version': '1.0.0',
        'usage': {
            'endpoint': '/relay',
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'],
            'header': 'X-Target-URL',
            'example': 'curl -H "X-Target-URL: https://api.example.com/data" http://localhost:8080/relay'
        },
        'health_check': '/health',
        'allowed_domains': ALLOWED_DOMAINS if ALLOWED_DOMAINS else ['None configured']
    })


if __name__ == '__main__':
    logger.info(f"Starting HTTP to HTTPS Relay Server on port {PORT}")
    logger.info(f"Allowed domains: {ALLOWED_DOMAINS if ALLOWED_DOMAINS else 'None configured'}")
    
    if not ALLOWED_DOMAINS:
        logger.warning("WARNING: No allowed domains configured! All requests will be blocked.")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)


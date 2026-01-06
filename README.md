# HTTP to HTTPS Relay Server

A Docker-based HTTP proxy server that relays HTTP requests to HTTPS endpoints for clients that don't support HTTPS connections. Includes domain whitelisting for security.

## Features

- ✅ HTTP to HTTPS relay
- ✅ Domain whitelist with wildcard support
- ✅ All HTTP methods supported (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- ✅ Request/response header forwarding
- ✅ SSL certificate verification
- ✅ Request logging
- ✅ Health check endpoint
- ✅ Configurable timeouts

## Quick Start

1. **Configure allowed domains**:
   - For development: Edit `docker-compose.dev.yml`
   - For production: Edit `docker-compose.yml`
   
   Update the `ALLOWED_DOMAINS` environment variable with your target domains.

2. **Start the server**:
   
   **Development mode** (with port mapping):
   ```bash
   ./start_dev.sh
   ```

   **Production mode** (for nginx-proxy):
   ```bash
   ./start_production.sh
   ```

   Or manually:
   ```bash
   # Development
   docker-compose -f docker-compose.dev.yml up -d --build
   
   # Production
   docker-compose up -d --build
   ```

3. **Stop the server**:
   ```bash
   # Development
   ./stop_dev.sh
   
   # Production
   ./stop_production.sh
   ```

4. **Check status**:
   ```bash
   # Development
   curl http://localhost:8080/health
   
   # Production (via nginx-proxy)
   curl https://relay.10botics.co/health
   ```

## Usage

### Making Requests

The relay server expects the target HTTPS URL in the `X-Target-URL` header:

```bash
# GET request
curl -H "X-Target-URL: https://api.example.com/endpoint" \
     http://localhost:8080/relay

# POST request with JSON data
curl -X POST \
     -H "X-Target-URL: https://api.example.com/data" \
     -H "Content-Type: application/json" \
     -d '{"key":"value"}' \
     http://localhost:8080/relay

# GET request with query parameters
curl -H "X-Target-URL: https://api.example.com/search?q=test" \
     http://localhost:8080/relay
```

### Client Example (Python)

```python
import requests

response = requests.get(
    'http://localhost:8080/relay',
    headers={
        'X-Target-URL': 'https://api.example.com/endpoint',
        'Authorization': 'Bearer your-token'
    }
)
print(response.json())
```

## Configuration

Edit `docker-compose.yml` or create a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | HTTP server port | `8080` |
| `ALLOWED_DOMAINS` | Comma-separated list of allowed domains | Required |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `REQUEST_TIMEOUT` | Timeout for HTTPS requests (seconds) | `30` |
| `TZ` | Timezone | `Asia/Hong_Kong` |

### Domain Whitelist

The `ALLOWED_DOMAINS` environment variable supports:

- **Exact match**: `api.example.com`
- **Wildcard subdomain**: `*.example.com` (matches `api.example.com`, `service.example.com`)
- **Wildcard in path**: `api.*.com` (matches `api.example.com`, `api.test.com`)

Example:
```
ALLOWED_DOMAINS=api.example.com,*.trusted-service.com,specific.domain.org
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/relay` | ALL | Relay endpoint (requires `X-Target-URL` header) |
| `/health` | GET | Health check |

## Logs

Logs are stored in `./logs/relay.log` and also output to stdout.

View logs:
```bash
# Follow logs
docker-compose logs -f relay

# View log file
tail -f logs/relay.log
```

## Security Considerations

1. **Domain Whitelist**: Always configure `ALLOWED_DOMAINS` - without it, all requests are blocked
2. **SSL Verification**: The server verifies SSL certificates of target HTTPS endpoints
3. **No Authentication**: This service doesn't include authentication - use behind a firewall or add your own auth layer
4. **Rate Limiting**: Consider adding rate limiting for production use

## Troubleshooting

### "Domain not allowed" Error

Make sure the target domain is in `ALLOWED_DOMAINS`:
```bash
# Check current configuration
curl http://localhost:8080/health
```

### SSL Certificate Errors

The server verifies SSL certificates. If you need to connect to servers with self-signed certificates, modify `verify=True` to `verify=False` in `relay_server.py` (not recommended for production).

### Connection Timeout

Increase `REQUEST_TIMEOUT` in the environment configuration:
```yaml
environment:
  - REQUEST_TIMEOUT=60
```

## Network Configuration

This service uses the external network `docker05` to integrate with other services (like nginx-proxy). Make sure the network exists:

```bash
docker network create docker05
```

Or modify `docker-compose.yml` to use a different network.

## Development

Run locally without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Set environment variables
export PORT=8080
export ALLOWED_DOMAINS="api.example.com,*.test.com"
export LOG_LEVEL=DEBUG

# Run server
python relay_server.py
```

## License

MIT


# Security Policy — Exquis

## Security Measures

### Authentication
- API Key authentication via `X-API-Key` header (configurable, disabled by default for local dev)
- Configure `EXQUIS_API_KEY` in `.env` to enable

### Rate Limiting
- 100 requests per minute per IP
- 1000 requests per hour per IP
- Powered by `flask-limiter`

### Security Headers (flask-talisman)
- Content Security Policy (CSP)
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (when behind HTTPS reverse proxy)

### CORS
- Restricted to `http://localhost:3000` by default
- Configurable via `CORS_ORIGINS` env var

### Input Validation
- Population size capped at 1000
- Agent list capped at 100 results
- All exceptions caught and sanitized

### Data Protection
- No secrets in version control
- `.env` excluded via `.gitignore`
- API keys stored server-side only
- No telemetry or analytics

## Deployment Checklist

- [ ] Set strong `EXQUIS_SECRET_KEY`
- [ ] Set `EXQUIS_API_KEY` for production
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Place behind reverse proxy (nginx/Caddy) with TLS
- [ ] Set `FLASK_DEBUG=0`
- [ ] Use strong Neo4j password

## Reporting Vulnerabilities

Contact: [@Foolafroos](https://x.com/Foolafroos)

# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅                 |

## Reporting a Vulnerability

If you discover a security vulnerability, please email the maintainer directly. Do NOT open a public issue.

## Security Best Practices

### API Keys
- All API keys are loaded from environment variables
- Never hardcode credentials in source code
- Use `.env` files (included in `.gitignore`) for local development

### Docker Deployment
- Neo4j credentials should be changed from defaults in production
- Use Docker secrets or a secrets manager for production deployments
- Restrict network access to necessary ports only

### Rate Limiting
- API endpoints do not implement rate limiting
- For production, implement rate limiting at the API gateway level

### Input Validation
- Image uploads are validated for file type
- Base64 images are not currently size-limited (should be added for production)

## Dependencies

Keep dependencies updated:
```bash
pip install -r requirements.txt
```

Check for vulnerabilities:
```bash
pip audit
```

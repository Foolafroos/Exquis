# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- Added API key authentication for all `/api/*` endpoints via `X-API-Key` header
- Implemented Flask-Talisman for security headers (CSP, X-Frame-Options, HSTS)
- Added Flask-Limiter rate limiting (100 req/min, 1000 req/hour)
- Removed hardcoded Neo4j password - now uses `NEO4J_PASSWORD` env var
- Added `.gitignore` to prevent `.env` file exposure
- Created `.env.example` template for secure configuration
- Added `SECURITY.md` with security policy and vulnerability disclosure guidelines
- Generic error messages in API responses - no stack traces exposed to clients

### Added
- `PRIVACY.md` - GDPR-compliant privacy policy
- `SECURITY.md` - Security policy and best practices documentation
- Environment variable configuration for all secrets

### Changed
- API routes now require authentication when `EXQUIS_API_KEY` is set
- Error handling to prevent information leakage

## [0.1.0] - 2026-05-12

### Added
- Initial project structure
- Flask backend with Neo4j integration
- Basic API endpoints
- CORS configuration

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# ── Security: CORS (restrict origins in production) ──
CORS(app, origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","))

# ── Security: HTTP security headers ──
csp = {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:", "https:"],
}
Talisman(
    app,
    force_https=False,  # Let reverse proxy handle HTTPS
    content_security_policy=csp,
    content_security_policy_nonce_in=["script-src"],
)

# ── Security: Rate limiting ──
Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute", "1000 per hour"],
    storage_uri="memory://",
)

# ── Configuration from environment ──
app.config["SECRET_KEY"] = os.getenv("EXQUIS_SECRET_KEY", "change-me-in-production")
app.config["API_KEY"] = os.getenv("EXQUIS_API_KEY", "")
app.config["NEO4J_URI"] = os.getenv("NEO4J_URI", "bolt://localhost:7687")
app.config["NEO4J_USER"] = os.getenv("NEO4J_USER", "neo4j")
app.config["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD", "")
app.config["NVIDIA_API_KEY"] = os.getenv("NVIDIA_API_KEY", "")
app.config["HUGGINGFACE_TOKEN"] = os.getenv("HUGGINGFACE_TOKEN", "")

# ── Security: API Key authentication ──
def require_api_key(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not app.config["API_KEY"]:
            return f(*args, **kwargs)  # Disable if no key set
        key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if key != app.config["API_KEY"]:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ── Error handlers (no sensitive data leakage) ──
@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(429)
def rate_limit(e):
    return jsonify({"error": "Rate limit exceeded. Slow down."}), 429


# Import routes
from src.routes import api_bp

app.register_blueprint(api_bp, url_prefix="/api")


@app.route("/health")
def health():
    return {"status": "healthy", "service": "exquis"}


@app.route("/")
def index():
    return {"message": "Exquis API", "version": "1.0.0"}


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=8000, debug=debug_mode)

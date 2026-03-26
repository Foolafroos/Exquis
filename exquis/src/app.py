from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configuration
app.config["NEO4J_URI"] = os.getenv("NEO4J_URI", "bolt://localhost:7687")
app.config["NEO4J_USER"] = os.getenv("NEO4J_USER", "neo4j")
app.config["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD", "exquis")
app.config["NVIDIA_API_KEY"] = os.getenv("NVIDIA_API_KEY", "")
app.config["HUGGINGFACE_TOKEN"] = os.getenv("HUGGINGFACE_TOKEN", "")

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
    app.run(host="0.0.0.0", port=8000, debug=True)

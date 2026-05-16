from flask import Blueprint, request, jsonify
import base64
import os
import io

api_bp = Blueprint("api", __name__)

# ── Security: API Key authentication on all API routes ──
@api_bp.before_request
def check_api_key():
    # Lazy import to avoid circular dependency
    from ..app import app as flask_app
    api_key = flask_app.config.get("API_KEY", "")
    if not api_key:
        return None  # Auth disabled if no key configured
    key = request.headers.get("X-API-Key") or request.args.get("api_key")
    if key != api_key:
        return (jsonify({"error": "Unauthorized"}), 401)

# Global state (in production, use proper state management)
_state = {
    "current_image": None,
    "current_caption": None,
    "population": None,
    "simulation_results": None,
}


@api_bp.route("/image/analyze", methods=["POST"])
def analyze_image():
    """Analyze an image and generate brain responses

    Request body:
    {
        "image": "base64_encoded_image" OR "image_url",
        "population_size": 1000 (optional, default 10)
    }
    """

    try:
        data = request.get_json()

        # Get image (either base64 or URL)
        image_data = data.get("image")
        population_size = data.get("population_size", 10)

        # Validate population size
        if population_size and population_size > 1000:
            return jsonify({"error": "population_size exceeds maximum of 1000"}), 400

        if not image_data:
            return jsonify({"error": "No image provided"}), 400

        # Determine image source
        if image_data.startswith("data:image") or len(image_data) > 200:
            # Base64 encoded
            is_base64 = True
        elif image_data.startswith("http"):
            is_base64 = False
        else:
            # Assume base64
            is_base64 = True

        # Initialize services
        from src.vision.nvidia_client import NVIDIAVisionClient
        from src.brain_engine.tribe_client import (
            TRIBEClient,
            CLIPVariationModel,
            PopulationBrainGenerator,
        )

        vision_client = NVIDIAVisionClient()
        tribe_client = TRIBEClient()
        clip_model = CLIPVariationModel()
        population_generator = PopulationBrainGenerator(tribe_client, clip_model)

        # Step 1: Generate image caption
        print("Step 1: Generating image caption...")
        if is_base64:
            caption = vision_client.describe_image_base64(image_data)
        else:
            caption = vision_client.describe_image(image_data)

        _state["current_caption"] = caption
        print(f"Caption: {caption[:100]}...")

        # Step 2: Generate CLIP embedding (placeholder for now)
        print("Step 2: Generating image embeddings...")
        import numpy as np

        # Create a mock CLIP embedding (in production, use actual CLIP)
        clip_embedding = np.random.randn(512).astype(np.float32)

        # Step 3: Generate population of brain profiles
        print(f"Step 3: Generating {population_size} brain profiles...")
        population = population_generator.generate_population(
            caption, clip_embedding, population_size
        )

        _state["current_image"] = image_data[:100] + "..."
        _state["population"] = population

        # Generate summary
        summary = population_generator.get_population_summary(population)

        return jsonify(
            {
                "success": True,
                "caption": caption,
                "population_size": len(population),
                "population_summary": summary,
                "sample_profiles": [
                    {
                        "id": p["id"],
                        "dominant_regions": p["dominant_regions"],
                        "personality_type": p.get("personality", {}).get(
                            "personality_type", "unknown"
                        ),
                    }
                    for p in population[:5]
                ],
            }
        )

    except Exception as e:
        # Log internally, return generic error to client
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Image analysis failed"}), 500


@api_bp.route("/simulation/run", methods=["POST"])
def run_simulation():
    """Run social simulation with the current brain profiles

    Request body:
    {
        "mode": "posts" | "debate" | "consensus" | "all",
        "config": {...} (optional)
    }
    """

    try:
        data = request.get_json()

        mode = data.get("mode", "posts")
        config = data.get("config", {})

        if _state.get("population") is None:
            return jsonify(
                {"error": "No image analyzed yet. Call /api/image/analyze first."}
            ), 400

        # Initialize LLM provider
        from src.llm.factory import LLMFactory
        from src.agents.brain_profile import AgentManager, BrainProfile

        # Get LLM configuration
        llm_provider_type = os.getenv("LLM_PROVIDER", "nvidia_nim")

        # Try to create provider, with fallbacks
        try:
            llm = LLMFactory.create_provider(llm_provider_type)
        except Exception as e:
            print(f"Failed to create {llm_provider_type}: {e}")
            # Fallback to any available provider
            for fallback_type in ["openai", "anthropic", "google", "ollama"]:
                try:
                    llm = LLMFactory.create_provider(fallback_type)
                    print(f"Using fallback: {fallback_type}")
                    break
                except:
                    continue
            else:
                return jsonify(
                    {
                        "error": "No LLM provider available. Configure API keys in .env."
                    }
                ), 500

        # Create agent manager with brain profiles
        agent_manager = AgentManager()
        brain_profiles = [BrainProfile(p) for p in _state["population"]]
        agent_manager.add_agents(brain_profiles)

        print(f"Running {mode} simulation with {len(brain_profiles)} agents...")

        # Import and run simulation
        from src.simulation.modes import SimulationOrchestrator

        orchestrator = SimulationOrchestrator(llm, agent_manager)
        results = orchestrator.run(mode, _state["current_caption"], config)

        _state["simulation_results"] = results

        return jsonify({"success": True, "mode": mode, "results": results})

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Simulation failed"}), 500


@api_bp.route("/brain/visualization", methods=["GET"])
def get_brain_visualization():
    """Get brain activation data for visualization"""

    try:
        if _state.get("population") is None:
            return jsonify({"error": "No data available"}), 400

        population = _state["population"]

        # Aggregate activation by region
        region_activations = {}
        for profile in population:
            for region, activation in profile["brain_response"].items():
                if region not in region_activations:
                    region_activations[region] = []
                region_activations[region].append(activation)

        # Calculate statistics
        import numpy as np

        visualization_data = {}
        for region, activations in region_activations.items():
            visualization_data[region] = {
                "mean": float(np.mean(activations)),
                "std": float(np.std(activations)),
                "min": float(np.min(activations)),
                "max": float(np.max(activations)),
                "histogram": _create_histogram(activations),
            }

        return jsonify(
            {
                "success": True,
                "visualization": visualization_data,
                "population_size": len(population),
            }
        )

    except Exception as e:
        return jsonify({"error": "Visualization failed"}), 500


@api_bp.route("/agents/list", methods=["GET"])
def list_agents():
    """List all agents with their brain profiles"""

    try:
        if _state.get("population") is None:
            return jsonify({"error": "No data available"}), 400

        limit = request.args.get("limit", 10, type=int)
        # Cap limit to prevent massive responses
        limit = min(limit, 100)

        agents = [
            {
                "id": p["id"],
                "dominant_regions": p["dominant_regions"],
                "brain_response": p["brain_response"],
                "personality": p.get("personality", {}),
            }
            for p in _state["population"][:limit]
        ]

        return jsonify(
            {"success": True, "total": len(_state["population"]), "agents": agents}
        )

    except Exception as e:
        return jsonify({"error": "Failed to list agents"}), 500


@api_bp.route("/config/providers", methods=["GET"])
def get_provider_config():
    """Get available LLM providers and their status"""

    from src.llm.factory import LLMFactory

    providers = {}
    for provider_type in LLMFactory.PROVIDERS.keys():
        try:
            provider = LLMFactory.create_provider(provider_type)
            providers[provider_type] = {
                "available": True,
                "health": provider.health_check(),
            }
        except Exception as e:
            # Don't leak internal error details
            providers[provider_type] = {"available": False, "error": "Provider unavailable"}

    return jsonify(
        {
            "primary_provider": os.getenv("LLM_PROVIDER", "nvidia_nim"),
            "providers": providers,
        }
    )


@api_bp.route("/config/test", methods=["POST"])
def test_provider():
    """Test a specific LLM provider

    Request body:
    {
        "provider": "nvidia_nim" | "openai" | etc.
    }
    """

    try:
        data = request.get_json()
        provider_type = data.get("provider", "nvidia_nim")

        from src.llm.factory import LLMFactory

        provider = LLMFactory.create_provider(provider_type)

        # Test generation
        response = provider.generate(
            "Say 'Hello from [provider name]' in exactly that format.", max_tokens=50
        )

        return jsonify(
            {
                "success": True,
                "provider": provider_type,
                "response": response,
                "health": provider.health_check(),
            }
        )

    except Exception as e:
        provider_name = request.get_json(silent=True)
        return jsonify(
            {"success": False, "provider": provider_name.get("provider") if provider_name else None, "error": "Provider test failed"}
        ), 500


def _create_histogram(values, bins=10):
    """Create histogram data for visualization"""
    import numpy as np

    hist, edges = np.histogram(values, bins=bins)

    return {"counts": hist.tolist(), "edges": edges.tolist()}

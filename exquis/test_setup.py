#!/usr/bin/env python3
"""
Exquis Test Script
Run this to test individual components before full deployment
"""

import os
import sys

print("🧪 Exquis Test Suite")
print("=" * 50)

# Test 1: Python imports
print("\n1. Testing Python imports...")
try:
    import flask
    import neo4j
    import requests
    import numpy

    print("   ✓ Core dependencies available")
except ImportError as e:
    print(f"   ✗ Missing dependency: {e}")
    sys.exit(1)

# Test 2: Project structure
print("\n2. Testing project structure...")
required_files = [
    "src/app.py",
    "src/llm/factory.py",
    "src/vision/nvidia_client.py",
    "src/brain_engine/tribe_client.py",
    "src/agents/brain_profile.py",
    "src/simulation/modes.py",
    "src/routes/api.py",
    "config/default.yaml",
    "docker-compose.yml",
]

missing = []
for f in required_files:
    if not os.path.exists(f):
        missing.append(f)

if missing:
    print(f"   ✗ Missing files: {missing}")
else:
    print("   ✓ All required files present")

# Test 3: Environment configuration
print("\n3. Testing configuration...")
try:
    import yaml

    with open("config/default.yaml") as f:
        config = yaml.safe_load(f)
    print(f"   ✓ Config loaded: {list(config.keys())}")
except Exception as e:
    print(f"   ✗ Config error: {e}")

# Test 4: LLM Factory
print("\n4. Testing LLM Factory...")
try:
    sys.path.insert(0, ".")
    from src.llm.factory import LLMFactory

    providers = list(LLMFactory.PROVIDERS.keys())
    print(f"   ✓ Available providers: {providers}")
except Exception as e:
    print(f"   ✗ LLM Factory error: {e}")

# Test 5: Vision Client
print("\n5. Testing Vision Client...")
try:
    from src.vision.nvidia_client import NVIDIAVisionClient

    print("   ✓ Vision client imports OK")
except Exception as e:
    print(f"   ✗ Vision client error: {e}")

# Test 6: TRIBE Client
print("\n6. Testing TRIBE Client...")
try:
    from src.brain_engine.tribe_client import TRIBEClient, CLIPVariationModel

    print("   ✓ TRIBE client imports OK")
except Exception as e:
    print(f"   ✗ TRIBE client error: {e}")

# Test 7: Agent modules
print("\n7. Testing Agent modules...")
try:
    from src.agents.brain_profile import BrainProfile, AgentManager

    print("   ✓ Agent modules OK")
except Exception as e:
    print(f"   ✗ Agent module error: {e}")

# Test 8: Simulation modules
print("\n8. Testing Simulation modules...")
try:
    from src.simulation.modes import SimulationOrchestrator

    print("   ✓ Simulation modules OK")
except Exception as e:
    print(f"   ✗ Simulation module error: {e}")

# API Keys check
print("\n9. Checking API keys...")
env_vars = [
    "NVIDIA_API_KEY",
    "HUGGINGFACE_TOKEN",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
]
configured = []
for var in env_vars:
    val = os.getenv(var, os.environ.get(var, ""))
    if val and val != "your_" + var.lower() + "_here":
        configured.append(var)

print(f"   Configured: {configured or 'None (will use fallbacks)'}")

print("\n" + "=" * 50)
print("✅ Test suite complete!")
print("\nTo run the full application:")
print("  1. cp config/.env.example config/.env")
print("  2. Edit .env with your API keys")
print("  3. docker-compose up --build")
print("  4. Open http://localhost:3000")

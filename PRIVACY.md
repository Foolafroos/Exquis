# Privacy Policy — Exquis (Brain Response Simulator)

**Last updated:** May 2026

## Overview
Exquis is a local-first Brain Response Simulator that predicts how diverse populations react to images. This policy describes what data flows where.

## Data We Process

### Images
- Images you upload are sent to your configured LLM/vision provider for analysis
- Images are **not** stored permanently by Exquis itself
- If you use cloud providers (NVIDIA NIM, OpenAI, Anthropic, Google), their privacy policies also apply
- If you use local providers (Ollama, local CLIP), images stay on your machine

### Simulation Data
- Generated brain response data lives in your Neo4j knowledge graph
- This data is stored locally in your Neo4j instance
- No simulation data is transmitted to third parties by Exquis

### Configuration
- API keys and credentials are stored in your `.env` file (not committed to git)
- Configuration is stored in `config/default.yaml` on your local filesystem

## What We Do NOT Do
- We do **not** collect telemetry
- We do **not** track user behavior
- We do **not** send data to analytics services
- We do **not** share data with third parties

## Your Responsibilities
- Choose your LLM provider based on your privacy requirements
- Use local providers (Ollama) for maximum data sovereignty
- Protect your `.env` file with API keys
- Secure your Neo4j instance with a strong password

## Data Deletion
- Delete your Neo4j data volume to remove all simulation data
- Remove your `.env` file to clear API keys

## Contact
Questions? Reach out via [@Foolafroos](https://x.com/Foolafroos)

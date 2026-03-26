# 🧠 Exquis

**Brain Response Simulator** - Predict how 1000 diverse brains react to any image

Exquis combines TRIBE v2 brain encoding with MiroShark multi-agent social simulation to visualize population-level brain responses to visual stimuli.

## Features

- **Image Analysis** - Upload any image and get AI-generated captions
- **Brain Encoding** - TRIBE v2 predicts brain activation patterns
- **Population Simulation** - Generate 1000 diverse brain profiles with individual variations
- **Social Simulation** - MiroFish agents react based on their unique brain profiles
- **Multi-Provider LLM** - Support for NVIDIA NIM, OpenAI, Anthropic, Google, and Ollama
- **Interactive Dashboard** - Visualize brain activation maps, distributions, and social reactions

## Architecture

```
Image → NVIDIA Vision (Caption) → TRIBE v2 (Brain Encoding) → Population Generator → MiroFish Agents → Dashboard
                                                              ↓
                                                      CLIP Variations
```

## Prerequisites

- Docker & Docker Compose
- Neo4j (included in Docker Compose)
- API Keys (see Configuration)

## Quick Start

### 1. Clone and Setup

```bash
cd exquis
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp config/.env.example config/.env
```

Edit `.env` with your keys:

```bash
# Required
NVIDIA_API_KEY=your_nvidia_api_key
HUGGINGFACE_TOKEN=your_huggingface_token

# Optional - Fallback providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

Get your keys:
- **NVIDIA API Key**: https://build.nvidia.com/
- **HuggingFace Token**: https://huggingface.co/settings/tokens

### 3. Run with Docker

```bash
docker-compose up --build
```

This will start:
- Neo4j on port 7474/7687
- Exquis API on port 8000
- Frontend dashboard on port 3000

### 4. Access the Dashboard

Open http://localhost:3000 in your browser

## Usage

### API Endpoints

**Analyze Image**
```bash
POST /api/image/analyze
{
  "image": "base64_encoded_image",
  "population_size": 10
}
```

**Run Simulation**
```bash
POST /api/simulation/run
{
  "mode": "posts"  # posts, debate, consensus, all
}
```

**Get Brain Visualization**
```bash
GET /api/brain/visualization
```

**List Agents**
```bash
GET /api/agents/list?limit=10
```

### Dashboard Workflow

1. **Upload Image** - Drag & drop or click to select an image
2. **Set Population Size** - Slider from 10 to 1000
3. **Analyze** - Click "Analyze Brain Response"
4. **View Results** - See brain activation maps and distributions
5. **Run Simulation** - Choose interaction mode (posts/debate/consensus/all)
6. **Explore Agents** - See how different brain profiles react

## Configuration

Edit `config/default.yaml` to customize:

```yaml
vision:
  provider: "nvidia_nim"
  model: "meta/llama-3.2-11b-vision-instruct"

llm:
  primary:
    provider: "nvidia_nim"
    model: "nvidia/nemotron-4-340b-instruct"
  fallbacks:
    - "openai"
    - "anthropic"
    - "google"

simulation:
  default_population_size: 10
  max_population_size: 1000
```

## Interaction Modes

| Mode | Description |
|------|-------------|
| `posts` | Each agent posts their individual reaction |
| `debate` | Agents argue with each other |
| `consensus` | Group opinion evolves over rounds |
| `all` | Run all modes sequentially |

## LLM Provider Priority

The system tries providers in this order:
1. NVIDIA NIM (primary)
2. OpenAI GPT-4o
3. Anthropic Claude
4. Google Gemini
5. Ollama (local)

Each provider has automatic fallback - if one fails, the next is used.

## Tech Stack

- **Backend**: Flask + Python
- **Database**: Neo4j
- **Brain Encoding**: TRIBE v2 (Facebook)
- **Vision**: NVIDIA NIM Vision LLMs
- **Agents**: MiroShark multi-agent system
- **Frontend**: Vue 3 + Vite

## Development

### Run locally without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NVIDIA_API_KEY=your_key
export HUGGINGFACE_TOKEN=your_token

# Run API
python -m flask run --app src.app:app

# Run frontend
cd frontend && npm install && npm run dev
```

### Test API endpoints

```bash
# Health check
curl http://localhost:8000/health

# List providers
curl http://localhost:8000/api/config/providers
```

## Troubleshooting

**Neo4j connection fails**
- Wait for Neo4j to initialize (first start takes ~30s)
- Check credentials in docker-compose.yml

**API key errors**
- Ensure keys are in `.env` file
- Check NVIDIA API key at https://build.nvidia.com/

**Image upload fails**
- Check file size limit (default 10MB)
- Supported formats: JPG, PNG, WebP

## License

AGPL-3.0

## Credits

- TRIBE v2 by Facebook Research
- MiroShark by aaronjmars
- NVIDIA NIM for vision models
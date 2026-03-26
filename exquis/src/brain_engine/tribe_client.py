import os
import requests
from typing import Optional, Dict, List
import numpy as np
from PIL import Image
import base64
import io


class TRIBEClient:
    """TRIBE v2 brain encoding model client"""

    def __init__(self, token: Optional[str] = None, use_api: bool = True):
        self.token = token or os.getenv("HUGGINGFACE_TOKEN")
        self.use_api = use_api

        if use_api:
            self.base_url = (
                "https://api-inference.huggingface.co/models/facebook/tribev2"
            )
            self.headers = {"Authorization": f"Bearer {self.token}"}

    def predict_brain_response(
        self,
        text_input: str,
        video_data: Optional[bytes] = None,
        audio_data: Optional[bytes] = None,
    ) -> Dict:
        """Predict brain responses to multimodal stimuli using TRIBE v2

        Args:
            text_input: Text description/caption of the image
            video_data: Optional video bytes (can pass image as single frame)
            audio_data: Optional audio bytes

        Returns:
            Dictionary with brain response predictions for different regions
        """

        if self.use_api:
            return self._predict_via_api(text_input, video_data, audio_data)
        else:
            return self._predict_local(text_input)

    def _predict_via_api(
        self,
        text_input: str,
        video_data: Optional[bytes] = None,
        audio_data: Optional[bytes] = None,
    ) -> Dict:
        """Use HuggingFace Inference API"""

        # For text-only input (our use case with image captions)
        payload = {"inputs": {"text": text_input}}

        response = requests.post(
            self.base_url, headers=self.headers, json=payload, timeout=120
        )

        if response.status_code != 200:
            raise Exception(f"TRIBE API error: {response.text}")

        return response.json()

    def _predict_local(self, text_input: str) -> Dict:
        """Fallback to local prediction (would require model download)"""
        # This would load the model locally - placeholder for now
        return self._generate_mock_brain_response(text_input)

    def _generate_mock_brain_response(self, text_input: str) -> Dict:
        """Generate mock brain response for testing (remove in production)"""

        # Schaefer 1000 parcellation regions
        regions = [
            "Vis",
            "SomMot",
            "Salience",
            "VentAttn",
            " DorsAttn",
            "Limbic",
            "Cont",
            "Default",
        ]

        # Generate realistic-looking brain response based on text content
        np.random.seed(hash(text_input) % 2**32)

        response = {}
        for region in regions:
            # Activation values between 0 and 1
            response[region] = float(np.random.uniform(0.2, 0.9))

        return {
            "regions": response,
            "full_brain": self._generate_full_brain_parcels(response),
            "metadata": {"text_input_length": len(text_input), "model": "tribev2"},
        }

    def _generate_full_brain_parcels(self, region_activations: Dict) -> Dict:
        """Generate parcel-level activations for 1000 regions"""

        # Map higher-level regions to Schaefer parcels
        parcel_mapping = {
            "Vis": list(range(1, 151)),
            "SomMot": list(range(151, 251)),
            "Salience": list(range(251, 301)),
            "VentAttn": list(range(301, 401)),
            "DorsAttn": list(range(401, 551)),
            "Limbic": list(range(551, 601)),
            "Cont": list(range(601, 851)),
            "Default": list(range(851, 1001)),
        }

        parcels = {}
        for region, activation in region_activations.items():
            parcel_ids = parcel_mapping.get(region, [])

            # Add some variation within region
            for parcel_id in parcel_ids:
                # Base activation + noise for individual parcel variation
                variation = np.random.normal(0, 0.1)
                parcels[f"parcel_{parcel_id}"] = max(0, min(1, activation + variation))

        return parcels

    def get_region_activations(self, text_input: str) -> Dict[str, float]:
        """Get activation levels for major brain regions"""

        response = self.predict_brain_response(text_input)

        if "regions" in response:
            return response["regions"]

        # Fallback to mock
        return self._generate_mock_brain_response(text_input)["regions"]

    def get_region_description(self, region: str) -> str:
        """Get functional description of a brain region"""

        descriptions = {
            "Vis": "Visual cortex - processes visual information",
            "SomMot": "Somato-motor - motor control and body sensation",
            "Salience": "Salience network - detects important stimuli",
            "VentAttn": "Ventral attention - stimulus-driven attention",
            "DorsAttn": "Dorsal attention - goal-directed attention",
            "Limbic": "Limbic system - emotion and memory",
            "Cont": "Control network - executive functions",
            "Default": "Default mode - internal thoughts and memory",
        }

        return descriptions.get(region, "Unknown region")


class CLIPVariationModel:
    """CLIP-based model for generating individual brain response variations"""

    def __init__(self, use_api: bool = True):
        self.use_api = use_api
        # In production, would use actual CLIP model
        # For now, using algorithmic variation

    def generate_variation_vector(
        self, clip_embedding: np.ndarray, seed: int
    ) -> np.ndarray:
        """Generate a variation vector for individual brain response

        Args:
            clip_embedding: CLIP image embedding (512-dim)
            seed: Seed for reproducible variation

        Returns:
            Variation vector to add to base brain response
        """

        np.random.seed(seed)

        # Create personalized variation based on CLIP embedding
        # Different people notice different aspects of images
        variation = np.random.randn(len(clip_embedding)) * 0.1

        # Weight by CLIP embedding importance
        importance_weights = np.abs(clip_embedding) / np.sum(np.abs(clip_embedding))
        weighted_variation = variation * importance_weights

        return weighted_variation

    def map_to_brain_regions(self, clip_embedding: np.ndarray) -> Dict[str, float]:
        """Map CLIP embedding to brain region sensitivities

        Returns:
            Dictionary of region -> sensitivity scores
        """

        # Map CLIP semantic features to brain regions
        # In production, this would be a trained model

        # Simple heuristic mapping based on CLIP features
        sensitivities = {}

        # Visual features -> Visual cortex
        visual_features = np.mean(clip_embedding[:128])
        sensitivities["Vis"] = float(visual_features)

        # Object features -> Ventral attention
        object_features = np.mean(clip_embedding[128:256])
        sensitivities["VentAttn"] = float(object_features)

        # Scene features -> Default mode
        scene_features = np.mean(clip_embedding[256:384])
        sensitivities["Default"] = float(scene_features)

        # Semantic features -> Control network
        semantic_features = np.mean(clip_embedding[384:512])
        sensitivities["Cont"] = float(semantic_features)

        # Normalize to 0-1
        max_val = max(sensitivities.values()) if sensitivities else 1
        if max_val > 0:
            sensitivities = {k: v / max_val for k, v in sensitivities.items()}

        return sensitivities


class PopulationBrainGenerator:
    """Generate diverse brain response profiles for a population"""

    def __init__(self, tribe_client: TRIBEClient, clip_model: CLIPVariationModel):
        self.tribe = tribe_client
        self.clip = clip_model

    def generate_population(
        self, image_caption: str, clip_embedding: np.ndarray, population_size: int
    ) -> List[Dict]:
        """Generate brain response profiles for a population

        Args:
            image_caption: Description of the image
            clip_embedding: CLIP embedding of the image
            population_size: Number of individuals to generate

        Returns:
            List of brain profiles for each individual
        """

        # Get base brain response from TRIBE
        base_response = self.tribe.get_region_activations(image_caption)

        # Generate individual variations
        population = []

        for i in range(population_size):
            # Create unique variation for this individual
            variation = self.clip.generate_variation_vector(clip_embedding, seed=i)

            # Apply variation to base response
            individual_response = self._apply_variation(
                base_response, variation, seed=i
            )

            # Generate personality traits (for MiroFish integration)
            personality = self._generate_personality(i, individual_response)

            population.append(
                {
                    "id": f"brain_{i:04d}",
                    "brain_response": individual_response,
                    "personality": personality,
                    "dominant_regions": self._get_dominant_regions(individual_response),
                    "variation_seed": i,
                }
            )

        return population

    def _apply_variation(
        self, base_response: Dict, variation: np.ndarray, seed: int
    ) -> Dict[str, float]:
        """Apply variation vector to base brain response"""

        np.random.seed(seed)

        # Map variation to regions
        region_weights = {
            "Vis": variation[0],
            "SomMot": variation[32],
            "Salience": variation[64],
            "VentAttn": variation[96],
            "DorsAttn": variation[128],
            "Limbic": variation[160],
            "Cont": variation[192],
            "Default": variation[224],
        }

        # Apply variation with dampening
        modified = {}
        for region, base_val in base_response.items():
            var = region_weights.get(region, 0)
            modified[region] = max(0, min(1, base_val + var * 0.3))

        return modified

    def _generate_personality(self, seed: int, brain_response: Dict) -> Dict:
        """Generate personality traits based on brain response profile

        These traits will be used by MiroFish agents
        """

        np.random.seed(seed + 1000)

        # Map brain activation patterns to personality
        # Higher visual activation = more visual thinker
        visual_score = brain_response.get("Vis", 0.5)

        # Higher salience = more reactive to stimuli
        salience_score = brain_response.get("Salience", 0.5)

        # Higher default = more introspective
        default_score = brain_response.get("Default", 0.5)

        # Higher control = more analytical
        cont_score = brain_response.get("Cont", 0.5)

        return {
            "visual_thinker": visual_score > 0.6,
            "analytical": cont_score > 0.6,
            "introspective": default_score > 0.6,
            "reactive": salience_score > 0.6,
            "extroversion": np.random.uniform(0.3, 0.8),
            "openness": np.random.uniform(0.4, 0.9),
            "agreeableness": np.random.uniform(0.3, 0.7),
            "neuroticism": np.random.uniform(0.2, 0.6),
        }

    def _get_dominant_regions(self, brain_response: Dict) -> List[str]:
        """Get the top 3 most activated brain regions"""

        sorted_regions = sorted(
            brain_response.items(), key=lambda x: x[1], reverse=True
        )

        return [region for region, _ in sorted_regions[:3]]

    def get_population_summary(self, population: List[Dict]) -> Dict:
        """Get summary statistics for the population"""

        if not population:
            return {}

        # Aggregate region activations
        all_responses = [p["brain_response"] for p in population]

        summary = {}
        for region in all_responses[0].keys():
            values = [r[region] for r in all_responses]
            summary[region] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }

        return {
            "size": len(population),
            "region_activations": summary,
            "dominant_regions_overall": self._get_overall_dominant_regions(population),
        }

    def _get_overall_dominant_regions(self, population: List[Dict]) -> List[str]:
        """Get the most common dominant regions across population"""

        from collections import Counter

        all_dominant = []
        for p in population:
            all_dominant.extend(p["dominant_regions"])

        counter = Counter(all_dominant)
        return [region for region, _ in counter.most_common(3)]

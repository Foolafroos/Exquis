import os
import requests
from typing import Optional


class NVIDIAVisionClient:
    """NVIDIA NIM Vision Language Model client for image captioning"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta/llama-3.2-11b-vision-instruct",
    ):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.model = model
        self.base_url = "https://integrate.api.nvidia.com/v1"

    def describe_image(
        self,
        image_url: str,
        prompt: str = "Describe this image in detail.",
        detail: str = "auto",
    ) -> str:
        """Generate a detailed description of an image"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url, "detail": detail},
                        },
                    ],
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise Exception(f"NVIDIA Vision API error: {response.text}")

        return response.json()["choices"][0]["message"]["content"]

    def describe_image_base64(
        self, base64_image: str, prompt: str = "Describe this image in detail."
    ) -> str:
        """Generate a description from a base64 encoded image"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Convert base64 to data URL format
        image_data_url = f"data:image/jpeg;base64,{base64_image}"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}},
                    ],
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != 200:
            raise Exception(f"NVIDIA Vision API error: {response.text}")

        return response.json()["choices"][0]["message"]["content"]

    def extract_visual_elements(self, image_url: str) -> dict:
        """Extract structured visual elements from an image"""

        prompt = """Extract the following information from this image:
        - Main objects and their positions
        - Colors and lighting mood
        - Text visible (if any)
        - People (number, actions, expressions)
        - Environment setting
        - Any notable details
        
        Format as a structured description."""

        description = self.describe_image(image_url, prompt)

        return {
            "full_description": description,
            "visual_elements": self._parse_elements(description),
        }

    def _parse_elements(self, description: str) -> dict:
        """Parse description into structured elements"""

        elements = {
            "objects": [],
            "colors": [],
            "mood": "unknown",
            "text_content": None,
            "people_count": 0,
            "setting": "unknown",
        }

        # Basic parsing - could be enhanced with LLM
        desc_lower = description.lower()

        # Detect mood/colors
        if any(w in desc_lower for w in ["bright", "vibrant", "colorful"]):
            elements["colors"].append("bright")
        if any(w in desc_lower for w in ["dark", "shadow", "dim"]):
            elements["colors"].append("dark")
        if any(w in desc_lower for w in ["warm", "sunset", "golden"]):
            elements["colors"].append("warm")
        if any(w in desc_lower for w in ["cool", "blue", "cold"]):
            elements["colors"].append("cool")

        # Detect mood
        if any(w in desc_lower for w in ["peaceful", "calm", "serene"]):
            elements["mood"] = "peaceful"
        elif any(w in desc_lower for w in ["energetic", "dynamic", "active"]):
            elements["mood"] = "energetic"
        elif any(w in desc_lower for w in ["sad", "melancholy", "dark"]):
            elements["mood"] = "melancholy"

        return elements

    def health_check(self) -> bool:
        """Check if the API is accessible"""
        try:
            # Use a placeholder image for health check
            test_url = "https://via.placeholder.com/100"
            self.describe_image(test_url, "Is this a valid test?", detail="low")
            return True
        except Exception as e:
            print(f"Health check failed: {e}")
            return False


class FallbackVisionClient:
    """Fallback vision clients for when NVIDIA NIM is unavailable"""

    @staticmethod
    def openai_vision(
        image_url: str, api_key: str, prompt: str = "Describe this image"
    ) -> str:
        """Use OpenAI GPT-4 Vision as fallback"""
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_tokens=1024,
        )

        return response.choices[0].message.content

    @staticmethod
    def anthropic_vision(
        image_url: str, api_key: str, prompt: str = "Describe this image"
    ) -> str:
        """Use Anthropic Claude as fallback"""
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        # Anthropic doesn't have native vision yet, so we use text-only approach
        # In production, would need different fallback
        raise NotImplementedError("Anthropic vision not yet available")

    @staticmethod
    def google_vision(
        image_url: str, api_key: str, prompt: str = "Describe this image"
    ) -> str:
        """Use Google Gemini as fallback"""
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.0-flash")

        # Download and process image
        import urllib.request
        from PIL import Image
        import io

        try:
            with urllib.request.urlopen(image_url) as response:
                image_data = response.read()

            image = Image.open(io.BytesIO(image_data))

            response = model.generate_content([prompt, image])

            return response.text
        except Exception as e:
            raise Exception(f"Google Vision failed: {e}")

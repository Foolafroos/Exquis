import os
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        pass

    @abstractmethod
    def generate_batch(self, prompts: List[str], **kwargs) -> List[str]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass


class NVIDIAProvider(LLMProvider):
    """NVIDIA NIM API provider"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "nvidia/nemotron-4-340b-instruct",
    ):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.model = model
        self.base_url = "https://integrate.api.nvidia.com/v1"

    def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        import requests

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
            },
            timeout=60,
        )

        if response.status_code != 200:
            raise Exception(f"NVIDIA API error: {response.text}")

        return response.json()["choices"][0]["message"]["content"]

    def generate_batch(self, prompts: List[str], **kwargs) -> List[str]:
        return [self.generate(p, **kwargs) for p in prompts]

    def health_check(self) -> bool:
        try:
            self.generate("Hello", max_tokens=10)
            return True
        except:
            return False


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        from openai import OpenAI

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )

        return response.choices[0].message.content

    def generate_batch(self, prompts: List[str], **kwargs) -> List[str]:
        return [self.generate(p, **kwargs) for p in prompts]

    def health_check(self) -> bool:
        try:
            self.generate("Hello", max_tokens=10)
            return True
        except:
            return False


class AnthropicProvider(LLMProvider):
    """Anthropic API provider"""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"
    ):
        import anthropic

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        messages = [{"role": "user", "content": prompt}]

        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
        )

        return response.content[0].text

    def generate_batch(self, prompts: List[str], **kwargs) -> List[str]:
        return [self.generate(p, **kwargs) for p in prompts]

    def health_check(self) -> bool:
        try:
            self.generate("Hello", max_tokens=10)
            return True
        except:
            return False


class GoogleProvider(LLMProvider):
    """Google Gemini API provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        import google.generativeai as genai

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        genai.configure(api_key=self.api_key)

    def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        import google.generativeai as genai

        generation_config = {
            "temperature": kwargs.get("temperature", 0.7),
            "max_output_tokens": kwargs.get("max_tokens", 2048),
        }

        model = genai.GenerativeModel(self.model)

        contents = [prompt]
        if system_prompt:
            contents.append(system_prompt)

        response = model.generate_content(contents, generation_config=generation_config)

        return response.text

    def generate_batch(self, prompts: List[str], **kwargs) -> List[str]:
        return [self.generate(p, **kwargs) for p in prompts]

    def health_check(self) -> bool:
        try:
            self.generate("Hello", max_tokens=10)
            return True
        except:
            return False


class OllamaProvider(LLMProvider):
    """Ollama local provider"""

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:32b"
    ):
        self.base_url = base_url
        self.model = model

    def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        import requests

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "options": {"temperature": kwargs.get("temperature", 0.7)},
            },
            timeout=120,
        )

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")

        return response.json()["choices"][0]["message"]["content"]

    def generate_batch(self, prompts: List[str], **kwargs) -> List[str]:
        return [self.generate(p, **kwargs) for p in prompts]

    def health_check(self) -> bool:
        try:
            self.generate("Hello", max_tokens=10)
            return True
        except:
            return False


class LLMFactory:
    """Factory for creating LLM providers with fallback support"""

    PROVIDERS = {
        "nvidia_nim": NVIDIAProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "ollama": OllamaProvider,
    }

    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> LLMProvider:
        if provider_type not in LLMFactory.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_type}")

        provider_class = LLMFactory.PROVIDERS[provider_type]
        return provider_class(**kwargs)

    @staticmethod
    def create_with_fallback(
        primary_type: str, fallback_types: List[str], **kwargs
    ) -> tuple:
        """Create primary provider with fallback chain"""
        primary = LLMFactory.create_provider(primary_type, **kwargs)

        fallbacks = []
        for fallback_type in fallback_types:
            try:
                fallback = LLMFactory.create_provider(fallback_type, **kwargs)
                fallbacks.append(fallback)
            except Exception as e:
                print(f"Warning: Could not create fallback {fallback_type}: {e}")

        return primary, fallbacks

    @staticmethod
    def generate_with_fallback(
        primary: LLMProvider,
        fallbacks: List[LLMProvider],
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate with automatic fallback on failure"""
        try:
            return primary.generate(prompt, system_prompt, **kwargs)
        except Exception as e:
            print(f"Primary provider failed: {e}")

            for i, fallback in enumerate(fallbacks):
                try:
                    print(f"Falling back to provider {i + 1}...")
                    return fallback.generate(prompt, system_prompt, **kwargs)
                except Exception as e2:
                    print(f"Fallback {i + 1} failed: {e2}")
                    continue

            raise Exception("All LLM providers failed")

from typing import Dict, List, Optional
import json
import random


class BrainProfile:
    """Brain profile for a single agent derived from TRIBE + CLIP variation"""

    def __init__(self, profile_data: Dict):
        self.id = profile_data.get("id", "unknown")
        self.brain_response = profile_data.get("brain_response", {})
        self.personality = profile_data.get("personality", {})
        self.dominant_regions = profile_data.get("dominant_regions", [])
        self.variation_seed = profile_data.get("variation_seed", 0)

    def get_reaction_bias(self) -> Dict:
        """Get reaction biases based on brain profile

        These biases influence how the agent reacts to visual stimuli
        """

        bias = {
            "focus_on_visual_details": self.brain_response.get("Vis", 0.5),
            "emotional_reactivity": self.brain_response.get("Salience", 0.5),
            "analytical_processing": self.brain_response.get("Cont", 0.5),
            "introspective_response": self.brain_response.get("Default", 0.5),
            "attentional_focus": self.brain_response.get("DorsAttn", 0.5),
        }

        return bias

    def get_prompt_context(self) -> str:
        """Generate context prompt for LLM based on brain profile"""

        bias = self.get_reaction_bias()

        context = f"""You are viewing an image with the following brain response profile:
        - Visual processing: {bias["focus_on_visual_details"]:.2f}
        - Emotional reactivity: {bias["emotional_reactivity"]:.2f}
        - Analytical processing: {bias["analytical_processing"]:.2f}
        - Introspective response: {bias["introspective_response"]:.2f}
        - Attentional focus: {bias["attentional_focus"]:.2f}
        
        Your dominant brain regions: {", ".join(self.dominant_regions)}
        
        Your personality traits:
        - Visual thinker: {self.personality.get("visual_thinker", False)}
        - Analytical: {self.personality.get("analytical", False)}
        - Introspective: {self.personality.get("introspective", False)}
        - Reactive: {self.personality.get("reactive", False)}
        - Extroversion: {self.personality.get("extroversion", 0.5):.2f}
        - Openness: {self.personality.get("openness", 0.5):.2f}
        
        Based on your unique brain response profile, generate a natural social media reaction to this image."""

        return context


class PersonalityMapper:
    """Map brain profiles to MiroFish agent personalities"""

    @staticmethod
    def map_to_mirofish_personality(brain_profile: BrainProfile) -> Dict:
        """Convert brain profile to MiroFish-style personality parameters

        MiroFish uses: opinion, reaction_speed, influence, etc.
        """

        bias = brain_profile.get_reaction_bias()
        personality = brain_profile.personality

        # Map brain-based traits to MiroFish parameters

        # Opinion based on emotional vs analytical balance
        emotional_score = bias.get("emotional_reactivity", 0.5)
        analytical_score = bias.get("analytical_processing", 0.5)

        # Higher emotional = more opinionated, higher analytical = more nuanced
        opinion_strength = (emotional_score + analytical_score) / 2

        # Reaction speed based on salience network
        salience = bias.get("emotional_reactivity", 0.5)
        reaction_speed = 0.5 + (salience * 0.5)  # 0.5 to 1.0

        # Influence based on default mode (introspection correlates with thought leadership)
        introspection = bias.get("introspective_response", 0.5)
        influence = 0.3 + (introspection * 0.5)  # 0.3 to 0.8

        # Memory retention based on limbic system (emotional memory)
        # We'll add this as a parameter

        return {
            "opinion": {
                "on_image": random.uniform(0.2, 0.8),
                "confidence": opinion_strength,
                "polarization": emotional_score * 0.5,
            },
            "reaction_speed": reaction_speed,
            "influence": influence,
            "personality_type": brain_profile._get_personality_type(),
            "preferred_aspect": brain_profile._get_preferred_aspect(),
        }

    def _get_personality_type(self) -> str:
        """Determine personality type based on brain profile"""

        bias = self.get_reaction_bias()

        # Classification based on dominant processing style
        if bias["analytical_processing"] > 0.6:
            return "analyst"
        elif bias["introspective_response"] > 0.6:
            return "contemplator"
        elif bias["focus_on_visual_details"] > 0.6:
            return "visualizer"
        elif bias["emotional_reactivity"] > 0.6:
            return "reactor"
        else:
            return "balanced"

    def _get_preferred_aspect(self) -> str:
        """Get which aspect of the image this person would focus on"""

        bias = self.get_reaction_bias()

        aspects = {
            "focus_on_visual_details": "aesthetics and composition",
            "emotional_reactivity": "emotional impact",
            "analytical_processing": "content and meaning",
            "introspective_response": "personal associations",
            "attentional_focus": "specific elements",
        }

        # Return the highest-scoring aspect
        max_key = max(bias, key=bias.get)
        return aspects.get(max_key, "general aspects")


class ReactionGenerator:
    """Generate reactions from agents based on their brain profiles"""

    def __init__(self, llm_provider):
        self.llm = llm_provider

    def generate_single_reaction(
        self,
        brain_profile: BrainProfile,
        image_caption: str,
        interaction_mode: str = "post",
    ) -> Dict:
        """Generate a reaction from an agent based on their brain profile

        Args:
            brain_profile: The agent's brain profile
            image_caption: Description of the image
            interaction_mode: Type of interaction (post, reply, debate)

        Returns:
            Generated reaction
        """

        context = brain_profile.get_prompt_context()

        # Different prompts based on interaction mode
        if interaction_mode == "post":
            prompt = f"""{context}

Image description: {image_caption}

Generate a short social media post (1-3 sentences) reacting to this image.
Be authentic to your personality and brain-based response pattern."""

        elif interaction_mode == "reply":
            prompt = f"""{context}

Someone posted about an image: "{image_caption}"

Generate a reply to this post (1-2 sentences).
Be authentic to your personality and brain-based response pattern."""

        elif interaction_mode == "debate":
            prompt = f"""{context}

An image has been described as: {image_caption}

Someone has a different opinion about this image.
Generate a response defending your view (2-3 sentences).
Be passionate but reasonable."""

        else:
            prompt = f"""{context}

Image description: {image_caption}

Generate a reaction to this image (2-3 sentences)."""

        try:
            response = self.llm.generate(
                prompt=prompt,
                system_prompt="You are a real person on social media. Your responses should feel authentic, natural, and varied. Not everyone agrees about everything. Some people are positive, some are negative, some are analytical, some are emotional.",
                temperature=0.8,
                max_tokens=150,
            )

            return {
                "agent_id": brain_profile.id,
                "reaction": response,
                "interaction_mode": interaction_mode,
                "brain_profile": {
                    "dominant_regions": brain_profile.dominant_regions,
                    "personality_type": brain_profile._get_personality_type(),
                },
                "success": True,
            }

        except Exception as e:
            return {
                "agent_id": brain_profile.id,
                "reaction": f"Can't react right now: {str(e)}",
                "interaction_mode": interaction_mode,
                "success": False,
                "error": str(e),
            }

    def generate_batch_reactions(
        self,
        brain_profiles: List[BrainProfile],
        image_caption: str,
        interaction_mode: str = "post",
    ) -> List[Dict]:
        """Generate reactions for multiple agents"""

        reactions = []

        for profile in brain_profiles:
            reaction = self.generate_single_reaction(
                profile, image_caption, interaction_mode
            )
            reactions.append(reaction)

        return reactions


class AgentManager:
    """Manage agents and their brain profiles"""

    def __init__(self):
        self.agents: Dict[str, BrainProfile] = {}

    def add_agent(self, brain_profile: BrainProfile):
        """Add an agent with a brain profile"""
        self.agents[brain_profile.id] = brain_profile

    def add_agents(self, brain_profiles: List[BrainProfile]):
        """Add multiple agents"""
        for profile in brain_profiles:
            self.add_agent(profile)

    def get_agent(self, agent_id: str) -> Optional[BrainProfile]:
        """Get a specific agent"""
        return self.agents.get(agent_id)

    def get_all_agents(self) -> List[BrainProfile]:
        """Get all agents"""
        return list(self.agents.values())

    def get_agents_by_type(self, personality_type: str) -> List[BrainProfile]:
        """Get agents of a specific personality type"""
        return [
            agent
            for agent in self.agents.values()
            if agent._get_personality_type() == personality_type
        ]

    def get_agent_count(self) -> int:
        """Get total number of agents"""
        return len(self.agents)

    def clear(self):
        """Clear all agents"""
        self.agents.clear()

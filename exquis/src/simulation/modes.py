from typing import List, Dict, Optional
from enum import Enum
import random


class InteractionMode(Enum):
    """Available interaction modes for the simulation"""

    POSTS = "posts"  # Individual posts only
    DEBATE = "debate"  # Agents discuss/argue
    CONSENSUS = "consensus"  # Group opinion forms
    ALL = "all"  # Run all modes sequentially


class SimulationMode:
    """Base class for simulation modes"""

    def __init__(self, llm_provider, agent_manager):
        self.llm = llm_provider
        self.agents = agent_manager

    def run(self, image_caption: str, config: Dict) -> Dict:
        """Run the simulation mode

        Args:
            image_caption: Description of the image
            config: Configuration for the simulation

        Returns:
            Results of the simulation
        """
        raise NotImplementedError


class PostsMode(SimulationMode):
    """Individual posts mode - each agent posts their reaction"""

    def run(self, image_caption: str, config: Dict) -> Dict:
        """Generate individual posts from all agents"""

        from src.agents.brain_profile import ReactionGenerator

        generator = ReactionGenerator(self.llm)

        agents = self.agents.get_all_agents()

        # Generate posts in batches for efficiency
        batch_size = config.get("batch_size", 10)

        posts = []
        for i in range(0, len(agents), batch_size):
            batch = agents[i : i + batch_size]
            batch_posts = generator.generate_batch_reactions(
                batch, image_caption, "post"
            )
            posts.extend(batch_posts)

        # Calculate sentiment distribution
        sentiment = self._calculate_sentiment(posts)

        return {
            "mode": "posts",
            "total_posts": len(posts),
            "posts": posts,
            "sentiment": sentiment,
            "dominant_personality_types": self._get_personality_distribution(agents),
        }

    def _calculate_sentiment(self, posts: List[Dict]) -> Dict:
        """Calculate sentiment distribution of posts"""

        # Simple heuristic - in production, use proper sentiment analysis
        positive = 0
        negative = 0
        neutral = 0

        positive_keywords = [
            "love",
            "great",
            "amazing",
            "beautiful",
            "nice",
            "good",
            "wonderful",
            "perfect",
        ]
        negative_keywords = [
            "hate",
            "bad",
            "ugly",
            "terrible",
            "worst",
            "disappointing",
            "awful",
        ]

        for post in posts:
            text = post.get("reaction", "").lower()

            if any(kw in text for kw in positive_keywords):
                positive += 1
            elif any(kw in text for kw in negative_keywords):
                negative += 1
            else:
                neutral += 1

        total = len(posts) if posts else 1

        return {
            "positive": positive / total * 100,
            "negative": negative / total * 100,
            "neutral": neutral / total * 100,
        }

    def _get_personality_distribution(self, agents: List) -> Dict:
        """Get distribution of personality types"""

        from collections import Counter

        types = [agent._get_personality_type() for agent in agents]
        counter = Counter(types)

        return {k: v / len(agents) * 100 for k, v in counter.items()}


class DebateMode(SimulationMode):
    """Debate mode - agents argue with each other"""

    def run(self, image_caption: str, config: Dict) -> Dict:
        """Run debate simulation between agents"""

        from src.agents.brain_profile import ReactionGenerator

        generator = ReactionGenerator(self.llm)
        agents = self.agents.get_all_agents()

        # Select a subset for debate (for efficiency)
        debate_size = min(config.get("debate_participants", 20), len(agents))
        debaters = random.sample(agents, debate_size)

        # Create debate pairs
        debates = []
        for i in range(0, len(debaters) - 1, 2):
            agent1 = debaters[i]
            agent2 = debaters[i + 1]

            # Generate debate exchange
            debate = self._generate_debate_pair(
                agent1, agent2, image_caption, generator
            )
            debates.append(debate)

        return {
            "mode": "debate",
            "total_debates": len(debates),
            "debates": debates,
            "debate_topics": self._extract_debate_topics(debates),
        }

    def _generate_debate_pair(self, agent1, agent2, image_caption, generator) -> Dict:
        """Generate a debate exchange between two agents"""

        # Get each agent's initial position
        reaction1 = generator.generate_single_reaction(agent1, image_caption, "post")
        reaction2 = generator.generate_single_reaction(agent2, image_caption, "post")

        # Generate responses to each other
        prompt1 = f"""You and another person are debating about this image: {image_caption}

Their view: "{reaction2["reaction"]}"

Respond to their观点, defending your own view (2-3 sentences):"""

        prompt2 = f"""You and another person are debating about this image: {image_caption}

Their view: "{reaction1["reaction"]}"

Respond to their view, defending your own view (2-3 sentences):"""

        try:
            response1 = self.llm.generate(prompt1, max_tokens=150)
            response2 = self.llm.generate(prompt2, max_tokens=150)
        except:
            response1 = "Can't respond right now"
            response2 = "Can't respond right now"

        return {
            "agent1": {
                "id": agent1.id,
                "initial_reaction": reaction1["reaction"],
                "rebuttal": response1,
            },
            "agent2": {
                "id": agent2.id,
                "initial_reaction": reaction2["reaction"],
                "rebuttal": response2,
            },
            "topic": "image_reaction",
        }

    def _extract_debate_topics(self, debates: List[Dict]) -> List[str]:
        """Extract common topics from debates"""

        # Simple extraction - in production, use NLP
        topics = []
        for debate in debates[:5]:
            topics.append("Visual aesthetics and composition")

        return topics


class ConsensusMode(SimulationMode):
    """Consensus mode - group opinion evolves over time"""

    def run(self, image_caption: str, config: Dict) -> Dict:
        """Run consensus formation simulation"""

        from src.agents.brain_profile import ReactionGenerator

        generator = ReactionGenerator(self.llm)
        agents = self.agents.get_all_agents()

        rounds = config.get("consensus_rounds", 3)

        # Initial opinions
        initial_posts = generator.generate_batch_reactions(
            agents[: min(50, len(agents))], image_caption, "post"
        )

        # Track opinion evolution
        evolution = {
            "round_0": {
                "posts": initial_posts,
                "sentiment": self._calculate_sentiment(initial_posts),
            }
        }

        # Subsequent rounds with influence from others
        for round_num in range(1, rounds):
            # Sample subset of posts from previous round to show as "influence"
            sample_size = min(10, len(evolution[f"round_{round_num - 1}"]["posts"]))
            influence_posts = random.sample(
                evolution[f"round_{round_num - 1}"]["posts"], sample_size
            )

            influence_text = "\n".join(
                [f"- {p['reaction']}" for p in influence_posts[:5]]
            )

            # Generate new responses with social influence
            influenced_posts = []
            for agent in agents[: min(30, len(agents))]:
                prompt = f"""You see various opinions about an image:
{influence_text}

Image: {image_caption}

After seeing these opinions, what's your current view? (1-2 sentences)"""

                try:
                    response = self.llm.generate(prompt, max_tokens=100)
                    influenced_posts.append(
                        {"agent_id": agent.id, "reaction": response, "round": round_num}
                    )
                except:
                    pass

            evolution[f"round_{round_num}"] = {
                "posts": influenced_posts,
                "sentiment": self._calculate_sentiment(influenced_posts),
            }

        return {
            "mode": "consensus",
            "rounds": rounds,
            "evolution": evolution,
            "final_sentiment": evolution[f"round_{rounds - 1}"]["sentiment"]
            if rounds > 0
            else {},
        }

    def _calculate_sentiment(self, posts: List[Dict]) -> Dict:
        """Calculate sentiment distribution"""

        # Same as PostsMode - could be shared
        positive = 0
        negative = 0
        neutral = 0

        positive_keywords = [
            "love",
            "great",
            "amazing",
            "beautiful",
            "nice",
            "good",
            "wonderful",
            "perfect",
        ]
        negative_keywords = [
            "hate",
            "bad",
            "ugly",
            "terrible",
            "worst",
            "disappointing",
            "awful",
        ]

        for post in posts:
            text = post.get("reaction", "").lower()

            if any(kw in text for kw in positive_keywords):
                positive += 1
            elif any(kw in text for kw in negative_keywords):
                negative += 1
            else:
                neutral += 1

        total = len(posts) if posts else 1

        return {
            "positive": positive / total * 100,
            "negative": negative / total * 100,
            "neutral": neutral / total * 100,
        }


class SimulationOrchestrator:
    """Orchestrate different simulation modes"""

    def __init__(self, llm_provider, agent_manager):
        self.llm = llm_provider
        self.agents = agent_manager

        self.modes = {
            "posts": PostsMode(llm_provider, agent_manager),
            "debate": DebateMode(llm_provider, agent_manager),
            "consensus": ConsensusMode(llm_provider, agent_manager),
        }

    def run(self, mode: str, image_caption: str, config: Dict) -> Dict:
        """Run a specific simulation mode

        Args:
            mode: Mode to run (posts, debate, consensus, all)
            image_caption: Image description
            config: Configuration

        Returns:
            Results
        """

        if mode == "all":
            # Run all modes sequentially
            results = {}
            for mode_name in ["posts", "debate", "consensus"]:
                print(f"Running {mode_name} mode...")
                results[mode_name] = self.modes[mode_name].run(image_caption, config)
            return results

        elif mode in self.modes:
            return self.modes[mode].run(image_caption, config)

        else:
            raise ValueError(f"Unknown mode: {mode}")

    def run_with_timeout(
        self, mode: str, image_caption: str, config: Dict, timeout_seconds: int = 300
    ) -> Dict:
        """Run with timeout handling"""

        import signal
        from functools import wraps

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Simulation timed out after {timeout_seconds} seconds")

        # Set timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)

        try:
            result = self.run(mode, image_caption, config)
            signal.alarm(0)  # Cancel alarm
            return result
        except TimeoutError as e:
            signal.alarm(0)
            return {"error": str(e), "partial_results": "Simulation did not complete"}

"""
NPC Personality Manager - Bonus Feature
Manages NPC personalities and evolution based on interactions
"""

from typing import Dict, List
import json


class NPCPersonalityManager:
    """Manages NPC personalities and their evolution over time"""
    
    def __init__(self):
        self.npcs = {}  # npc_name -> personality_vector
        
        # Default personality traits
        self.default_traits = {
            "friendly": 0.5,
            "greedy": 0.5,
            "fearful": 0.5,
            "wise": 0.5,
            "aggressive": 0.5,
            "honest": 0.5,
            "loyal": 0.5
        }
        
        print("✓ NPC Personality Manager initialized")
    
    def initialize_npc(self, npc_name: str, custom_traits: Dict[str, float] = None):
        """Initialize a new NPC with personality traits"""
        npc_key = npc_name.lower().replace(" ", "_")
        
        if npc_key in self.npcs:
            return  # Already exists
        
        # Start with defaults and override with custom traits
        personality = self.default_traits.copy()
        if custom_traits:
            personality.update(custom_traits)
        
        self.npcs[npc_key] = {
            "name": npc_name,
            "personality": personality,
            "interaction_count": 0,
            "relationship_score": 0.5,  # Neutral starting point
            "memory": []
        }
        
        print(f"✓ Initialized NPC: {npc_name}")
    
    def analyze_sentiment(self, player_input: str, dm_response: str) -> Dict[str, float]:
        """Simple sentiment analysis to determine interaction impact"""
        # Keywords for different sentiments
        positive_keywords = ["thank", "help", "gift", "friend", "save", "protect"]
        negative_keywords = ["attack", "steal", "threaten", "betray", "lie", "harm"]
        
        player_lower = player_input.lower()
        dm_lower = dm_response.lower()
        
        sentiment = {
            "friendliness_delta": 0.0,
            "trust_delta": 0.0,
            "fear_delta": 0.0
        }
        
        # Analyze player input
        for keyword in positive_keywords:
            if keyword in player_lower:
                sentiment["friendliness_delta"] += 0.05
                sentiment["trust_delta"] += 0.03
        
        for keyword in negative_keywords:
            if keyword in player_lower:
                sentiment["friendliness_delta"] -= 0.08
                sentiment["trust_delta"] -= 0.05
                sentiment["fear_delta"] += 0.06
        
        return sentiment
    
    def update_npc_personality(
        self, 
        npc_name: str, 
        player_input: str, 
        dm_response: str
    ):
        """Update NPC personality based on interaction"""
        npc_key = npc_name.lower().replace(" ", "_")
        
        # Initialize if doesn't exist
        if npc_key not in self.npcs:
            self.initialize_npc(npc_name)
        
        npc = self.npcs[npc_key]
        
        # Analyze sentiment of interaction
        sentiment = self.analyze_sentiment(player_input, dm_response)
        
        # Update personality traits
        personality = npc["personality"]
        
        # Friendly trait
        personality["friendly"] = self._clamp(
            personality["friendly"] + sentiment["friendliness_delta"],
            0.0, 1.0
        )
        
        # Honest/Trust related (inverse of fearful)
        personality["honest"] = self._clamp(
            personality["honest"] + sentiment["trust_delta"],
            0.0, 1.0
        )
        
        # Fearful trait
        personality["fearful"] = self._clamp(
            personality["fearful"] + sentiment["fear_delta"],
            0.0, 1.0
        )
        
        # Loyal trait (increases with positive interactions)
        if sentiment["friendliness_delta"] > 0:
            personality["loyal"] = self._clamp(
                personality["loyal"] + 0.02,
                0.0, 1.0
            )
        
        # Update relationship score
        relationship_change = (
            sentiment["friendliness_delta"] + 
            sentiment["trust_delta"] - 
            sentiment["fear_delta"] * 0.5
        )
        npc["relationship_score"] = self._clamp(
            npc["relationship_score"] + relationship_change,
            0.0, 1.0
        )
        
        # Increment interaction count
        npc["interaction_count"] += 1
        
        # Store interaction memory
        npc["memory"].append({
            "player_action": player_input,
            "npc_response_context": dm_response[:100],  # Store snippet
            "sentiment": sentiment,
            "turn": npc["interaction_count"]
        })
        
        # Keep only last 10 interactions
        if len(npc["memory"]) > 10:
            npc["memory"] = npc["memory"][-10:]
    
    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp value between min and max"""
        return max(min_val, min(max_val, value))
    
    def get_npc_personality(self, npc_name: str) -> Dict:
        """Get current personality state of an NPC"""
        npc_key = npc_name.lower().replace(" ", "_")
        
        if npc_key not in self.npcs:
            return None
        
        return self.npcs[npc_key].copy()
    
    def get_personality_description(self, npc_name: str) -> str:
        """Get human-readable personality description"""
        npc = self.get_npc_personality(npc_name)
        
        if not npc:
            return f"{npc_name} is unknown."
        
        personality = npc["personality"]
        relationship = npc["relationship_score"]
        
        # Generate description based on traits
        traits = []
        
        if personality["friendly"] > 0.7:
            traits.append("very friendly")
        elif personality["friendly"] < 0.3:
            traits.append("cold and distant")
        
        if personality["wise"] > 0.7:
            traits.append("wise")
        
        if personality["fearful"] > 0.7:
            traits.append("fearful")
        elif personality["fearful"] < 0.3:
            traits.append("brave")
        
        if personality["honest"] > 0.7:
            traits.append("trustworthy")
        elif personality["honest"] < 0.3:
            traits.append("deceptive")
        
        if personality["greedy"] > 0.7:
            traits.append("greedy")
        
        if personality["loyal"] > 0.7:
            traits.append("loyal")
        
        # Relationship status
        if relationship > 0.8:
            rel_status = "considers you a close ally"
        elif relationship > 0.6:
            rel_status = "is friendly toward you"
        elif relationship > 0.4:
            rel_status = "is neutral toward you"
        elif relationship > 0.2:
            rel_status = "is wary of you"
        else:
            rel_status = "is hostile toward you"
        
        trait_str = ", ".join(traits) if traits else "average"
        
        return f"{npc['name']} is {trait_str} and {rel_status}. (Interactions: {npc['interaction_count']})"
    
    def get_all_npcs(self) -> List[str]:
        """Get list of all tracked NPCs"""
        return [npc["name"] for npc in self.npcs.values()]
    
    def export_npc_data(self) -> str:
        """Export NPC data as JSON"""
        return json.dumps(self.npcs, indent=2)
    def export_personality_log(self) -> str:
        return json.dumps(self.npcs, indent=2)

    def get_recent_npc_interactions(self, npc_name: str, count: int=3) -> List[Dict]:
        npc = self.get_npc_personality(npc_name)
        if npc and npc.get("memory"):
            return npc["memory"][-count:]
        return []

    
    def get_npc_context_for_dm(self, npc_name: str) -> str:
        """Get personality context string for DM to use"""
        npc = self.get_npc_personality(npc_name)
        
        if not npc:
            return ""
        
        personality = npc["personality"]
        relationship = npc["relationship_score"]
        
        context = f"\n--- NPC Personality Context for {npc['name']} ---\n"
        context += f"Relationship Score: {relationship:.2f}\n"
        context += f"Traits: "
        context += ", ".join([f"{k}={v:.2f}" for k, v in personality.items()])
        context += f"\nInteractions: {npc['interaction_count']}\n"
        
        if npc["memory"]:
            context += "\nRecent interactions:\n"
            for mem in npc["memory"][-3:]:
                context += f"- Turn {mem['turn']}: {mem['player_action'][:50]}...\n"
        
        return context
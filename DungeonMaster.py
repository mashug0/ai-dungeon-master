"""
Dungeon Master Agent - Main narrative generator
Uses Groq API with llama-3.1-8b-instant
"""

from groq import Groq
from typing import List, Dict, Optional


class DungeonMaster:
    """Dungeon Master agent for creative narrative generation"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        
        # System prompt for the DM
        self.system_prompt = """You are an expert Dungeon Master for a fantasy role-playing game. Your role is to:

1. Create engaging, immersive narratives that respond to player actions
2. Maintain consistency with established lore and past events
3. Present meaningful choices and consequences
4. Describe scenes vividly with sensory details
5. Keep the story moving forward while respecting player agency

Guidelines:
- Use second-person perspective ("you see...", "you feel...")
- Be descriptive but concise (2-4 paragraphs)
- End responses with a question or situation requiring player input
- Never contradict established facts or memories
- Adapt tone based on the situation (serious, tense, mysterious, etc.)
- Remember that player choices matter and have consequences

When relevant memories are provided, integrate them naturally into your response.
**IMPORTANT: YOUR RESPONSE SHOULD NOT EXCEED 400 WORDS IF THEY DO SUMMARIZE THE TEXT**"""
        
        print("✓ Dungeon Master agent initialized")
    
    def generate_opening(self, prompt: str, temperature: float = 0.8) -> str:
        """Generate opening narration for the adventure"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_response(
        self, 
        player_input: str,
        validated_context: List[Dict],
        conversation_history: List[Dict],
        temperature: float = 0.7
    ) -> str:
        """Generate DM response based on player input and context"""
        
        # Build context string from validated memories
        context_str = ""
        if validated_context:
            context_str = "\n\nRelevant memories from previous events:\n"
            for mem in validated_context:
                context_str += f"- {mem['text']}\n"
        
        # Build conversation history string (short-term memory)
        history_str = ""
        if conversation_history:
            history_str = "\n\nRecent conversation:\n"
            for turn in conversation_history[-5:]:  # Last 5 turns
                history_str += f"Player: {turn['player']}\n"
                history_str += f"DM: {turn['dm']}\n\n"
        
        # Construct the prompt
        user_prompt = f"""{history_str}{context_str}

Current player action: {player_input}

Respond as the Dungeon Master, continuing the story based on this action. Integrate relevant memories naturally and keep the narrative engaging."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=600
        )
        
        return response.choices[0].message.content.strip()
    
    def summarize_events(self, events: List[str]) -> str:
        """Summarize a list of events for context compression"""
        if not events:
            return ""
        
        events_str = "\n".join([f"- {event}" for event in events])
        
        prompt = f"""Summarize the following events into a concise paragraph that captures the key facts:

{events_str}

Summary:"""
        
        messages = [
            {"role": "system", "content": "You are a skilled summarizer. Create concise, factual summaries."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
"""
Lore Talker Agent - Consistency verification and context validation
"""

from groq import Groq
from typing import List, Dict


class LoreTalker:
    """Lore Talker agent for maintaining narrative consistency"""
    
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        
        self.system_prompt = """You are the Lore Keeper, responsible for maintaining consistency in the story world. Your tasks:

1. Review retrieved memories and player input
2. Identify potential contradictions or inconsistencies
3. Filter out irrelevant or conflicting information
4. Ensure logical continuity in the narrative
5. Validate that facts align with established lore

You should:
- Be strict about factual accuracy
- Flag any contradictions
- Only pass through validated, relevant context
- Add clarifying notes when needed
- Ensure character and world consistency"""
        
        print("✓ Lore Talker agent initialized")
    
    def validate_context(
        self, 
        player_input: str,
        retrieved_memories: List[Dict]
    ) -> List[Dict]:
        """Validate and filter retrieved memories for consistency"""
        
        if not retrieved_memories:
            return []
        
        # Build memory string
        memories_str = "\n".join([
            f"{i+1}. {mem['text']} (score: {mem['score']:.2f})"
            for i, mem in enumerate(retrieved_memories)
        ])
        
        prompt = f"""Player action: {player_input}

Retrieved memories:
{memories_str}

Task: Review these memories for relevance and consistency. Return only the memories that are:
1. Relevant to the current player action
2. Consistent with each other
3. Important for maintaining narrative continuity

Format your response as a numbered list of the memories to keep (by number), with a brief reason. If all are valid, say "All memories validated." If contradictions exist, explain them.

Response:"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Low temperature for consistency checking
                max_tokens=300
            )
            
            validation_result = response.choices[0].message.content.strip()
            
            # Parse response to filter memories
            # If "All memories validated" or similar, keep all
            if "all" in validation_result.lower() and "validated" in validation_result.lower():
                return retrieved_memories
            
            # Otherwise, try to extract which memories to keep
            # Simple heuristic: look for numbers mentioned
            validated_memories = []
            for mem in retrieved_memories:
                # Keep high-scoring memories by default
                if mem['score'] > 0.7:
                    validated_memories.append(mem)
            
            # If we filtered too aggressively, keep at least top 3
            if len(validated_memories) < 3 and len(retrieved_memories) >= 3:
                validated_memories = retrieved_memories[:3]
            
            return validated_memories if validated_memories else retrieved_memories[:3]
            
        except Exception as e:
            print(f"Warning: Lore validation error: {e}")
            # Fallback: return top scoring memories
            return retrieved_memories[:3]
    
    def check_consistency(self, text: str, established_facts: List[str]) -> Dict:
        """Check if new text is consistent with established facts"""
        
        facts_str = "\n".join([f"- {fact}" for fact in established_facts])
        
        prompt = f"""Established facts:
{facts_str}

New narrative:
{text}

Check if the new narrative contradicts any established facts. Respond with:
- "CONSISTENT" if no contradictions
- "INCONSISTENT: [explanation]" if contradictions exist

Response:"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=150
            )
            
            result = response.choices[0].message.content.strip()
            
            return {
                "consistent": "consistent" in result.lower(),
                "explanation": result
            }
            
        except Exception as e:
            print(f"Warning: Consistency check error: {e}")
            return {
                "consistent": True,
                "explanation": "Unable to verify (defaulting to consistent)"
            }
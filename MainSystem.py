"""
AI Dungeon Master - Memory-Driven Multi-Agent Storytelling System
Main orchestration module
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import re # Import the re module

class DungeonMasterOrchestrator:
    """Main orchestrator for the AI Dungeon Master system"""

    def __init__(self, groq_api_key: str, enable_bonus_features: bool = True):
        self.groq_api_key = groq_api_key
        self.memory_manager = None
        self.dungeon_master = None
        self.lore_talker = None
        self.npc_manager = None
        self.quest_log = None
        self.enable_bonus_features = enable_bonus_features
        self.turn_count = 0
        self.conversation_history = []
        self.displayed_memories_ids = set()
        self.debug_mode = True
        self.is_running = True

    def initialize_agents(self):
        from MemoryAgent import MemoryManager
        from DungeonMaster import DungeonMaster
        from LoreTalker import LoreTalker

        self.memory_manager = MemoryManager()
        self.dungeon_master = DungeonMaster(self.groq_api_key)
        self.lore_talker = LoreTalker(self.groq_api_key)

        if self.enable_bonus_features:
            from NPCPersonalityManager import NPCPersonalityManager
            from DynamicQuestLog import DynamicQuestLog

            self.npc_manager = NPCPersonalityManager()
            self.quest_log = DynamicQuestLog()
            print("✓ Bonus features enabled (NPC Evolution + Quest Log)")

        print("✓ All agents initialized successfully")

    def detect_context_type(self, player_input: str) -> str:
        """Detect the type of context from player input"""
        lore_keywords = ["remember", "who was", "when", "recall", "what happened"]
        action_keywords = ["attack", "run", "danger", "fight", "escape", "hide"]

        input_lower = player_input.lower()

        if any(keyword in input_lower for keyword in lore_keywords):
            return "lore"
        elif any(keyword in input_lower for keyword in action_keywords):
            return "action"
        else:
            return "normal"

    def get_temperature(self, context_type: str) -> float:
        """Dynamic temperature control based on context"""
        temperature_map = {
            "lore": 0.3,
            "normal": 0.7,
            "action": 1.0
        }
        return temperature_map.get(context_type, 0.7)

    def process_turn(self, player_input: str) -> str:
        """Process a single turn of gameplay"""
        if not self.is_running:
            return ""
        self.turn_count += 1
        print(f"\n-- Turn {self.turn_count} --")
        print(f"Player input: {player_input}")

        # Step 1: Memory Manager retrieves relevant context
        print("[Memory Manager] Retrieving relevant memories...")
        retrieved_memories = self.memory_manager.retrieve_memories(
            player_input,
            top_k=5
        )
        print(f"Retrieved {len(retrieved_memories)} memories")

        # Step 2: Lore Talker validates consistency
        print("[Lore Talker] Validating context consistency...")
        validated_context = self.lore_talker.validate_context(
            player_input,
            retrieved_memories
        )

        # Step 3: Detect context and set temperature
        context_type = self.detect_context_type(player_input)
        temperature = self.get_temperature(context_type)
        print(f"[Context] Type: {context_type}, Temperature: {temperature}")

        # Step 4: Dungeon Master generates response
        print("[Dungeon Master] Generating narrative...")
        dm_response = self.dungeon_master.generate_response(
            player_input,
            validated_context,
            self.conversation_history[-10:],  # Last 10 turns
            temperature=temperature
        )
        print(f"DM response (first 100 chars): {dm_response[:100]}...")

        # Step 5: Extract and store new memories
        print("[Memory Manager] Extracting and storing new facts...")
        self.memory_manager.extract_and_store(
            player_input,
            dm_response,
            self.turn_count
        )
        if hasattr(self.memory_manager, 'maybe_summarize_memory'):
          self.memory_manager.maybe_summarize_memory(self.turn_count)

        # Bonus: Update NPC personalities and quest log
        if self.enable_bonus_features and self.npc_manager and self.quest_log:
            entities = self.memory_manager._extract_entities(dm_response)
            for npc in entities["npcs"]:
                self.npc_manager.update_npc_personality(npc, player_input, dm_response)
                print(f"[NPC Manager] Updated personality for NPC '{npc}'")
            self.quest_log.process_turn(player_input, dm_response, self.turn_count)
            print("[Quest Log] Updated quests")

        # self.memory_manager.maybe_summarize_memory(self.turn_count)
        # Update conversation history
        self.conversation_history.append({
            "turn": self.turn_count,
            "player": player_input,
            "dm": dm_response,
            "timestamp": datetime.now().isoformat()
        })



        # Display debug info
        if self.debug_mode:
            self.display_debug_info()

        return dm_response

    def display_debug_info(self):
        print("\n" + "="*60)
        print("SMART DEBUG CONSOLE")
        print("="*60)

        stats = self.memory_manager.get_stats()
        print(f"\n📊 Memory Stats:")
        print(f"  Total Memories: {stats['total_memories']}")
        print(f"  NPC Collections: {stats['npc_collections']}")
        print(f"  Location Collections: {stats['location_collections']}")
        print(f"  Short-term turns: {min(self.turn_count, 5)}/5")

        recent_memories = self.memory_manager.get_recent_memories(10)
        # Assuming get_recent_memories provides 'id' or 'text' for tracking
        new_memories = [mem for mem in recent_memories if mem.get('id', mem.get('text')) not in self.displayed_memories_ids]

        if new_memories:
            print(f"\n🔍 New memories added:")
            for mem in new_memories:
                preview = mem['text'][:60]
                print(f"  • {preview}... [importance: {mem['importance']:.2f}]")
                # Track displayed to avoid repeats
                self.displayed_memories_ids.add(mem.get('id', mem.get('text')))
        else:
            print("\n🔍 No new memories since last check.")

        if self.enable_bonus_features and self.npc_manager:
            npcs = self.npc_manager.get_all_npcs()
            if npcs:
                print(f"\n👥 NPC Status:")
                for npc in npcs[:3]:  # Show top 3 NPCs
                    desc = self.npc_manager.get_personality_description(npc)
                    print(f"  • {desc}")

        print("="*60 + "\n")

    def start_game(self):
        """Start the game loop"""
        print("\n" + "="*60)
        print("🎲 AI DUNGEON MASTER - Interactive Storytelling")
        print("="*60)
        print("\nCommands:")
        print("  'quit' - Exit game")
        print("  'debug' - Toggle debug mode")
        if self.enable_bonus_features:
            print("  'quests' - View quest log")
            print("  'npcs' - View NPC relationships")
        print("\nThe adventure begins...\n")

        # Initial narration
        initial_prompt = "Start an exciting fantasy adventure. Introduce the setting and present the player with an initial situation."
        opening = self.dungeon_master.generate_opening(initial_prompt)
        print(f"DM: {opening}\n")

        # Store opening in memory
        self.memory_manager.extract_and_store("", opening, turn_number=0)

        while self.is_running:
            try:
                player_input = input("You: ").strip()

                if not player_input:
                    continue

                if player_input.lower() == 'quit':
                    print("\nThanks for playing! The adventure continues in your imagination...")
                    break

                if player_input.lower() == 'debug':
                    self.display_debug_info()
                    continue

                # Process the turn
                response = self.process_turn(player_input)
                print(f"\nDM: {response}\n")

            except KeyboardInterrupt:
                print("\n\nGame interrupted. Saving progress...")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("The Dungeon Master stumbles momentarily but recovers...\n")


def main():
    """Main entry point"""
    # Get API key from environment or user input
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        print("Please enter your Groq API key:")
        groq_api_key = input().strip()

    # Initialize and start the game
    orchestrator = DungeonMasterOrchestrator(groq_api_key)
    orchestrator.initialize_agents()
    orchestrator.start_game()



if __name__ == "__main__":
    main()
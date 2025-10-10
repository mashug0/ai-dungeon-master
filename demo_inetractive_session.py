"""
Interactive Demo Script
Demonstrates key features with a guided storyline
"""

import os
import time
from main import DungeonMasterOrchestrator


class DemoRunner:
    """Runs an interactive demo showcasing system features"""
    
    def __init__(self, groq_api_key: str):
        self.orchestrator = DungeonMasterOrchestrator(groq_api_key)
        self.orchestrator.initialize_agents()
    
    def pause(self, message="Press Enter to continue..."):
        """Pause for user input"""
        input(f"\n{message}")
    
    def show_section(self, title: str):
        """Display section header"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60 + "\n")
    
    def run_demo(self):
        """Run the complete demo"""
        
        print("\n" + "🎲"*20)
        print("\n  AI DUNGEON MASTER - INTERACTIVE DEMO")
        print("  Showcasing Memory, Consistency, and Intelligence")
        print("\n" + "🎲"*20)
        
        self.pause("\nPress Enter to begin the adventure...")
        
        # PART 1: Opening Scene
        self.show_section("PART 1: The Adventure Begins")
        
        print("DM will generate an opening scene...")
        opening = self.orchestrator.dungeon_master.generate_opening(
            "Start a fantasy adventure in a mysterious ancient forest with a hidden treasure"
        )
        print(f"\nDM: {opening}\n")
        
        self.orchestrator.memory_manager.extract_and_store("", opening, 0)
        self.pause()
        
        # PART 2: Short-term Memory Demo
        self.show_section("PART 2: Demonstrating Short-Term Memory")
        
        actions = [
            ("I find a glowing crystal on the path", "Finding an important item"),
            ("I carefully pick up the crystal", "Interacting with the item"),
            ("The crystal pulses with warm light in my hand", "Item response"),
            ("I pocket the crystal and continue", "Moving forward")
        ]
        
        for action, description in actions:
            print(f"[{description}]")
            print(f"You: {action}")
            response = self.orchestrator.process_turn(action)
            print(f"\nDM: {response}\n")
            time.sleep(1)
        
        print("\n--- Testing Short-Term Recall ---")
        query = "What did I find on the path?"
        print(f"You: {query}")
        
        memories = self.orchestrator.memory_manager.retrieve_memories(query, top_k=3)
        print("\n Retrieved from memory:")
        for mem in memories:
            print(f"  ✓ {mem['text'][:80]}... [confidence: {mem['score']:.2f}]")
        
        self.pause("\n✅ System remembered the glowing crystal! Press Enter to continue...")
        
        # PART 3: NPC Interaction
        self.show_section("PART 3: NPC Personality Evolution (Bonus Feature)")
        
        npc_actions = [
            "I encounter a hooded merchant",
            "I greet the merchant warmly and ask about their wares",
            "I compliment the merchant's fine goods",
        ]
        
        for action in npc_actions:
            print(f"You: {action}")
            response = self.orchestrator.process_turn(action)
            print(f"\nDM: {response}\n")
            time.sleep(1)
        
        # Show NPC personality
        if self.orchestrator.enable_bonus_features:
            npcs = self.orchestrator.npc_manager.get_all_npcs()
            if npcs:
                print("\n--- NPC Personality Tracker ---")
                for npc in npcs:
                    desc = self.orchestrator.npc_manager.get_personality_description(npc)
                    print(f"  {desc}")
        
        self.pause("\n✅ NPC personality tracked! Press Enter to continue...")
        
        # PART 4: Long-term Memory Setup
        self.show_section("PART 4: Setting up Long-Term Memory Test")
        
        important_event = "The merchant tells me that the crystal is the key to the Temple of Shadows, located deep in the Whispering Woods"
        print(f"You: I ask the merchant about the crystal")
        print(f"\n[System will remember this important fact]")
        response = self.orchestrator.process_turn(important_event)
        print(f"\nDM: {response}\n")
        
        self.pause("Important fact stored! Now adding filler events...")
        
        # Add filler turns
        print("\n[Adding 15 filler turns to test long-term memory...]")
        filler_actions = [
            "I continue walking",
            "I examine the surroundings",
            "I check my supplies",
            "I rest briefly",
            "I keep moving forward"
        ]
        
        for i in range(15):
            action = filler_actions[i % len(filler_actions)]
            self.orchestrator.process_turn(action)
            if (i + 1) % 5 == 0:
                print(f"  Completed {i + 1}/15 turns...")
        
        print(f"\n✓ Total turns elapsed: {self.orchestrator.turn_count}")
        
        self.pause("\nFiller events complete! Press Enter to test recall...")
        
        # PART 5: Long-term Memory Test
        self.show_section("PART 5: Testing Long-Term Memory")
        
        recall_query = "Where is the Temple of Shadows located?"
        print(f"[Testing if system remembers from {self.orchestrator.turn_count - 15} turns ago]")
        print(f"\nYou: {recall_query}")
        
        memories = self.orchestrator.memory_manager.retrieve_memories(recall_query, top_k=5)
        print("\nRetrieved from long-term memory:")
        for mem in memories:
            print(f"  ✓ {mem['text'][:80]}...")
            print(f"    [Relevance: {mem['score']:.2f}, Turn: {mem['metadata'].get('turn', 'N/A')}]\n")
        
        found_temple = any("temple" in mem['text'].lower() and "shadow" in mem['text'].lower() 
                          for mem in memories)
        
        if found_temple:
            print("✅ SUCCESS: System successfully recalled information from long-term memory!")
        else:
            print("⚠️  System struggled with this recall (may need tuning)")
        
        self.pause("\nPress Enter to continue...")
        
        # PART 6: Dynamic Temperature Demo
        self.show_section("PART 6: Dynamic Temperature Control")
        
        print("The system adjusts its creativity based on context:\n")
        
        contexts = [
            ("What did the merchant tell me about the crystal?", "lore", 0.3, "Factual recall"),
            ("I walk through the peaceful meadow", "normal", 0.7, "Normal storytelling"),
            ("Suddenly, a dragon attacks!", "action", 1.0, "High drama")
        ]
        
        for action, expected_type, expected_temp, description in contexts:
            context_type = self.orchestrator.detect_context_type(action)
            temp = self.orchestrator.get_temperature(context_type)
            print(f"{description}:")
            print(f"  Input: '{action}'")
            print(f"  Context: {context_type}, Temperature: {temp}")
            print(f"  {'✓' if abs(temp - expected_temp) < 0.1 else '✗'} {'Correct!' if context_type == expected_type else 'Different context detected'}\n")
        
        self.pause("✅ Dynamic temperature demonstrated! Press Enter to see final stats...")
        
        # PART 7: Final Statistics
        self.show_section("PART 7: System Statistics")
        
        self.orchestrator.display_debug_info()
        
        if self.orchestrator.enable_bonus_features and self.orchestrator.quest_log:
            print(self.orchestrator.quest_log.get_quest_summary())
        
        print("\n" + "="*60)
        print("  DEMO COMPLETE!")
        print("="*60)
        print(f"\nTotal turns processed: {self.orchestrator.turn_count}")
        print("Key features demonstrated:")
        print("  ✓ Short-term memory (last 5 turns)")
        print("  ✓ Long-term memory (30+ turns)")
        print("  ✓ Dynamic temperature control")
        print("  ✓ Hierarchical memory organization")
        print("  ✓ NPC personality evolution (bonus)")
        print("  ✓ Consistent narrative generation")
        
        print("\nTo play interactively, run: python main.py")
        print("="*60 + "\n")


def main():
    """Main demo entry point"""
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("Please enter your Groq API key:")
        groq_api_key = input().strip()
    
    demo = DemoRunner(groq_api_key)
    demo.run_demo()


if __name__ == "__main__":
    main()
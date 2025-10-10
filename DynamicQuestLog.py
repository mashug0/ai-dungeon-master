"""
Dynamic Quest Log - Bonus Feature
Automatically tracks and updates quests based on game events
"""

from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class QuestStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    AVAILABLE = "available"


class Quest:
    """Represents a single quest"""
    
    def __init__(self, quest_id: str, title: str, description: str):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.status = QuestStatus.AVAILABLE
        self.objectives = []
        self.rewards = []
        self.started_turn = None
        self.completed_turn = None
        self.notes = []
    
    def add_objective(self, objective: str, completed: bool = False):
        """Add an objective to the quest"""
        self.objectives.append({
            "description": objective,
            "completed": completed
        })
    
    def complete_objective(self, objective_index: int):
        """Mark an objective as completed"""
        if 0 <= objective_index < len(self.objectives):
            self.objectives[objective_index]["completed"] = True
    
    def add_note(self, note: str, turn: int):
        """Add a note to the quest"""
        self.notes.append({
            "text": note,
            "turn": turn,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict:
        """Convert quest to dictionary"""
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "started_turn": self.started_turn,
            "completed_turn": self.completed_turn,
            "notes": self.notes
        }


class DynamicQuestLog:
    """Manages dynamic quest tracking"""
    
    def __init__(self):
        self.quests = {}  # quest_id -> Quest
        self.quest_counter = 0
        
        # Keywords for auto-detection
        self.quest_keywords = [
            "quest", "mission", "task", "find", "retrieve", "rescue",
            "defeat", "protect", "deliver", "investigate", "discover"
        ]
        
        self.completion_keywords = [
            "completed", "finished", "done", "succeeded", "accomplished",
            "delivered", "defeated", "rescued", "found"
        ]
        
        print("✓ Dynamic Quest Log initialized")
    
    def auto_detect_quest(self, text: str, turn: int) -> Optional[str]:
        """Automatically detect new quests from narrative text"""
        text_lower = text.lower()
        
        # Check for quest keywords
        has_quest_keyword = any(keyword in text_lower for keyword in self.quest_keywords)
        
        if not has_quest_keyword:
            return None
        
        # Try to extract quest information
        # Simple heuristic: look for sentences with quest keywords
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            
            # Check if this sentence describes a task
            if any(keyword in sentence_lower for keyword in self.quest_keywords):
                # Create a new quest
                quest_id = self._generate_quest_id()
                
                # Extract title (first few words)
                words = sentence.strip().split()
                title = " ".join(words[:6]) + "..."
                
                quest = Quest(
                    quest_id=quest_id,
                    title=title,
                    description=sentence.strip()
                )
                
                quest.status = QuestStatus.ACTIVE
                quest.started_turn = turn
                
                self.quests[quest_id] = quest
                
                return quest_id
        
        return None
    
    def auto_detect_progress(self, text: str, turn: int):
        """Automatically detect quest progress from narrative text"""
        text_lower = text.lower()
        
        # Check each active quest for progress
        for quest_id, quest in self.quests.items():
            if quest.status != QuestStatus.ACTIVE:
                continue
            
            # Check for completion keywords
            has_completion = any(
                keyword in text_lower 
                for keyword in self.completion_keywords
            )
            
            if has_completion:
                # Check if this text relates to this quest
                quest_words = quest.description.lower().split()
                common_words = set(quest_words) & set(text_lower.split())
                
                if len(common_words) > 3:  # Significant overlap
                    # Mark quest as potentially completed
                    quest.add_note(f"Progress detected: {text[:100]}...", turn)
                    
                    # If explicit completion, mark as complete
                    if "quest complete" in text_lower or "mission accomplished" in text_lower:
                        self.complete_quest(quest_id, turn)
    
    def _generate_quest_id(self) -> str:
        """Generate unique quest ID"""
        self.quest_counter += 1
        return f"quest_{self.quest_counter}"
    
    def add_quest(
        self, 
        title: str, 
        description: str, 
        turn: int,
        objectives: List[str] = None
    ) -> str:
        """Manually add a quest"""
        quest_id = self._generate_quest_id()
        
        quest = Quest(
            quest_id=quest_id,
            title=title,
            description=description
        )
        
        quest.status = QuestStatus.ACTIVE
        quest.started_turn = turn
        
        if objectives:
            for obj in objectives:
                quest.add_objective(obj)
        
        self.quests[quest_id] = quest
        
        return quest_id
    
    def complete_quest(self, quest_id: str, turn: int):
        """Mark a quest as completed"""
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            quest.status = QuestStatus.COMPLETED
            quest.completed_turn = turn
            
            # Mark all objectives as completed
            for obj in quest.objectives:
                obj["completed"] = True
    
    def fail_quest(self, quest_id: str, turn: int):
        """Mark a quest as failed"""
        if quest_id in self.quests:
            self.quests[quest_id].status = QuestStatus.FAILED
            self.quests[quest_id].completed_turn = turn
    
    def get_active_quests(self) -> List[Quest]:
        """Get all active quests"""
        return [
            quest for quest in self.quests.values()
            if quest.status == QuestStatus.ACTIVE
        ]
    
    def get_completed_quests(self) -> List[Quest]:
        """Get all completed quests"""
        return [
            quest for quest in self.quests.values()
            if quest.status == QuestStatus.COMPLETED
        ]
    
    def get_quest_summary(self) -> str:
        """Get formatted summary of all quests"""
        summary = "\n" + "="*50 + "\n"
        summary += "📜 QUEST LOG\n"
        summary += "="*50 + "\n"
        
        active = self.get_active_quests()
        completed = self.get_completed_quests()
        
        if active:
            summary += "\n🔥 Active Quests:\n"
            for quest in active:
                summary += f"\n  • {quest.title}\n"
                summary += f"    {quest.description}\n"
                
                if quest.objectives:
                    summary += "    Objectives:\n"
                    for i, obj in enumerate(quest.objectives):
                        status = "✓" if obj["completed"] else "○"
                        summary += f"      {status} {obj['description']}\n"
        else:
            summary += "\n  No active quests.\n"
        
        if completed:
            summary += f"\n✅ Completed Quests ({len(completed)}):\n"
            for quest in completed[:5]:  # Show last 5 completed
                summary += f"  • {quest.title}\n"
        
        summary += "\n" + "="*50 + "\n"
        
        return summary
    
    def process_turn(self, player_input: str, dm_response: str, turn: int):
        """Process a turn for quest updates"""
        combined_text = f"{player_input} {dm_response}"
        
        # Try to detect new quests
        new_quest_id = self.auto_detect_quest(dm_response, turn)
        
        if new_quest_id:
            print(f"  [Quest Log] New quest detected: {self.quests[new_quest_id].title}")
        
        # Check for progress on existing quests
        self.auto_detect_progress(combined_text, turn)
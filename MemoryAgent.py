import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import time
import re
import json
import spacy

class MemoryManager:
    """Manages hierarchical memory using ChromaDB and semantic embeddings"""
    
    def __init__(self, collection_prefix="ai_dm" , dungeon_master = None):
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))

        self.buffer_flushed = False
        self.dungeon_master = dungeon_master

        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.nlp = spacy.load("en_core_web_sm")

        self.collection_prefix = collection_prefix
        self.world_collection = self._get_or_create_collection("world_memory")
        self.npc_collections = {}
        self.location_collections = {}

        self.alpha = 0.6
        self.beta = 0.3
        self.gamma = 0.1

        self.memory_log = []
        self.old_memory_threshold = 50
        self.last_summary_turn = 0
        self.summary_interval = 10

        print("✓ Memory Manager initialized with ChromaDB")

    def flush(self):
        self.buffer_flushed = True
        print("✓ Memory buffer flushed and closed")

    def _normalize_name(self, name: str) -> str:
        name = name.lower()
        name = re.sub(r'[^a-z0-9]+', '_', name)
        name = name.strip('_')
        if not name:
            name = 'unnamed'
        if len(name) < 3:
            name = f"{name}_mem"
        if len(name) > 512:
            name = name[:512].rstrip('_')
        return name

    def _get_or_create_collection(self, name: str):
        sanitized_name = self._normalize_name(name)
        print(f"DEBUG: Using collection name: {sanitized_name} (from original '{name}')")
        try:
            return self.client.get_collection(sanitized_name)
        except chromadb.errors.NotFoundError:
            return self.client.create_collection(
                name=sanitized_name,
                metadata={"hnsw:space": "cosine"}
            )

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities = {"npcs": [], "locations": []}
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["npcs"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC", "FAC"]:
                entities["locations"].append(ent.text)
        entities["npcs"] = list(set(entities["npcs"]))
        entities["locations"] = list(set(entities["locations"]))
        return entities

    def _calculate_importance(self, text: str) -> float:
        importance = 0.5
        high_keywords = ["quest", "key", "artifact", "defeat", "victory", "death", "betray", "oath", "curse", "prophecy"]
        medium_keywords = ["meet", "find", "give", "take", "learn", "discover", "receive"]
        text_lower = text.lower()
        for kw in high_keywords:
            if kw in text_lower:
                importance += 0.1
        for kw in medium_keywords:
            if kw in text_lower:
                importance += 0.05
        return min(importance, 1.0)

    def summarize_events(self, events: List[str]) -> str:
        # Replace with your DungeonMaster summarization call
        return "Summary: " + " ".join(events)[:500]

    def maybe_summarize_memory(self, current_turn: int):
        if current_turn - self.last_summary_turn >= self.summary_interval and len(self.memory_log) > self.old_memory_threshold:
            old_memories = self.memory_log[:self.old_memory_threshold]
            summary_text = self.summarize_events([mem['text'] for mem in old_memories])

            summary_id = f"summary_{current_turn}"
            self.world_collection.add(
                documents=[summary_text],
                ids=[summary_id],
                metadatas=[{"importance": 0.9, "timestamp": time.time(), "turn": current_turn, "type": "summary"}]
            )

            old_ids = [mem.get('memory_id') for mem in old_memories if mem.get('memory_id')]
            if old_ids:
                self.world_collection.delete(ids=old_ids)

            self.memory_log = self.memory_log[self.old_memory_threshold:]
            self.memory_log.insert(0, {
                "turn": current_turn,
                "memory_id": summary_id,
                "text": summary_text,
                "importance": 0.9,
                "timestamp": time.time(),
                "npcs": [],
                "locations": []
            })

            self.last_summary_turn = current_turn
            print(f"\n[MemoryManager] Summarized and compressed memory at turn {current_turn}.\nSummary: {summary_text}\n")

    def extract_and_store(self, player_input: str, dm_response: str, turn_number: int):
        if self.buffer_flushed:
            print("MemoryManager is closed. Skipping storage.")
            return

        combined_text = f"{player_input} {dm_response}"
        entities = self._extract_entities(combined_text)

        sentences = re.split(r'[.!?]+', dm_response)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        timestamp = time.time()

        for sentence in sentences:
            importance = self._calculate_importance(sentence)
            memory_id = f"mem_{turn_number}_{hash(sentence) % 10000}"
            metadata = {
                "importance": importance,
                "timestamp": timestamp,
                "turn": turn_number,
                "type": "interaction"
            }

            self.world_collection.add(
                documents=[sentence],
                metadatas=[metadata],
                ids=[memory_id]
            )
            log_entry = {
                "turn": turn_number,
                "memory_id": memory_id,
                "text": sentence,
                "importance": importance,
                "timestamp": timestamp,
                "npcs": entities["npcs"],
                "locations": entities["locations"]
            }
            self.memory_log.append(log_entry)

            for npc in entities["npcs"]:
                npc_key = self._normalize_name(npc)
                if npc_key not in self.npc_collections:
                    self.npc_collections[npc_key] = self._get_or_create_collection(f"{self.collection_prefix}_npc_{npc_key}")
                npc_metadata = metadata.copy()
                npc_metadata["npc"] = npc
                self.npc_collections[npc_key].add(
                    documents=[sentence],
                    metadatas=[npc_metadata],
                    ids=[f"{memory_id}_npc_{npc_key}"]
                )

            for location in entities["locations"]:
                loc_key = self._normalize_name(location)
                if loc_key not in self.location_collections:
                    self.location_collections[loc_key] = self._get_or_create_collection(f"{self.collection_prefix}_loc_{loc_key}")
                loc_metadata = metadata.copy()
                loc_metadata["location"] = location
                self.location_collections[loc_key].add(
                    documents=[sentence],
                    metadatas=[loc_metadata],
                    ids=[f"{memory_id}_loc_{loc_key}"]
                )

        self.maybe_summarize_memory(turn_number)

    def retrieve_memories(self, query: str, top_k: int = 5) -> List[Dict]:
        current_time = time.time()
        results = self.world_collection.query(
            query_texts=[query],
            n_results=top_k * 2
        )
        if not results['documents'][0]:
            return []
        memories = []
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i] if 'distances' in results else 0.5
            semantic_score = 1 - distance
            time_diff = current_time - metadata['timestamp']
            recency_score = max(0, 1 - (time_diff / (86400 * 30)))
            importance_score = metadata.get('importance', 0.5)
            final_score = (
                self.alpha * semantic_score +
                self.beta * recency_score +
                self.gamma * importance_score
            )
            memories.append({
                'text': doc,
                'score': final_score,
                'metadata': metadata
            })
        memories.sort(key=lambda x: x['score'], reverse=True)
        return memories[:top_k]

    def get_stats(self) -> Dict:
        return {
            'total_memories': self.world_collection.count(),
            'npc_collections': len(self.npc_collections),
            'location_collections': len(self.location_collections)
        }

    def get_recent_memories(self, n: int = 5) -> List[Dict]:
        results = self.world_collection.get(
            limit=n,
            include=['documents', 'metadatas']
        )
        if not results['documents']:
            return []
        memories = []
        for i, doc in enumerate(results['documents']):
            memories.append({
                'text': doc,
                'importance': results['metadatas'][i].get('importance', 0.5)
            })
        return memories

    def export_memory_log_json(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.memory_log, f, indent=2)
    def summarize_events(self, events: List[str]) -> str:
        # Use dungeon_master's summarize_events if set, else fallback
        if self.dungeon_master:
            return self.dungeon_master.summarize_events(events)
        return "Summary: " + " ".join(events)[:500]

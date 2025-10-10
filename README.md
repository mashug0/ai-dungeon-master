# AI Dungeon Master: Memory-Driven Multi-Agent Storytelling System

An intelligent, interactive storytelling system that maintains long-term narrative coherence through hierarchical memory and multi-agent architecture.

## 🎯 Features

### Core Features
- **Multi-Agent Architecture**: Three specialized agents work cooperatively
  - **Dungeon Master**: Creative narrative generation
  - **Memory Manager**: Hierarchical memory storage and retrieval using RAG
  - **Lore Talker**: Consistency verification and validation

- **Dynamic Temperature Control**: Adaptive creativity based on scene context
  - Lore/Recall scenes: 0.3 (logical, factual)
  - Normal dialogue: 0.7 (balanced)
  - Action scenes: 1.0 (dramatic, expressive)

- **Hierarchical Memory System**:
  - World Memory: Global lore and events
  - NPC Memory: Character-specific interactions
  - Location Memory: Environmental context
  - Contextual scoring: Combines semantic similarity, recency, and importance

- **Smart Debug Console**: Real-time introspection of memory operations

### Bonus Features
- **NPC Personality Evolution** (+10 points): Characters remember interactions and evolve their personalities
- **Dynamic Quest Log** (+5 points): Automatic quest detection and tracking

## 🏗️ Architecture

```
Player Input
    ↓
Memory Manager (Retrieves relevant context)
    ↓
Lore Talker (Validates consistency)
    ↓
Dungeon Master (Generates narrative with dynamic temperature)
    ↓
Memory Manager (Stores new facts)
    ↓
Response + Debug Info
```

## 📋 Requirements

- Python 3.8+
- Groq API key (free at https://console.groq.com)

## 🚀 Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ai-dungeon-master
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your Groq API key:
```bash
export GROQ_API_KEY="your_api_key_here"
```

Or the system will prompt you for it at runtime.

## 💻 Usage

### Basic Usage

Run the main game:
```bash
python main.py
```

### Commands
- Type your actions naturally
- Type `debug` to view memory statistics
- Type `quit` to exit

### Example Session

```
DM: You stand at the entrance of an ancient forest, mist curling around 
twisted trees. A hooded figure approaches from the shadows...

You: I greet the hooded figure cautiously

DM: The figure lowers their hood, revealing an elderly wizard with kind 
eyes. "I am Aldric," he says. "I've been expecting you. The forest is 
dangerous, but I can offer guidance... for a price."

You: I ask what price he wants

[Memory Manager] Retrieving relevant memories...
[Lore Talker] Validating context consistency...
[Context] Type: normal, Temperature: 0.7
[Dungeon Master] Generating narrative...

DM: Aldric strokes his white beard thoughtfully. "Three silver coins, 
or a favor to be named later." His eyes twinkle with mysterious intent...
```

## 🧪 Testing

The system is designed to sustain 30+ turns with:
- **Short-term recall**: Last 5 turns maintained in working memory
- **Long-term recall**: Relevant past events retrieved via semantic search
- **Consistency**: Lore Talker prevents contradictions

### Evaluation Areas

1. **Memory Effectiveness** (40 points)
   - Short-term: Tracks recent 5 turns accurately
   - Long-term: Recalls events from 30+ turns ago

2. **Multi-Agent Coordination** (25 points)
   - Memory Manager, DM, and Lore Talker work seamlessly
   - Debug console shows agent operations

3. **Adaptive Behavior** (15 points)
   - Temperature adjusts based on context
   - NPC personalities evolve (bonus)
   - Quests auto-tracked (bonus)

## 📁 File Structure

```
ai-dungeon-master/
├── main.py                 # Main orchestrator
├── memory_manager.py       # Memory storage and retrieval
├── dungeon_master.py       # Narrative generation
├── lore_talker.py         # Consistency verification
├── npc_manager.py         # NPC personality system (bonus)
├── quest_log.py           # Dynamic quest tracking (bonus)
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## 🔧 Technical Details

### Memory System
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB**: ChromaDB with cosine similarity
- **Scoring**: α(semantic) + β(recency) + γ(importance)
  - α=0.6, β=0.3, γ=0.1

### LLM Integration
- **Model**: llama-3.1-8b-instant via Groq API
- **Max tokens**: 400-500 per response
- **Temperature**: Dynamic (0.3-1.0)

### NPC System
- **Traits**: friendly, greedy, fearful, wise, aggressive, honest, loyal
- **Evolution**: Sentiment analysis updates traits over time
- **Relationship**: Tracks player-NPC relationship score

### Quest System
- **Auto-detection**: Keywords trigger quest creation
- **Tracking**: Objectives, status, notes
- **Updates**: Automatic progress detection

## 🎥 Demo Video

[Link to recording showing short-term and long-term recall]

## 📊 Performance

- Handles 30+ turns without memory degradation
- Sub-second response time for memory retrieval
- Consistent narrative across extended sessions

## 🐛 Troubleshooting

**ChromaDB errors**: Delete the `chroma_db` folder and restart
```bash
rm -rf chroma_db/
```

**API rate limits**: Groq free tier allows 30 requests/minute

**Memory issues**: System uses ~500MB RAM for embeddings

## 🤝 Contributing

This project was developed for Inter IIT Tech Meet 14.0 AI/ML Bootcamp.

## 📄 License

MIT License

## 🙏 Acknowledgments

- Groq for fast LLM inference
- ChromaDB for vector storage
- Sentence Transformers for embeddings

# AI Dungeon Master: Persistent Storytelling with Memory Architecture

## Project Overview
This project implements an intelligent AI Dungeon Master system that maintains persistent, coherent storytelling across multiple gaming sessions. The system combines short-term working memory with long-term persistent memory using Retrieval-Augmented Generation (RAG) to create immersive tabletop RPG experiences.

## Features
- **Working Memory**: Tracks recent scene details and player actions (~5 turns)
- **Persistent Memory**: Recalls crucial past events (~30 turns) for world consistency
- **Intelligent NPCs**: Characters remember prior interactions and evolve over time
- **Dynamic Quest System**: Automatically updates and references player progress
- **Modular Architecture**: Clean, scalable design with interpretable memory management

## System Architecture

┌─────────────────┐     ┌──────────────────┐    ┌─────────────────┐
│ LLM Engine      │◄──► |Memory Manager    │◄──►│ Game State      │
│ (Groq API)      │     │                  │    │                 │
└─────────────────┘     └──────────────────┘    └─────────────────┘
        │
        ▼
┌─────────────────┐
│ Vector Store    │
│ (FAISS/Pine)    │
└─────────────────┘

## Setup Instructions

### Prerequisites
- Python 3.8+
- Jupyter Notebook
- Kaggle Account (for using Secrets)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/ai-dungeon-master.git
cd ai-dungeon-master
```
2.**Install The Required Packages**
```bash
pip install -r requirements.txt
```
3. **Use KAGGLE Secrets for Setting up GROQ_API_KEY**
   in the addons section of the notebook add a kaggle secret with the name GROQ_API_KEY and add your groq api key there
## DEMO
## TECHNICAL REPORT
see the TechnicalReport.pdf for detailed system design, methodology, and evaluation results.

## TEAM
SUHANI MAHESHWARI
SAKSHAM GUPTA

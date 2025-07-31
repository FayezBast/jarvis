# jarvis_memory_manager.py
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from logger import log_info, log_error, log_warning
from config import Config

class JarvisMemoryManager:
    """Manages JARVIS's short-term and long-term memory."""

    def __init__(self, memory_file: str = "jarvis_memory.json"):
        self.memory_file = Config.WORKSPACE_DIR / memory_file
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory: Dict[str, Any] = self._load_memory()
        log_info(f"Memory Manager initialized. Memory loaded from: {self.memory_file}")

    def _load_memory(self) -> Dict[str, Any]:
        """Loads memory from the JSON file."""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except json.JSONDecodeError as e:
            log_error(f"Error decoding memory JSON: {e}. Starting with empty memory.")
        except Exception as e:
            log_error(f"Failed to load memory from {self.memory_file}: {e}. Starting with empty memory.")
        return {"facts": [], "conversations": [], "preferences": {}}

    def _save_memory(self):
        """Saves current memory to the JSON file."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            log_error(f"Failed to save memory to {self.memory_file}: {e}")

    def add_conversation_entry(self, role: str, content: str, session_id: str):
        """Adds a new entry to the conversation history."""
        timestamp = datetime.now().isoformat()
        entry = {"role": role, "content": content, "timestamp": timestamp, "session_id": session_id}
        
        if "conversations" not in self.memory:
            self.memory["conversations"] = []
        
        self.memory["conversations"].append(entry)
        self.memory["conversations"] = self.memory["conversations"][-Config.MAX_HISTORY_ENTRIES:]
        self._save_memory()
        log_info(f"Added conversation entry ({role}): {content[:50]}...")

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieves recent conversation history for AI context."""
        return self.memory.get("conversations", [])[-limit:]

    def add_fact(self, fact_type: str, content: str, source: str):
        """Adds a new fact to long-term memory."""
        timestamp = datetime.now().isoformat()
        fact = {"type": fact_type, "content": content, "timestamp": timestamp, "source": source}
        
        if "facts" not in self.memory:
            self.memory["facts"] = []
        
        if not any(f['type'] == fact_type and f['content'] == content for f in self.memory["facts"]):
            self.memory["facts"].append(fact)
            self._save_memory()
            log_info(f"Added fact ({fact_type}): {content}")
        else:
            log_info(f"Fact already exists: ({fact_type}): {content}")

    def get_facts(self) -> List[Dict[str, str]]:
        """Retrieves all stored facts."""
        return self.memory.get("facts", [])

    def search_memory(self, query: str) -> List[Dict[str, str]]:
        """Searches memory for relevant entries based on a query."""
        results = []
        query_lower = query.lower()
        
        for conv in self.memory.get("conversations", []):
            if query_lower in conv.get("content", "").lower():
                results.append(conv)
                
        for fact in self.memory.get("facts", []):
            if query_lower in fact.get("content", "").lower() or query_lower in fact.get("type", "").lower():
                results.append(fact)
                
        unique_results = []
        seen_contents = set()
        for r in results:
            content_key = f"{r.get('type')}_{r.get('content')}"
            if content_key not in seen_contents:
                unique_results.append(r)
                seen_contents.add(content_key)
        
        log_info(f"Memory search for '{query}' found {len(unique_results)} results.")
        return unique_results

    def update_preference(self, key: str, value: Any):
        """Updates a user preference."""
        if "preferences" not in self.memory:
            self.memory["preferences"] = {}
        self.memory["preferences"][key] = value
        self._save_memory()
        log_info(f"Updated preference '{key}': {value}")

    def get_preference(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieves a user preference."""
        return self.memory.get("preferences", {}).get(key, default)

    def clear_memory(self):
        """Clears all stored memory."""
        self.memory = {"facts": [], "conversations": [], "preferences": {}}
        self._save_memory()
        log_info("Memory cleared.")

    def close(self):
        """Ensures memory is saved on shutdown."""
        self._save_memory()
        log_info("Memory Manager closed.")
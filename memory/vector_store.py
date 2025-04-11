# Placeholder for vector store integration (e.g., ChromaDB, SQLite)
class VectorStore:
    def __init__(self):
        pass

    def add(self, vector, metadata=None):
        pass

    def query(self, vector, top_k=5):
        pass

class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self.memory = {}

    def add(self, chat_id, vector, metadata=None):
        if chat_id not in self.memory:
            self.memory[chat_id] = []
        self.memory[chat_id].append({"vector": vector, "metadata": metadata})

    def query(self, chat_id, top_k=5):
        if chat_id not in self.memory:
            return []
        # For simplicity, just return the last top_k entries
        return self.memory[chat_id][-top_k:]

    def delete(self, chat_id):
        if chat_id in self.memory:
            del self.memory[chat_id]

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
        # Memory structure will now have both user-specific and conversation-specific entries
        self.memory = {
            'user': {},      # User-specific memory (persists across conversations)
            'conversation': {}  # Conversation-specific memory
        }

    def add(self, id, vector, metadata=None, memory_type='conversation'):
        """
        Add a memory entry to the store.
        
        Args:
            id: User ID or conversation ID
            vector: The text content to store
            metadata: Additional information about the entry
            memory_type: Either 'user' (persists across conversations) or 'conversation' (specific to one chat)
        """
        if metadata is None:
            metadata = {}
            
        # Set memory type in metadata
        metadata['memory_type'] = memory_type
        
        # Store in the appropriate memory section
        if memory_type == 'user':
            if id not in self.memory['user']:
                self.memory['user'][id] = []
            self.memory['user'][id].append({"vector": vector, "metadata": metadata})
        else:  # conversation memory
            if id not in self.memory['conversation']:
                self.memory['conversation'][id] = []
            self.memory['conversation'][id].append({"vector": vector, "metadata": metadata})

    def query(self, id, include_user_memory=True, top_k=5):
        """
        Query the memory store for a specific ID.
        
        Args:
            id: User ID or conversation ID to query
            include_user_memory: Whether to include user-specific memory in results
            top_k: Maximum number of entries to return
            
        Returns:
            List of memory entries
        """
        results = []
        
        # Get conversation-specific memory
        if id in self.memory['conversation']:
            results.extend(self.memory['conversation'][id])
        
        # Also get user-specific memory if requested and available
        if include_user_memory and id in self.memory['user']:
            results.extend(self.memory['user'][id])
            
        # Sort by timestamp if available in metadata
        results.sort(key=lambda x: x.get('metadata', {}).get('timestamp', 0))
            
        # Return the most recent entries up to top_k
        return results[-top_k:] if results else []

    def delete_conversation(self, conversation_id):
        """
        Delete all memory associated with a specific conversation.
        
        Args:
            conversation_id: ID of the conversation to delete
        """
        if conversation_id in self.memory['conversation']:
            del self.memory['conversation'][conversation_id]

    def delete_user_memory(self, user_id):
        """
        Delete all user-specific memory.
        
        Args:
            user_id: ID of the user whose memory should be deleted
        """
        if user_id in self.memory['user']:
            del self.memory['user'][user_id]

    def delete_all_user_memories(self):
        """Delete all user-specific memories across all users."""
        self.memory['user'] = {}

    def delete_all_conversation_memories(self):
        """Delete all conversation-specific memories."""
        self.memory['conversation'] = {}

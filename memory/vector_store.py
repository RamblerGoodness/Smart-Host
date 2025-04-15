# Placeholder for vector store integration (e.g., ChromaDB, SQLite)
import sqlite3
import threading
import json
import time

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

class SQLiteVectorStore(VectorStore):
    def __init__(self, db_path='memory_store.sqlite3'):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    user_id TEXT,
                    vector TEXT NOT NULL,
                    role TEXT,
                    timestamp REAL,
                    metadata TEXT
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS user_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    vector TEXT NOT NULL,
                    role TEXT,
                    timestamp REAL,
                    metadata TEXT
                )
            ''')
            conn.commit()

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def add(self, id, vector, metadata=None, memory_type='conversation', user_id=None):
        if metadata is None:
            metadata = {}
        role = metadata.get('role')
        timestamp = metadata.get('timestamp', time.time())
        meta_json = json.dumps(metadata)
        with self._lock, self._get_conn() as conn:
            c = conn.cursor()
            if memory_type == 'user':
                c.execute('''INSERT INTO user_memory (user_id, vector, role, timestamp, metadata)
                             VALUES (?, ?, ?, ?, ?)''',
                          (id, vector, role, timestamp, meta_json))
            else:
                c.execute('''INSERT INTO conversation_memory (chat_id, user_id, vector, role, timestamp, metadata)
                             VALUES (?, ?, ?, ?, ?, ?)''',
                          (id, user_id, vector, role, timestamp, meta_json))
            conn.commit()

    def query(self, id, include_user_memory=True, user_id=None, top_k=5):
        results = []
        with self._lock, self._get_conn() as conn:
            c = conn.cursor()
            # Conversation-specific memory
            c.execute('''SELECT vector, metadata FROM conversation_memory WHERE chat_id=? ORDER BY timestamp ASC''', (id,))
            for row in c.fetchall():
                results.append({"vector": row[0], "metadata": json.loads(row[1]) if row[1] else {}})
            # User-specific memory
            if include_user_memory and user_id:
                c.execute('''SELECT vector, metadata FROM user_memory WHERE user_id=? ORDER BY timestamp ASC''', (user_id,))
                for row in c.fetchall():
                    results.append({"vector": row[0], "metadata": json.loads(row[1]) if row[1] else {}})
        # Sort by timestamp if available
        results.sort(key=lambda x: x.get('metadata', {}).get('timestamp', 0))
        return results[-top_k:] if results else []

    def delete_conversation(self, conversation_id):
        with self._lock, self._get_conn() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM conversation_memory WHERE chat_id=?', (conversation_id,))
            conn.commit()

    def delete_user_memory(self, user_id):
        with self._lock, self._get_conn() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM user_memory WHERE user_id=?', (user_id,))
            conn.commit()

    def delete_all_user_memories(self):
        with self._lock, self._get_conn() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM user_memory')
            conn.commit()

    def delete_all_conversation_memories(self):
        with self._lock, self._get_conn() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM conversation_memory')
            conn.commit()

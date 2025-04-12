import requests
import json
import time
import uuid
import random
import sys
import os

# Add the parent directory to the Python path so we can import modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api_wrapper import app
from router import MEMORY_STORE

client = TestClient(app)

def print_separator():
    print("\n" + "="*50 + "\n")

def print_test_header(title):
    print_separator()
    print(f"🔍 {title}")
    print_separator()

# Clear any existing memory before testing
MEMORY_STORE.delete_all_conversation_memories()
MEMORY_STORE.delete_all_user_memories()

# Generate unique test IDs
timestamp = int(time.time())
conversation_id_1 = f"conv-{timestamp}-{uuid.uuid4().hex[:8]}"
conversation_id_2 = f"conv-{timestamp}-{uuid.uuid4().hex[:8]}"
user_id = f"user-{timestamp}-{uuid.uuid4().hex[:8]}"

# Generate unique, random information for testing
random_color = random.choice(["cerulean", "vermilion", "chartreuse", "magenta", "periwinkle", "amber"])
random_name = f"X{uuid.uuid4().hex[:6]}Z"  # Very unique name that wouldn't be guessed
random_number = random.randint(10000, 99999)
random_fact = f"My secret code is {random.randint(100000, 999999)}"

print(f"Using random color: {random_color}")
print(f"Using random name: {random_name}")
print(f"Using random number: {random_number}")
print(f"Using random fact: {random_fact}")

#####################################
# Test 1: Conversation-only Memory
#####################################
print_test_header("TEST 1: CONVERSATION-SPECIFIC MEMORY")

print(f"Using conversation_id: {conversation_id_1}")

# First message in conversation 1
print("\n1. Sending first message to conversation 1:")
response = client.post("/chat", json={
    "provider": "openrouter", 
    "messages": [{"role": "user", "content": f"My favorite color is {random_color} and I have {random_number} coins."}],
    "model": "openai/gpt-3.5-turbo",
    "chat_id": conversation_id_1
})
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    chat_response = response.json()
    if "choices" in chat_response and chat_response["choices"]:
        content = chat_response["choices"][0]["message"]["content"]
        print(f"Response: {content}")

# Inject some dummy messages to dilute the context window
for i in range(3):
    client.post("/chat", json={
        "provider": "openrouter", 
        "messages": [{"role": "user", "content": f"Random message {i+1}: The weather is nice today."}],
        "model": "openai/gpt-3.5-turbo",
        "chat_id": f"dummy-{uuid.uuid4().hex}"  # Use different chat_id
    })

# Second message in conversation 1 (should remember the color)
print("\n2. Asking about favorite color and coins in conversation 1:")
response = client.post("/chat", json={
    "provider": "openrouter", 
    "messages": [{"role": "user", "content": "What's my favorite color and how many coins do I have?"}],
    "model": "openai/gpt-3.5-turbo",
    "chat_id": conversation_id_1
})
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    chat_response = response.json()
    if "choices" in chat_response and chat_response["choices"]:
        content = chat_response["choices"][0]["message"]["content"]
        print(f"Response: {content}")
        if random_color.lower() in content.lower() and str(random_number) in content:
            print("✅ Conversation memory test PASSED! The API remembered both the color and number of coins.")
        else:
            print("❌ Conversation memory test FAILED. The API did not remember both pieces of information.")

#####################################
# Test 2: User-specific Memory
#####################################
print_test_header("TEST 2: USER-SPECIFIC MEMORY ACROSS CONVERSATIONS")

print(f"Using user_id: {user_id}")
print(f"Using conversation_id_1: {conversation_id_1}")
print(f"Using conversation_id_2: {conversation_id_2}")

# First message with user memory in conversation 1
print("\n1. Telling name and secret code in conversation 1 (saving to user memory):")
response = client.post("/chat", json={
    "provider": "openrouter", 
    "messages": [{"role": "user", "content": f"My name is {random_name}. {random_fact}"}],
    "model": "openai/gpt-3.5-turbo",
    "chat_id": conversation_id_1,
    "user_id": user_id,
    "save_to_user_memory": True
})
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    chat_response = response.json()
    if "choices" in chat_response and chat_response["choices"]:
        content = chat_response["choices"][0]["message"]["content"]
        print(f"Response: {content}")

# Inject some dummy messages to dilute the context window
for i in range(5):
    client.post("/chat", json={
        "provider": "openrouter", 
        "messages": [{"role": "user", "content": f"Completely irrelevant message {i+1} about nothing important."}],
        "model": "openai/gpt-3.5-turbo",
        "chat_id": f"dummy-{uuid.uuid4().hex}"  # Use different chat_id
    })

# Start a new conversation and check if user memory persists
print("\n2. Asking about name and secret code in conversation 2 (should use user memory):")
response = client.post("/chat", json={
    "provider": "openrouter", 
    "messages": [{"role": "user", "content": "What's my name and what's my secret code?"}],
    "model": "openai/gpt-3.5-turbo",
    "chat_id": conversation_id_2,  # Completely different conversation
    "user_id": user_id,
    "include_user_memory": True
})
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    chat_response = response.json()
    if "choices" in chat_response and chat_response["choices"]:
        content = chat_response["choices"][0]["message"]["content"]
        print(f"Response: {content}")
        if random_name in content and random_fact.split()[-1] in content:
            print("✅ User memory test PASSED! The API remembered the unique name and secret code across conversations.")
        else:
            print("❌ User memory test FAILED. The API did not remember the information across conversations.")

# Verify that conversation-specific memory doesn't leak between conversations
print("\n3. Testing conversation isolation - asking about coins in conversation 2:")
response = client.post("/chat", json={
    "provider": "openrouter", 
    "messages": [{"role": "user", "content": "How many coins do I have?"}],
    "model": "openai/gpt-3.5-turbo",
    "chat_id": conversation_id_2,  # Different conversation
    "user_id": user_id,
    "include_user_memory": True
})
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    chat_response = response.json()
    if "choices" in chat_response and chat_response["choices"]:
        content = chat_response["choices"][0]["message"]["content"]
        print(f"Response: {content}")
        if "sorry" in content.lower() or "don't know" in content.lower() or "not sure" in content.lower() or str(random_number) not in content:
            print("✅ Conversation isolation test PASSED! The API correctly isolated conversation-specific memory.")
        else:
            print("❌ Conversation isolation test FAILED. Information leaked between conversations.")

#####################################
# Test 3: Memory Management API
#####################################
print_test_header("TEST 3: MEMORY MANAGEMENT API")

# Test memory status endpoint
print("\n1. Testing memory status endpoint:")
response = client.get("/memory/status")
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    status_data = response.json()
    print(json.dumps(status_data, indent=2))
    
    # Verify our test IDs are in the memory
    user_ids = status_data.get("users", {}).get("ids", [])
    conversation_ids = status_data.get("conversations", {}).get("ids", [])
    
    if user_id in user_ids:
        print(f"✅ User ID {user_id} found in memory.")
    else:
        print(f"❌ User ID {user_id} not found in memory.")
        
    if conversation_id_1 in conversation_ids and conversation_id_2 in conversation_ids:
        print(f"✅ Conversation IDs {conversation_id_1} and {conversation_id_2} found in memory.")
    else:
        print(f"❌ One or more conversation IDs not found in memory.")

# Delete conversation memory
print("\n2. Deleting conversation 1 memory:")
response = client.delete(f"/memory/conversation/{conversation_id_1}")
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.json()}")
    
    # Verify conversation was deleted but user memory remains
    response = client.get("/memory/status")
    if response.status_code == 200:
        status_data = response.json()
        conversation_ids = status_data.get("conversations", {}).get("ids", [])
        user_ids = status_data.get("users", {}).get("ids", [])
        
        if conversation_id_1 not in conversation_ids:
            print(f"✅ Conversation memory deletion successful.")
        else:
            print(f"❌ Conversation memory deletion failed.")
            
        if user_id in user_ids:
            print(f"✅ User memory correctly preserved after conversation deletion.")
        else:
            print(f"❌ User memory unexpectedly deleted.")

# Delete user memory
print("\n3. Deleting user memory:")
response = client.delete(f"/memory/user/{user_id}")
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.json()}")
    
    # Verify user memory was deleted
    response = client.get("/memory/status")
    if response.status_code == 200:
        status_data = response.json()
        user_ids = status_data.get("users", {}).get("ids", [])
        
        if user_id not in user_ids:
            print(f"✅ User memory deletion successful.")
        else:
            print(f"❌ User memory deletion failed.")

#####################################
# Test 4: Verify Memory Behavior After Deletion
#####################################
print_test_header("TEST 4: MEMORY BEHAVIOR AFTER DELETION")

# First, delete the second conversation to clear any lingering context
print("\n1. Deleting conversation 2 memory to clear context:")
response = client.delete(f"/memory/conversation/{conversation_id_2}")
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.json()}")

# Create a brand new conversation ID to test with truly fresh context
conversation_id_3 = f"conv-{timestamp}-{uuid.uuid4().hex[:8]}"
print(f"\n2. Created fresh conversation ID: {conversation_id_3}")

# Ask about the name in a completely new conversation after user memory deletion
print("\n3. Asking about name in a brand new conversation after user memory deletion:")
response = client.post("/chat", json={
    "provider": "openrouter", 
    "messages": [{"role": "user", "content": "What is my name? And what is my secret code?"}],
    "model": "openai/gpt-3.5-turbo",
    "chat_id": conversation_id_3,
    "user_id": user_id,
    "include_user_memory": True
})
print(f"Status code: {response.status_code}")
if response.status_code == 200:
    chat_response = response.json()
    if "choices" in chat_response and chat_response["choices"]:
        content = chat_response["choices"][0]["message"]["content"]
        print(f"Response: {content}")
        if ("sorry" in content.lower() or 
            "don't know" in content.lower() or 
            "not sure" in content.lower() or 
            "can't recall" in content.lower() or
            "no information" in content.lower() or
            "don't have that information" in content.lower() or
            "unable to" in content.lower() or
            "don't have access" in content.lower() or
            "no record" in content.lower() or
            "no data" in content.lower() or
            random_name not in content):
            print("✅ Memory deletion test PASSED! The API forgot the name after deletion with a fresh conversation.")
        else:
            print("❌ Memory deletion test FAILED. The API still remembers information that should be deleted.")

print_separator()
print("✅ MEMORY SYSTEM TESTS COMPLETE")
print_separator()
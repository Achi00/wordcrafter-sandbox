from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime
import sys  # For logging errors
from bson import ObjectId


load_dotenv()
# uri = os.getenv("MONGODB_URI")
uri = 'mongodb+srv://test-user:f6b3AzyrSyvJUie9@auth-chat.7lezelm.mongodb.net/?retryWrites=true&w=majority'
print("URI:", uri)  # Debug print

try:
    client = MongoClient(uri)
    # Force a request to the server to check for a successful connection
    client.admin.command('ping')
    print("MongoDB connection successful.")
except Exception as e:
    print("Error connecting to MongoDB: ", e)
    sys.exit(1)  # Exit the script if the connection fails

# Select the 'node_modules' database
db = client['node_modules']

def get_user_plan(user_id):
    # Select the 'test' database for user-related operations
    db_test = client['test']
    """Fetches the user plan from the database based on user_id."""
    user_record = db_test.users.find_one({"_id": ObjectId(user_id)})
    if user_record:
        return user_record.get("plan", "free")  # Default to "free" if the plan is not set
    else:
        return None  # User not found

def chat_exists(chat_id):
    # Select the 'test' database for chat-related operations
    db_test = client['test']
    """Checks if a chat exists in the database based on chat_id."""
    chat_record = db_test.chats.find_one({"_id": ObjectId(chat_id)})
    if chat_record:
        print("Chat found")  # For debugging, you can remove or comment this out in production
        return True  # Chat exists
    else:
        print("Chat not found")  # For debugging, you can remove or comment this out in production
        return False  # Chat does not exist


def save_execution_metadata(userId, chatId, execution_details):
    execution_hash = execution_details["executionHash"]
    try:
        db.script_executions.insert_one({
            "userId": userId,
            "chatId": chatId,
            "executionHash": execution_hash,
            "status": execution_details["status"],
            "output": execution_details.get("output", ""),
            "error": execution_details.get("error", ""),
            "startedAt": execution_details["startedAt"],
            "endedAt": execution_details["endedAt"]
        })
        print("Execution metadata saved successfully.")
    except Exception as e:
        print(f"Error saving execution metadata: {e}")

def get_execution_metadata_by_hash(execution_hash):
    try:
        record = db.script_executions.find_one({
            "executionHash": execution_hash
        })
        if record:
            print("Execution metadata found.")
            return record
        else:
            print("No execution metadata found.")
            return None
    except Exception as e:
        print(f"Error retrieving execution metadata: {e}")
        return None

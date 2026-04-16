# OpenCortex
# src/database.py

# Import Libraries
from pymongo import MongoClient
import bcrypt
from utils.logger import setup_logger

logger = setup_logger("database")

# MongoDB Manager Class
class MongoManager:

    # Initialize connection to MongoDB
    def __init__(self, url="mongodb://mongodb:27017/"):
        """Initialize connection to MongoDB (using the Docker service name)."""

        # Try to connect to MongoDB
        try:
            self.client = MongoClient(url, serverSelectionTimeoutMS=5000)
            self.client.server_info() 

            # Set the database and users
            self.db = self.client["opencortex"]
            self.users = self.db["users"]

            logger.info("Successfully connected to MongoDB.")
        
        # Handle connection errors
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.client = None

    # Create a new user
    def create_user(self, username, password):
        """Hash the password and save a new user if they don't exist."""

        # Check if database is available
        if not self.client:
            return False, "Database connection unavailable."

        # Check if user already exists
        if self.users.find_one({"username": username}):
            return False, "Username already exists."
        
        # Hash the password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert the new user
        self.users.insert_one({
            "username": username, 
            "password": hashed_pw
        })

        logger.info(f"User {username} created successfully.")
        return True, "User created successfully."

    # Verify a user
    def verify_user(self, username, password):
        """Check credentials against stored hashes."""

        # Check if database is available
        if not self.client:
            return False, "Database connection unavailable."

        # Find the user
        user = self.users.find_one({"username": username})
        if not user:
            return False, "User not found."
        
        # Check if the provided password matches the hash
        if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            logger.info(f"User {username} logged in successfully.")
            return True, "Login successful."
        
        logger.error(f"User {username} login failed.")
        return False, "Invalid password."

    def save_message(self, username, role, content):
        """Append a message to the user's history."""

        # Save the message
        self.db.conversations.update_one(
            {"username": username},
            {"$push": {"messages": {"role": role, "content": content}}},
            upsert=True
        )

        logger.info(f"Message saved for user {username}.")

    # Get a user's chat history
    def get_history(self, username):
        """Retrieve all previous messages for a user."""

        # Get the user's data
        user_data = self.db.conversations.find_one({"username": username})

        return user_data["messages"] if user_data else []

    # Clear a user's chat history
    def clear_history(self, username):
        """Wipe chat history for a clean slate."""

        # Delete the user's data
        self.db.conversations.delete_one({"username": username})
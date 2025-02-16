import os
import subprocess
import logging
import json
import requests
from notion_client import Client
from requests.exceptions import RequestException

# Load Notion API credentials
with open("notion_config.json") as f:
    config = json.load(f)

notion = Client(auth=config["token"])
database_id = config["database_id"]

# Load Vast.ai API credentials
with open("vast_config.json") as f:
    vast_config = json.load(f)

VAST_API_KEY = vast_config["api_key"]
VAST_BASE_URL = "https://vast.ai/api/v0"

# Configure logging
logging.basicConfig(
    filename="autobot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='a'
)

def log_to_notion(action):
    """Logs actions to Notion Database."""
    try:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={"Name": {"title": [{"text": {"content": action}}]}}
        )
        logging.info(f"Logged to Notion: {action}")
    except Exception as e:
        logging.error(f"Error logging to Notion: {str(e)}")

def log_action(action, level='info'):
    """Logs actions locally and in Notion."""
    log_method = getattr(logging, level, logging.info)
    log_method(action)
    log_to_notion(action)

class Autobot:
    def __init__(self):
        """Initialize the automation bot."""
        log_action("Autobot initialized.", 'info')

    def say_hello(self):
        """A simple function that returns a greeting."""
        return "Hello from the Autobot!"

    def run_command(self, command):
        """Execute a system command synchronously."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout.strip()
                log_action(f"Executed command: {command} | Output: {output}")
                return output
            else:
                error_msg = result.stderr.strip()
                log_action(f"Command failed: {command} | Error: {error_msg}", 'error')
                return f"❌ Command failed: {error_msg}"
        except Exception as e:
            log_action(f"Error executing command: {command} | Error: {str(e)}", 'error')
            return f"❌ Error: {str(e)}"

    def git_commit(self, message):
        """Commit changes in the Git repository with a provided message."""
        self.run_command("git add -A")
        commit_result = self.run_command(f"git commit -m '{message}'")
        if "nothing to commit" in commit_result:
            log_action("No changes to commit.")
            return "No changes to commit."
        else:
            log_action(f"Changes committed: {message}")
            return "Changes committed successfully."

    def git_push(self):
        """Push the latest commits to the remote Git repository."""
        push_result = self.run_command("git push origin main")
        if push_result:
            log_action("Changes pushed to remote repository successfully.")
            return "Changes pushed to remote repository successfully."
        else:
            log_action("Failed to push changes.")
            return "Failed to push changes."

    def modify_self(self, new_code, function_name):
        """Modify autobot.py by adding a new function inside the Autobot class."""
        script_path = "autobot.py"

        try:
            with open(script_path, "r") as file:
                existing_code = file.readlines()

            # Check if function already exists
            if any(f"def {function_name}(" in line for line in existing_code):
                return f"❌ Function {function_name} already exists in autobot.py!"

            # Find the index of `class Autobot`
            class_index = None
            for i, line in enumerate(existing_code):
                if line.strip().startswith("class Autobot"):
                    class_index = i
                    break

            if class_index is None:
                return "❌ Error: Could not find Autobot class in autobot.py!"

            # Find the last function inside the class
            insert_index = class_index + 1
            while insert_index < len(existing_code):
                if existing_code[insert_index].strip().startswith("def "):
                    last_function_index = insert_index
                insert_index += 1

            # Ensure proper indentation (inside class)
            indented_code = "\n".join(["    " + line for line in new_code.split("\n")])

            # Insert new function inside the Autobot class
            existing_code.insert(last_function_index + 1, "\n" + indented_code + "\n")

            with open(script_path, "w") as file:
                file.writelines(existing_code)

            # Commit and push changes
            self.git_commit(f"Added new feature: {function_name}")
            self.git_push()

            return f"✅ Successfully added {function_name} to autobot.py and pushed to GitHub!"
        
        except Exception as e:
            return f"❌ Error modifying autobot.py: {str(e)}"

    def list_files(self, directory="."):
        """List files in a directory."""
        try:
            files = os.listdir(directory)
            log_action(f"Listed files in directory: {directory}")
            return "\n".join(files)
        except Exception as e:
            log_action(f"Error listing files in {directory}: {str(e)}", 'error')
            return f"❌ Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    bot = Autobot()
    print("🔹 Running test commands...")
    print(bot.run_command("ls"))

    # Test adding a new function
    new_function_code = """
def say_hello(self):

    
    def introduce(self):
        \"\"\"A function that introduces the bot.\"\"\"
        return "I am Autobot, your automation assistant!"
    
    \\\"\\\"\\\"A simple function that returns a greeting.\\\"\\\"\\\"
    return "Hello from the Autobot!"
"""
    print(bot.modify_self(new_function_code, "say_hello"))

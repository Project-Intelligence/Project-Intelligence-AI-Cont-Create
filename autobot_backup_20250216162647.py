import os
import subprocess
import logging
import json
import requests
import importlib
import shutil
import sys
from datetime import datetime
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

def log_action(action, level='info'):
    """Logs actions locally and in Notion."""
    log_method = getattr(logging, level, logging.info)
    log_method(action)
    try:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={"Name": {"title": [{"text": {"content": action}}]}}
        )
    except Exception as e:
        logging.error(f"Notion logging failed: {str(e)}")

class Autobot:
    def __init__(self):
        """Initialize the automation bot."""
        log_action("Autobot initialized.", 'info')

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

    def setup_git_credentials(self):
        """Configures Git to remember the user's credentials."""
        self.run_command("git config --global credential.helper store")
        log_action("Git credentials stored for future use.")

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
        if "rejected" in push_result:
            log_action("Git push failed. Pulling latest changes first.", 'warning')
            self.run_command("git pull origin main --rebase")
            push_result = self.run_command("git push origin main")
        return push_result

    def check_function_exists(self, function_name):
        """Check if a function exists inside the Autobot class."""
        return hasattr(self, function_name)

    def backup_script(self):
        """Create a backup of the script before modification."""
        backup_name = f"autobot_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
        shutil.copy("autobot.py", backup_name)
        log_action(f"Backup created: {backup_name}")
        return backup_name

    def modify_self(self, new_code, function_name):
        """Modify autobot.py by adding a new function inside the Autobot class."""
        script_path = "autobot.py"
        backup_name = self.backup_script()

        try:
            with open(script_path, "r") as file:
                existing_code = file.readlines()

            # Check if function already exists
            if any(f"def {function_name}(" in line for line in existing_code):
                return f"❌ Function {function_name} already exists in autobot.py!"

            # Find `class Autobot`
            class_index = next(
                (i for i, line in enumerate(existing_code) if line.strip().startswith("class Autobot")), None
            )

            if class_index is None:
                return "❌ Error: Could not find Autobot class in autobot.py!"

            # Find the last function inside `Autobot`
            last_function_index = class_index
            for i in range(class_index + 1, len(existing_code)):
                if existing_code[i].strip().startswith("def "):
                    last_function_index = i

            # Ensure correct indentation
            new_code_lines = new_code.strip().split("\n")
            if not new_code_lines[0].strip().startswith("def "):
                return "❌ Error: Function definition must start with 'def'."

            formatted_code = "\n".join(["    " + line.lstrip() for line in new_code_lines])

            # Insert new function inside the Autobot class
            existing_code.insert(last_function_index + 1, "\n" + formatted_code + "\n")

            with open(script_path, "w") as file:
                file.writelines(existing_code)

            # Run syntax check before committing
            syntax_check = self.run_command(f"python -m py_compile {script_path}")
            if "SyntaxError" in syntax_check:
                shutil.copy(backup_name, script_path)
                return f"❌ Syntax error detected! Rollback performed."

            # Commit and push changes
            self.git_commit(f"Added new feature: {function_name}")
            self.git_push()

            # Reload `autobot` after modification
            import autobot
            importlib.reload(autobot)

            # Verify function exists
            test_bot = autobot.Autobot()
            if not hasattr(test_bot, function_name):
                shutil.copy(backup_name, script_path)
                return f"❌ Rollback performed. {function_name} was not added correctly."

            os.execv(sys.executable, ['python'] + sys.argv)  # Restart script
            return f"✅ Successfully added {function_name} to autobot.py and pushed to GitHub!"

        except Exception as e:
            shutil.copy(backup_name, script_path)
            return f"❌ Error modifying autobot.py: {str(e)}. Rollback performed."

# Example usage
if __name__ == "__main__":
    bot = Autobot()
    bot.setup_git_credentials()  # Ensure Git credentials are stored
    print("🔹 Running test commands...")
    print(bot.run_command("ls"))

    # Test adding a new function
    new_function_code = """def auto_fix(self):
    \"\"\"A function that confirms if the bot can debug itself.\"\"\"
    return "I can now check and debug my own modifications!"
"""

    print(bot.modify_self(new_function_code, "auto_fix"))
    print(f"Function exists? {bot.check_function_exists('auto_fix')}")

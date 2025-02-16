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
    filemode='a'  # Append logs to retain history
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
        push_result = self.run_command("git push")
        if push_result:
            log_action("Changes pushed to remote repository successfully.")
            return "Changes pushed to remote repository successfully."
        else:
            log_action("Failed to push changes.")
            return "Failed to push changes."

    def generate_script(self, script_name, language="python", content=None):
        """Generate a script file."""
        templates = {
            "python": f"""# {script_name}.py
print("Hello from {script_name} script!")
""",
            "bash": f"""#!/bin/bash
echo "Hello from {script_name} script!"
""",
            "javascript": f"""// {script_name}.js
console.log("Hello from {script_name} script!");
""",
            "go": f"""// {script_name}.go
package main
import "fmt"
func main() {{
    fmt.Println("Hello from {script_name} script!")
}}
""",
            "rust": f"""// {script_name}.rs
fn main() {{
    println!("Hello from {script_name} script!");
}}
"""
        }

        if language not in templates:
            log_action(f"Failed script generation: Unsupported language {language}", 'error')
            return "❌ Unsupported language!"

        file_name = f"{script_name}.{language}"
        script_content = content if content else templates[language]

        with open(file_name, "w") as file:
            file.write(script_content)
        log_action(f"Generated script: {file_name}")
        self.git_commit(f"Generated script {file_name}")
        return f"✅ Script {file_name} created."

    def list_files(self, directory="."):
        """List files in a directory."""
        try:
            files = os.listdir(directory)
            log_action(f"Listed files in directory: {directory}")
            return "\n".join(files)
        except Exception as e:
            log_action(f"Error listing files in {directory}: {str(e)}", 'error')
            return f"❌ Error: {str(e)}"

    def list_vast_instances(self):
        """List active Vast.ai instances."""
        url = f"{VAST_BASE_URL}/instances?api_key={VAST_API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            instances = data.get("instances", {})

            if not instances:
                log_action("No active Vast.ai instances found.")
                return "ℹ️ No active instances."

            result = "\n".join([
                f"ID: {inst.get('id', 'N/A')} | Machine: {inst.get('label', 'Unknown')} | Status: {inst.get('actual_status', 'Unknown')}"
                for inst in instances.values()
            ])
            
            log_action(f"Listed Vast.ai instances: {result}")
            return result
        except RequestException as e:
            log_action(f"Network error listing Vast.ai instances: {str(e)}", 'error')
            return f"❌ Network Error: {str(e)}"
        except ValueError:
            log_action("Error parsing Vast.ai API response", 'error')
            return "❌ Error: Invalid API response format."

    def manage_vast_instance(self, instance_id, action="start"):
        """Start or stop a Vast.ai instance."""
        url = f"{VAST_BASE_URL}/instances/{action}?api_key={VAST_API_KEY}"
        payload = {"id": instance_id}

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                log_action(f"{action.capitalize()}ed Vast.ai instance: {instance_id}")
                return f"✅ {action.capitalize()}ed instance {instance_id}"
            else:
                log_action(f"Failed to {action} Vast.ai instance {instance_id}: {response.text}", 'error')
                return f"❌ Error {action}ing instance: {response.text}"
        except RequestException as e:
            log_action(f"Error {action}ing Vast.ai instance {instance_id}: {str(e)}", 'error')
            return f"❌ Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    bot = Autobot()
    print("🔹 Running test commands...")
    print(bot.run_command("ls"))
    print(bot.generate_script("test_script", "python"))
    print(bot.list_vast_instances())


import importlib
import os
import json
import logging
import openai
import time
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Setup logging
logging.basicConfig(
    filename="autobot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Autobot:
    def __init__(self, plugin_folder='plugins', max_plugins=10):
        """Initialize Autobot with AI-powered script generation, quality control, and automation capabilities."""
        self.plugin_folder = plugin_folder
        self.max_plugins = max_plugins
        self.config_file = "config.json"
        self.plugins = {}

        self.ensure_plugin_folder()
        self.load_api_keys()
        self.load_plugins()
        print("✅ Autobot initialized and ready!")

    def ensure_plugin_folder(self):
        """Ensure the plugins folder exists."""
        if not os.path.exists(self.plugin_folder):
            print(f"📁 Creating plugin folder: {self.plugin_folder}")
            os.makedirs(self.plugin_folder)

    def load_api_keys(self):
        """Load API keys from config.json."""
        if not os.path.exists(self.config_file):
            print("⚠️ No config.json file found. Creating a new one.")
            self.create_config_file()
        try:
            with open(self.config_file, "r") as file:
                self.api_keys = json.load(file)
            print("🔑 API keys successfully loaded.")
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON format in config file.")
            self.api_keys = {}

    def create_config_file(self):
        """Create a default config.json file if missing."""
        default_config = {
            "token": "",
            "database_id": "",
            "openai_api_key": "",
            "twitter_api_key": "",
            "twitter_api_secret": "",
            "twitter_access_token": "",
            "twitter_access_secret": ""
        }
        with open(self.config_file, "w") as file:
            json.dump(default_config, file, indent=4)
        print("✅ Default config.json file created. Please update it with your API keys.")

    def generate_ai_plugin(self, plugin_name):
        """Use AI (GPT-4) to generate a new automation plugin script with built-in quality control."""
        prompt = f"""
        Write a Python plugin script for Autobot named '{plugin_name}'. 
        The script must include a function named `run()` that performs an automation task.
        Example tasks: generate a random fact, pull data from an API, format text, or process JSON.
        Ensure:
        - Code is fully functional, follows best practices, and has no syntax errors.
        - The script is properly formatted and structured.
        - No redundancy or unnecessary functions.
        """

        openai.api_key = self.api_keys.get("openai_api_key", "")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            script_content = response["choices"][0]["message"]["content"].strip()

            if self.validate_script(script_content):
                plugin_path = os.path.join(self.plugin_folder, f"{plugin_name}.py")
                with open(plugin_path, "w") as file:
                    file.write(script_content)
                print(f"✅ AI-generated plugin '{plugin_name}.py' created successfully!")
                logging.info(f"AI-generated plugin: {plugin_name}.py")
            else:
                print("❌ AI script validation failed. Script was not saved.")
                logging.error(f"AI script validation failed for: {plugin_name}.py")

        except Exception as e:
            print(f"❌ Error generating AI plugin: {e}")
            logging.error(f"Error generating AI plugin: {e}")

    def validate_script(self, script_content):
        """Use AI to validate script quality before saving."""
        validation_prompt = f"""
        Analyze the following Python script for correctness, readability, and formatting. 
        Ensure:
        - The code runs without syntax errors.
        - All functions are necessary and meaningful.
        - No spelling mistakes in comments or outputs.
        - The script is aligned and formatted correctly.

        Here is the script:
        ```python
        {script_content}
        ```

        Respond with "VALID" if the script is acceptable, otherwise list issues.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": validation_prompt}]
        )

        validation_result = response["choices"][0]["message"]["content"].strip()

        if "VALID" in validation_result:
            return True
        else:
            print("⚠️ AI detected issues with the script:")
            print(validation_result)
            logging.error(f"AI validation failed: {validation_result}")
            return False

    def run_web_automation(self, search_query):
        """Automate web browsing using OpenAI Operator or other sites."""
        driver = webdriver.Chrome()  # Requires ChromeDriver installed
        driver.get("https://google.com")

        search_box = driver.find_element("name", "q")
        search_box.send_keys(search_query + Keys.RETURN)

        time.sleep(3)  # Wait for results

        results = driver.find_elements("xpath", "//h3")
        output = [result.text for result in results[:5]]  # Get first 5 results

        driver.quit()
        return "\n".join(output)

    def start_cli(self):
        """Interactive CLI for managing plugins and automation."""
        while True:
            command = input("\n🔹 Enter command (generate, list, run, reload, web, exit): ").strip().lower()
            
            if command == "generate":
                script_name = input("🤖 Enter script name (without .py): ").strip()
                self.generate_ai_plugin(script_name)

            elif command == "list":
                plugin_files = [f for f in os.listdir(self.plugin_folder) if f.endswith(".py")]
                if plugin_files:
                    print("📂 Available Plugins:", ", ".join(plugin_files))
                else:
                    print("⚠️ No plugins found.")

            elif command == "run":
                for plugin_name, plugin in self.plugins.items():
                    try:
                        result = plugin.run()
                        print(f"➡️ {plugin_name}: {result}")
                    except AttributeError:
                        print(f"❌ Plugin '{plugin_name}' is missing a 'run()' function.")

            elif command == "reload":
                self.load_plugins()

            elif command == "web":
                query = input("🔍 Enter search query: ")
                result = self.run_web_automation(query)
                print(f"🔎 Web Search Results:\n{result}")

            elif command == "exit":
                print("👋 Exiting Autobot...")
                exit()

            else:
                print("⚠️ Unknown command. Use: generate, list, run, reload, web, exit.")

if __name__ == '__main__':
    bot = Autobot()
    bot.start_cli()

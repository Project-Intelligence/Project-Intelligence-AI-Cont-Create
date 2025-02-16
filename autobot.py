import importlib
import os
import json
import logging
import subprocess
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename="autobot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Autobot:
    def __init__(self, plugin_folder='plugins', max_plugins=10, git_repo="https://github.com/Project-Intelligence/Project-Intelligence-AI-Cont-Create.git"):
        """Initialize Autobot with manual plugin control and Git-based API key retrieval."""
        self.plugin_folder = plugin_folder
        self.max_plugins = max_plugins
        self.git_repo = git_repo
        self.config_file = "config.json"
        self.plugins = {}

        self.ensure_plugin_folder()
        self.pull_api_keys_from_git()
        self.load_api_keys()
        self.load_plugins()
        print("✅ Autobot initialized and ready!")

    def ensure_plugin_folder(self):
        """Ensure the plugins folder exists."""
        if not os.path.exists(self.plugin_folder):
            print(f"📁 Creating plugin folder: {self.plugin_folder}")
            os.makedirs(self.plugin_folder)

    def pull_api_keys_from_git(self):
        """Pull the latest API keys from a Git repository and store them in config.json."""
        try:
            if os.path.exists("api_keys"):
                subprocess.run(["rm", "-rf", "api_keys"], check=True)  # Remove old keys if they exist
            
            print("🔄 Pulling API keys from Git...")
            subprocess.run(["git", "clone", self.git_repo, "api_keys"], check=True)
            
            # Ensure notion_config.json exists and copy it to config.json
            notion_config_path = "api_keys/notion_config.json"
            if os.path.exists(notion_config_path):
                subprocess.run(["cp", notion_config_path, self.config_file], check=True)
                print("✅ API keys successfully copied to config.json")
            else:
                print("⚠️ No notion_config.json found. Creating a default config.json...")
                self.create_config_file()

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to pull API keys: {e}")
            self.create_config_file()  # If Git fails, create a blank config.json

    def create_config_file(self):
        """Create a default config.json file if one does not exist."""
        if not os.path.exists(self.config_file):
            default_config = {
                "token": "",
                "database_id": ""
            }
            with open(self.config_file, "w") as file:
                json.dump(default_config, file, indent=4)
            print("✅ Default config.json file created. Please update it with your API keys.")

    def load_api_keys(self):
        """Load API keys from config.json."""
        if not os.path.exists(self.config_file):
            print("⚠️ No config.json file found. API keys not loaded.")
            self.api_keys = {}
            return

        try:
            with open(self.config_file, "r") as file:
                self.api_keys = json.load(file)
            print("🔑 API keys successfully loaded.")
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON format in config file.")
            self.api_keys = {}

    def create_plugin(self, plugin_name):
        """Manually create a new plugin."""
        plugin_path = os.path.join(self.plugin_folder, f"{plugin_name}.py")

        if os.path.exists(plugin_path):
            print(f"⚠️ Plugin '{plugin_name}' already exists.")
            return
        
        plugin_code = f"""def run():
    return "🤖 Automation Plugin: {plugin_name} executed successfully!"
"""

        with open(plugin_path, "w") as plugin_file:
            plugin_file.write(plugin_code)

        print(f"📝 New plugin created: {plugin_name}.py")
        logging.info(f"Manually created plugin: {plugin_name}")

    def load_plugins(self):
        """Load all plugins dynamically."""
        self.plugins = {}

        plugin_files = [f[:-3] for f in os.listdir(self.plugin_folder) if f.endswith(".py") and f != "__init__.py"]

        for plugin_name in plugin_files:
            if plugin_name not in self.plugins:
                try:
                    module = importlib.import_module(f"{self.plugin_folder}.{plugin_name}")
                    self.plugins[plugin_name] = module
                    print(f"✅ Loaded plugin: {plugin_name}")
                    logging.info(f"Loaded plugin: {plugin_name}")
                except Exception as e:
                    print(f"❌ Failed to load plugin '{plugin_name}': {e}")
                    logging.error(f"Failed to load plugin '{plugin_name}': {e}")

    def reload_plugins(self):
        """Reload plugins manually."""
        print("\n🔄 Reloading Plugins...")
        logging.info("Reloading plugins...")
        self.load_plugins()
        print("✅ Plugins reloaded successfully!\n")

    def run_plugins(self):
        """Run all loaded plugins."""
        if not self.plugins:
            print("❌ No plugins loaded.")
            return

        print("\n🔹 Running Plugins:")
        for plugin_name, plugin in self.plugins.items():
            try:
                result = plugin.run()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"➡️ [{timestamp}] {plugin_name}: {result}")
                logging.info(f"[{timestamp}] {plugin_name} executed successfully.")
            except AttributeError:
                print(f"❌ Plugin '{plugin_name}' is missing a 'run()' function.")
                logging.error(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Plugin '{plugin_name}' is missing a 'run()' function.")

    def start_cli(self):
        """Interactive CLI for managing plugins."""
        while True:
            command = input("\n🔹 Enter command (create, list, run, reload, exit): ").strip().lower()
            
            if command == "create":
                plugin_name = input("📝 Enter plugin name (without .py): ").strip()
                self.create_plugin(plugin_name)
            
            elif command == "list":
                plugin_files = [f for f in os.listdir(self.plugin_folder) if f.endswith(".py")]
                if plugin_files:
                    print("📂 Available Plugins:", ", ".join(plugin_files))
                else:
                    print("⚠️ No plugins found.")

            elif command == "run":
                self.run_plugins()

            elif command == "reload":
                self.reload_plugins()

            elif command == "exit":
                print("👋 Exiting Autobot...")
                logging.info("Autobot terminated by user.")
                exit()

            else:
                print("⚠️ Unknown command. Use: create, list, run, reload, exit.")

if __name__ == '__main__':
    bot = Autobot(max_plugins=10, git_repo="https://github.com/Project-Intelligence/Project-Intelligence-AI-Cont-Create.git")
    bot.start_cli()

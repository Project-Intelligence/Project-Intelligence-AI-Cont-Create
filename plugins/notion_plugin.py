import requests
import json

# Load API keys from config.json
with open("config.json", "r") as file:
    api_keys = json.load(file)

NOTION_API_KEY = api_keys.get("token", "")
NOTION_DATABASE_ID = api_keys.get("database_id", "")

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_notion_page(title, content):
    """Create a new Notion page with the given title and content."""
    url = "https://api.notion.com/v1/pages"

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": content}}]
                }
            }
        ]
    }

    response = requests.post(url, headers=HEADERS, json=data)
    
    if response.status_code == 200:
        return f"✅ Notion page created: {title}"
    else:
        return f"❌ Error creating Notion page: {response.text}"

def run():
    """Execute the Notion automation plugin."""
    return create_notion_page("Autobot Test Page", "This page was created by Autobot using Notion API!")

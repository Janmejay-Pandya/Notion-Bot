import os
from notion_client import Client
from dotenv import load_dotenv
from notion_formatter import parse_to_notion_blocks

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))
PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

def create_notion_page(title: str, content: str):
    """Create a Notion page with full markdown formatting."""
    blocks = parse_to_notion_blocks(content)

    page = notion.pages.create(
        parent={"page_id": PAGE_ID},
        properties={
            "title": [{"text": {"content": title}}],
        },
        children=blocks,
    )

    return page

import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
NOTION_TOKEN=os.getenv("NOTION_TOKEN")
NOTION_PARENT_PAGE_ID=os.getenv("NOTION_PARENT_PAGE_ID")

if not NOTION_TOKEN or not NOTION_PARENT_PAGE_ID:
    raise ValueError("Set notion env")

notion=Client(auth=NOTION_TOKEN)

def create_notion_page(title: str,content:str):
    """ Create a new Notion page under the configured parent page,
    with a title property and a single paragraph block for content."""
    # Notion's page creation payload: parent + properties + children
    page= notion.pages.create(
        parent={"page_id":NOTION_PARENT_PAGE_ID},
        properties={
            "title":[
                {
                    "type":"text",
                    "text":{"content":title}
                }
            ]
        },
        children=[
            {
                "object":"block",
                "type":"heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": title}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
            }
        ]
    )
    return page



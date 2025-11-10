# backend/notion_formatter.py

import re

def parse_to_notion_blocks(text: str):
    """
    Converts markdown-like text into Notion API blocks.
    Supports:
    - Headings (#, ##, ###)
    - Checkboxes (- [ ] or - [x])
    - Bulleted lists (- item)
    - Numbered lists (1. item)
    - Quotes (> text)
    - Code blocks (```...```)
    - Tables (| Col1 | Col2 |)
    - Paragraphs
    """

    lines = text.splitlines()
    blocks = []
    table_buffer = []
    code_buffer = []
    in_code_block = False

    for raw in lines:
        line = raw.rstrip()

        # --- CODE BLOCK START / END ---
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_buffer = []
            else:
                # Close code block
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(code_buffer)}}],
                        "language": "python"  # you can dynamically detect later
                    }
                })
                in_code_block = False
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        # --- EMPTY LINE: flush tables if needed ---
        if not line.strip():
            if table_buffer:
                blocks.append(table_to_notion(table_buffer))
                table_buffer = []
            continue

        # --- CHECKBOXES ---
        if re.match(r"^- \[[ xX]\]", line):
            checked = "[x]" in line.lower()
            content = re.sub(r"^- \[[ xX]\]\s*", "", line)
            blocks.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": [{"type": "text", "text": {"content": content}}],
                    "checked": checked
                }
            })
            continue

        # --- NUMBERED LIST ---
        if re.match(r"^\d+\.\s+", line):
            content = re.sub(r"^\d+\.\s+", "", line)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            })
            continue

        # --- BULLETED LIST ---
        if re.match(r"^- ", line) and not re.match(r"^- \[[ xX]\]", line):
            content = re.sub(r"^- ", "", line)
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                }
            })
            continue

        # --- HEADINGS ---
        if line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]}
            })
            continue
        if line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}
            })
            continue
        if line.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
            })
            continue

        # --- QUOTES ---
        if line.startswith("> "):
            content = line[2:].strip()
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {"rich_text": [{"type": "text", "text": {"content": content}}]}
            })
            continue

        # --- TABLES ---
        line = line.replace("||", "|")  # collapse double pipes if Gemini adds them
        if "|" in line:
            # Skip markdown table dividers like |---|
            if re.match(r"^\|?[-\s|]+\|?$", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            table_buffer.append(cells)
            continue

        # --- PARAGRAPH (default fallback) ---
        if table_buffer:
            blocks.append(table_to_notion(table_buffer))
            table_buffer = []
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}
        })

    # Flush table buffer if any at end
    if table_buffer:
        blocks.append(table_to_notion(table_buffer))
    return blocks


def table_to_notion(rows):
    """Convert list[list[str]] into a valid Notion table block."""
    # Determine max number of columns in any row
    width = max(len(r) for r in rows)
    normalized_rows = []

    print(f"ℹ️ Normalizing table to width {width} columns.")

    for row in rows:
        # Pad short rows to the correct width
        padded_row = row + [""] * (width - len(row))

        # Each row in Notion expects cells as a list of lists of rich_text objects
        notion_cells = [[{"type": "text", "text": {"content": c}}] for c in padded_row]

        if len(row) < width:
            print(f"⚠️ Padded table row from {len(row)} to {width} cells: {row}")

        normalized_rows.append({
            "object": "block",
            "type": "table_row",
            "table_row": {"cells": notion_cells}
        })

    # Return the full table block
    return {
        "object": "block",
        "type": "table",
        "table": {
            "has_column_header": True,
            "has_row_header": False,
            "table_width": width,
            "children": normalized_rows
        },
    }



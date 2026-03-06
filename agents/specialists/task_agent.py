"""
agents/specialists/task_agent.py
Creates/updates tasks in Notion and Trello.
"""

from __future__ import annotations
import os
import structlog

logger = structlog.get_logger()


async def create_notion_task(params: dict) -> dict:
    title = params.get("title", "Untitled Task")
    description = params.get("description", "")
    due_date = params.get("due_date")
    tags = params.get("tags", [])

    notion_key = os.getenv("NOTION_API_KEY", "")
    db_id = os.getenv("NOTION_DATABASE_ID", "")

    if not notion_key or not db_id:
        return {"error": "NOTION_API_KEY and NOTION_DATABASE_ID not set"}

    try:
        from notion_client import AsyncClient
        notion = AsyncClient(auth=notion_key)

        properties = {
            "Name": {"title": [{"text": {"content": title}}]},
        }
        if tags:
            properties["Tags"] = {"multi_select": [{"name": t} for t in tags]}
        if due_date:
            properties["Due Date"] = {"date": {"start": due_date}}

        result = await notion.pages.create(
            parent={"database_id": db_id},
            properties=properties,
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": description}}]},
            }] if description else [],
        )

        logger.info("task.notion_created", title=title, page_id=result["id"])
        return {"page_id": result["id"], "url": result["url"], "success": True}

    except Exception as e:
        logger.error("task.notion_create_error", error=str(e))
        return {"error": str(e), "success": False}


async def list_notion_tasks(params: dict) -> dict:
    notion_key = os.getenv("NOTION_API_KEY", "")
    db_id = os.getenv("NOTION_DATABASE_ID", "")

    if not notion_key or not db_id:
        return {"error": "NOTION_API_KEY and NOTION_DATABASE_ID not set", "tasks": []}

    try:
        from notion_client import AsyncClient
        notion = AsyncClient(auth=notion_key)

        result = await notion.databases.query(
            database_id=db_id,
            filter=params.get("filter"),
            sorts=[{"timestamp": "created_time", "direction": "descending"}],
        )

        tasks = []
        for page in result["results"]:
            title_prop = page["properties"].get("Name", {})
            title_parts = title_prop.get("title", [])
            title = "".join(t["plain_text"] for t in title_parts)
            tasks.append({"id": page["id"], "title": title, "url": page["url"]})

        return {"tasks": tasks}

    except Exception as e:
        logger.error("task.notion_list_error", error=str(e))
        return {"error": str(e), "tasks": []}

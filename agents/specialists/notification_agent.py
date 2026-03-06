"""
agents/specialists/notification_agent.py
Sends notifications to users via Telegram, Discord, or email.
"""

from __future__ import annotations
import os
import structlog

logger = structlog.get_logger()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway:8000")


async def send_notification(params: dict) -> dict:
    """
    Send a notification to the user.

    params:
      - user_key: str — The user identifier (telegram_id, discord_id, etc.)
      - message: str — The notification text
      - priority: str — "normal" | "high"
      - channel: str — "telegram" | "discord" | "email" (auto-detected if not set)
    """
    message = params.get("message", "")
    user_key = params.get("user_key", "default")
    priority = params.get("priority", "normal")
    channel = params.get("channel", "telegram")

    if not message:
        return {"success": False, "error": "No message provided"}

    if channel == "telegram":
        return await _send_telegram(user_key, message)
    elif channel == "discord":
        return await _send_discord(user_key, message)
    else:
        logger.warning("notification.unknown_channel", channel=channel)
        return {"success": False, "error": f"Unknown channel: {channel}"}


async def _send_telegram(user_key: str, message: str) -> dict:
    """Send a Telegram message to the user identified by user_key (their Telegram chat ID)."""
    if not TELEGRAM_TOKEN:
        logger.warning("notification.no_telegram_token")
        return {"success": False, "error": "TELEGRAM_BOT_TOKEN not configured"}

    # user_key is the Telegram chat_id for direct messages
    chat_id = user_key

    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            )
        data = resp.json()
        if data.get("ok"):
            logger.info("notification.telegram_sent", user=user_key)
            return {"success": True, "channel": "telegram"}
        else:
            logger.error("notification.telegram_error", error=data.get("description"))
            return {"success": False, "error": data.get("description")}
    except Exception as e:
        logger.error("notification.telegram_exception", error=str(e))
        return {"success": False, "error": str(e)}


async def _send_discord(user_key: str, message: str) -> dict:
    """Send a Discord DM to the user."""
    discord_token = os.getenv("DISCORD_BOT_TOKEN", "")
    if not discord_token:
        return {"success": False, "error": "DISCORD_BOT_TOKEN not configured"}

    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            # Create DM channel
            dm_resp = await client.post(
                "https://discord.com/api/v10/users/@me/channels",
                json={"recipient_id": user_key},
                headers={"Authorization": f"Bot {discord_token}"},
            )
            channel_id = dm_resp.json().get("id")
            if not channel_id:
                return {"success": False, "error": "Could not create DM channel"}

            # Send message
            msg_resp = await client.post(
                f"https://discord.com/api/v10/channels/{channel_id}/messages",
                json={"content": message},
                headers={"Authorization": f"Bot {discord_token}"},
            )

        if msg_resp.status_code in (200, 201):
            return {"success": True, "channel": "discord"}
        return {"success": False, "error": f"Discord API error: {msg_resp.status_code}"}

    except Exception as e:
        logger.error("notification.discord_exception", error=str(e))
        return {"success": False, "error": str(e)}

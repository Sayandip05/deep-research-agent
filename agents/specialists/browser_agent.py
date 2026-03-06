"""
agents/specialists/browser_agent.py
Controls Chromium via Playwright. Handles price scraping, social posting,
and general web navigation.
"""

from __future__ import annotations
import asyncio
import re
import structlog
from typing import Any

logger = structlog.get_logger()


async def scrape_price(params: dict) -> dict:
    """Navigate to a product page and extract the price."""
    url = params.get("url", "")
    if not url:
        return {"error": "No URL provided"}

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Stealth headers to avoid bot detection
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)  # let JS render

            # Extract title
            title = await page.title()

            # Try common price selectors (Amazon, generic e-commerce)
            price_selectors = [
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                ".a-price .a-offscreen",
                "[data-asin-price]",
                "[itemprop='price']",
                ".price",
                ".product-price",
                ".offer-price",
            ]

            price_text = None
            for selector in price_selectors:
                try:
                    el = page.locator(selector).first
                    if await el.count() > 0:
                        price_text = await el.text_content(timeout=2000)
                        break
                except Exception:
                    continue

            await browser.close()

            if not price_text:
                return {"error": "Could not find price on page", "title": title, "url": url}

            # Parse price number
            price_str = re.sub(r"[^\d.,]", "", price_text).replace(",", "")
            try:
                price = float(price_str)
            except ValueError:
                price = None

            logger.info("browser.price_scraped", url=url, price=price)
            return {"price": price, "price_text": price_text.strip(), "product_name": title, "url": url}

    except Exception as e:
        logger.error("browser.scrape_price_error", error=str(e))
        return {"error": str(e)}


async def scrape_page(params: dict) -> dict:
    """Scrape full text content from a URL."""
    url = params.get("url", "")
    selector = params.get("selector", "body")

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            title = await page.title()
            content = await page.inner_text(selector)
            await browser.close()

            return {"content": content[:5000], "title": title, "url": url}

    except Exception as e:
        logger.error("browser.scrape_page_error", error=str(e))
        return {"error": str(e)}


async def post_to_social(params: dict) -> dict:
    """Post text to Twitter/X — requires an active browser session."""
    text = params.get("text", "")
    platform = params.get("platform", "twitter")

    # TODO: implement actual social posting with stored session cookies
    logger.info("browser.post_to_social", platform=platform, text_length=len(text))
    return {
        "success": False,
        "message": "Social posting requires session setup. See skills/browser/SKILL.md",
    }

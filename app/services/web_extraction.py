"""Webpage fetching and readable text extraction."""

import httpx
from bs4 import BeautifulSoup


async def extract_webpage_text(url: str) -> str:
    """Fetch a webpage and return readable text."""
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=15.0,
        headers={"User-Agent": "ClearViewBot/0.1"},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
        tag.decompose()

    main = soup.find("main") or soup.find("article") or soup.body or soup
    return main.get_text(separator="\n", strip=True)

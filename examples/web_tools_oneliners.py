#!/usr/bin/env python3
"""
Web Search & Crawler One-Liners - Minimal Examples

Copy and paste these functions for instant web search/crawl capabilities.
No API key needed from localhost!
"""

import asyncio
import httpx
import json


async def quick_search(query: str, num_results: int = 5):
    """One-liner web search"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9000/api/v1/services/web_search/call",
            json={"tool_name": "search", "arguments": {"query": query, "num_results": num_results}}
        )
        result = response.json()
        return result["result"]["results"] if result["success"] else []


async def quick_crawl(url: str):
    """One-liner page crawl"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://localhost:9000/api/v1/services/web_crawler/call",
            json={"tool_name": "crawl", "arguments": {"url": url, "max_depth": 1}}
        )
        result = response.json()
        return result["result"]["pages"] if result["success"] else []


async def quick_extract(url: str):
    """One-liner content extraction"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:9000/api/v1/services/web_crawler/call",
            json={"tool_name": "extract_content", "arguments": {"url": url}}
        )
        result = response.json()
        return result["result"] if result["success"] else {}


# Example usage
async def demo():
    """Demo the one-liner functions"""
    print("⚡ Web Tools One-Liners Demo")
    print("=" * 40)
    
    # Search example
    print("🔍 Quick search...")
    results = await quick_search("Python asyncio", 3)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title'][:50]}...")
    
    # Crawl example  
    print(f"\n🕷️ Quick crawl...")
    pages = await quick_crawl("https://httpbin.org")
    print(f"Found {len(pages)} pages")
    
    # Extract example
    print(f"\n📄 Quick extract...")
    content = await quick_extract("https://python.org")
    print(f"Title: {content.get('title', 'No title')}")
    print(f"Content length: {len(content.get('text', ''))} chars")


if __name__ == "__main__":
    asyncio.run(demo())
#!/usr/bin/env python3
"""
Example demonstrating how to use the new web_search and crawl_page tools.

This example shows:
1. How to search for information using the Serper API
2. How to crawl and extract content from web pages
3. How to combine both tools to search and then analyze results

Prerequisites:
- Set the SERPER_API_KEY environment variable with your Serper API key
- Install dependencies: pip install requests beautifulsoup4 lxml
"""

import asyncio
import os
import sys
sys.path.insert(0, '/mnt/home/zomux/works/openmcp/src')

from openmcp.services.web_search_service import WebSearchService
from openmcp.services.web_crawler_service import WebCrawlerService


async def demo_web_search():
    """Demonstrate web search capabilities."""
    print("=" * 80)
    print("🔍 WEB SEARCH DEMO")
    print("=" * 80)
    
    # Get API key from environment
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("❌ Please set SERPER_API_KEY environment variable")
        return None, None
    
    # Initialize service
    config = {"serper_api_key": api_key}
    search_service = WebSearchService(config)
    await search_service.start()
    
    print("✅ Web Search Service initialized")
    
    # Example 1: Basic web search
    print("\n1️⃣ Basic Web Search")
    print("-" * 40)
    
    search_result = await search_service.call_tool("web_search", {
        "query": "artificial intelligence latest news 2024",
        "num_results": 5
    })
    
    if "error" in search_result:
        print(f"❌ Search failed: {search_result['error']}")
        return None, None
    
    results = search_result["results"]["organic"]
    print(f"Found {len(results)} results:")
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['title']}")
        print(f"     URL: {result['link']}")
        print(f"     Snippet: {result['snippet'][:100]}...")
        print()
    
    # Example 2: News search
    print("2️⃣ News Search")
    print("-" * 40)
    
    news_result = await search_service.call_tool("web_search", {
        "query": "OpenAI GPT latest developments",
        "search_type": "news",
        "num_results": 3
    })
    
    if "error" not in news_result:
        news = news_result["results"].get("news", [])
        print(f"Found {len(news)} news articles:")
        
        for i, article in enumerate(news, 1):
            print(f"  {i}. {article['title']}")
            print(f"     Source: {article['source']} | Date: {article.get('date', 'N/A')}")
            print(f"     URL: {article['link']}")
            print()
    
    # Example 3: Image search
    print("3️⃣ Image Search")
    print("-" * 40)
    
    image_result = await search_service.call_tool("web_search", {
        "query": "Python programming logo",
        "search_type": "images",
        "num_results": 3
    })
    
    if "error" not in image_result:
        images = image_result["results"].get("images", [])
        print(f"Found {len(images)} images:")
        
        for i, image in enumerate(images, 1):
            print(f"  {i}. {image['title']}")
            print(f"     Image URL: {image['imageUrl']}")
            print(f"     Source: {image['source']}")
            print()
    
    return search_service, results[0]['link'] if results else None


async def demo_web_crawler(test_url=None):
    """Demonstrate web crawling capabilities."""
    print("=" * 80)
    print("🕷️ WEB CRAWLER DEMO")
    print("=" * 80)
    
    # Initialize service
    config = {
        "timeout": 30,
        "max_content_length": 512 * 1024  # 512KB for demo
    }
    crawler_service = WebCrawlerService(config)
    await crawler_service.start()
    
    print("✅ Web Crawler Service initialized")
    
    # Use provided URL or default
    if not test_url:
        test_url = "https://example.com"
    
    print(f"\n🎯 Target URL: {test_url}")
    
    # Example 1: Basic page crawling
    print("\n1️⃣ Basic Page Crawling")
    print("-" * 40)
    
    crawl_result = await crawler_service.call_tool("crawl_page", {
        "url": test_url,
        "extract_metadata": True,
        "extract_links": False,
        "extract_images": False,
        "clean_html": False
    })
    
    if "error" in crawl_result:
        print(f"❌ Crawling failed: {crawl_result['error']}")
    else:
        print(f"✅ Successfully crawled page")
        print(f"   Status: {crawl_result['status_code']}")
        print(f"   Final URL: {crawl_result['url']}")
        print(f"   Content Type: {crawl_result['content_type']}")
        print(f"   Content Length: {crawl_result['content_length']} characters")
        
        # Show metadata
        metadata = crawl_result.get("metadata", {})
        if metadata:
            print("\n📋 Page Metadata:")
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Description: {metadata.get('description', 'N/A')[:100]}...")
            print(f"   Language: {metadata.get('language', 'N/A')}")
            print(f"   Author: {metadata.get('author', 'N/A')}")
        
        # Show content preview
        content = crawl_result.get("content", "")
        print(f"\n📄 Content Preview ({len(content)} chars):")
        print("-" * 40)
        print(content[:500] + ("..." if len(content) > 500 else ""))
    
    # Example 2: Extract links and images
    print("\n\n2️⃣ Extract Links and Images")
    print("-" * 40)
    
    detailed_result = await crawler_service.call_tool("crawl_page", {
        "url": test_url,
        "extract_metadata": True,
        "extract_links": True,
        "extract_images": True,
        "clean_html": False
    })
    
    if "error" not in detailed_result:
        # Show links
        links = detailed_result.get("links", [])
        print(f"🔗 Found {len(links)} links:")
        for i, link in enumerate(links[:5], 1):  # Show first 5
            print(f"   {i}. {link['text'][:50]}..." if len(link['text']) > 50 else f"   {i}. {link['text']}")
            print(f"      URL: {link['url']}")
        if len(links) > 5:
            print(f"   ... and {len(links) - 5} more")
        
        # Show images
        images = detailed_result.get("images", [])
        print(f"\n🖼️ Found {len(images)} images:")
        for i, image in enumerate(images[:3], 1):  # Show first 3
            print(f"   {i}. Alt: {image['alt'] or 'N/A'}")
            print(f"      URL: {image['url']}")
        if len(images) > 3:
            print(f"   ... and {len(images) - 3} more")
    
    # Example 3: Clean HTML extraction
    print("\n\n3️⃣ Clean HTML Extraction")
    print("-" * 40)
    
    html_result = await crawler_service.call_tool("crawl_page", {
        "url": test_url,
        "extract_metadata": False,
        "clean_html": True
    })
    
    if "error" not in html_result:
        html_content = html_result.get("content", "")
        print(f"📝 Clean HTML ({len(html_content)} chars):")
        print("-" * 40)
        print(html_content[:300] + ("..." if len(html_content) > 300 else ""))
    
    return crawler_service


async def demo_integration():
    """Demonstrate integration of search + crawling."""
    print("\n" + "=" * 80)
    print("🔄 INTEGRATION DEMO: Search → Crawl → Analyze")
    print("=" * 80)
    
    # Get API key
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("❌ Please set SERPER_API_KEY environment variable for integration demo")
        return
    
    # Initialize both services
    search_service = WebSearchService({"serper_api_key": api_key})
    await search_service.start()
    
    crawler_service = WebCrawlerService({
        "timeout": 30,
        "max_content_length": 256 * 1024  # 256KB
    })
    await crawler_service.start()
    
    print("✅ Both services initialized")
    
    # Step 1: Search for a topic
    search_query = "Python web scraping tutorial"
    print(f"\n🔍 Step 1: Searching for '{search_query}'")
    print("-" * 50)
    
    search_result = await search_service.call_tool("web_search", {
        "query": search_query,
        "num_results": 3
    })
    
    if "error" in search_result:
        print(f"❌ Search failed: {search_result['error']}")
        return
    
    results = search_result["results"]["organic"]
    print(f"Found {len(results)} results")
    
    # Step 2: Crawl the top results
    print(f"\n🕷️ Step 2: Crawling top {min(2, len(results))} results")
    print("-" * 50)
    
    analyzed_pages = []
    
    for i, result in enumerate(results[:2], 1):  # Crawl first 2 results
        url = result["link"]
        title = result["title"]
        
        print(f"\n   Crawling {i}: {title}")
        print(f"   URL: {url}")
        
        crawl_result = await crawler_service.call_tool("crawl_page", {
            "url": url,
            "extract_metadata": True,
            "extract_links": False,
            "extract_images": False
        })
        
        if "error" in crawl_result:
            print(f"   ❌ Failed to crawl: {crawl_result['error']}")
            continue
        
        # Analyze the content
        content = crawl_result.get("content", "")
        metadata = crawl_result.get("metadata", {})
        
        analysis = {
            "title": title,
            "url": url,
            "metadata_title": metadata.get("title", ""),
            "content_length": len(content),
            "has_python_keywords": "python" in content.lower(),
            "has_scraping_keywords": "scraping" in content.lower() or "beautifulsoup" in content.lower(),
            "description": metadata.get("description", "")[:100]
        }
        
        analyzed_pages.append(analysis)
        
        print(f"   ✅ Content length: {analysis['content_length']} chars")
        print(f"   🐍 Contains Python keywords: {analysis['has_python_keywords']}")
        print(f"   🕸️ Contains scraping keywords: {analysis['has_scraping_keywords']}")
    
    # Step 3: Summary
    print(f"\n📊 Step 3: Analysis Summary")
    print("-" * 50)
    
    for i, page in enumerate(analyzed_pages, 1):
        print(f"\n   Page {i}: {page['title'][:60]}...")
        print(f"   URL: {page['url']}")
        print(f"   Content: {page['content_length']} chars")
        print(f"   Python: {'✅' if page['has_python_keywords'] else '❌'}")
        print(f"   Scraping: {'✅' if page['has_scraping_keywords'] else '❌'}")
        if page['description']:
            print(f"   Description: {page['description']}...")
    
    # Cleanup
    await search_service.stop()
    await crawler_service.stop()
    print(f"\n🔴 Services stopped")


async def main():
    """Main demo function."""
    print("🚀 OpenMCP Web Tools Demo")
    print("🔍 Web Search (Serper API) + 🕷️ Web Crawler")
    print("=" * 80)
    
    # Check for API key
    if not os.getenv("SERPER_API_KEY"):
        print("⚠️  Note: Set SERPER_API_KEY environment variable for full demo")
        print("         Using example.com for crawler-only demo")
        print()
    
    # Demo 1: Web Search
    search_service, sample_url = await demo_web_search()
    if search_service:
        await search_service.stop()
    
    # Demo 2: Web Crawler
    crawler_service = await demo_web_crawler(sample_url)
    if crawler_service:
        await crawler_service.stop()
    
    # Demo 3: Integration
    if os.getenv("SERPER_API_KEY"):
        await demo_integration()
    else:
        print("\n⚠️  Skipping integration demo (no SERPER_API_KEY)")
    
    print("\n" + "=" * 80)
    print("🏁 Demo completed!")
    print("=" * 80)
    print("\n💡 Usage Tips:")
    print("  - Set SERPER_API_KEY for web search functionality")
    print("  - Configure services in config.yaml")
    print("  - Use with OpenMCP server for full MCP protocol support")
    print("  - Combine with browseruse service for interactive web automation")


if __name__ == "__main__":
    asyncio.run(main())
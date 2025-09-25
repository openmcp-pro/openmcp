#!/usr/bin/env python3
"""
Simple Web Tools Example - Basic usage of web_search and crawl_page tools.

This example shows straightforward usage patterns:
1. Basic web search with different types (web, news, images)
2. Simple webpage crawling and content extraction
3. Combining search and crawl for quick research
4. Error handling and best practices

Prerequisites:
- Set SERPER_API_KEY environment variable
- Install: pip install requests beautifulsoup4 lxml
"""

import asyncio
import os
import sys
from pprint import pprint

# Add the src directory to Python path
sys.path.insert(0, '/mnt/home/zomux/works/openmcp/src')

from openmcp.services.web_search_service import WebSearchService
from openmcp.services.web_crawler_service import WebCrawlerService


async def example_web_search():
    """Basic web search examples."""
    print("🔍 WEB SEARCH EXAMPLES")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("❌ SERPER_API_KEY not set. Using example key for demo.")
        api_key = "53f66cade9c650fe1f44b92dff2f0854ee4b83b4"  # Example key from user
    
    # Initialize service
    config = {"serper_api_key": api_key}
    service = WebSearchService(config)
    await service.start()
    
    try:
        # Example 1: Basic web search
        print("\n1️⃣ Basic Web Search")
        print("-" * 30)
        
        result = await service.call_tool("web_search", {
            "query": "best Python web frameworks 2024",
            "num_results": 3
        })
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Found {len(result['results']['organic'])} results")
            for i, item in enumerate(result['results']['organic'], 1):
                print(f"   {i}. {item['title']}")
                print(f"      {item['link']}")
                print(f"      {item['snippet'][:100]}...")
                print()
        
        # Example 2: News search
        print("2️⃣ News Search")
        print("-" * 30)
        
        news_result = await service.call_tool("web_search", {
            "query": "Python programming news",
            "search_type": "news",
            "num_results": 2
        })
        
        if "error" not in news_result and news_result['results'].get('news'):
            print(f"✅ Found {len(news_result['results']['news'])} news articles")
            for i, article in enumerate(news_result['results']['news'], 1):
                print(f"   {i}. {article['title']}")
                print(f"      Source: {article['source']}")
                print(f"      Date: {article.get('date', 'N/A')}")
                print(f"      {article['link']}")
                print()
        
        # Example 3: Image search
        print("3️⃣ Image Search")
        print("-" * 30)
        
        image_result = await service.call_tool("web_search", {
            "query": "Python logo",
            "search_type": "images",
            "num_results": 2
        })
        
        if "error" not in image_result and image_result['results'].get('images'):
            print(f"✅ Found {len(image_result['results']['images'])} images")
            for i, image in enumerate(image_result['results']['images'], 1):
                print(f"   {i}. {image['title']}")
                print(f"      Image: {image['imageUrl']}")
                print(f"      Source: {image['source']}")
                print()
    
    except Exception as e:
        print(f"❌ Error in web search: {str(e)}")
    
    finally:
        await service.stop()
        print("🔴 Web search service stopped")


async def example_web_crawler():
    """Basic web crawler examples."""
    print("\n🕷️ WEB CRAWLER EXAMPLES")
    print("=" * 50)
    
    # Initialize service
    config = {
        "timeout": 30,
        "max_content_length": 512 * 1024  # 512KB
    }
    service = WebCrawlerService(config)
    await service.start()
    
    try:
        # Example 1: Basic page crawling
        print("\n1️⃣ Basic Page Crawling")
        print("-" * 30)
        
        url = "https://httpbin.org/html"
        result = await service.call_tool("crawl_page", {
            "url": url,
            "extract_metadata": True
        })
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Successfully crawled: {url}")
            print(f"   Status: {result['status_code']}")
            print(f"   Content length: {result['content_length']} characters")
            print(f"   Content type: {result['content_type']}")
            
            # Show content preview
            content = result.get('content', '')
            print(f"   Content preview: {content[:200]}...")
        
        # Example 2: Extract metadata and links
        print("\n2️⃣ Extract Metadata and Links")
        print("-" * 30)
        
        url2 = "https://example.com"
        result2 = await service.call_tool("crawl_page", {
            "url": url2,
            "extract_metadata": True,
            "extract_links": True,
            "extract_images": True
        })
        
        if "error" not in result2:
            print(f"✅ Analyzed: {url2}")
            
            # Show metadata
            metadata = result2.get('metadata', {})
            if metadata:
                print(f"   Title: {metadata.get('title', 'N/A')}")
                print(f"   Description: {metadata.get('description', 'N/A')[:100]}...")
            
            # Show links and images count
            links = result2.get('links', [])
            images = result2.get('images', [])
            print(f"   Links found: {len(links)}")
            print(f"   Images found: {len(images)}")
            
            # Show first few links
            if links:
                print("   First few links:")
                for i, link in enumerate(links[:3], 1):
                    print(f"     {i}. {link['text'][:30]}... → {link['url']}")
        
        # Example 3: Get clean HTML
        print("\n3️⃣ Extract Clean HTML")
        print("-" * 30)
        
        html_result = await service.call_tool("crawl_page", {
            "url": url,
            "clean_html": True
        })
        
        if "error" not in html_result:
            html_content = html_result.get('content', '')
            print(f"✅ Clean HTML extracted ({len(html_content)} chars)")
            print(f"   HTML preview: {html_content[:150]}...")
    
    except Exception as e:
        print(f"❌ Error in web crawler: {str(e)}")
    
    finally:
        await service.stop()
        print("🔴 Web crawler service stopped")


async def example_combined_workflow():
    """Example of combining search and crawl for research."""
    print("\n🔄 COMBINED SEARCH + CRAWL WORKFLOW")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("❌ SERPER_API_KEY not set. Using example key for demo.")
        api_key = "53f66cade9c650fe1f44b92dff2f0854ee4b83b4"
    
    # Initialize both services
    search_service = WebSearchService({"serper_api_key": api_key})
    crawler_service = WebCrawlerService({"timeout": 25, "max_content_length": 256 * 1024})
    
    await search_service.start()
    await crawler_service.start()
    
    try:
        # Step 1: Search for a topic
        topic = "FastAPI Python tutorial"
        print(f"\n🔍 Step 1: Searching for '{topic}'")
        
        search_result = await search_service.call_tool("web_search", {
            "query": topic,
            "num_results": 2
        })
        
        if "error" in search_result:
            print(f"❌ Search failed: {search_result['error']}")
            return
        
        results = search_result['results']['organic']
        print(f"✅ Found {len(results)} results")
        
        # Step 2: Crawl the top result
        if results:
            top_result = results[0]
            print(f"\n🕷️ Step 2: Crawling top result")
            print(f"   Title: {top_result['title']}")
            print(f"   URL: {top_result['link']}")
            
            crawl_result = await crawler_service.call_tool("crawl_page", {
                "url": top_result['link'],
                "extract_metadata": True
            })
            
            if "error" in crawl_result:
                print(f"   ❌ Crawling failed: {crawl_result['error']}")
            else:
                content = crawl_result.get('content', '')
                metadata = crawl_result.get('metadata', {})
                
                print(f"   ✅ Successfully crawled!")
                print(f"   Content length: {len(content)} characters")
                print(f"   Page title: {metadata.get('title', 'N/A')}")
                
                # Count tutorial-related keywords
                tutorial_keywords = ['tutorial', 'guide', 'example', 'learn', 'how to']
                keyword_count = sum(1 for keyword in tutorial_keywords if keyword in content.lower())
                
                print(f"   Tutorial relevance: {keyword_count}/5 keywords found")
                
                # Show content preview
                print(f"   Content preview: {content[:300]}...")
        
        # Step 3: Quick analysis
        print(f"\n📊 Step 3: Quick Analysis")
        
        for i, result in enumerate(results, 1):
            domain = result['link'].split('/')[2] if '/' in result['link'] else result['link']
            print(f"   {i}. {result['title'][:40]}...")
            print(f"      Domain: {domain}")
            print(f"      Snippet: {result['snippet'][:80]}...")
            print()
    
    except Exception as e:
        print(f"❌ Error in combined workflow: {str(e)}")
    
    finally:
        await search_service.stop()
        await crawler_service.stop()
        print("🔴 Both services stopped")


async def main():
    """Main function to run all examples."""
    print("🚀 Simple Web Tools Examples")
    print("🔍 Web Search + 🕷️ Web Crawler")
    print("=" * 60)
    
    # Run examples
    await example_web_search()
    await example_web_crawler()
    await example_combined_workflow()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("\n💡 Quick Reference:")
    print("   Web Search tool: web_search")
    print("     - search_type: 'search', 'news', 'images', 'shopping', 'places'")
    print("     - num_results: 1-100")
    print("     - country: 'us', 'uk', 'ca', etc.")
    print("     - language: 'en', 'es', 'fr', etc.")
    print()
    print("   Web Crawler tool: crawl_page")
    print("     - extract_metadata: true/false")
    print("     - extract_links: true/false")
    print("     - extract_images: true/false")
    print("     - clean_html: true/false")
    print("     - custom_headers: {}")


if __name__ == "__main__":
    asyncio.run(main())
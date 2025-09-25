#!/usr/bin/env python3
"""Test script for the new web_search and crawl_page tools."""

import asyncio
import os
from pprint import pprint

from openmcp.services.web_search_service import WebSearchService
from openmcp.services.web_crawler_service import WebCrawlerService


async def test_web_search():
    """Test the web search service."""
    print("=" * 60)
    print("Testing Web Search Service")
    print("=" * 60)
    
    # Check if API key is available
    api_key = os.getenv("SERPER_API_KEY", "53f66cade9c650fe1f44b92dff2f0854ee4b83b4")
    if not api_key:
        print("❌ SERPER_API_KEY not found in environment variables")
        return
    
    config = {
        "serper_api_key": api_key
    }
    
    try:
        service = WebSearchService(config)
        await service.start()
        
        print("✅ Web Search Service started successfully")
        
        # Test basic search
        print("\n🔍 Testing basic search for 'Python programming'...")
        result = await service.call_tool("web_search", {
            "query": "Python programming",
            "num_results": 3
        })
        
        if "error" in result:
            print(f"❌ Search failed: {result['error']}")
        else:
            print("✅ Search successful!")
            print(f"Found {len(result['results'].get('organic', []))} results")
            
            # Print first result
            organic = result['results'].get('organic', [])
            if organic:
                first_result = organic[0]
                print(f"First result: {first_result.get('title', 'No title')}")
                print(f"URL: {first_result.get('link', 'No URL')}")
                print(f"Snippet: {first_result.get('snippet', 'No snippet')[:100]}...")
        
        await service.stop()
        print("🔴 Web Search Service stopped")
        
    except Exception as e:
        print(f"❌ Web Search Service test failed: {str(e)}")


async def test_web_crawler():
    """Test the web crawler service."""
    print("\n" + "=" * 60)
    print("Testing Web Crawler Service")
    print("=" * 60)
    
    config = {
        "timeout": 30,
        "max_content_length": 1024 * 1024  # 1MB
    }
    
    try:
        service = WebCrawlerService(config)
        await service.start()
        
        print("✅ Web Crawler Service started successfully")
        
        # Test crawling a simple webpage
        test_url = "https://httpbin.org/html"
        print(f"\n🕷️ Testing crawling {test_url}...")
        
        result = await service.call_tool("crawl_page", {
            "url": test_url,
            "extract_metadata": True,
            "extract_links": True,
            "extract_images": False
        })
        
        if "error" in result:
            print(f"❌ Crawling failed: {result['error']}")
        else:
            print("✅ Crawling successful!")
            print(f"Status: {result['status_code']}")
            print(f"Content length: {result['content_length']} characters")
            print(f"URL: {result['url']}")
            
            # Show metadata
            if result.get("metadata"):
                metadata = result["metadata"]
                print(f"Page title: {metadata.get('title', 'No title')}")
                print(f"Description: {metadata.get('description', 'No description')[:100]}...")
            
            # Show content preview
            if result.get("content"):
                content = result["content"]
                print(f"Content preview: {content[:200]}...")
            
            # Show links count
            if result.get("links"):
                print(f"Found {len(result['links'])} links")
        
        await service.stop()
        print("🔴 Web Crawler Service stopped")
        
    except Exception as e:
        print(f"❌ Web Crawler Service test failed: {str(e)}")


async def test_integration():
    """Test integration of both services."""
    print("\n" + "=" * 60)
    print("Testing Integration: Search + Crawl")
    print("=" * 60)
    
    # First search for something
    api_key = os.getenv("SERPER_API_KEY", "53f66cade9c650fe1f44b92dff2f0854ee4b83b4")
    if not api_key:
        print("❌ SERPER_API_KEY not found, skipping integration test")
        return
    
    try:
        # Start search service
        search_service = WebSearchService({"serper_api_key": api_key})
        await search_service.start()
        
        # Start crawler service  
        crawler_service = WebCrawlerService({
            "timeout": 30,
            "max_content_length": 512 * 1024  # 512KB for faster test
        })
        await crawler_service.start()
        
        print("✅ Both services started")
        
        # Search for something
        print("\n🔍 Searching for 'GitHub Python'...")
        search_result = await search_service.call_tool("web_search", {
            "query": "GitHub Python",
            "num_results": 1
        })
        
        if "error" in search_result:
            print(f"❌ Search failed: {search_result['error']}")
            return
        
        # Get the first result URL
        organic = search_result['results'].get('organic', [])
        if not organic:
            print("❌ No search results found")
            return
        
        first_url = organic[0].get('link')
        if not first_url:
            print("❌ No URL found in first result")
            return
        
        print(f"✅ Found URL: {first_url}")
        
        # Now crawl that URL
        print(f"\n🕷️ Crawling the search result...")
        crawl_result = await crawler_service.call_tool("crawl_page", {
            "url": first_url,
            "extract_metadata": True
        })
        
        if "error" in crawl_result:
            print(f"❌ Crawling failed: {crawl_result['error']}")
        else:
            print("✅ Integration test successful!")
            print(f"Crawled page title: {crawl_result.get('metadata', {}).get('title', 'No title')}")
            print(f"Content length: {crawl_result.get('content_length', 0)} characters")
        
        # Clean up
        await search_service.stop()
        await crawler_service.stop()
        print("🔴 Both services stopped")
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")


async def main():
    """Main test function."""
    print("🚀 Starting tests for new web tools...")
    
    await test_web_search()
    await test_web_crawler()
    await test_integration()
    
    print("\n" + "=" * 60)
    print("🏁 All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
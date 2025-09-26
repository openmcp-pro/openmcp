#!/usr/bin/env python3
"""
Simple Web Search & Crawler Examples - Copy & Paste Ready!

No API key needed from localhost.
"""

import asyncio
import httpx
import json


async def web_search_example():
    """Simple web search example"""
    print("🔍 Web Search Example")
    print("=" * 30)
    
    # No auth headers needed from localhost!
    async with httpx.AsyncClient() as client:
        # Search for something
        response = await client.post(
            "http://localhost:9000/api/v1/services/web_search/call",
            json={
                "tool_name": "search",
                "arguments": {
                    "query": "Python FastAPI tutorial",
                    "num_results": 5
                }
            }
        )
        
        result = response.json()
        if result["success"]:
            results = result["result"]["results"]
            print(f"✅ Found {len(results)} search results:")
            
            for i, item in enumerate(results, 1):
                print(f"\n{i}. {item['title']}")
                print(f"   🔗 {item['url']}")
                print(f"   📝 {item['snippet'][:100]}...")
        else:
            print(f"❌ Search failed: {result.get('error')}")


async def web_crawler_example():
    """Simple web crawler example"""
    print("\n🕷️ Web Crawler Example")
    print("=" * 30)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Crawl a page
        response = await client.post(
            "http://localhost:9000/api/v1/services/web_crawler/call",
            json={
                "tool_name": "crawl",
                "arguments": {
                    "url": "https://httpbin.org",
                    "max_depth": 1
                }
            }
        )
        
        result = response.json()
        if result["success"]:
            pages = result["result"]["pages"]
            print(f"✅ Crawled {len(pages)} pages:")
            
            for i, page in enumerate(pages[:3], 1):  # Show first 3
                print(f"\n{i}. {page['title']}")
                print(f"   🔗 {page['url']}")
                print(f"   📊 Status: {page['status_code']}")
                if page.get('content'):
                    preview = page['content'][:100].replace('\n', ' ')
                    print(f"   📝 Content: {preview}...")
        else:
            print(f"❌ Crawling failed: {result.get('error')}")


async def content_extraction_example():
    """Simple content extraction example"""
    print("\n📄 Content Extraction Example")
    print("=" * 35)
    
    async with httpx.AsyncClient() as client:
        # Extract content from a page
        response = await client.post(
            "http://localhost:9000/api/v1/services/web_crawler/call",
            json={
                "tool_name": "extract_content",
                "arguments": {
                    "url": "https://python.org"
                }
            }
        )
        
        result = response.json()
        if result["success"]:
            content = result["result"]
            print(f"✅ Content extracted:")
            print(f"📄 Title: {content.get('title', 'No title')}")
            print(f"📊 Status: {content.get('status_code')}")
            
            # Show text preview
            text = content.get('text', '')
            if text:
                preview = text[:200].replace('\n', ' ').strip()
                print(f"📝 Text preview: {preview}...")
                print(f"📏 Total text length: {len(text)} characters")
            
            # Show links
            links = content.get('links', [])
            if links:
                print(f"🔗 Found {len(links)} links (first 3):")
                for link in links[:3]:
                    print(f"   • {link}")
        else:
            print(f"❌ Extraction failed: {result.get('error')}")


async def research_workflow_example():
    """Research workflow: search + extract content"""
    print("\n🧠 Research Workflow Example")
    print("=" * 35)
    
    topic = "Python web scraping"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Search
        print(f"🔎 Searching for: '{topic}'")
        search_response = await client.post(
            "http://localhost:9000/api/v1/services/web_search/call",
            json={
                "tool_name": "search",
                "arguments": {"query": topic, "num_results": 3}
            }
        )
        
        if not search_response.json()["success"]:
            print("❌ Search failed")
            return
        
        search_results = search_response.json()["result"]["results"]
        print(f"✅ Found {len(search_results)} results")
        
        # Step 2: Extract content from first result
        first_url = search_results[0]["url"]
        print(f"\n📄 Extracting content from: {first_url}")
        
        extract_response = await client.post(
            "http://localhost:9000/api/v1/services/web_crawler/call",
            json={
                "tool_name": "extract_content",
                "arguments": {"url": first_url}
            }
        )
        
        if extract_response.json()["success"]:
            content = extract_response.json()["result"]
            text = content.get('text', '')
            
            # Simple analysis
            word_count = len(text.split()) if text else 0
            print(f"✅ Extracted {word_count} words")
            
            # Save research data
            research_data = {
                "topic": topic,
                "search_results": search_results,
                "extracted_content": {
                    "url": first_url,
                    "title": content.get('title'),
                    "word_count": word_count,
                    "text_preview": text[:300] if text else ""
                }
            }
            
            with open('quick_research.json', 'w') as f:
                json.dump(research_data, f, indent=2)
            print("💾 Research saved to: quick_research.json")
        else:
            print("❌ Content extraction failed")


async def main():
    """Run simple web tools examples"""
    print("🌐 Simple Web Search & Crawler Examples")
    print("🏠 No API key needed from localhost!")
    print("=" * 50)
    
    # Check server
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:9000/health", timeout=3.0)
            if response.status_code != 200:
                raise Exception("Server not healthy")
    except Exception:
        print("❌ OpenMCP server not running!")
        print("🚀 Start it with: openmcp serve")
        return
    
    # Run examples
    try:
        await web_search_example()
        await web_crawler_example()
        await content_extraction_example()
        await research_workflow_example()
        
        print(f"\n🎉 All examples completed!")
        print(f"📁 Check quick_research.json for saved data")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
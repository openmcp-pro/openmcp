#!/usr/bin/env python3
"""
Web Search and Web Crawler Examples for OpenMCP - Localhost Usage

No API key needed from localhost!
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List


class OpenMCPWebTools:
    """Easy interface for web search and crawler tools"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        # No auth headers needed from localhost!
        self.headers = {}
    
    async def web_search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web using the web_search service"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/web_search/call",
                headers=self.headers,
                json={
                    "tool_name": "search",
                    "arguments": {
                        "query": query,
                        "num_results": num_results
                    }
                }
            )
            result = response.json()
            if result["success"]:
                return result["result"]["results"]
            else:
                raise Exception(f"Search failed: {result.get('error', 'Unknown error')}")
    
    async def crawl_page(self, url: str, max_depth: int = 1) -> Dict[str, Any]:
        """Crawl a web page using the web_crawler service"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/web_crawler/call",
                headers=self.headers,
                json={
                    "tool_name": "crawl",
                    "arguments": {
                        "url": url,
                        "max_depth": max_depth,
                        "follow_links": True
                    }
                }
            )
            result = response.json()
            if result["success"]:
                return result["result"]
            else:
                raise Exception(f"Crawling failed: {result.get('error', 'Unknown error')}")
    
    async def extract_content(self, url: str) -> Dict[str, Any]:
        """Extract content from a single page"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/services/web_crawler/call",
                headers=self.headers,
                json={
                    "tool_name": "extract_content",
                    "arguments": {
                        "url": url
                    }
                }
            )
            result = response.json()
            if result["success"]:
                return result["result"]
            else:
                raise Exception(f"Content extraction failed: {result.get('error', 'Unknown error')}")


async def example_1_web_search():
    """Example 1: Basic web search"""
    print("🔍 Example 1: Web Search")
    print("=" * 40)
    
    web_tools = OpenMCPWebTools()
    
    try:
        # Search for Python tutorials
        print("🔎 Searching for 'Python asyncio tutorial'...")
        results = await web_tools.web_search("Python asyncio tutorial", num_results=5)
        
        print(f"✅ Found {len(results)} search results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('title', 'No title')}")
            print(f"   🔗 {result.get('url', 'No URL')}")
            print(f"   📝 {result.get('snippet', 'No snippet')[:100]}...")
        
    except Exception as e:
        print(f"❌ Search error: {e}")


async def example_2_web_search_comparison():
    """Example 2: Compare search results for different queries"""
    print("\n🔄 Example 2: Search Comparison")
    print("=" * 40)
    
    web_tools = OpenMCPWebTools()
    
    queries = [
        "FastAPI tutorial",
        "Flask vs Django",
        "Python web frameworks 2024"
    ]
    
    try:
        for query in queries:
            print(f"\n🔎 Searching for: '{query}'")
            results = await web_tools.web_search(query, num_results=3)
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')[:50]
                url = result.get('url', 'No URL')
                print(f"   {i}. {title}... -> {url}")
    
    except Exception as e:
        print(f"❌ Comparison error: {e}")


async def example_3_page_crawling():
    """Example 3: Crawl a single page"""
    print("\n🕷️ Example 3: Page Crawling")
    print("=" * 40)
    
    web_tools = OpenMCPWebTools()
    
    try:
        # Crawl Python.org
        print("🌐 Crawling python.org...")
        crawl_result = await web_tools.crawl_page("https://python.org", max_depth=1)
        
        print("✅ Crawling completed!")
        print(f"📄 Pages found: {len(crawl_result.get('pages', []))}")
        
        # Show some crawled pages
        pages = crawl_result.get('pages', [])
        for i, page in enumerate(pages[:5], 1):
            print(f"\n{i}. {page.get('title', 'No title')}")
            print(f"   🔗 {page.get('url', 'No URL')}")
            print(f"   📊 Status: {page.get('status_code', 'Unknown')}")
            
            # Show some content if available
            content = page.get('content', '')
            if content:
                print(f"   📝 Content preview: {content[:100]}...")
        
    except Exception as e:
        print(f"❌ Crawling error: {e}")


async def example_4_content_extraction():
    """Example 4: Extract content from specific pages"""
    print("\n📄 Example 4: Content Extraction")
    print("=" * 40)
    
    web_tools = OpenMCPWebTools()
    
    urls = [
        "https://httpbin.org",
        "https://python.org",
        "https://github.com"
    ]
    
    try:
        for url in urls:
            print(f"\n🔍 Extracting content from: {url}")
            
            try:
                content = await web_tools.extract_content(url)
                
                print(f"✅ Content extracted!")
                print(f"📄 Title: {content.get('title', 'No title')}")
                print(f"📊 Status: {content.get('status_code', 'Unknown')}")
                
                # Show text content preview
                text_content = content.get('text', '')
                if text_content:
                    preview = text_content[:200].replace('\n', ' ').strip()
                    print(f"📝 Text preview: {preview}...")
                
                # Show links found
                links = content.get('links', [])
                if links:
                    print(f"🔗 Links found: {len(links)} (showing first 3)")
                    for i, link in enumerate(links[:3], 1):
                        print(f"   {i}. {link}")
                
            except Exception as url_error:
                print(f"❌ Failed to extract from {url}: {url_error}")
    
    except Exception as e:
        print(f"❌ Content extraction error: {e}")


async def example_5_search_and_crawl_workflow():
    """Example 5: Combined workflow - search then crawl results"""
    print("\n🔄 Example 5: Search + Crawl Workflow")
    print("=" * 40)
    
    web_tools = OpenMCPWebTools()
    
    try:
        # Step 1: Search for something
        search_query = "OpenMCP documentation"
        print(f"🔎 Step 1: Searching for '{search_query}'...")
        search_results = await web_tools.web_search(search_query, num_results=3)
        
        print(f"✅ Found {len(search_results)} search results")
        
        # Step 2: Extract content from top search results
        print(f"\n📄 Step 2: Extracting content from top results...")
        
        for i, result in enumerate(search_results[:2], 1):  # Only process first 2
            url = result.get('url', '')
            title = result.get('title', 'No title')
            
            if url:
                print(f"\n🔍 Processing result {i}: {title}")
                print(f"   🔗 URL: {url}")
                
                try:
                    content = await web_tools.extract_content(url)
                    text_content = content.get('text', '')
                    
                    if text_content:
                        # Show word count and preview
                        word_count = len(text_content.split())
                        preview = text_content[:150].replace('\n', ' ').strip()
                        print(f"   📊 Word count: {word_count}")
                        print(f"   📝 Preview: {preview}...")
                    else:
                        print(f"   ⚠️  No text content extracted")
                        
                except Exception as extract_error:
                    print(f"   ❌ Extraction failed: {extract_error}")
    
    except Exception as e:
        print(f"❌ Workflow error: {e}")


async def example_6_research_assistant():
    """Example 6: Research assistant - gather info on a topic"""
    print("\n🧠 Example 6: Research Assistant")
    print("=" * 40)
    
    web_tools = OpenMCPWebTools()
    research_topic = "Python web scraping best practices"
    
    try:
        print(f"🔬 Researching: '{research_topic}'")
        
        # Search for information
        print("🔎 Gathering search results...")
        results = await web_tools.web_search(research_topic, num_results=5)
        
        research_data = {
            "topic": research_topic,
            "sources": [],
            "total_content": 0
        }
        
        # Process each result
        for i, result in enumerate(results, 1):
            url = result.get('url', '')
            title = result.get('title', 'No title')
            snippet = result.get('snippet', '')
            
            print(f"\n📖 Processing source {i}: {title[:50]}...")
            
            source_info = {
                "title": title,
                "url": url,
                "snippet": snippet,
                "content_length": 0,
                "key_points": []
            }
            
            # Try to extract full content
            try:
                content = await web_tools.extract_content(url)
                text_content = content.get('text', '')
                
                if text_content:
                    source_info["content_length"] = len(text_content)
                    research_data["total_content"] += len(text_content)
                    
                    # Extract key sentences (simple approach)
                    sentences = text_content.split('.')[:5]  # First 5 sentences
                    source_info["key_points"] = [s.strip() for s in sentences if len(s.strip()) > 20]
                
            except Exception:
                print(f"   ⚠️  Could not extract content from {url}")
            
            research_data["sources"].append(source_info)
        
        # Display research summary
        print(f"\n📊 Research Summary for: '{research_topic}'")
        print("=" * 50)
        print(f"📚 Sources analyzed: {len(research_data['sources'])}")
        print(f"📝 Total content: {research_data['total_content']:,} characters")
        
        print(f"\n🔍 Key Sources:")
        for i, source in enumerate(research_data['sources'], 1):
            print(f"\n{i}. {source['title'][:60]}...")
            print(f"   🔗 {source['url']}")
            print(f"   📊 Content: {source['content_length']:,} chars")
            
            if source['key_points']:
                print(f"   💡 Key point: {source['key_points'][0][:100]}...")
        
        # Save research data
        with open('research_results.json', 'w') as f:
            json.dump(research_data, f, indent=2)
        print(f"\n💾 Research data saved to: research_results.json")
        
    except Exception as e:
        print(f"❌ Research error: {e}")


async def check_services():
    """Check if web search and crawler services are available"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:9000/api/v1/services", timeout=5.0)
            if response.status_code == 200:
                services = response.json()
                available = services.get('available_services', [])
                running = services.get('running_services', [])
                
                print("🔧 Service Status:")
                for service in ['web_search', 'web_crawler']:
                    if service in available:
                        status = "🟢 Running" if service in running else "🟡 Available"
                        print(f"   {service}: {status}")
                    else:
                        print(f"   {service}: ❌ Not available")
                return True
            else:
                print("❌ Cannot check services")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to OpenMCP server: {e}")
        print("🚀 Start it with: openmcp serve")
        return False


async def main():
    """Run all web search and crawler examples"""
    print("🌐 OpenMCP Web Search & Crawler Examples")
    print("🏠 No API key needed - running from localhost!")
    print("=" * 60)
    
    # Check if server and services are available
    if not await check_services():
        return
    
    print()
    
    # Run all examples
    examples = [
        example_1_web_search,
        example_2_web_search_comparison,
        example_3_page_crawling,
        example_4_content_extraction,
        example_5_search_and_crawl_workflow,
        example_6_research_assistant
    ]
    
    for example in examples:
        try:
            await example()
            await asyncio.sleep(1)  # Brief pause between examples
        except Exception as e:
            print(f"❌ Example failed: {e}")
    
    print(f"\n🎉 All web tools examples completed!")
    print(f"📁 Check research_results.json for saved research data")


if __name__ == "__main__":
    asyncio.run(main())
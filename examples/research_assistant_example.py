#!/usr/bin/env python3
"""
Research Assistant Example using Web Search and Web Crawler tools.

This example demonstrates practical use cases:
1. Research a topic by searching and analyzing multiple sources
2. News monitoring and content extraction
3. Competitor analysis by crawling websites
4. Technical documentation gathering
5. Price comparison research

Prerequisites:
- Set SERPER_API_KEY environment variable
- Install: pip install requests beautifulsoup4 lxml
"""

import asyncio
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add the src directory to Python path
sys.path.insert(0, '/mnt/home/zomux/works/openmcp/src')

from openmcp.services.web_search_service import WebSearchService
from openmcp.services.web_crawler_service import WebCrawlerService


class ResearchAssistant:
    """Research assistant using web search and crawling capabilities."""
    
    def __init__(self, serper_api_key: str):
        self.search_service = None
        self.crawler_service = None
        self.serper_api_key = serper_api_key
        
    async def initialize(self):
        """Initialize both services."""
        # Initialize search service
        search_config = {"serper_api_key": self.serper_api_key}
        self.search_service = WebSearchService(search_config)
        await self.search_service.start()
        
        # Initialize crawler service
        crawler_config = {
            "timeout": 30,
            "max_content_length": 1024 * 1024  # 1MB
        }
        self.crawler_service = WebCrawlerService(crawler_config)
        await self.crawler_service.start()
        
        print("🤖 Research Assistant initialized successfully!")
    
    async def cleanup(self):
        """Clean up services."""
        if self.search_service:
            await self.search_service.stop()
        if self.crawler_service:
            await self.crawler_service.stop()
        print("🔴 Research Assistant stopped")
    
    async def search_and_analyze_topic(self, topic: str, num_sources: int = 5) -> Dict[str, Any]:
        """Research a topic by searching and analyzing multiple sources."""
        print(f"📚 Researching topic: {topic}")
        print("=" * 60)
        
        # Step 1: Search for the topic
        print("🔍 Step 1: Searching for information...")
        search_result = await self.search_service.call_tool("web_search", {
            "query": topic,
            "num_results": num_sources * 2  # Get more results to filter from
        })
        
        if "error" in search_result:
            return {"error": f"Search failed: {search_result['error']}"}
        
        organic_results = search_result["results"].get("organic", [])
        print(f"   Found {len(organic_results)} search results")
        
        # Step 2: Filter and crawl relevant sources
        print(f"\n🕷️ Step 2: Analyzing top {min(num_sources, len(organic_results))} sources...")
        analyzed_sources = []
        
        for i, result in enumerate(organic_results[:num_sources], 1):
            url = result["link"]
            title = result["title"]
            snippet = result["snippet"]
            
            print(f"\n   📄 Source {i}: {title[:60]}...")
            print(f"       URL: {url}")
            
            # Crawl the page
            crawl_result = await self.crawler_service.call_tool("crawl_page", {
                "url": url,
                "extract_metadata": True,
                "extract_links": False,
                "extract_images": False
            })
            
            if "error" in crawl_result:
                print(f"       ❌ Failed to crawl: {crawl_result['error'][:50]}...")
                continue
            
            content = crawl_result.get("content", "")
            metadata = crawl_result.get("metadata", {})
            
            # Analyze content relevance
            topic_keywords = topic.lower().split()
            content_lower = content.lower()
            keyword_matches = sum(1 for keyword in topic_keywords if keyword in content_lower)
            relevance_score = keyword_matches / len(topic_keywords) if topic_keywords else 0
            
            source_analysis = {
                "rank": i,
                "title": title,
                "url": url,
                "snippet": snippet,
                "metadata_title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "content_length": len(content),
                "content_preview": content[:300] + "..." if len(content) > 300 else content,
                "relevance_score": relevance_score,
                "keyword_matches": keyword_matches,
                "language": metadata.get("language", ""),
                "author": metadata.get("author", "")
            }
            
            analyzed_sources.append(source_analysis)
            
            print(f"       ✅ Content: {len(content)} chars, Relevance: {relevance_score:.2f}")
        
        # Step 3: Generate summary
        print(f"\n📊 Step 3: Research Summary")
        print("-" * 40)
        
        # Sort by relevance score
        analyzed_sources.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        summary = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "total_sources_found": len(organic_results),
            "sources_analyzed": len(analyzed_sources),
            "top_sources": analyzed_sources[:3],  # Top 3 most relevant
            "all_sources": analyzed_sources
        }
        
        print(f"   📈 Total sources found: {len(organic_results)}")
        print(f"   📊 Sources analyzed: {len(analyzed_sources)}")
        print(f"   🏆 Most relevant source: {analyzed_sources[0]['title'] if analyzed_sources else 'None'}")
        
        return summary
    
    async def monitor_news_topic(self, topic: str, num_articles: int = 3) -> Dict[str, Any]:
        """Monitor news about a specific topic."""
        print(f"📰 Monitoring news for: {topic}")
        print("=" * 50)
        
        # Search for news
        news_result = await self.search_service.call_tool("web_search", {
            "query": topic,
            "search_type": "news",
            "num_results": num_articles * 2
        })
        
        if "error" in news_result:
            return {"error": f"News search failed: {news_result['error']}"}
        
        news_articles = news_result["results"].get("news", [])
        print(f"🔍 Found {len(news_articles)} news articles")
        
        analyzed_articles = []
        
        for i, article in enumerate(news_articles[:num_articles], 1):
            print(f"\n📄 Article {i}: {article['title']}")
            print(f"   Source: {article['source']} | Date: {article.get('date', 'Unknown')}")
            
            # Crawl the article
            crawl_result = await self.crawler_service.call_tool("crawl_page", {
                "url": article["link"],
                "extract_metadata": True
            })
            
            if "error" in crawl_result:
                print(f"   ❌ Failed to crawl article")
                continue
            
            content = crawl_result.get("content", "")
            word_count = len(content.split()) if content else 0
            
            article_analysis = {
                "title": article["title"],
                "source": article["source"],
                "date": article.get("date", ""),
                "url": article["link"],
                "snippet": article.get("snippet", ""),
                "full_content": content,
                "word_count": word_count,
                "summary": content[:500] + "..." if len(content) > 500 else content
            }
            
            analyzed_articles.append(article_analysis)
            print(f"   ✅ Extracted {word_count} words")
        
        return {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "articles_found": len(news_articles),
            "articles_analyzed": len(analyzed_articles),
            "articles": analyzed_articles
        }
    
    async def analyze_competitors(self, competitor_urls: List[str]) -> Dict[str, Any]:
        """Analyze competitor websites."""
        print(f"🏢 Analyzing {len(competitor_urls)} competitors")
        print("=" * 50)
        
        competitor_analysis = []
        
        for i, url in enumerate(competitor_urls, 1):
            print(f"\n🌐 Competitor {i}: {url}")
            
            # Crawl the website
            crawl_result = await self.crawler_service.call_tool("crawl_page", {
                "url": url,
                "extract_metadata": True,
                "extract_links": True,
                "extract_images": True
            })
            
            if "error" in crawl_result:
                print(f"   ❌ Failed to analyze: {crawl_result['error'][:50]}...")
                continue
            
            content = crawl_result.get("content", "")
            metadata = crawl_result.get("metadata", {})
            links = crawl_result.get("links", [])
            images = crawl_result.get("images", [])
            
            # Extract key information
            analysis = {
                "url": url,
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "content_length": len(content),
                "word_count": len(content.split()) if content else 0,
                "links_count": len(links),
                "images_count": len(images),
                "language": metadata.get("language", ""),
                "technologies": self._detect_technologies(content),
                "key_phrases": self._extract_key_phrases(content),
                "contact_info": self._extract_contact_info(content)
            }
            
            competitor_analysis.append(analysis)
            
            print(f"   📊 Content: {len(content)} chars, {len(links)} links, {len(images)} images")
            print(f"   🛠️ Technologies: {', '.join(analysis['technologies'][:3])}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "competitors_analyzed": len(competitor_analysis),
            "analysis": competitor_analysis
        }
    
    async def research_products(self, product_query: str, num_results: int = 5) -> Dict[str, Any]:
        """Research products and prices."""
        print(f"🛍️ Researching products: {product_query}")
        print("=" * 50)
        
        # Search for shopping results
        shopping_result = await self.search_service.call_tool("web_search", {
            "query": product_query,
            "search_type": "shopping",
            "num_results": num_results
        })
        
        if "error" in shopping_result:
            return {"error": f"Product search failed: {shopping_result['error']}"}
        
        products = shopping_result["results"].get("shopping", [])
        print(f"🔍 Found {len(products)} products")
        
        # Also search for regular results for reviews and comparisons
        review_result = await self.search_service.call_tool("web_search", {
            "query": f"{product_query} review comparison",
            "num_results": 3
        })
        
        review_urls = []
        if "error" not in review_result:
            review_urls = [r["link"] for r in review_result["results"].get("organic", [])]
        
        # Analyze review pages
        reviews_analysis = []
        for url in review_urls[:2]:  # Analyze top 2 review pages
            print(f"\n📝 Analyzing review: {url}")
            
            crawl_result = await self.crawler_service.call_tool("crawl_page", {
                "url": url,
                "extract_metadata": True
            })
            
            if "error" not in crawl_result:
                content = crawl_result.get("content", "")
                metadata = crawl_result.get("metadata", {})
                
                reviews_analysis.append({
                    "url": url,
                    "title": metadata.get("title", ""),
                    "content_length": len(content),
                    "pros_cons": self._extract_pros_cons(content),
                    "rating_mentions": self._extract_ratings(content)
                })
                
                print(f"   ✅ Extracted {len(content)} chars of review content")
        
        return {
            "query": product_query,
            "timestamp": datetime.now().isoformat(),
            "products_found": len(products),
            "products": products,
            "reviews_analyzed": len(reviews_analysis),
            "reviews": reviews_analysis
        }
    
    def _detect_technologies(self, content: str) -> List[str]:
        """Detect technologies mentioned in content."""
        tech_patterns = {
            "React": r"\bReact\b",
            "Vue": r"\bVue\.js\b|\bVue\b",
            "Angular": r"\bAngular\b",
            "WordPress": r"\bWordPress\b",
            "Shopify": r"\bShopify\b",
            "Python": r"\bPython\b",
            "JavaScript": r"\bJavaScript\b|\bJS\b",
            "PHP": r"\bPHP\b",
            "Node.js": r"\bNode\.js\b|\bNodeJS\b"
        }
        
        detected = []
        content_lower = content.lower()
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                detected.append(tech)
        
        return detected
    
    def _extract_key_phrases(self, content: str, max_phrases: int = 5) -> List[str]:
        """Extract key phrases from content."""
        # Simple keyword extraction (in real implementation, use NLP libraries)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        
        # Skip common words
        stop_words = {'that', 'this', 'with', 'have', 'will', 'from', 'they', 'been', 'their', 'said', 'each', 'which', 'more', 'very', 'what', 'know', 'just', 'first', 'about', 'other', 'many', 'some', 'time', 'could', 'would', 'there'}
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top phrases
        return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:max_phrases]
    
    def _extract_contact_info(self, content: str) -> Dict[str, Any]:
        """Extract contact information from content."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
        
        emails = re.findall(email_pattern, content)
        phones = re.findall(phone_pattern, content)
        
        return {
            "emails": list(set(emails))[:3],  # Limit to 3 unique emails
            "phones": list(set(phones))[:3]   # Limit to 3 unique phones
        }
    
    def _extract_pros_cons(self, content: str) -> Dict[str, List[str]]:
        """Extract pros and cons from review content."""
        content_lower = content.lower()
        
        # Simple pattern matching for pros/cons
        pros = []
        cons = []
        
        # Look for positive indicators
        if "excellent" in content_lower or "great" in content_lower:
            pros.append("Positive user feedback")
        if "fast" in content_lower or "quick" in content_lower:
            pros.append("Good performance")
        if "easy" in content_lower:
            pros.append("User-friendly")
        
        # Look for negative indicators
        if "slow" in content_lower:
            cons.append("Performance issues")
        if "difficult" in content_lower or "hard" in content_lower:
            cons.append("Usability concerns")
        if "expensive" in content_lower or "costly" in content_lower:
            cons.append("Price concerns")
        
        return {"pros": pros, "cons": cons}
    
    def _extract_ratings(self, content: str) -> List[str]:
        """Extract rating mentions from content."""
        rating_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:out of|/)\s*(\d+)',
            r'(\d+(?:\.\d+)?)\s*(?:stars?|★)',
            r'rating:\s*(\d+(?:\.\d+)?)'
        ]
        
        ratings = []
        for pattern in rating_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            ratings.extend([f"{m[0]}/5" if isinstance(m, tuple) else str(m) for m in matches])
        
        return ratings[:5]  # Limit to 5 ratings


async def demo_research_assistant():
    """Demonstrate the Research Assistant capabilities."""
    print("🤖 OpenMCP Research Assistant Demo")
    print("🔍 Powered by Web Search + Web Crawler")
    print("=" * 70)
    
    # Check for API key
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("❌ Please set SERPER_API_KEY environment variable")
        print("   Example: export SERPER_API_KEY='your-api-key-here'")
        return
    
    assistant = ResearchAssistant(api_key)
    await assistant.initialize()
    
    try:
        # Demo 1: Research a topic
        print("\n" + "🔬 DEMO 1: Topic Research")
        topic_result = await assistant.search_and_analyze_topic("artificial intelligence trends 2024", num_sources=3)
        
        if "error" not in topic_result:
            print(f"\n📋 Research Summary:")
            print(f"   Topic: {topic_result['topic']}")
            print(f"   Sources analyzed: {topic_result['sources_analyzed']}")
            
            if topic_result['top_sources']:
                top_source = topic_result['top_sources'][0]
                print(f"   Most relevant: {top_source['title'][:50]}...")
                print(f"   Relevance score: {top_source['relevance_score']:.2f}")
        
        # Demo 2: News monitoring
        print("\n" + "📰 DEMO 2: News Monitoring")
        news_result = await assistant.monitor_news_topic("OpenAI ChatGPT", num_articles=2)
        
        if "error" not in news_result:
            print(f"\n📋 News Summary:")
            print(f"   Articles found: {news_result['articles_found']}")
            print(f"   Articles analyzed: {news_result['articles_analyzed']}")
            
            for article in news_result['articles'][:2]:
                print(f"   📄 {article['title'][:50]}... ({article['word_count']} words)")
        
        # Demo 3: Competitor analysis
        print("\n" + "🏢 DEMO 3: Competitor Analysis")
        competitor_urls = [
            "https://example.com",
            "https://httpbin.org"
        ]
        
        competitor_result = await assistant.analyze_competitors(competitor_urls)
        
        if competitor_result['competitors_analyzed'] > 0:
            print(f"\n📋 Competitor Summary:")
            print(f"   Competitors analyzed: {competitor_result['competitors_analyzed']}")
            
            for comp in competitor_result['analysis']:
                print(f"   🌐 {comp['url']}: {comp['word_count']} words, {comp['links_count']} links")
        
        # Demo 4: Product research
        print("\n" + "🛍️ DEMO 4: Product Research")
        product_result = await assistant.research_products("wireless headphones", num_results=3)
        
        if "error" not in product_result:
            print(f"\n📋 Product Summary:")
            print(f"   Products found: {product_result['products_found']}")
            print(f"   Reviews analyzed: {product_result['reviews_analyzed']}")
            
            for product in product_result['products'][:2]:
                print(f"   🎧 {product['title'][:50]}... - {product.get('price', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")
    
    finally:
        await assistant.cleanup()
    
    print("\n" + "=" * 70)
    print("🏁 Research Assistant Demo Completed!")
    print("\n💡 Use Cases:")
    print("  • Market research and competitor analysis")
    print("  • News monitoring and content curation")
    print("  • Product research and price comparison")
    print("  • Academic research and fact-checking")
    print("  • SEO content research and analysis")


if __name__ == "__main__":
    asyncio.run(demo_research_assistant())
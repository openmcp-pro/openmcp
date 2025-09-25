#!/usr/bin/env python3
"""
Content Aggregator Example using Web Search and Web Crawler tools.

This example demonstrates:
1. Building a news aggregator from multiple sources
2. Creating a curated reading list with summaries
3. Monitoring social media mentions (via web search)
4. Creating automated content briefs
5. Fact-checking across multiple sources

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
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

# Add the src directory to Python path
sys.path.insert(0, '/mnt/home/zomux/works/openmcp/src')

from openmcp.services.web_search_service import WebSearchService
from openmcp.services.web_crawler_service import WebCrawlerService


class ContentAggregator:
    """Content aggregation and analysis using web search and crawling."""
    
    def __init__(self, serper_api_key: str):
        self.search_service = None
        self.crawler_service = None
        self.serper_api_key = serper_api_key
        
    async def initialize(self):
        """Initialize both services."""
        search_config = {"serper_api_key": self.serper_api_key}
        self.search_service = WebSearchService(search_config)
        await self.search_service.start()
        
        crawler_config = {
            "timeout": 25,
            "max_content_length": 512 * 1024  # 512KB for faster processing
        }
        self.crawler_service = WebCrawlerService(crawler_config)
        await self.crawler_service.start()
        
        print("📰 Content Aggregator initialized!")
    
    async def cleanup(self):
        """Clean up services."""
        if self.search_service:
            await self.search_service.stop()
        if self.crawler_service:
            await self.crawler_service.stop()
        print("🔴 Content Aggregator stopped")
    
    async def create_news_digest(self, topics: List[str], articles_per_topic: int = 3) -> Dict[str, Any]:
        """Create a comprehensive news digest from multiple topics."""
        print(f"📰 Creating news digest for {len(topics)} topics")
        print("=" * 60)
        
        digest = {
            "created_at": datetime.now().isoformat(),
            "topics": {},
            "summary": {
                "total_topics": len(topics),
                "total_articles": 0,
                "sources": set()
            }
        }
        
        for topic in topics:
            print(f"\n🔍 Processing topic: {topic}")
            
            # Search for news on this topic
            news_result = await self.search_service.call_tool("web_search", {
                "query": f"{topic} latest news",
                "search_type": "news",
                "num_results": articles_per_topic + 2  # Get extra for filtering
            })
            
            if "error" in news_result:
                print(f"   ❌ Failed to search: {news_result['error'][:50]}...")
                continue
            
            articles = news_result["results"].get("news", [])
            topic_data = {
                "articles": [],
                "sources": set(),
                "total_found": len(articles)
            }
            
            # Process each article
            for i, article in enumerate(articles[:articles_per_topic], 1):
                print(f"   📄 Article {i}: {article['title'][:50]}...")
                
                # Extract article content
                crawl_result = await self.crawler_service.call_tool("crawl_page", {
                    "url": article["link"],
                    "extract_metadata": True
                })
                
                article_data = {
                    "title": article["title"],
                    "source": article["source"],
                    "date": article.get("date", ""),
                    "url": article["link"],
                    "snippet": article.get("snippet", ""),
                    "crawl_success": "error" not in crawl_result
                }
                
                if crawl_result and "error" not in crawl_result:
                    content = crawl_result.get("content", "")
                    metadata = crawl_result.get("metadata", {})
                    
                    article_data.update({
                        "word_count": len(content.split()) if content else 0,
                        "summary": self._create_summary(content, max_sentences=3),
                        "key_points": self._extract_key_points(content),
                        "metadata": {
                            "description": metadata.get("description", ""),
                            "author": metadata.get("author", ""),
                            "language": metadata.get("language", "")
                        }
                    })
                    
                    print(f"       ✅ Extracted {article_data['word_count']} words")
                else:
                    print(f"       ❌ Failed to crawl content")
                
                topic_data["articles"].append(article_data)
                topic_data["sources"].add(article["source"])
                digest["summary"]["sources"].add(article["source"])
            
            digest["topics"][topic] = {
                "articles": topic_data["articles"],
                "sources": list(topic_data["sources"]),
                "article_count": len(topic_data["articles"])
            }
            digest["summary"]["total_articles"] += len(topic_data["articles"])
            
            print(f"   📊 Processed {len(topic_data['articles'])} articles from {len(topic_data['sources'])} sources")
        
        digest["summary"]["sources"] = list(digest["summary"]["sources"])
        return digest
    
    async def create_reading_list(self, topic: str, content_types: List[str] = None) -> Dict[str, Any]:
        """Create a curated reading list with summaries."""
        if content_types is None:
            content_types = ["articles", "tutorials", "guides"]
        
        print(f"📚 Creating reading list for: {topic}")
        print("=" * 50)
        
        reading_list = {
            "topic": topic,
            "created_at": datetime.now().isoformat(),
            "sections": {},
            "total_items": 0
        }
        
        for content_type in content_types:
            print(f"\n📖 Finding {content_type} for {topic}")
            
            # Search for specific content type
            search_query = f"{topic} {content_type} comprehensive guide"
            search_result = await self.search_service.call_tool("web_search", {
                "query": search_query,
                "num_results": 4
            })
            
            if "error" in search_result:
                continue
            
            results = search_result["results"].get("organic", [])
            section_items = []
            
            for result in results:
                print(f"   🔗 {result['title'][:60]}...")
                
                # Analyze the content
                crawl_result = await self.crawler_service.call_tool("crawl_page", {
                    "url": result["link"],
                    "extract_metadata": True,
                    "extract_links": True
                })
                
                item = {
                    "title": result["title"],
                    "url": result["link"],
                    "snippet": result["snippet"],
                    "domain": urlparse(result["link"]).netloc
                }
                
                if "error" not in crawl_result:
                    content = crawl_result.get("content", "")
                    metadata = crawl_result.get("metadata", {})
                    links = crawl_result.get("links", [])
                    
                    # Estimate reading time (average 200 words per minute)
                    word_count = len(content.split()) if content else 0
                    reading_time = max(1, word_count // 200)
                    
                    item.update({
                        "word_count": word_count,
                        "reading_time": f"{reading_time} min",
                        "summary": self._create_summary(content, max_sentences=2),
                        "difficulty": self._assess_difficulty(content),
                        "topics_covered": self._extract_topics(content, topic),
                        "external_links": len([l for l in links if urlparse(l["url"]).netloc != item["domain"]]),
                        "description": metadata.get("description", "")
                    })
                    
                    print(f"       📊 {word_count} words, {reading_time} min read, Difficulty: {item['difficulty']}")
                
                section_items.append(item)
            
            if section_items:
                reading_list["sections"][content_type] = section_items
                reading_list["total_items"] += len(section_items)
        
        return reading_list
    
    async def monitor_brand_mentions(self, brand_name: str, timeframe: str = "week") -> Dict[str, Any]:
        """Monitor brand mentions across the web."""
        print(f"👀 Monitoring mentions for: {brand_name}")
        print("=" * 40)
        
        queries = [
            f'"{brand_name}" review',
            f'"{brand_name}" news',
            f'"{brand_name}" opinion',
            f"{brand_name} vs competitor"
        ]
        
        mention_data = {
            "brand": brand_name,
            "timeframe": timeframe,
            "monitored_at": datetime.now().isoformat(),
            "mentions": [],
            "sentiment_summary": {"positive": 0, "negative": 0, "neutral": 0},
            "sources": set()
        }
        
        for query in queries:
            print(f"\n🔍 Searching: {query}")
            
            search_result = await self.search_service.call_tool("web_search", {
                "query": query,
                "num_results": 3
            })
            
            if "error" in search_result:
                continue
            
            results = search_result["results"].get("organic", [])
            
            for result in results:
                print(f"   📄 {result['title'][:50]}...")
                
                # Analyze the mention
                crawl_result = await self.crawler_service.call_tool("crawl_page", {
                    "url": result["link"],
                    "extract_metadata": True
                })
                
                mention = {
                    "title": result["title"],
                    "url": result["link"],
                    "snippet": result["snippet"],
                    "source": urlparse(result["link"]).netloc,
                    "found_via": query
                }
                
                if "error" not in crawl_result:
                    content = crawl_result.get("content", "")
                    
                    # Extract brand mentions and context
                    brand_contexts = self._extract_brand_context(content, brand_name)
                    sentiment = self._simple_sentiment_analysis(content, brand_name)
                    
                    mention.update({
                        "mention_count": len(brand_contexts),
                        "contexts": brand_contexts[:3],  # Top 3 contexts
                        "sentiment": sentiment,
                        "word_count": len(content.split()) if content else 0
                    })
                    
                    mention_data["sentiment_summary"][sentiment] += 1
                    print(f"       💭 {len(brand_contexts)} mentions, Sentiment: {sentiment}")
                
                mention_data["mentions"].append(mention)
                mention_data["sources"].add(mention["source"])
        
        mention_data["sources"] = list(mention_data["sources"])
        return mention_data
    
    async def fact_check_claim(self, claim: str, num_sources: int = 5) -> Dict[str, Any]:
        """Fact-check a claim across multiple sources."""
        print(f"🔍 Fact-checking: {claim}")
        print("=" * 50)
        
        # Search for information about the claim
        search_result = await self.search_service.call_tool("web_search", {
            "query": f'"{claim}" fact check verify',
            "num_results": num_sources
        })
        
        if "error" in search_result:
            return {"error": f"Search failed: {search_result['error']}"}
        
        fact_check = {
            "claim": claim,
            "checked_at": datetime.now().isoformat(),
            "sources_analyzed": 0,
            "sources": [],
            "evidence_summary": {
                "supporting": 0,
                "contradicting": 0,
                "neutral": 0
            },
            "credible_sources": []
        }
        
        results = search_result["results"].get("organic", [])
        
        for result in results:
            print(f"\n📄 Analyzing: {result['title'][:50]}...")
            
            # Check source credibility
            domain = urlparse(result["link"]).netloc
            is_credible = self._assess_source_credibility(domain)
            
            # Crawl the content
            crawl_result = await self.crawler_service.call_tool("crawl_page", {
                "url": result["link"],
                "extract_metadata": True
            })
            
            source_analysis = {
                "title": result["title"],
                "url": result["link"],
                "domain": domain,
                "is_credible": is_credible,
                "snippet": result["snippet"]
            }
            
            if "error" not in crawl_result:
                content = crawl_result.get("content", "")
                metadata = crawl_result.get("metadata", {})
                
                # Analyze how this source relates to the claim
                evidence_type = self._analyze_evidence(content, claim)
                key_quotes = self._extract_relevant_quotes(content, claim)
                
                source_analysis.update({
                    "evidence_type": evidence_type,
                    "key_quotes": key_quotes,
                    "word_count": len(content.split()) if content else 0,
                    "author": metadata.get("author", ""),
                    "date": metadata.get("date", "")
                })
                
                fact_check["evidence_summary"][evidence_type] += 1
                
                if is_credible:
                    fact_check["credible_sources"].append(source_analysis)
                
                print(f"   📊 Evidence: {evidence_type}, Credible: {is_credible}")
                fact_check["sources_analyzed"] += 1
            
            fact_check["sources"].append(source_analysis)
        
        # Generate conclusion
        fact_check["conclusion"] = self._generate_fact_check_conclusion(fact_check)
        
        return fact_check
    
    def _create_summary(self, content: str, max_sentences: int = 3) -> str:
        """Create a simple extractive summary."""
        if not content:
            return ""
        
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Simple heuristic: pick sentences with common keywords
        if len(sentences) <= max_sentences:
            return '. '.join(sentences[:max_sentences]) + '.'
        
        # Score sentences by length and position (earlier sentences weighted more)
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = len(sentence.split()) * (1 - i / len(sentences) * 0.5)
            scored_sentences.append((score, sentence))
        
        # Get top sentences
        top_sentences = sorted(scored_sentences, key=lambda x: x[0], reverse=True)[:max_sentences]
        return '. '.join([s[1] for s in top_sentences]) + '.'
    
    def _extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """Extract key points from content."""
        if not content:
            return []
        
        # Look for bullet points, numbered lists, or sentences with key indicators
        key_indicators = ['important', 'key', 'main', 'significant', 'crucial', 'essential']
        
        sentences = re.split(r'[.!?]+', content)
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            
            # Check for list markers
            if re.match(r'^\s*[\d\-\*\•]\s*', sentence):
                key_points.append(sentence)
            elif any(indicator in sentence.lower() for indicator in key_indicators):
                key_points.append(sentence)
        
        return key_points[:max_points]
    
    def _assess_difficulty(self, content: str) -> str:
        """Assess content difficulty level."""
        if not content:
            return "unknown"
        
        # Simple heuristics
        words = content.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Count technical terms (words > 10 characters)
        technical_words = len([w for w in words if len(w) > 10])
        technical_ratio = technical_words / len(words) if words else 0
        
        if avg_word_length > 6 or technical_ratio > 0.1:
            return "Advanced"
        elif avg_word_length > 5 or technical_ratio > 0.05:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _extract_topics(self, content: str, main_topic: str) -> List[str]:
        """Extract related topics from content."""
        if not content:
            return []
        
        # Simple topic extraction based on frequent meaningful words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        stop_words = {'that', 'this', 'with', 'have', 'will', 'from', 'they', 'been', 'their'}
        
        word_freq = {}
        for word in words:
            if word not in stop_words and word != main_topic.lower():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top topics
        return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:5]
    
    def _extract_brand_context(self, content: str, brand_name: str) -> List[str]:
        """Extract contexts where the brand is mentioned."""
        if not content or not brand_name:
            return []
        
        contexts = []
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            if brand_name.lower() in sentence.lower():
                contexts.append(sentence.strip())
        
        return contexts[:5]  # Return up to 5 contexts
    
    def _simple_sentiment_analysis(self, content: str, brand_name: str) -> str:
        """Simple sentiment analysis for brand mentions."""
        if not content:
            return "neutral"
        
        positive_words = ['excellent', 'great', 'amazing', 'love', 'best', 'good', 'fantastic', 'wonderful']
        negative_words = ['terrible', 'awful', 'hate', 'worst', 'bad', 'horrible', 'disappointing', 'poor']
        
        content_lower = content.lower()
        
        # Count positive and negative words near brand mentions
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _assess_source_credibility(self, domain: str) -> bool:
        """Assess if a source domain is credible."""
        credible_domains = {
            'bbc.com', 'reuters.com', 'ap.org', 'npr.org', 'pbs.org',
            'wikipedia.org', 'edu', '.gov', 'nature.com', 'science.org'
        }
        
        return any(credible in domain for credible in credible_domains)
    
    def _analyze_evidence(self, content: str, claim: str) -> str:
        """Analyze how content relates to a claim."""
        if not content:
            return "neutral"
        
        content_lower = content.lower()
        claim_lower = claim.lower()
        
        # Simple keyword-based analysis
        supporting_words = ['confirms', 'proves', 'shows', 'demonstrates', 'supports']
        contradicting_words = ['disproves', 'contradicts', 'false', 'incorrect', 'debunked']
        
        support_score = sum(1 for word in supporting_words if word in content_lower)
        contradict_score = sum(1 for word in contradicting_words if word in content_lower)
        
        if support_score > contradict_score:
            return "supporting"
        elif contradict_score > support_score:
            return "contradicting"
        else:
            return "neutral"
    
    def _extract_relevant_quotes(self, content: str, claim: str) -> List[str]:
        """Extract relevant quotes related to the claim."""
        if not content:
            return []
        
        sentences = re.split(r'[.!?]+', content)
        claim_words = set(claim.lower().split())
        relevant_quotes = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            
            sentence_words = set(sentence.lower().split())
            overlap = len(claim_words.intersection(sentence_words))
            
            if overlap >= 2:  # At least 2 words overlap
                relevant_quotes.append(sentence)
        
        return relevant_quotes[:3]  # Return top 3 relevant quotes
    
    def _generate_fact_check_conclusion(self, fact_check: Dict[str, Any]) -> str:
        """Generate a conclusion for the fact check."""
        evidence = fact_check["evidence_summary"]
        credible_count = len(fact_check["credible_sources"])
        
        total_evidence = sum(evidence.values())
        if total_evidence == 0:
            return "Insufficient evidence found to verify this claim."
        
        supporting_pct = evidence["supporting"] / total_evidence * 100
        contradicting_pct = evidence["contradicting"] / total_evidence * 100
        
        conclusion = f"Based on {fact_check['sources_analyzed']} sources ({credible_count} credible): "
        
        if supporting_pct > 60:
            conclusion += f"The claim appears to be SUPPORTED ({supporting_pct:.0f}% supporting evidence)."
        elif contradicting_pct > 60:
            conclusion += f"The claim appears to be CONTRADICTED ({contradicting_pct:.0f}% contradicting evidence)."
        else:
            conclusion += f"The evidence is MIXED ({supporting_pct:.0f}% supporting, {contradicting_pct:.0f}% contradicting)."
        
        if credible_count < 2:
            conclusion += " Note: Limited credible sources found."
        
        return conclusion


async def demo_content_aggregator():
    """Demonstrate the Content Aggregator capabilities."""
    print("📰 OpenMCP Content Aggregator Demo")
    print("🔍 Web Search + 🕷️ Web Crawler = 📊 Content Intelligence")
    print("=" * 70)
    
    # Check for API key
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("❌ Please set SERPER_API_KEY environment variable")
        print("   Example: export SERPER_API_KEY='your-api-key-here'")
        return
    
    aggregator = ContentAggregator(api_key)
    await aggregator.initialize()
    
    try:
        # Demo 1: News Digest
        print("\n📰 DEMO 1: Multi-Topic News Digest")
        topics = ["artificial intelligence", "climate change"]
        news_digest = await aggregator.create_news_digest(topics, articles_per_topic=2)
        
        print(f"\n📋 News Digest Summary:")
        print(f"   Topics covered: {news_digest['summary']['total_topics']}")
        print(f"   Total articles: {news_digest['summary']['total_articles']}")
        print(f"   Unique sources: {len(news_digest['summary']['sources'])}")
        
        for topic, data in news_digest["topics"].items():
            print(f"\n   📊 {topic.title()}:")
            print(f"      Articles: {data['article_count']}")
            print(f"      Sources: {', '.join(data['sources'][:3])}")
        
        # Demo 2: Reading List
        print("\n📚 DEMO 2: Curated Reading List")
        reading_list = await aggregator.create_reading_list("machine learning", ["tutorials", "guides"])
        
        print(f"\n📋 Reading List Summary:")
        print(f"   Topic: {reading_list['topic']}")
        print(f"   Total items: {reading_list['total_items']}")
        
        for section, items in reading_list["sections"].items():
            print(f"\n   📖 {section.title()} ({len(items)} items):")
            for item in items[:2]:
                print(f"      • {item['title'][:50]}...")
                if 'reading_time' in item:
                    print(f"        {item['reading_time']}, Difficulty: {item.get('difficulty', 'N/A')}")
        
        # Demo 3: Brand Monitoring
        print("\n👀 DEMO 3: Brand Mention Monitoring")
        mentions = await aggregator.monitor_brand_mentions("OpenAI")
        
        print(f"\n📋 Brand Monitor Summary:")
        print(f"   Brand: {mentions['brand']}")
        print(f"   Mentions found: {len(mentions['mentions'])}")
        print(f"   Sources: {len(mentions['sources'])}")
        
        sentiment = mentions["sentiment_summary"]
        total_sentiment = sum(sentiment.values())
        if total_sentiment > 0:
            print(f"   Sentiment: {sentiment['positive']}/{sentiment['negative']}/{sentiment['neutral']} (pos/neg/neu)")
        
        # Demo 4: Fact Checking
        print("\n🔍 DEMO 4: Fact Checking")
        claim = "Python is the most popular programming language in 2024"
        fact_check = await aggregator.fact_check_claim(claim, num_sources=3)
        
        if "error" not in fact_check:
            print(f"\n📋 Fact Check Summary:")
            print(f"   Claim: {fact_check['claim']}")
            print(f"   Sources analyzed: {fact_check['sources_analyzed']}")
            print(f"   Credible sources: {len(fact_check['credible_sources'])}")
            
            evidence = fact_check["evidence_summary"]
            print(f"   Evidence: {evidence['supporting']} supporting, {evidence['contradicting']} contradicting")
            print(f"   Conclusion: {fact_check['conclusion']}")
    
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")
    
    finally:
        await aggregator.cleanup()
    
    print("\n" + "=" * 70)
    print("🏁 Content Aggregator Demo Completed!")
    print("\n💡 Use Cases:")
    print("  • Automated news curation and digests")
    print("  • Educational content organization")
    print("  • Brand monitoring and reputation management")
    print("  • Fact-checking and verification workflows")
    print("  • Research paper and literature reviews")


if __name__ == "__main__":
    asyncio.run(demo_content_aggregator())
"""Web search MCP service using Serper API for Google search."""

import json
import os
from typing import Any, Dict, List, Optional

import requests

from .base import BaseMCPService


class WebSearchService(BaseMCPService):
    """Web search MCP service using Serper API."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("serper_api_key") or os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev"
        
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in config or environment variables")
    
    async def start(self) -> None:
        """Start the web search service."""
        self.is_running = True
        self.logger.info("Web search service started")
    
    async def stop(self) -> None:
        """Stop the web search service."""
        self.is_running = False
        self.logger.info("Web search service stopped")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for web search service."""
        return [
            {
                "name": "web_search",
                "description": "Search Google using Serper API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return (default: 10, max: 100)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search (search, images, news, shopping, places)",
                            "enum": ["search", "images", "news", "shopping", "places"],
                            "default": "search"
                        },
                        "country": {
                            "type": "string",
                            "description": "Country code for localized results (e.g., 'us', 'uk', 'ca')",
                            "default": "us"
                        },
                        "language": {
                            "type": "string",
                            "description": "Language code for results (e.g., 'en', 'es', 'fr')",
                            "default": "en"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call a web search tool."""
        try:
            if tool_name == "web_search":
                return await self._perform_search(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            self.logger.error("Tool call failed", tool=tool_name, error=str(e))
            return {"error": str(e)}
    
    async def _perform_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a web search using Serper API."""
        query = arguments["query"]
        num_results = arguments.get("num_results", 10)
        search_type = arguments.get("search_type", "search")
        country = arguments.get("country", "us")
        language = arguments.get("language", "en")
        
        # Map search type to endpoint
        endpoint_map = {
            "search": "/search",
            "images": "/images", 
            "news": "/news",
            "shopping": "/shopping",
            "places": "/places"
        }
        
        if search_type not in endpoint_map:
            return {"error": f"Invalid search type: {search_type}"}
        
        url = f"{self.base_url}{endpoint_map[search_type]}"
        
        payload = {
            "q": query,
            "num": num_results,
            "gl": country,
            "hl": language
        }
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            
            search_results = response.json()
            
            # Format the results for better readability
            formatted_results = self._format_search_results(search_results, search_type)
            
            return {
                "status": "success",
                "query": query,
                "search_type": search_type,
                "results": search_results,
                "formatted_results": formatted_results,
                "credits_used": search_results.get("credits", 1)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Search request failed: {str(e)}",
                "status": "failed"
            }
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse search response: {str(e)}",
                "status": "failed"
            }
    
    def _format_search_results(self, results: Dict[str, Any], search_type: str) -> Dict[str, Any]:
        """Format search results for better readability."""
        formatted = {
            "search_parameters": results.get("searchParameters", {}),
            "total_results": 0,
            "formatted_results": []
        }
        
        if search_type == "search":
            # Format regular search results
            organic = results.get("organic", [])
            formatted["total_results"] = len(organic)
            
            for idx, result in enumerate(organic, 1):
                formatted_result = {
                    "rank": idx,
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "date": result.get("date", "")
                }
                
                # Add sitelinks if available
                if result.get("sitelinks"):
                    formatted_result["sitelinks"] = result["sitelinks"]
                
                formatted["formatted_results"].append(formatted_result)
            
            # Add knowledge graph if available
            if results.get("knowledgeGraph"):
                formatted["knowledge_graph"] = results["knowledgeGraph"]
            
            # Add people also ask if available
            if results.get("peopleAlsoAsk"):
                formatted["people_also_ask"] = results["peopleAlsoAsk"]
            
            # Add related searches if available
            if results.get("relatedSearches"):
                formatted["related_searches"] = results["relatedSearches"]
        
        elif search_type == "images":
            # Format image search results
            images = results.get("images", [])
            formatted["total_results"] = len(images)
            
            for idx, image in enumerate(images, 1):
                formatted["formatted_results"].append({
                    "rank": idx,
                    "title": image.get("title", ""),
                    "image_url": image.get("imageUrl", ""),
                    "source_url": image.get("link", ""),
                    "source": image.get("source", ""),
                    "width": image.get("imageWidth", ""),
                    "height": image.get("imageHeight", "")
                })
        
        elif search_type == "news":
            # Format news search results
            news = results.get("news", [])
            formatted["total_results"] = len(news)
            
            for idx, article in enumerate(news, 1):
                formatted["formatted_results"].append({
                    "rank": idx,
                    "title": article.get("title", ""),
                    "link": article.get("link", ""),
                    "snippet": article.get("snippet", ""),
                    "date": article.get("date", ""),
                    "source": article.get("source", ""),
                    "image_url": article.get("imageUrl", "")
                })
        
        elif search_type == "shopping":
            # Format shopping search results
            shopping = results.get("shopping", [])
            formatted["total_results"] = len(shopping)
            
            for idx, product in enumerate(shopping, 1):
                formatted["formatted_results"].append({
                    "rank": idx,
                    "title": product.get("title", ""),
                    "link": product.get("link", ""),
                    "price": product.get("price", ""),
                    "source": product.get("source", ""),
                    "rating": product.get("rating", ""),
                    "reviews": product.get("ratingCount", ""),
                    "image_url": product.get("imageUrl", "")
                })
        
        elif search_type == "places":
            # Format places search results
            places = results.get("places", [])
            formatted["total_results"] = len(places)
            
            for idx, place in enumerate(places, 1):
                formatted["formatted_results"].append({
                    "rank": idx,
                    "title": place.get("title", ""),
                    "address": place.get("address", ""),
                    "phone": place.get("phoneNumber", ""),
                    "website": place.get("website", ""),
                    "rating": place.get("rating", ""),
                    "reviews": place.get("ratingCount", ""),
                    "category": place.get("category", ""),
                    "latitude": place.get("latitude", ""),
                    "longitude": place.get("longitude", "")
                })
        
        return formatted
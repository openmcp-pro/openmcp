"""Web crawler MCP service for extracting webpage content."""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseMCPService


class WebCrawlerService(BaseMCPService):
    """Web crawler MCP service for extracting webpage content."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.timeout = config.get("timeout", 30)
        self.max_content_length = config.get(
            "max_content_length", 1024 * 1024
        )  # 1MB default

        # Default headers with fake referer
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def start(self) -> None:
        """Start the web crawler service."""
        self.is_running = True
        self.logger.info("Web crawler service started")

    async def stop(self) -> None:
        """Stop the web crawler service."""
        self.is_running = False
        self.logger.info("Web crawler service stopped")

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for web crawler service."""
        return [
            {
                "name": "crawl_page",
                "description": "Crawl and extract content from a webpage, cleaning up JavaScript and non-content elements",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL of the webpage to crawl",
                        },
                        "extract_links": {
                            "type": "boolean",
                            "description": "Whether to extract links from the page",
                            "default": False,
                        },
                        "extract_images": {
                            "type": "boolean",
                            "description": "Whether to extract image URLs from the page",
                            "default": False,
                        },
                        "extract_metadata": {
                            "type": "boolean",
                            "description": "Whether to extract page metadata (title, description, etc.)",
                            "default": True,
                        },
                        "clean_html": {
                            "type": "boolean",
                            "description": "Whether to return cleaned HTML instead of plain text",
                            "default": False,
                        },
                        "custom_headers": {
                            "type": "object",
                            "description": "Custom headers to use for the request",
                            "default": {},
                        },
                    },
                    "required": ["url"],
                },
            }
        ]

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Call a web crawler tool."""
        try:
            if tool_name == "crawl_page":
                return await self._crawl_page(arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            self.logger.error("Tool call failed", tool=tool_name, error=str(e))
            return {"error": str(e)}

    async def _crawl_page(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Crawl and extract content from a webpage."""
        url = arguments["url"]
        extract_links = arguments.get("extract_links", False)
        extract_images = arguments.get("extract_images", False)
        extract_metadata = arguments.get("extract_metadata", True)
        clean_html = arguments.get("clean_html", False)
        custom_headers = arguments.get("custom_headers", {})

        # Validate URL
        if not self._is_valid_url(url):
            return {"error": "Invalid URL provided"}

        # Prepare headers
        headers = self.default_headers.copy()
        headers.update(custom_headers)

        try:
            # Make request
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True,
            )
            response.raise_for_status()

            # Check content length
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_content_length:
                return {"error": f"Content too large: {content_length} bytes"}

            # Get content with size limit
            content = ""
            size = 0
            for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                if chunk:
                    content += chunk
                    size += len(chunk.encode("utf-8"))
                    if size > self.max_content_length:
                        content = content[: self.max_content_length]
                        break

            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")

            # Extract content
            result = {
                "url": response.url,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "content_length": len(content),
                "status": "success",
            }

            # Extract metadata
            if extract_metadata:
                result["metadata"] = self._extract_metadata(soup)

            # Extract main content
            if clean_html:
                result["content"] = self._extract_clean_html(soup)
                result["content_type_returned"] = "html"
            else:
                result["content"] = self._extract_clean_text(soup)
                result["content_type_returned"] = "text"

            # Extract links
            if extract_links:
                result["links"] = self._extract_links(soup, url)

            # Extract images
            if extract_images:
                result["images"] = self._extract_images(soup, url)

            return result

        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to fetch webpage: {str(e)}",
                "status": "failed",
                "url": url,
            }
        except Exception as e:
            return {
                "error": f"Failed to process webpage: {str(e)}",
                "status": "failed",
                "url": url,
            }

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from the webpage."""
        metadata = {}

        # Title
        title_tag = soup.find("title")
        if title_tag:
            metadata["title"] = title_tag.get_text().strip()

        # Meta tags
        meta_tags = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property") or meta.get("http-equiv")
            content = meta.get("content")
            if name and content:
                meta_tags[name] = content

        metadata["meta_tags"] = meta_tags

        # Extract common metadata
        metadata["description"] = meta_tags.get("description", "")
        metadata["keywords"] = meta_tags.get("keywords", "")
        metadata["author"] = meta_tags.get("author", "")
        metadata["og_title"] = meta_tags.get("og:title", "")
        metadata["og_description"] = meta_tags.get("og:description", "")
        metadata["og_image"] = meta_tags.get("og:image", "")

        # Language
        html_tag = soup.find("html")
        if html_tag:
            metadata["language"] = html_tag.get("lang", "")

        # Canonical URL
        canonical = soup.find("link", rel="canonical")
        if canonical:
            metadata["canonical"] = canonical.get("href", "")

        return metadata

    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from the webpage."""
        # Remove script and style elements
        for script in soup(
            [
                "script",
                "style",
                "nav",
                "header",
                "footer",
                "aside",
                "iframe",
                "noscript",
            ]
        ):
            script.decompose()

        # Remove comments
        for comment in soup.find_all(
            string=lambda text: isinstance(text, str)
            and text.strip().startswith("<!--")
        ):
            comment.extract()

        # Get text content
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        # Remove excessive newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)

        return text.strip()

    def _extract_clean_html(self, soup: BeautifulSoup) -> str:
        """Extract cleaned HTML content from the webpage."""
        # Remove script and style elements and their content
        for script in soup(
            [
                "script",
                "style",
                "nav",
                "header",
                "footer",
                "aside",
                "iframe",
                "noscript",
            ]
        ):
            script.decompose()

        # Remove comments
        for comment in soup.find_all(
            string=lambda text: isinstance(text, str)
            and text.strip().startswith("<!--")
        ):
            comment.extract()

        # Find main content area
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_=re.compile(r"content|main|article", re.I))
            or soup.find("div", id=re.compile(r"content|main|article", re.I))
            or soup.body
            or soup
        )

        if main_content:
            # Remove empty tags
            for tag in main_content.find_all():
                if not tag.get_text(strip=True) and not tag.find("img"):
                    tag.decompose()

            return str(main_content.prettify())

        return str(soup.prettify())

    def _extract_links(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Dict[str, str]]:
        """Extract links from the webpage."""
        links = []

        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            if not href or href.startswith("#"):
                continue

            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)

            text = link.get_text().strip()
            title = link.get("title", "").strip()

            links.append({"url": full_url, "text": text, "title": title})

        return links

    def _extract_images(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Dict[str, str]]:
        """Extract images from the webpage."""
        images = []

        for img in soup.find_all("img", src=True):
            src = img["src"].strip()
            if not src:
                continue

            # Convert relative URLs to absolute
            full_url = urljoin(base_url, src)

            alt = img.get("alt", "").strip()
            title = img.get("title", "").strip()

            images.append({"url": full_url, "alt": alt, "title": title})

        return images

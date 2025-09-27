"""Browseruse MCP service for web browsing capabilities."""

import asyncio
import uuid
from typing import Any, Dict, List, Optional, AsyncGenerator

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .base import BaseMCPService


class BrowserSession:
    """Represents a browser session."""
    
    def __init__(self, session_id: str, headless: bool = True, timeout: int = 30):
        self.session_id = session_id
        self.headless = headless
        self.timeout = timeout
        self.driver: Optional[webdriver.Chrome] = None
        self.is_active = False
    
    async def start(self) -> None:
        """Start the browser session."""
        chrome_options = ChromeOptions()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(self.timeout)
        self.is_active = True
    
    async def stop(self) -> None:
        """Stop the browser session."""
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.is_active = False
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        if not self.driver:
            raise RuntimeError("Browser session not started")
        
        self.driver.get(url)
        return {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "status": "success"
        }
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        if not self.driver:
            raise RuntimeError("Browser session not started")
        
        return {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "page_source_length": len(self.driver.page_source)
        }
    
    def find_elements(self, selector: str, by: str = "css") -> List[Dict[str, Any]]:
        """Find elements on the page."""
        if not self.driver:
            raise RuntimeError("Browser session not started")
        
        by_mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "name": By.NAME
        }
        
        if by not in by_mapping:
            raise ValueError(f"Unsupported selector type: {by}")
        
        elements = self.driver.find_elements(by_mapping[by], selector)
        return [
            {
                "tag": elem.tag_name,
                "text": elem.text,
                "attributes": {
                    "id": elem.get_attribute("id"),
                    "class": elem.get_attribute("class"),
                    "href": elem.get_attribute("href")
                }
            }
            for elem in elements
        ]
    
    def click_element(self, selector: str, by: str = "css") -> Dict[str, Any]:
        """Click an element."""
        if not self.driver:
            raise RuntimeError("Browser session not started")
        
        by_mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME
        }
        
        if by not in by_mapping:
            raise ValueError(f"Unsupported selector type: {by}")
        
        wait = WebDriverWait(self.driver, self.timeout)
        element = wait.until(EC.element_to_be_clickable((by_mapping[by], selector)))
        element.click()
        
        return {
            "status": "success",
            "current_url": self.driver.current_url
        }
    
    def type_text(self, selector: str, text: str, by: str = "css") -> Dict[str, Any]:
        """Type text into an element."""
        if not self.driver:
            raise RuntimeError("Browser session not started")
        
        by_mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME
        }
        
        if by not in by_mapping:
            raise ValueError(f"Unsupported selector type: {by}")
        
        wait = WebDriverWait(self.driver, self.timeout)
        element = wait.until(EC.presence_of_element_located((by_mapping[by], selector)))
        element.clear()
        element.send_keys(text)
        
        return {"status": "success"}
    
    def take_screenshot(self) -> str:
        """Take a screenshot and return base64 encoded image."""
        if not self.driver:
            raise RuntimeError("Browser session not started")
        
        return self.driver.get_screenshot_as_base64()
    
    def observe(self) -> Dict[str, Any]:
        """Get simplified text-based DOM tree of important visible elements with interaction paths."""
        if not self.driver:
            raise RuntimeError("Browser session not started")
        
        # JavaScript to get simplified DOM structure with paths
        js_script = """
        function getSimplifiedDOM() {
            const interactiveSelectors = [
                'button', 'a[href]', 'input', 'textarea', 'select', 
                '[onclick]', '[role="button"]', '[role="link"]', '[role="textbox"]',
                '[type="submit"]', '[type="button"]', '[type="text"]', '[type="email"]',
                '[type="password"]', '[type="search"]', '[type="url"]', '[type="tel"]',
                '[type="number"]', '[contenteditable="true"]'
            ];
            
            const importantSelectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'p', 'span', 'div[role="main"]', 'main', 'article',
                'nav', 'header', 'footer', 'section',
                'img[alt]', 'form', 'table', 'ul', 'ol', 'li'
            ];
            
            function isVisible(element) {
                const style = window.getComputedStyle(element);
                const rect = element.getBoundingClientRect();
                return style.display !== 'none' && 
                       style.visibility !== 'hidden' && 
                       style.opacity !== '0' &&
                       rect.width > 0 && 
                       rect.height > 0 &&
                       rect.top < window.innerHeight &&
                       rect.bottom > 0 &&
                       rect.left < window.innerWidth &&
                       rect.right > 0;
            }
            
            function getTextContent(element) {
                let text = element.textContent || element.innerText || '';
                text = text.trim().replace(/\\s+/g, ' ');
                return text.substring(0, 200); // Limit text length
            }
            
            function getElementPath(element) {
                if (element.id) {
                    return '#' + element.id;
                }
                
                let path = element.tagName.toLowerCase();
                let parent = element.parentElement;
                let childIndex = Array.from(parent?.children || []).indexOf(element);
                
                if (parent && childIndex >= 0) {
                    path = parent.tagName.toLowerCase() + ' > ' + path + ':nth-child(' + (childIndex + 1) + ')';
                }
                
                // Add class information if available
                if (element.className && typeof element.className === 'string') {
                    const classes = element.className.split(' ').filter(c => c.trim()).slice(0, 2);
                    if (classes.length > 0) {
                        path += '.' + classes.join('.');
                    }
                }
                
                return path;
            }
            
            function getElementAttributes(element) {
                const attrs = {};
                if (element.getAttribute('placeholder')) attrs.placeholder = element.getAttribute('placeholder');
                if (element.getAttribute('title')) attrs.title = element.getAttribute('title');
                if (element.getAttribute('alt')) attrs.alt = element.getAttribute('alt');
                if (element.getAttribute('href')) attrs.href = element.getAttribute('href');
                if (element.getAttribute('type')) attrs.type = element.getAttribute('type');
                if (element.getAttribute('value')) attrs.value = element.getAttribute('value');
                if (element.getAttribute('aria-label')) attrs['aria-label'] = element.getAttribute('aria-label');
                return attrs;
            }
            
            const result = {
                interactive_elements: [],
                content_elements: [],
                page_structure: {
                    title: document.title,
                    url: window.location.href,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                }
            };
            
            // Get interactive elements
            interactiveSelectors.forEach(selector => {
                try {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(element => {
                        if (isVisible(element)) {
                            const text = getTextContent(element);
                            const path = getElementPath(element);
                            const attrs = getElementAttributes(element);
                            
                            result.interactive_elements.push({
                                tag: element.tagName.toLowerCase(),
                                text: text,
                                dom_path: path,
                                attributes: attrs,
                                bounds: {
                                    x: Math.round(element.getBoundingClientRect().left),
                                    y: Math.round(element.getBoundingClientRect().top),
                                    width: Math.round(element.getBoundingClientRect().width),
                                    height: Math.round(element.getBoundingClientRect().height)
                                }
                            });
                        }
                    });
                } catch (e) {
                    // Ignore selector errors
                }
            });
            
            // Get important content elements
            importantSelectors.forEach(selector => {
                try {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(element => {
                        if (isVisible(element)) {
                            const text = getTextContent(element);
                            if (text.length > 3) { // Only include elements with meaningful text
                                const path = getElementPath(element);
                                const attrs = getElementAttributes(element);
                                
                                result.content_elements.push({
                                    tag: element.tagName.toLowerCase(),
                                    text: text,
                                    dom_path: path,
                                    attributes: attrs
                                });
                            }
                        }
                    });
                } catch (e) {
                    // Ignore selector errors
                }
            });
            
            // Remove duplicates and sort by position
            result.interactive_elements = result.interactive_elements.filter((elem, index, arr) => 
                arr.findIndex(e => e.dom_path === elem.dom_path) === index
            ).sort((a, b) => a.bounds.y - b.bounds.y || a.bounds.x - b.bounds.x);
            
            result.content_elements = result.content_elements.filter((elem, index, arr) => 
                arr.findIndex(e => e.dom_path === elem.dom_path) === index
            );
            
            return result;
        }
        
        return getSimplifiedDOM();
        """
        
        try:
            dom_data = self.driver.execute_script(js_script)
            
            # Format the result into a readable text representation
            formatted_result = self._format_dom_observation(dom_data)
            
            return {
                "status": "success",
                "raw_data": dom_data,
                "formatted_text": formatted_result,
                "interactive_count": len(dom_data.get("interactive_elements", [])),
                "content_count": len(dom_data.get("content_elements", []))
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _format_dom_observation(self, dom_data: Dict[str, Any]) -> str:
        """Format DOM data into readable text representation."""
        lines = []
        
        # Page info
        page_info = dom_data.get("page_structure", {})
        lines.append(f"=== PAGE OBSERVATION ===")
        lines.append(f"Title: {page_info.get('title', 'N/A')}")
        lines.append(f"URL: {page_info.get('url', 'N/A')}")
        lines.append(f"Viewport: {page_info.get('viewport', {}).get('width', 0)}x{page_info.get('viewport', {}).get('height', 0)}")
        lines.append("")
        
        # Interactive elements
        interactive = dom_data.get("interactive_elements", [])
        if interactive:
            lines.append(f"=== INTERACTIVE ELEMENTS ({len(interactive)}) ===")
            for i, elem in enumerate(interactive):
                lines.append(f"[{i+1}] {elem['tag'].upper()}")
                lines.append(f"    Path: {elem['dom_path']}")
                if elem.get('text'):
                    lines.append(f"    Text: {elem['text'][:100]}{'...' if len(elem['text']) > 100 else ''}")
                
                attrs = elem.get('attributes', {})
                attr_str = []
                for key, value in attrs.items():
                    if value:
                        attr_str.append(f"{key}='{value[:50]}{'...' if len(str(value)) > 50 else ''}'")
                if attr_str:
                    lines.append(f"    Attributes: {', '.join(attr_str)}")
                
                bounds = elem.get('bounds', {})
                if bounds:
                    lines.append(f"    Position: ({bounds.get('x', 0)}, {bounds.get('y', 0)}) Size: {bounds.get('width', 0)}x{bounds.get('height', 0)}")
                lines.append("")
            lines.append("")
        
        # Content elements (abbreviated)
        content = dom_data.get("content_elements", [])
        if content:
            lines.append(f"=== CONTENT ELEMENTS ({len(content)}) ===")
            
            # Group by tag type
            by_tag = {}
            for elem in content:
                tag = elem['tag']
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(elem)
            
            for tag, elements in by_tag.items():
                lines.append(f"{tag.upper()} ({len(elements)}):")
                for elem in elements[:5]:  # Show first 5 of each type
                    text = elem.get('text', '')[:80]
                    if len(elem.get('text', '')) > 80:
                        text += '...'
                    lines.append(f"  • {text}")
                if len(elements) > 5:
                    lines.append(f"  ... and {len(elements) - 5} more")
                lines.append("")
        
        return "\\n".join(lines)


class BrowseruseService(BaseMCPService):
    """Browseruse MCP service for web automation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.sessions: Dict[str, BrowserSession] = {}
        self.max_sessions = config.get("max_sessions", 5)
        self.default_headless = config.get("headless", True)
        self.default_timeout = config.get("timeout", 30)
    
    async def start(self) -> None:
        """Start the browseruse service."""
        self.is_running = True
        self.logger.info("Browseruse service started")
    
    async def stop(self) -> None:
        """Stop the browseruse service."""
        # Close all active sessions
        for session in list(self.sessions.values()):
            await session.stop()
        self.sessions.clear()
        self.is_running = False
        self.logger.info("Browseruse service stopped")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for browseruse service."""
        return [
            {
                "name": "create_session",
                "description": "Create a new browser session",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "headless": {
                            "type": "boolean",
                            "description": "Run browser in headless mode",
                            "default": True
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Default timeout in seconds",
                            "default": 30
                        }
                    }
                }
            },
            {
                "name": "navigate",
                "description": "Navigate to a URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to navigate to"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "get_page_info",
                "description": "Get current page information",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "find_elements",
                "description": "Find elements on the page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector or XPath"
                        },
                        "by": {
                            "type": "string",
                            "description": "Selector type (css, xpath, id, class, tag, name)",
                            "default": "css"
                        }
                    },
                    "required": ["selector"]
                }
            },
            {
                "name": "click_element",
                "description": "Click an element",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector or XPath"
                        },
                        "by": {
                            "type": "string",
                            "description": "Selector type (css, xpath, id, class)",
                            "default": "css"
                        }
                    },
                    "required": ["selector"]
                }
            },
            {
                "name": "type_text",
                "description": "Type text into an element",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector or XPath"
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to type"
                        },
                        "by": {
                            "type": "string",
                            "description": "Selector type (css, xpath, id, class)",
                            "default": "css"
                        }
                    },
                    "required": ["selector", "text"]
                }
            },
            {
                "name": "take_screenshot",
                "description": "Take a screenshot of the current page",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "observe",
                "description": "Get simplified text-based DOM tree of important visible elements with interaction paths",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "close_session",
                "description": "Close a browser session",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call a browseruse tool."""
        try:
            if tool_name == "create_session":
                return await self._create_session(arguments)
            
            # For other tools, we need a session
            if not session_id or session_id not in self.sessions:
                return {
                    "error": "No active session. Create a session first.",
                    "session_id": session_id
                }
            
            session = self.sessions[session_id]
            
            if tool_name == "navigate":
                return session.navigate(arguments["url"])
            elif tool_name == "get_page_info":
                return session.get_page_info()
            elif tool_name == "find_elements":
                return {
                    "elements": session.find_elements(
                        arguments["selector"], 
                        arguments.get("by", "css")
                    )
                }
            elif tool_name == "click_element":
                return session.click_element(
                    arguments["selector"], 
                    arguments.get("by", "css")
                )
            elif tool_name == "type_text":
                return session.type_text(
                    arguments["selector"],
                    arguments["text"],
                    arguments.get("by", "css")
                )
            elif tool_name == "take_screenshot":
                return {
                    "screenshot": session.take_screenshot(),
                    "format": "base64"
                }
            elif tool_name == "observe":
                return session.observe()
            elif tool_name == "close_session":
                return await self._close_session(session_id)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            self.logger.error("Tool call failed", tool=tool_name, error=str(e))
            return {"error": str(e)}
    
    async def call_tool_stream(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream tool execution with real-time updates for browser operations."""
        
        # Send start event
        yield {
            "type": "start",
            "tool_name": tool_name,
            "session_id": session_id,
            "message": f"Starting browser operation: {tool_name}",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        try:
            # Special handling for create_session
            if tool_name == "create_session":
                yield {
                    "type": "progress",
                    "progress": 25,
                    "message": "Checking session limits...",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                if len(self.sessions) >= self.max_sessions:
                    yield {
                        "type": "error",
                        "error": f"Maximum sessions ({self.max_sessions}) reached",
                        "timestamp": asyncio.get_event_loop().time()
                    }
                    return
                
                yield {
                    "type": "progress",
                    "progress": 50,
                    "message": "Starting browser session...",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                result = await self._create_session(arguments)
                
                yield {
                    "type": "progress",
                    "progress": 100,
                    "message": "Browser session created successfully",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                yield {
                    "type": "success",
                    "result": result,
                    "session_id": result.get("session_id"),
                    "message": "Browser session ready",
                    "timestamp": asyncio.get_event_loop().time()
                }
                return
            
            # For other tools, check session exists
            if session_id is None:
                yield {
                    "type": "error",
                    "error": "Session ID required for this operation",
                    "timestamp": asyncio.get_event_loop().time()
                }
                return
            
            if session_id not in self.sessions:
                yield {
                    "type": "error",
                    "error": "Session not found",
                    "session_id": session_id,
                    "timestamp": asyncio.get_event_loop().time()
                }
                return
            
            session = self.sessions[session_id]
            
            # Navigation with progress updates
            if tool_name == "navigate":
                url = arguments.get("url", "")
                yield {
                    "type": "progress",
                    "progress": 30,
                    "message": f"Navigating to {url}...",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                result = session.navigate(url)
                
                yield {
                    "type": "progress",
                    "progress": 80,
                    "message": "Page loaded, getting information...",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                # Add brief delay to simulate loading time for streaming demo
                await asyncio.sleep(0.5)
                
                yield {
                    "type": "success",
                    "result": result,
                    "session_id": session_id,
                    "message": f"Successfully navigated to {result.get('title', 'page')}",
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            # Element interaction with progress
            elif tool_name in ["click_element", "type_text"]:
                selector = arguments.get("selector", "")
                yield {
                    "type": "progress",
                    "progress": 40,
                    "message": f"Finding element: {selector}...",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                if tool_name == "click_element":
                    result = session.click_element(selector, arguments.get("by", "css"))
                    action_msg = f"Clicked element: {selector}"
                else:  # type_text
                    text = arguments.get("text", "")
                    result = session.type_text(selector, text, arguments.get("by", "css"))
                    action_msg = f"Typed text into: {selector}"
                
                yield {
                    "type": "progress",
                    "progress": 90,
                    "message": action_msg,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                yield {
                    "type": "success",
                    "result": result,
                    "session_id": session_id,
                    "message": action_msg,
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            # Screenshot with progress
            elif tool_name == "take_screenshot":
                yield {
                    "type": "progress",
                    "progress": 50,
                    "message": "Capturing screenshot...",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                screenshot = session.take_screenshot()
                
                yield {
                    "type": "progress",
                    "progress": 90,
                    "message": "Processing image data...",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                result = {
                    "screenshot": screenshot,
                    "format": "base64"
                }
                
                yield {
                    "type": "success",
                    "result": result,
                    "session_id": session_id,
                    "message": "Screenshot captured successfully",
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            # Other operations fall back to default streaming
            else:
                yield {
                    "type": "progress",
                    "progress": 50,
                    "message": f"Executing {tool_name}...",
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                result = await self.call_tool(tool_name, arguments, session_id)
                
                if "error" in result:
                    yield {
                        "type": "error",
                        "error": result["error"],
                        "session_id": session_id,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                else:
                    yield {
                        "type": "success",
                        "result": result,
                        "session_id": session_id,
                        "message": f"{tool_name} completed successfully",
                        "timestamp": asyncio.get_event_loop().time()
                    }
        
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "session_id": session_id,
                "message": f"Browser operation failed: {str(e)}",
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def _create_session(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new browser session."""
        if len(self.sessions) >= self.max_sessions:
            return {"error": f"Maximum sessions ({self.max_sessions}) reached"}
        
        session_id = str(uuid.uuid4())
        headless = arguments.get("headless", self.default_headless)
        timeout = arguments.get("timeout", self.default_timeout)
        
        session = BrowserSession(session_id, headless, timeout)
        await session.start()
        
        self.sessions[session_id] = session
        
        return {
            "session_id": session_id,
            "status": "created",
            "headless": headless,
            "timeout": timeout
        }
    
    async def _close_session(self, session_id: str) -> Dict[str, Any]:
        """Close a browser session."""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        await session.stop()
        del self.sessions[session_id]
        
        return {
            "session_id": session_id,
            "status": "closed"
        }

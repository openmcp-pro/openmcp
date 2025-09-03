"""Browseruse MCP service for web browsing capabilities."""

import asyncio
import uuid
from typing import Any, Dict, List, Optional

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
            elif tool_name == "close_session":
                return await self._close_session(session_id)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            self.logger.error("Tool call failed", tool=tool_name, error=str(e))
            return {"error": str(e)}
    
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

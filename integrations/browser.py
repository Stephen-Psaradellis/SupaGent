"""
Browser automation service using BrowserUse.

Provides autonomous, reasoning-driven browser capabilities through
BrowserUse's vision/DOM reasoning and memory of recent browser state.
"""
from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse
from datetime import datetime, timedelta

try:
    from playwright.async_api import Page, BrowserContext, async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    Page = None
    BrowserContext = None
    async_playwright = None
    PLAYWRIGHT_AVAILABLE = False

from core.secrets import get_openai_api_key

logger = logging.getLogger(__name__)

# Try different browser-use package versions and APIs
BROWSER_USE_AVAILABLE = False
Agent = None
Browser = None
BrowserConfig = None

# Try modern browser-use API (Python 3.11+ required)
try:
    from browser_use import Agent, Browser, BrowserConfig
    BROWSER_USE_AVAILABLE = True
    logger.info("✅ Browser-use package available - AI-powered automation enabled")
except ImportError:
    # Try legacy browser-use-sdk API
    try:
        from browser_use_sdk import BrowserUse as Agent, BrowserUse as Browser
        # Create a simple BrowserConfig class for compatibility
        class BrowserConfig:
            def __init__(self, headless=True, **kwargs):
                self.headless = headless
        BROWSER_USE_AVAILABLE = True
        logger.info("✅ Browser-use-sdk package available - basic automation enabled")
    except ImportError:
        logger.warning(
            "Browser-use package not available. Browser automation will use "
            "Playwright directly without AI-powered features. "
            "To enable advanced features, upgrade to Python 3.11+ and install browser-use>=0.9.0"
        )
        BROWSER_USE_AVAILABLE = False


class BrowserSession:
    """Manages a single browser session with context and state."""
    
    def __init__(self, session_id: str, browser: Optional[Browser] = None):
        """Initialize a browser session.
        
        Args:
            session_id: Unique identifier for this session
            browser: BrowserUse Browser instance (optional, created if None)
        """
        self.session_id = session_id
        self.browser = browser
        self.agent: Optional[Agent] = None
        self.page: Optional[Page] = None
        self.current_url: Optional[str] = None
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.action_count = 0
        self.max_idle_time = timedelta(minutes=30)  # Auto-close after 30 min idle
        
    def is_expired(self) -> bool:
        """Check if session has expired due to inactivity."""
        return datetime.now() - self.last_activity > self.max_idle_time
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
        self.action_count += 1


class BrowserService:
    """Service for managing browser automation with BrowserUse.
    
    Provides autonomous browser control with safety controls including:
    - Session management with automatic cleanup
    - Rate limiting
    - Domain whitelisting
    - No persistent cookies
    - Graceful error handling
    """
    
    def __init__(
        self,
        allowed_domains: Optional[List[str]] = None,
        rate_limit_per_minute: int = 30,
        screenshot_dir: Optional[str] = None,
        headless: bool = True,
        openai_api_key: Optional[str] = None,
        openai_model: str = "gpt-4o-mini",
    ):
        """Initialize the browser service.
        
        Args:
            allowed_domains: List of allowed domain patterns (e.g., ['*.example.com'])
                           If None, all domains are allowed (use with caution)
            rate_limit_per_minute: Maximum actions per minute per session
            screenshot_dir: Directory to save screenshots (defaults to ./data/screenshots)
            headless: Whether to run browser in headless mode
            openai_api_key: OpenAI API key for BrowserUse agent (defaults to getting from secrets)
            openai_model: OpenAI model to use (default: gpt-4o-mini)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "playwright package not installed. Install with: pip install playwright && playwright install"
            )
        
        if not BROWSER_USE_AVAILABLE:
            logger.warning(
                "browser-use-sdk not available. Browser automation will use Playwright directly "
                "without BrowserUse's autonomous control features."
            )
        
        # Get OpenAI API key
        self.openai_api_key = openai_api_key or get_openai_api_key()
        self.openai_model = openai_model
        
        if BROWSER_USE_AVAILABLE and not self.openai_api_key:
            logger.warning(
                "OpenAI API key not found. BrowserUse agent will not work properly. "
                "Set OPENAI_API_KEY in Doppler or pass openai_api_key parameter."
            )
        
        self.allowed_domains = allowed_domains or []
        self.rate_limit_per_minute = rate_limit_per_minute
        self.headless = headless
        
        # Session management
        self._sessions: Dict[str, BrowserSession] = {}
        self._rate_limit_tracker: Dict[str, List[float]] = {}  # session_id -> [timestamps]
        
        # Screenshot directory
        if screenshot_dir:
            self.screenshot_dir = Path(screenshot_dir)
        else:
            self.screenshot_dir = Path("./data/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Browser configuration
        if BROWSER_USE_AVAILABLE and BrowserConfig:
            self._browser_config = BrowserConfig(
                headless=headless,
                disable_security=True,  # Disable security for automation
            )
        else:
            self._browser_config = None
            self._playwright = None
        
        logger.info(f"BrowserService initialized: headless={headless}, allowed_domains={len(self.allowed_domains)}")
    
    def _check_domain_allowed(self, url: str) -> bool:
        """Check if a URL's domain is allowed.
        
        Args:
            url: URL to check
            
        Returns:
            True if domain is allowed, False otherwise
        """
        if not self.allowed_domains:
            return True  # No restrictions
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            for pattern in self.allowed_domains:
                if pattern.startswith('*.'):
                    # Wildcard subdomain matching
                    base_domain = pattern[2:]
                    if domain == base_domain or domain.endswith('.' + base_domain):
                        return True
                elif domain == pattern.lower():
                    return True
            
            return False
        except Exception as e:
            logger.warning(f"Error parsing URL {url}: {e}")
            return False
    
    def _check_rate_limit(self, session_id: str) -> bool:
        """Check if session is within rate limit.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if within rate limit, False otherwise
        """
        now = time.time()
        if session_id not in self._rate_limit_tracker:
            self._rate_limit_tracker[session_id] = []
        
        # Remove timestamps older than 1 minute
        cutoff = now - 60
        self._rate_limit_tracker[session_id] = [
            ts for ts in self._rate_limit_tracker[session_id] if ts > cutoff
        ]
        
        # Check if limit exceeded
        if len(self._rate_limit_tracker[session_id]) >= self.rate_limit_per_minute:
            return False
        
        # Record this action
        self._rate_limit_tracker[session_id].append(now)
        return True
    
    async def _get_or_create_session(self, session_id: str) -> BrowserSession:
        """Get existing session or create a new one.
        
        Args:
            session_id: Session identifier
            
        Returns:
            BrowserSession instance
        """
        # Clean up expired sessions
        await self._cleanup_expired_sessions()
        
        if session_id in self._sessions:
            session = self._sessions[session_id]
            if session.is_expired():
                logger.info(f"Session {session_id} expired, creating new one")
                await self._close_session(session_id)
            else:
                session.update_activity()
                return session
        
        # Create new session
        logger.info(f"Creating new browser session: {session_id}")
        
        if BROWSER_USE_AVAILABLE and Browser:
            browser = Browser(config=self._browser_config)
            session = BrowserSession(session_id, browser)
            session.browser = browser
            
            # Initialize browser and get page
            await browser.start()
            session.page = await browser.new_page()
            if Agent and self.openai_api_key:
                # Create Agent with OpenAI configuration
                agent_kwargs = {
                    "task": "Navigate and interact with web pages",
                    "browser": browser,
                }
                
                # Try to pass OpenAI configuration - BrowserUse may accept different parameter names
                # Common patterns: llm, model, api_key, openai_api_key, etc.
                try:
                    # Try with llm parameter (common pattern)
                    from langchain_openai import ChatOpenAI
                    llm = ChatOpenAI(
                        model=self.openai_model,
                        api_key=self.openai_api_key,
                        temperature=0,
                    )
                    agent_kwargs["llm"] = llm
                except (ImportError, Exception) as e:
                    logger.debug(f"Could not use langchain_openai for LLM: {e}")
                    # Fallback: try direct parameters
                    try:
                        agent_kwargs["model"] = self.openai_model
                        agent_kwargs["api_key"] = self.openai_api_key
                    except Exception:
                        # Try alternative parameter names
                        agent_kwargs["openai_api_key"] = self.openai_api_key
                        agent_kwargs["openai_model"] = self.openai_model
                
                session.agent = Agent(**agent_kwargs)
                logger.info(f"Created BrowserUse Agent with model: {self.openai_model}")
            elif Agent:
                logger.warning("BrowserUse Agent created without OpenAI API key - limited functionality")
                session.agent = Agent(
                    task="Navigate and interact with web pages",
                    browser=browser,
                )
        else:
            # Fallback to Playwright directly
            if self._playwright is None:
                self._playwright = await async_playwright().start()
            
            browser = await self._playwright.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            session = BrowserSession(session_id, None)
            session.browser = browser
            session.page = await context.new_page()
        
        self._sessions[session_id] = session
        return session
    
    async def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions."""
        expired_ids = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]
        for sid in expired_ids:
            await self._close_session(sid)
    
    async def _close_session(self, session_id: str) -> None:
        """Close and remove a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id not in self._sessions:
            return
        
        session = self._sessions[session_id]
        try:
            if session.browser:
                if BROWSER_USE_AVAILABLE and hasattr(session.browser, 'close'):
                    # BrowserUse Browser instance
                    await session.browser.close()
                elif hasattr(session.browser, 'close'):
                    # Playwright Browser instance
                    await session.browser.close()
        except Exception as e:
            logger.warning(f"Error closing browser for session {session_id}: {e}")
        
        del self._sessions[session_id]
        if session_id in self._rate_limit_tracker:
            del self._rate_limit_tracker[session_id]
        
        logger.info(f"Closed session: {session_id}")
    
    async def navigate(
        self,
        url: str,
        session_id: str = "default",
        wait_for: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Navigate to a URL.
        
        Args:
            url: URL to navigate to
            session_id: Session identifier (defaults to "default")
            wait_for: Optional selector or text to wait for after navigation
            
        Returns:
            Dictionary with status, url, title, and any extracted data
        """
        try:
            # Check domain whitelist
            if not self._check_domain_allowed(url):
                return {
                    "status": "error",
                    "error": f"Domain not allowed: {urlparse(url).netloc}",
                    "allowed_domains": self.allowed_domains,
                }
            
            # Check rate limit
            if not self._check_rate_limit(session_id):
                return {
                    "status": "error",
                    "error": f"Rate limit exceeded: {self.rate_limit_per_minute} actions/minute",
                }
            
            # Get or create session
            session = await self._get_or_create_session(session_id)
            
            # Navigate
            logger.info(f"Navigating to {url} (session: {session_id})")
            await session.page.goto(url, wait_until="networkidle")
            session.current_url = url
            session.update_activity()
            
            # Wait for element if specified
            if wait_for:
                try:
                    await session.page.wait_for_selector(wait_for, timeout=10000)
                except Exception:
                    logger.warning(f"Timeout waiting for selector: {wait_for}")
            
            # Extract basic page info
            title = await session.page.title()
            current_url = session.page.url
            
            return {
                "status": "success",
                "url": current_url,
                "title": title,
                "session_id": session_id,
            }
            
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "url": url,
            }
    
    async def interact(
        self,
        action: str,
        selector: Optional[str] = None,
        text: Optional[str] = None,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """Perform an interaction on the page.
        
        Args:
            action: Action to perform (click, type, submit, scroll, wait)
            selector: CSS selector or text to identify element
            text: Text to type (for type action)
            session_id: Session identifier
            
        Returns:
            Dictionary with status and result
        """
        try:
            # Check rate limit
            if not self._check_rate_limit(session_id):
                return {
                    "status": "error",
                    "error": f"Rate limit exceeded: {self.rate_limit_per_minute} actions/minute",
                }
            
            session = await self._get_or_create_session(session_id)
            if not session.page:
                return {
                    "status": "error",
                    "error": "No active page in session",
                }
            
            session.update_activity()
            
            # Use BrowserUse agent for intelligent interactions
            if session.agent:
                if action == "click":
                    task = f"Click on the element: {selector}"
                elif action == "type":
                    task = f"Type '{text}' into the element: {selector}"
                elif action == "submit":
                    task = f"Submit the form containing: {selector}"
                elif action == "scroll":
                    task = f"Scroll to the element: {selector}" if selector else "Scroll down the page"
                elif action == "wait":
                    task = f"Wait for the element: {selector} to appear"
                else:
                    task = f"Perform {action} on {selector}"
                
                result = await session.agent.run(task)
                
                return {
                    "status": "success",
                    "action": action,
                    "result": result,
                    "session_id": session_id,
                }
            else:
                # Fallback to direct Playwright if agent not available
                page = session.page
                if action == "click" and selector:
                    await page.click(selector)
                elif action == "type" and selector and text:
                    await page.fill(selector, text)
                elif action == "submit" and selector:
                    await page.locator(selector).press("Enter")
                elif action == "scroll":
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                elif action == "wait" and selector:
                    await page.wait_for_selector(selector, timeout=10000)
                else:
                    return {
                        "status": "error",
                        "error": f"Unknown action or missing parameters: {action}",
                    }
                
                return {
                    "status": "success",
                    "action": action,
                    "session_id": session_id,
                }
                
        except Exception as e:
            logger.error(f"Error performing interaction: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "action": action,
            }
    
    async def extract(
        self,
        extract_type: str = "all",
        selector: Optional[str] = None,
        session_id: str = "default",
    ) -> Dict[str, Any]:
        """Extract structured data from the page.
        
        Args:
            extract_type: Type of data to extract (all, title, text, links, metadata)
            selector: Optional CSS selector to limit extraction scope
            session_id: Session identifier
            
        Returns:
            Dictionary with extracted data
        """
        try:
            session = await self._get_or_create_session(session_id)
            if not session.page:
                return {
                    "status": "error",
                    "error": "No active page in session",
                }
            
            session.update_activity()
            page = session.page
            
            extracted = {}
            
            if extract_type in ("all", "title"):
                extracted["title"] = await page.title()
            
            if extract_type in ("all", "url"):
                extracted["url"] = page.url
            
            if extract_type in ("all", "text"):
                if selector:
                    element = page.locator(selector)
                    extracted["text"] = await element.inner_text()
                else:
                    extracted["text"] = await page.inner_text("body")
            
            if extract_type in ("all", "links"):
                links = await page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        return links.map(a => ({
                            text: a.innerText.trim(),
                            href: a.href
                        })).filter(l => l.text && l.href);
                    }
                """)
                extracted["links"] = links
            
            if extract_type in ("all", "metadata"):
                metadata = await page.evaluate("""
                    () => {
                        const meta = {};
                        document.querySelectorAll('meta').forEach(m => {
                            const name = m.getAttribute('name') || m.getAttribute('property');
                            const content = m.getAttribute('content');
                            if (name && content) {
                                meta[name] = content;
                            }
                        });
                        return meta;
                    }
                """)
                extracted["metadata"] = metadata
            
            return {
                "status": "success",
                "extracted": extracted,
                "extract_type": extract_type,
                "session_id": session_id,
            }
            
        except Exception as e:
            logger.error(f"Error extracting data: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "extract_type": extract_type,
            }
    
    async def screenshot(
        self,
        session_id: str = "default",
        full_page: bool = False,
        selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Capture a screenshot of the page.
        
        Args:
            session_id: Session identifier
            full_page: Whether to capture full page or just viewport
            selector: Optional CSS selector to screenshot specific element
            
        Returns:
            Dictionary with status and screenshot path
        """
        try:
            session = await self._get_or_create_session(session_id)
            if not session.page:
                return {
                    "status": "error",
                    "error": "No active page in session",
                }
            
            session.update_activity()
            page = session.page
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{session_id}_{timestamp}.png"
            screenshot_path = self.screenshot_dir / filename
            
            # Take screenshot
            if selector:
                element = page.locator(selector)
                await element.screenshot(path=str(screenshot_path))
            else:
                await page.screenshot(
                    path=str(screenshot_path),
                    full_page=full_page,
                )
            
            return {
                "status": "success",
                "screenshot_path": str(screenshot_path),
                "screenshot_url": f"/screenshots/{filename}",
                "session_id": session_id,
            }
            
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def get_html(
        self,
        session_id: str = "default",
        selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get HTML content of the page or element.
        
        Args:
            session_id: Session identifier
            selector: Optional CSS selector to get HTML of specific element
            
        Returns:
            Dictionary with HTML content
        """
        try:
            session = await self._get_or_create_session(session_id)
            if not session.page:
                return {
                    "status": "error",
                    "error": "No active page in session",
                }
            
            session.update_activity()
            page = session.page
            
            if selector:
                element = page.locator(selector)
                html = await element.inner_html()
            else:
                html = await page.content()
            
            return {
                "status": "success",
                "html": html,
                "session_id": session_id,
            }
            
        except Exception as e:
            logger.error(f"Error getting HTML: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close a browser session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with status
        """
        try:
            await self._close_session(session_id)
            return {
                "status": "success",
                "message": f"Session {session_id} closed",
            }
        except Exception as e:
            logger.error(f"Error closing session: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
            }
    
    async def cleanup_all_sessions(self) -> None:
        """Close all active sessions."""
        session_ids = list(self._sessions.keys())
        for session_id in session_ids:
            await self._close_session(session_id)


# Global browser service instance
_browser_service: Optional[BrowserService] = None


def get_browser_service() -> BrowserService:
    """Get the global browser service instance.
    
    Returns:
        BrowserService instance
    """
    global _browser_service
    if _browser_service is None:
        from core.config import get_config
        from core.secrets import get_openai_api_key
        config = get_config()
        
        # Get allowed domains from config
        allowed_domains = getattr(config, 'browser_allowed_domains', None)
        if allowed_domains:
            allowed_domains = allowed_domains.split(',') if isinstance(allowed_domains, str) else allowed_domains
        
        # Get OpenAI API key and model
        openai_api_key = get_openai_api_key()
        openai_model = getattr(config, 'browser_openai_model', 'gpt-4o-mini')
        
        _browser_service = BrowserService(
            allowed_domains=allowed_domains,
            rate_limit_per_minute=getattr(config, 'browser_rate_limit', 30),
            screenshot_dir=getattr(config, 'browser_screenshot_dir', None),
            headless=getattr(config, 'browser_headless', True),
            openai_api_key=openai_api_key,
            openai_model=openai_model,
        )
    return _browser_service


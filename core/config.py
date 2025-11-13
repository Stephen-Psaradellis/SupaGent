"""
Centralized configuration management for SupaGent.

Provides a single source of truth for all configuration values.
Secrets (API keys) are loaded from Doppler, while other configuration
is loaded from .env file via dotenv.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from core.secrets import get_elevenlabs_api_key, get_openai_api_key

# Load environment variables from .env file (non-secrets only)
load_dotenv()


@dataclass
class AppConfig:
    """Application configuration with environment-aware defaults.
    
    Automatically detects deployment environment (Railway, local) and
    adjusts paths and URLs accordingly.
    """
    
    # ElevenLabs Configuration
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_agent_id: Optional[str] = None
    elevenlabs_voice_id: Optional[str] = None
    elevenlabs_mcp_server_id: Optional[str] = None
    
    # Vector Store Configuration
    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_backend: str = "CHROMA"
    
    # Session and Data Storage
    sessions_dir: str = "./data/sessions"
    analytics_dir: str = "./data/analytics"
    escalations_dir: str = "./data/escalations"
    compliance_dir: str = "./data/compliance"
    
    # Base URL Configuration
    base_url: str = "http://localhost:8000"
    mcp_server_name: str = "SupaGent Knowledge Base"
    
    # Feature Flags
    dummy_tts: bool = False
    
    # CRM Configuration
    crm_type: str = "generic"
    crm_api_endpoint: Optional[str] = None
    crm_api_key: Optional[str] = None
    crm_auth_type: str = "bearer"
    
    # Browser Configuration
    browser_allowed_domains: Optional[str] = None  # Comma-separated list or None for all
    browser_rate_limit: int = 30  # Actions per minute per session
    browser_screenshot_dir: Optional[str] = None  # Defaults to ./data/screenshots
    browser_headless: bool = True  # Run browser in headless mode
    browser_openai_model: str = "gpt-4o-mini"  # OpenAI model for BrowserUse agent

    # Database Configuration
    database_url: Optional[str] = None  # Railway Postgres DATABASE_URL
    
    @classmethod
    def from_env(cls) -> AppConfig:
        """Create configuration from environment variables.
        
        Automatically detects Railway environment and adjusts paths.
        Uses sensible defaults for all values.
        
        Returns:
            AppConfig instance with values from environment or defaults.
        """
        is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT"))
        
        # Base paths - Railway uses /app, local uses ./
        if is_railway:
            default_data_dir = "/app/data"
            default_chroma_dir = "/app/data/chroma"
            default_sessions_dir = "/app/data/sessions"
        else:
            default_data_dir = "./data"
            default_chroma_dir = "./data/chroma"
            default_sessions_dir = "./data/sessions"
        
        # Base URL detection
        railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if railway_public_domain:
            base_url = f"https://{railway_public_domain}"
        else:
            base_url = os.getenv("SUPAGENT_BASE_URL", "http://localhost:8000")
        
        return cls(
            # ElevenLabs - API key from Doppler, others from .env
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
            elevenlabs_agent_id=os.getenv("ELEVENLABS_AGENT_ID"),
            elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
            elevenlabs_mcp_server_id=os.getenv("ELEVENLABS_MCP_SERVER_ID"),
            
            # Vector Store
            chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", default_chroma_dir),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            vector_backend=os.getenv("VECTOR_BACKEND", "CHROMA").upper(),
            
            # Data Directories
            sessions_dir=os.getenv("SESSIONS_DIR", default_sessions_dir),
            analytics_dir=os.path.join(default_data_dir, "analytics"),
            escalations_dir=os.path.join(default_data_dir, "escalations"),
            compliance_dir=os.path.join(default_data_dir, "compliance"),
            
            # Base URL
            base_url=base_url,
            mcp_server_name=os.getenv("SUPAGENT_MCP_SERVER_NAME", "SupaGent Knowledge Base"),
            
            # Feature Flags
            dummy_tts=os.getenv("SUPAGENT_DUMMY_TTS") == "1",
            
            # CRM
            crm_type=os.getenv("CRM_TYPE", "generic").lower(),
            crm_api_endpoint=os.getenv("CRM_API_ENDPOINT"),
            crm_api_key=os.getenv("CRM_API_KEY"),
            crm_auth_type=os.getenv("CRM_AUTH_TYPE", "bearer"),
            
            # Browser
            browser_allowed_domains=os.getenv("BROWSER_ALLOWED_DOMAINS"),
            browser_rate_limit=int(os.getenv("BROWSER_RATE_LIMIT", "30")),
            browser_screenshot_dir=os.getenv("BROWSER_SCREENSHOT_DIR"),
            browser_headless=os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
            browser_openai_model=os.getenv("BROWSER_OPENAI_MODEL", "gpt-4o-mini"),

            # Database
            database_url=os.getenv("DATABASE_URL"),
        )
    
    def is_railway(self) -> bool:
        """Check if running in Railway environment.
        
        Returns:
            True if RAILWAY_ENVIRONMENT is set, False otherwise.
        """
        # RAILWAY_ENVIRONMENT is a non-secret env var, safe to read directly
        return bool(os.getenv("RAILWAY_ENVIRONMENT"))
    
    def get_mcp_endpoint(self) -> str:
        """Get the MCP protocol endpoint URL.
        
        Returns:
            Full URL to the MCP endpoint.
        """
        return f"{self.base_url}/mcp"
    
    def get_tool_endpoint(self) -> str:
        """Get the tool endpoint URL.
        
        Returns:
            Full URL to the tool endpoint.
        """
        return f"{self.base_url}/tools/search_knowledge_base"
    
    def ensure_directories(self) -> None:
        """Ensure all data directories exist.
        
        Creates directories if they don't exist.
        """
        directories = [
            self.chroma_persist_dir,
            self.sessions_dir,
            self.analytics_dir,
            self.escalations_dir,
            self.compliance_dir,
        ]
        
        # Add browser screenshot directory if configured
        if self.browser_screenshot_dir:
            directories.append(self.browser_screenshot_dir)
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance.
    
    Creates and caches the configuration on first call.
    
    Returns:
        AppConfig instance.
    """
    global _config
    if _config is None:
        _config = AppConfig.from_env()
        _config.ensure_directories()
    return _config


def reset_config() -> None:
    """Reset the global configuration (useful for testing).
    
    Forces re-creation of config on next get_config() call.
    """
    global _config
    _config = None


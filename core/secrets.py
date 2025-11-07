"""
Doppler secrets management.

This module provides a centralized way to access secrets from Doppler.
Secrets (API keys) are loaded from Doppler, while other configuration
is loaded from .env file via dotenv.
"""
from __future__ import annotations

import subprocess
from typing import Optional


def get_doppler_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a secret from Doppler.
    
    Args:
        key: Secret key name (e.g., "ELEVENLABS_API_KEY").
        default: Default value if secret is not found.
        
    Returns:
        Secret value or default if not found.
        
    Raises:
        RuntimeError: If Doppler CLI is not available or command fails.
    """
    try:
        result = subprocess.run(
            ["doppler", "secrets", "get", key, "--plain"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        secret_value = result.stdout.strip()
        return secret_value if secret_value else default
    except FileNotFoundError:
        raise RuntimeError(
            f"Doppler CLI not found. Install Doppler CLI and ensure it's in your PATH. "
            f"See https://docs.doppler.com/docs/install-cli for installation instructions."
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to get secret '{key}' from Doppler. "
            f"Make sure you're authenticated (run 'doppler login') and project is linked (run 'doppler setup'). "
            f"Error: {e.stderr.strip() if e.stderr else str(e)}"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"Timeout while getting secret '{key}' from Doppler. "
            f"Check your Doppler connection and try again."
        )
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error getting secret '{key}' from Doppler: {str(e)}"
        )


def get_elevenlabs_api_key() -> Optional[str]:
    """Get ElevenLabs API key from Doppler.
    
    Returns:
        ElevenLabs API key or None if not found.
        
    Raises:
        RuntimeError: If Doppler CLI is not available or command fails.
    """
    return get_doppler_secret("ELEVENLABS_API_KEY")


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from Doppler.
    
    Returns:
        OpenAI API key or None if not found.
        
    Raises:
        RuntimeError: If Doppler CLI is not available or command fails.
    """
    return get_doppler_secret("OPENAI_API_KEY")


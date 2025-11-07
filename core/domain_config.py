"""
Domain configuration for support agent customization.

This module provides domain-specific configurations that allow the agent
to be easily reconfigured for different companies/products (e.g., GitLab,
McDonald's, etc.). Each domain config includes:
- Company/product information
- Agent personality and branding
- Domain-specific test scenarios
- Evaluation questions
- System prompt customization
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class DomainConfig:
    """Configuration for a specific support domain.
    
    Attributes:
        domain_id: Unique identifier for this domain (e.g., "gitlab", "mcdonalds")
        company_name: Name of the company (e.g., "GitLab", "McDonald's")
        product_name: Name of the product/service (e.g., "GitLab", "McDonald's App")
        agent_name: Name of the support agent (e.g., "Alex")
        support_type: Type of support (e.g., "technical", "customer service")
        industry: Industry sector (e.g., "software development", "restaurant")
        
        # Test scenarios
        test_scenarios: List of test scenarios for this domain
        
        # Evaluation questions
        eval_questions: List of evaluation questions with expected substrings
        
        # Prompt customization
        prompt_customizations: Additional prompt sections or overrides
    """
    domain_id: str
    company_name: str
    product_name: str
    agent_name: str = "Alex"
    support_type: str = "customer support"
    industry: str = "general"
    
    # Test scenarios - list of dicts with name, messages, expected_tool_calls, expected_keywords
    test_scenarios: List[Dict[str, Any]] = field(default_factory=list)
    
    # Evaluation questions - list of dicts with question and expected_substring
    eval_questions: List[Dict[str, str]] = field(default_factory=list)
    
    # Prompt customizations
    prompt_customizations: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, file_path: str | Path) -> DomainConfig:
        """Load domain configuration from a JSON file.
        
        Args:
            file_path: Path to the domain configuration JSON file.
            
        Returns:
            DomainConfig instance loaded from the file.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Domain config file not found: {file_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return cls(
            domain_id=data.get("domain_id", ""),
            company_name=data.get("company_name", ""),
            product_name=data.get("product_name", ""),
            agent_name=data.get("agent_name", "Alex"),
            support_type=data.get("support_type", "customer support"),
            industry=data.get("industry", "general"),
            test_scenarios=data.get("test_scenarios", []),
            eval_questions=data.get("eval_questions", []),
            prompt_customizations=data.get("prompt_customizations", {}),
        )
    
    def to_file(self, file_path: str | Path) -> None:
        """Save domain configuration to a JSON file.
        
        Args:
            file_path: Path where to save the configuration.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "domain_id": self.domain_id,
            "company_name": self.company_name,
            "product_name": self.product_name,
            "agent_name": self.agent_name,
            "support_type": self.support_type,
            "industry": self.industry,
            "test_scenarios": self.test_scenarios,
            "eval_questions": self.eval_questions,
            "prompt_customizations": self.prompt_customizations,
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_system_prompt_template_vars(self) -> Dict[str, str]:
        """Get template variables for system prompt customization.
        
        Returns:
            Dictionary of template variables that can be used in prompts.
        """
        return {
            "company_name": self.company_name,
            "product_name": self.product_name,
            "agent_name": self.agent_name,
            "support_type": self.support_type,
            "industry": self.industry,
        }


# Global domain configuration instance
_domain_config: Optional[DomainConfig] = None


def get_domain_config() -> DomainConfig:
    """Get the current domain configuration.
    
    Loads from environment variable DOMAIN_CONFIG_FILE or defaults to "gitlab".
    
    Returns:
        DomainConfig instance for the current domain.
    """
    global _domain_config
    
    if _domain_config is None:
        # Check for domain config file path in environment
        config_file = os.getenv("DOMAIN_CONFIG_FILE")
        
        if config_file:
            _domain_config = DomainConfig.from_file(config_file)
        else:
            # Default to gitlab if no config specified
            domain_id = os.getenv("DOMAIN_ID", "gitlab")
            config_path = Path(__file__).parent.parent / "domains" / f"{domain_id}.json"
            
            if config_path.exists():
                _domain_config = DomainConfig.from_file(config_path)
            else:
                # Fallback to GitLab config
                _domain_config = get_gitlab_config()
    
    return _domain_config


def set_domain_config(config: DomainConfig) -> None:
    """Set the current domain configuration.
    
    Args:
        config: DomainConfig instance to use.
    """
    global _domain_config
    _domain_config = config


def reset_domain_config() -> None:
    """Reset the domain configuration (useful for testing)."""
    global _domain_config
    _domain_config = None


# Predefined domain configurations are in core/domain_factories.py
# Import them here for backward compatibility
from core.domain_factories import get_gitlab_config, get_mcdonalds_config


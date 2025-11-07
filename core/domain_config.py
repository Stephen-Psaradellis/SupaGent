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


# Predefined domain configurations

def get_gitlab_config() -> DomainConfig:
    """Get GitLab domain configuration.
    
    Returns:
        DomainConfig for GitLab support.
    """
    return DomainConfig(
        domain_id="gitlab",
        company_name="GitLab",
        product_name="GitLab",
        agent_name="Alex",
        support_type="technical support",
        industry="software development",
        test_scenarios=[
            {
                "name": "Password Reset Query",
                "messages": [{"role": "user", "content": "How do I reset my password?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["password", "reset"],
            },
            {
                "name": "SSH Key Configuration",
                "messages": [{"role": "user", "content": "How do I configure SSH keys?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["SSH", "key"],
            },
            {
                "name": "CI/CD Pipeline Setup",
                "messages": [{"role": "user", "content": "How do I set up a CI/CD pipeline?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["pipeline", "CI", "CD"],
            },
            {
                "name": "Merge Request Creation",
                "messages": [{"role": "user", "content": "How do I create a merge request?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["merge request"],
            },
            {
                "name": "GitLab Runner Setup",
                "messages": [{"role": "user", "content": "What are GitLab runners and how do I set them up?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["runner"],
            },
        ],
        eval_questions=[
            {"question": "How do I reset my password?", "expected_substring": "password"},
            {"question": "How do I configure SSH keys?", "expected_substring": "SSH"},
            {"question": "What are GitLab runners?", "expected_substring": "runner"},
            {"question": "How do I create a new project?", "expected_substring": "project"},
            {"question": "How to set up CI/CD pipeline?", "expected_substring": "pipeline"},
            {"question": "How do I create a merge request?", "expected_substring": "merge request"},
            {"question": "How do I file an issue?", "expected_substring": "issue"},
            {"question": "How to use labels for issues?", "expected_substring": "labels"},
            {"question": "How do I create a milestone?", "expected_substring": "milestone"},
            {"question": "How do I enable two-factor authentication?", "expected_substring": "two-factor"},
        ],
    )


def get_mcdonalds_config() -> DomainConfig:
    """Get McDonald's domain configuration.
    
    Returns:
        DomainConfig for McDonald's support.
    """
    return DomainConfig(
        domain_id="mcdonalds",
        company_name="McDonald's",
        product_name="McDonald's App",
        agent_name="Alex",
        support_type="customer service",
        industry="restaurant",
        test_scenarios=[
            {
                "name": "App Login Issue",
                "messages": [{"role": "user", "content": "I can't log into the McDonald's app"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["login", "app"],
            },
            {
                "name": "Order Status Inquiry",
                "messages": [{"role": "user", "content": "How do I check my order status?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["order", "status"],
            },
            {
                "name": "Rewards Program Question",
                "messages": [{"role": "user", "content": "How does the rewards program work?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["rewards", "points"],
            },
            {
                "name": "Refund Request",
                "messages": [{"role": "user", "content": "How do I request a refund?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["refund"],
            },
            {
                "name": "Store Locator",
                "messages": [{"role": "user", "content": "How do I find a nearby McDonald's location?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["location", "store"],
            },
            {
                "name": "Mobile Order Issue",
                "messages": [{"role": "user", "content": "My mobile order didn't go through"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["mobile order", "order"],
            },
            {
                "name": "Payment Method Question",
                "messages": [{"role": "user", "content": "What payment methods do you accept?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["payment", "method"],
            },
            {
                "name": "Nutritional Information",
                "messages": [{"role": "user", "content": "Where can I find nutritional information?"}],
                "expected_tool_calls": ["knowledgebase"],
                "expected_keywords": ["nutrition", "nutritional"],
            },
        ],
        eval_questions=[
            {"question": "How do I log into the McDonald's app?", "expected_substring": "login"},
            {"question": "How do I check my order status?", "expected_substring": "order"},
            {"question": "How does the rewards program work?", "expected_substring": "rewards"},
            {"question": "How do I request a refund?", "expected_substring": "refund"},
            {"question": "How do I find a nearby McDonald's?", "expected_substring": "location"},
            {"question": "What payment methods do you accept?", "expected_substring": "payment"},
            {"question": "Where can I find nutritional information?", "expected_substring": "nutrition"},
            {"question": "How do I redeem rewards points?", "expected_substring": "redeem"},
            {"question": "Can I modify my order after placing it?", "expected_substring": "modify"},
            {"question": "How do I contact customer service?", "expected_substring": "contact"},
        ],
    )


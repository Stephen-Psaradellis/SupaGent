"""
Factory functions for creating predefined domain configurations.

This module contains factory functions for creating domain configurations
for specific companies/products. This keeps the main domain_config.py
focused on the DomainConfig class and its management.
"""
from __future__ import annotations

from core.domain_config import DomainConfig


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










"""
OpenAI-powered domain configuration generator.

This service uses OpenAI to automatically generate domain configurations
including test scenarios, evaluation questions, and prompt customizations
based on basic domain information (company name, product, industry, etc.).
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, Any, List, Optional

from core.domain_config import DomainConfig
from core.secrets import get_openai_api_key


class DomainGenerator:
    """Service for generating domain configurations using OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize the domain generator.
        
        Args:
            api_key: OpenAI API key. If not provided, reads from Doppler.
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency).
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai>=1.0.0"
            )
        
        self.api_key = api_key or get_openai_api_key()
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY in Doppler "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def generate_test_scenarios(
        self,
        company_name: str,
        product_name: str,
        support_type: str,
        industry: str,
        num_scenarios: int = 10,
    ) -> List[Dict[str, Any]]:
        """Generate test scenarios for a domain.
        
        Args:
            company_name: Name of the company.
            product_name: Name of the product/service.
            support_type: Type of support (e.g., "technical support", "customer service").
            industry: Industry sector.
            num_scenarios: Number of test scenarios to generate (default: 10).
            
        Returns:
            List of test scenario dictionaries.
        """
        prompt = f"""Generate {num_scenarios} realistic customer support test scenarios for {company_name} ({product_name}).

Company: {company_name}
Product: {product_name}
Support Type: {support_type}
Industry: {industry}

For each scenario, create a realistic customer question that a support agent would encounter.
The scenarios should cover:
- Common support issues (account access, password reset, troubleshooting)
- Product/service questions
- Policy and procedure questions
- Technical issues (if applicable)
- Payment/billing questions (if applicable)

Return a JSON object with a "scenarios" array where each element has this structure:
{{
  "name": "Short descriptive name for the test",
  "messages": [
    {{"role": "user", "content": "The customer's question"}}
  ],
  "expected_tool_calls": ["knowledgebase"],
  "expected_keywords": ["keyword1", "keyword2"]
}}

The expected_keywords should be 2-3 words that should appear in a good answer to this question.
Return ONLY valid JSON in this format: {{"scenarios": [...]}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates test scenarios in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            # Handle different response formats
            try:
                data = json.loads(content)
                # Handle {"scenarios": [...]} format
                if "scenarios" in data:
                    return data["scenarios"]
                # Handle {"test_scenarios": [...]} format
                elif "test_scenarios" in data:
                    return data["test_scenarios"]
                # Handle direct array format
                elif isinstance(data, list):
                    return data
                else:
                    # Try to extract scenarios from any key that contains a list
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            # Check if it looks like a test scenario
                            if isinstance(value[0], dict) and ("name" in value[0] or "messages" in value[0]):
                                return value
                    return []
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                # Try to find any JSON array in the content
                json_match = re.search(r'(\[.*?\])', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                raise ValueError(f"Could not parse JSON from response: {content[:200]}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate test scenarios: {e}") from e
    
    def generate_eval_questions(
        self,
        company_name: str,
        product_name: str,
        support_type: str,
        industry: str,
        num_questions: int = 10,
    ) -> List[Dict[str, str]]:
        """Generate evaluation questions for a domain.
        
        Args:
            company_name: Name of the company.
            product_name: Name of the product/service.
            support_type: Type of support.
            industry: Industry sector.
            num_questions: Number of evaluation questions to generate (default: 10).
            
        Returns:
            List of evaluation question dictionaries with "question" and "expected_substring" keys.
        """
        prompt = f"""Generate {num_questions} evaluation questions for testing a customer support agent for {company_name} ({product_name}).

Company: {company_name}
Product: {product_name}
Support Type: {support_type}
Industry: {industry}

For each question, create a realistic customer question and identify a key word or phrase that should appear in a good answer.

Return a JSON object with a "questions" array where each element has this structure:
{{
  "question": "The customer's question",
  "expected_substring": "A key word or phrase that should appear in the answer"
}}

The expected_substring should be a single word or short phrase (2-3 words max) that indicates the answer is relevant.
Return ONLY valid JSON, no markdown formatting, no explanation."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates evaluation questions in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Handle different response formats
            if "questions" in data:
                return data["questions"]
            elif "eval_questions" in data:
                return data["eval_questions"]
            elif isinstance(data, list):
                return data
            else:
                # Try to extract questions from any key that contains a list
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        # Check if it looks like an eval question
                        if isinstance(value[0], dict) and ("question" in value[0] or "expected_substring" in value[0]):
                            return value
                return []
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate evaluation questions: {e}") from e
    
    def generate_domain_config(
        self,
        domain_id: str,
        company_name: str,
        product_name: str,
        agent_name: str = "Alex",
        support_type: str = "customer support",
        industry: str = "general",
        num_test_scenarios: int = 10,
        num_eval_questions: int = 10,
    ) -> DomainConfig:
        """Generate a complete domain configuration.
        
        Args:
            domain_id: Unique identifier for the domain.
            company_name: Name of the company.
            product_name: Name of the product/service.
            agent_name: Name of the support agent (default: "Alex").
            support_type: Type of support (default: "customer support").
            industry: Industry sector (default: "general").
            num_test_scenarios: Number of test scenarios to generate (default: 10).
            num_eval_questions: Number of evaluation questions to generate (default: 10).
            
        Returns:
            DomainConfig instance with generated test scenarios and eval questions.
        """
        print(f"Generating test scenarios for {company_name}...", file=sys.stderr)
        test_scenarios = self.generate_test_scenarios(
            company_name=company_name,
            product_name=product_name,
            support_type=support_type,
            industry=industry,
            num_scenarios=num_test_scenarios,
        )
        
        print(f"Generating evaluation questions for {company_name}...", file=sys.stderr)
        eval_questions = self.generate_eval_questions(
            company_name=company_name,
            product_name=product_name,
            support_type=support_type,
            industry=industry,
            num_questions=num_eval_questions,
        )
        
        return DomainConfig(
            domain_id=domain_id,
            company_name=company_name,
            product_name=product_name,
            agent_name=agent_name,
            support_type=support_type,
            industry=industry,
            test_scenarios=test_scenarios,
            eval_questions=eval_questions,
            prompt_customizations={},
        )


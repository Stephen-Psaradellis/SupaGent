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
from pathlib import Path
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
    
    def _load_elevenlabs_prompting_guide(self) -> str:
        """Load the ElevenLabs prompting guide content.
        
        Returns:
            The content of the ElevenLabs prompting guide as a string.
        """
        # Get the project root (assuming this file is in core/)
        project_root = Path(__file__).parent.parent
        guide_path = project_root / "docs" / "ELEVENLABS_PROMPTING_GUIDE.md"
        
        if not guide_path.exists():
            raise FileNotFoundError(
                f"ElevenLabs prompting guide not found at {guide_path}. "
                "Please ensure docs/ELEVENLABS_PROMPTING_GUIDE.md exists."
            )
        
        return guide_path.read_text(encoding="utf-8")
    
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
    
    def generate_system_prompt(
        self,
        company_name: str,
        product_name: str,
        agent_name: str = "Alex",
        support_type: str = "customer support",
        industry: str = "general",
    ) -> str:
        """Generate a system prompt for a voice agent using OpenAI.
        
        This method generates a system prompt following the ElevenLabs Agent
        Prompting Guide structure, ensuring the prompt is optimized for voice
        interactions and follows best practices.
        
        Args:
            company_name: Name of the company.
            product_name: Name of the product/service.
            agent_name: Name of the support agent (default: "Alex").
            support_type: Type of support (default: "customer support").
            industry: Industry sector (default: "general").
            
        Returns:
            Generated system prompt string following the ElevenLabs guide structure.
        """
        # Load the ElevenLabs prompting guide as context
        try:
            prompting_guide = self._load_elevenlabs_prompting_guide()
        except FileNotFoundError as e:
            raise RuntimeError(
                f"Failed to load ElevenLabs prompting guide: {e}. "
                "The guide is required to generate high-quality system prompts."
            ) from e
        
        prompt = f"""Generate a comprehensive system prompt for an ElevenLabs voice agent that provides {support_type} for {company_name} ({product_name}).

Company: {company_name}
Product: {product_name}
Agent Name: {agent_name}
Support Type: {support_type}
Industry: {industry}

You must follow the ElevenLabs Agent Prompting Guide structure exactly. The prompt must be organized into these six building blocks:

1. **Personality**: Define the agent's identity, name ({agent_name}), core traits, role, and relevant background
2. **Environment**: Specify the communication context (voice conversation), channel, and situational factors
3. **Tone**: Control linguistic style, speech patterns, conversational elements, and TTS compatibility (formatting for spoken delivery)
4. **Goal**: Establish clear objectives and sequential pathways for helping customers
5. **Guardrails**: Set boundaries ensuring appropriate and ethical interactions
6. **Tools**: Define the knowledgebase tool and when/how to use it

The prompt should be optimized for voice interactions, with clear instructions for:
- Natural speech patterns and conversational elements
- TTS-compatible formatting (spelling out emails, formatting phone numbers, converting numbers to spoken form)
- Empathy and understanding customer frustration
- Clear step-by-step guidance
- Knowledge base tool usage

Return ONLY the system prompt text, structured with clear section headers (using # for main sections). Do not include any explanation, markdown code blocks, or additional commentary - just the prompt itself.

Reference the ElevenLabs Prompting Guide below for detailed guidance on each section:

---
{prompting_guide}
---"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating system prompts for voice agents following the ElevenLabs Agent Prompting Guide. Generate prompts that are clear, structured, and optimized for voice interactions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            
            # Clean up the response - remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                # Remove markdown code block markers
                lines = content.split("\n")
                # Remove first line if it's a code block marker
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # Remove last line if it's a code block marker
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines)
            
            return content.strip()
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate system prompt: {e}") from e
    
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


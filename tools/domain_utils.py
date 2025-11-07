"""
Utility functions for domain configuration management.

These functions are used by the switch_domain tool and can be reused
by other tools that need to work with domain configurations.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain_config import DomainConfig


def list_available_domains(domains_dir: Path | None = None) -> list[dict[str, str]]:
    """List all available domain configurations.
    
    Args:
        domains_dir: Optional path to domains directory. Defaults to project root / domains.
        
    Returns:
        List of dictionaries with 'domain_id' and 'company_name' keys.
    """
    if domains_dir is None:
        domains_dir = Path(__file__).parent.parent / "domains"
    
    if not domains_dir.exists():
        print("No domains directory found. Creating example domains...", file=sys.stderr)
        domains_dir.mkdir(parents=True, exist_ok=True)
        from core.domain_config import get_gitlab_config, get_mcdonalds_config
        get_gitlab_config().to_file(domains_dir / "gitlab.json")
        get_mcdonalds_config().to_file(domains_dir / "mcdonalds.json")
    
    domain_files = list(domains_dir.glob("*.json"))
    
    if not domain_files:
        print("No domain configurations found in domains/ directory.", file=sys.stderr)
        return []
    
    domains = []
    print("Available domains:", file=sys.stderr)
    for domain_file in sorted(domain_files):
        try:
            with open(domain_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            domain_id = data.get("domain_id", domain_file.stem)
            company_name = data.get("company_name", "Unknown")
            print(f"  - {domain_id}: {company_name}", file=sys.stderr)
            domains.append({"domain_id": domain_id, "company_name": company_name})
        except Exception as e:
            print(f"  - {domain_file.stem}: (error loading: {e})", file=sys.stderr)
    
    return domains


def regenerate_eval_file(domain_config: "DomainConfig", eval_file: Path | None = None) -> None:
    """Regenerate the evaluation file from domain configuration.
    
    Args:
        domain_config: DomainConfig instance.
        eval_file: Optional path to eval file. Defaults to dataset/eval.jsonl.
    """
    if eval_file is None:
        eval_file = Path("dataset/eval.jsonl")
    eval_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not domain_config.eval_questions:
        print(f"Warning: Domain '{domain_config.domain_id}' has no eval questions defined.", file=sys.stderr)
        return
    
    with open(eval_file, "w", encoding="utf-8") as f:
        for q in domain_config.eval_questions:
            json.dump(q, f, ensure_ascii=False)
            f.write("\n")
    
    print(f"✓ Regenerated {eval_file} with {len(domain_config.eval_questions)} questions", file=sys.stderr)


def update_elevenlabs_agent(domain_config: "DomainConfig") -> None:
    """Update the ElevenLabs agent with the new domain configuration.
    
    Args:
        domain_config: DomainConfig instance.
    """
    try:
        from agents.agent_testing import ElevenLabsAgentTester
        from agents.system_prompt import get_system_prompt
        from core.secrets import get_elevenlabs_api_key
        from dotenv import load_dotenv
        
        load_dotenv()  # Load .env for ELEVENLABS_AGENT_ID
        
        api_key = get_elevenlabs_api_key()
        agent_id = os.getenv("ELEVENLABS_AGENT_ID")
        
        if not api_key or not agent_id:
            print("Warning: ELEVENLABS_API_KEY (from Doppler) or ELEVENLABS_AGENT_ID not set. Skipping agent update.", file=sys.stderr)
            return
        
        tester = ElevenLabsAgentTester(agent_id=agent_id, api_key=api_key)
        prompt = get_system_prompt()
        
        result = tester.update_agent(prompt=prompt)
        print(f"✓ Updated ElevenLabs agent prompt for {domain_config.company_name}", file=sys.stderr)
        
    except Exception as e:
        print(f"Warning: Failed to update ElevenLabs agent: {e}", file=sys.stderr)


def regenerate_tests(domain_config: "DomainConfig") -> None:
    """Regenerate test suites in ElevenLabs.
    
    Args:
        domain_config: DomainConfig instance.
    """
    try:
        from agents.agent_testing import ElevenLabsAgentTester
        from agents.test_suites import get_comprehensive_test_suite
        from core.secrets import get_elevenlabs_api_key
        from dotenv import load_dotenv
        
        load_dotenv()  # Load .env for ELEVENLABS_AGENT_ID
        
        api_key = get_elevenlabs_api_key()
        agent_id = os.getenv("ELEVENLABS_AGENT_ID")
        
        if not api_key or not agent_id:
            print("Warning: ELEVENLABS_API_KEY (from Doppler) or ELEVENLABS_AGENT_ID not set. Skipping test regeneration.", file=sys.stderr)
            return
        
        tester = ElevenLabsAgentTester(agent_id=agent_id, api_key=api_key)
        scenarios = get_comprehensive_test_suite()
        
        if not scenarios:
            print(f"Warning: No test scenarios found for domain '{domain_config.domain_id}'.", file=sys.stderr)
            return
        
        print(f"Creating {len(scenarios)} tests in ElevenLabs...", file=sys.stderr)
        created_tests = tester.create_tests_from_scenarios(scenarios)
        
        successful = [t for t in created_tests if "test_id" in t]
        failed = [t for t in created_tests if "error" in t]
        
        print(f"✓ Successfully created {len(successful)}/{len(scenarios)} tests", file=sys.stderr)
        
        if failed:
            print(f"Warning: {len(failed)} tests failed to create:", file=sys.stderr)
            for test in failed:
                print(f"  - {test.get('scenario_name', 'Unknown')}: {test.get('error', 'Unknown error')}", file=sys.stderr)
        
    except Exception as e:
        print(f"Warning: Failed to regenerate tests: {e}", file=sys.stderr)


def update_env_file(domain_id: str, env_file: Path | None = None) -> None:
    """Update .env file with DOMAIN_ID.
    
    Args:
        domain_id: Domain identifier to set.
        env_file: Optional path to .env file. Defaults to .env in project root.
    """
    if env_file is None:
        env_file = Path(".env")
    
    if env_file.exists():
        # Read existing .env
        env_lines = env_file.read_text(encoding="utf-8").splitlines()
        
        # Update or add DOMAIN_ID
        updated = False
        new_lines = []
        for line in env_lines:
            if line.startswith("DOMAIN_ID="):
                new_lines.append(f"DOMAIN_ID={domain_id}")
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            new_lines.append(f"DOMAIN_ID={domain_id}")
        
        env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"✓ Updated .env file with DOMAIN_ID={domain_id}", file=sys.stderr)
    else:
        print(f"Note: .env file not found. Set DOMAIN_ID={domain_id} manually.", file=sys.stderr)


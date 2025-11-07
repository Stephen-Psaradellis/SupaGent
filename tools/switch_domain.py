"""
Switch the agent to a different domain configuration.

This tool allows you to quickly reconfigure the agent for a different purpose
(e.g., from GitLab to McDonald's). It:
1. Loads the domain configuration
2. Regenerates evaluation data files
3. Optionally updates the ElevenLabs agent prompt
4. Optionally regenerates test suites in ElevenLabs

Usage:
    python -m tools.switch_domain gitlab
    python -m tools.switch_domain mcdonalds
    python -m tools.switch_domain --list
    python -m tools.switch_domain mcdonalds --update-agent --regenerate-tests
"""
from __future__ import annotations

import sys
from pathlib import Path

from tools.domain_utils import (
    list_available_domains,
    regenerate_eval_file,
    update_elevenlabs_agent,
    regenerate_tests,
    update_env_file,
)


def generate_domain(
    domain_id: str,
    company_name: str,
    product_name: str,
    agent_name: str = "Alex",
    support_type: str = "customer support",
    industry: str = "general",
    num_test_scenarios: int = 10,
    num_eval_questions: int = 10,
    save: bool = True,
) -> DomainConfig:
    """Generate a new domain configuration using OpenAI.
    
    Args:
        domain_id: Unique identifier for the domain.
        company_name: Name of the company.
        product_name: Name of the product/service.
        agent_name: Name of the support agent.
        support_type: Type of support.
        industry: Industry sector.
        num_test_scenarios: Number of test scenarios to generate.
        num_eval_questions: Number of evaluation questions to generate.
        save: Whether to save the generated config to a file.
        
    Returns:
        Generated DomainConfig instance.
    """
    from core.domain_generator import DomainGenerator
    
    try:
        generator = DomainGenerator()
    except (ImportError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Make sure OPENAI_API_KEY is set in Doppler.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Generating domain configuration for {company_name}...", file=sys.stderr)
    
    try:
        domain_config = generator.generate_domain_config(
            domain_id=domain_id,
            company_name=company_name,
            product_name=product_name,
            agent_name=agent_name,
            support_type=support_type,
            industry=industry,
            num_test_scenarios=num_test_scenarios,
            num_eval_questions=num_eval_questions,
        )
        
        if save:
            domains_dir = Path(__file__).parent.parent / "domains"
            domains_dir.mkdir(parents=True, exist_ok=True)
            config_file = domains_dir / f"{domain_id}.json"
            domain_config.to_file(config_file)
            print(f"✓ Saved domain configuration to {config_file}", file=sys.stderr)
        
        print(f"✓ Generated {len(domain_config.test_scenarios)} test scenarios", file=sys.stderr)
        print(f"✓ Generated {len(domain_config.eval_questions)} evaluation questions", file=sys.stderr)
        
        return domain_config
        
    except Exception as e:
        print(f"Error generating domain configuration: {e}", file=sys.stderr)
        sys.exit(1)


def switch_domain(
    domain_id: str,
    update_agent: bool = False,
    regenerate_tests: bool = False,
) -> None:
    """Switch to a different domain configuration.
    
    Args:
        domain_id: Domain identifier (e.g., "gitlab", "mcdonalds")
        update_agent: Whether to update the ElevenLabs agent prompt
        regenerate_tests: Whether to regenerate test suites in ElevenLabs
    """
    from core.domain_config import DomainConfig, set_domain_config, reset_domain_config
    
    # Reset cached config
    reset_domain_config()
    
    # Load domain configuration
    domains_dir = Path(__file__).parent.parent / "domains"
    config_file = domains_dir / f"{domain_id}.json"
    
    if not config_file.exists():
        print(f"Error: Domain configuration not found: {config_file}", file=sys.stderr)
        print(f"Available domains:", file=sys.stderr)
        list_available_domains()
        sys.exit(1)
    
    try:
        domain_config = DomainConfig.from_file(config_file)
    except Exception as e:
        print(f"Error: Failed to load domain configuration: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Switching to domain: {domain_config.company_name} ({domain_config.domain_id})", file=sys.stderr)
    print(f"  Product: {domain_config.product_name}", file=sys.stderr)
    print(f"  Support Type: {domain_config.support_type}", file=sys.stderr)
    print(f"  Industry: {domain_config.industry}", file=sys.stderr)
    
    # Set the domain config
    set_domain_config(domain_config)
    
    # Regenerate evaluation file
    regenerate_eval_file(domain_config)
    
    # Update environment variable for persistence
    update_env_file(domain_id)
    
    # Update ElevenLabs agent if requested
    if update_agent:
        update_elevenlabs_agent(domain_config)
    
    # Regenerate tests if requested
    if regenerate_tests:
        regenerate_tests(domain_config)
    
    print(f"\n✓ Successfully switched to {domain_config.company_name} domain", file=sys.stderr)
    print(f"\nNext steps:", file=sys.stderr)
    print(f"  1. Update your dataset: python -m tools.ingest --dir dataset", file=sys.stderr)
    if not update_agent:
        print(f"  2. Update ElevenLabs agent: python -m tools.switch_domain {domain_id} --update-agent", file=sys.stderr)
    if not regenerate_tests:
        print(f"  3. Regenerate tests: python -m tools.switch_domain {domain_id} --regenerate-tests", file=sys.stderr)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Switch the agent to a different domain configuration or generate a new one",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Switch to existing domain
  python -m tools.switch_domain gitlab
  python -m tools.switch_domain mcdonalds --update-agent
  
  # Generate new domain with OpenAI
  python -m tools.switch_domain mycompany --generate --company "My Company" --product "My Product"
  python -m tools.switch_domain mycompany --generate --company "My Company" --product "My Product" --industry "technology"
  
  # List available domains
  python -m tools.switch_domain --list
        """,
    )
    parser.add_argument(
        "domain_id",
        nargs="?",
        help="Domain identifier to switch to or generate (e.g., 'gitlab', 'mcdonalds')",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available domain configurations",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate a new domain configuration using OpenAI (requires OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--company",
        help="Company name (required for --generate)",
    )
    parser.add_argument(
        "--product",
        help="Product/service name (required for --generate)",
    )
    parser.add_argument(
        "--agent-name",
        default="Alex",
        help="Agent name (default: Alex)",
    )
    parser.add_argument(
        "--support-type",
        default="customer support",
        help="Support type (default: customer support)",
    )
    parser.add_argument(
        "--industry",
        default="general",
        help="Industry sector (default: general)",
    )
    parser.add_argument(
        "--num-test-scenarios",
        type=int,
        default=10,
        help="Number of test scenarios to generate (default: 10)",
    )
    parser.add_argument(
        "--num-eval-questions",
        type=int,
        default=10,
        help="Number of evaluation questions to generate (default: 10)",
    )
    parser.add_argument(
        "--update-agent",
        action="store_true",
        help="Update the ElevenLabs agent prompt with the new domain configuration",
    )
    parser.add_argument(
        "--regenerate-tests",
        action="store_true",
        help="Regenerate test suites in ElevenLabs dashboard",
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_domains()
        return
    
    if not args.domain_id:
        parser.print_help()
        print("\nError: domain_id is required (or use --list to see available domains)", file=sys.stderr)
        sys.exit(1)
    
    # Generate new domain if requested
    if args.generate:
        if not args.company or not args.product:
            print("Error: --company and --product are required when using --generate", file=sys.stderr)
            sys.exit(1)
        
        domain_config = generate_domain(
            domain_id=args.domain_id,
            company_name=args.company,
            product_name=args.product,
            agent_name=args.agent_name,
            support_type=args.support_type,
            industry=args.industry,
            num_test_scenarios=args.num_test_scenarios,
            num_eval_questions=args.num_eval_questions,
            save=True,
        )
        
        # After generating, optionally switch to it
        print(f"\nSwitching to newly generated domain...", file=sys.stderr)
        switch_domain(
            domain_id=args.domain_id,
            update_agent=args.update_agent,
            regenerate_tests=args.regenerate_tests,
        )
    else:
        # Switch to existing domain
        switch_domain(
            domain_id=args.domain_id,
            update_agent=args.update_agent,
            regenerate_tests=args.regenerate_tests,
        )


if __name__ == "__main__":
    main()


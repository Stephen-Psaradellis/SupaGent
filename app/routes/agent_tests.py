"""
Agent testing routes.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, List
from fastapi import APIRouter

router = APIRouter(prefix="/agent-tests", tags=["agent-tests"])


@router.post("/create-suite")
def create_test_suite(
    name: str,
    scenarios: List[Dict[str, Any]],
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a test suite for the agent."""
    try:
        from agents.agent_testing import ElevenLabsAgentTester, TestScenario
        
        tester = ElevenLabsAgentTester()
        test_scenarios = [
            TestScenario(
                name=s.get("name", ""),
                messages=s.get("messages", []),
                expected_tool_calls=s.get("expected_tool_calls"),
                expected_keywords=s.get("expected_keywords"),
            )
            for s in scenarios
        ]
        
        result = tester.create_test_suite(name, test_scenarios, description)
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/create-tool-invocation")
def create_tool_invocation_test_suite() -> Dict[str, Any]:
    """Create the 10 tool invocation test suite in ElevenLabs dashboard using REST API."""
    try:
        from agents.agent_testing import ElevenLabsAgentTester
        from agents.test_suites import get_tool_invocation_test_suite
        
        tester = ElevenLabsAgentTester()
        scenarios = get_tool_invocation_test_suite()
        
        created_tests = tester.create_tests_from_scenarios(scenarios)
        
        successful = [t for t in created_tests if "test_id" in t]
        failed = [t for t in created_tests if "error" in t]
        
        return {
            "success": len(failed) == 0,
            "created": len(successful),
            "failed": len(failed),
            "tests": created_tests,
            "test_ids": [t["test_id"] for t in successful],
        }
    except Exception as e:
        return {
            "error": str(e),
            "note": "Make sure ELEVENLABS_API_KEY (in Doppler) and ELEVENLABS_AGENT_ID are set",
        }


@router.post("/run")
def run_agent_tests(
    test_suite_id: Optional[str] = None,
    scenarios: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Run agent tests."""
    try:
        from agents.agent_testing import ElevenLabsAgentTester, TestScenario
        
        tester = ElevenLabsAgentTester()
        
        test_scenarios = None
        if scenarios:
            test_scenarios = [
                TestScenario(
                    name=s.get("name", ""),
                    messages=s.get("messages", []),
                    expected_tool_calls=s.get("expected_tool_calls"),
                    expected_keywords=s.get("expected_keywords"),
                )
                for s in scenarios
            ]
        
        results = tester.run_tests(test_suite_id, test_scenarios)
        
        return {
            "results": [
                {
                    "test_id": r.test_id,
                    "scenario_name": r.scenario_name,
                    "passed": r.passed,
                    "details": r.details,
                    "tool_calls": r.tool_calls,
                    "response": r.response,
                    "error": r.error,
                }
                for r in results
            ],
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed),
            }
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/results")
def get_test_results(
    test_suite_id: Optional[str] = None,
    test_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Get test results."""
    try:
        from agents.agent_testing import ElevenLabsAgentTester
        
        tester = ElevenLabsAgentTester()
        return tester.get_test_results(test_suite_id, test_id)
    except Exception as e:
        return {"error": str(e)}


@router.get("/suites")
def list_test_suites() -> Dict[str, Any]:
    """List all test suites."""
    try:
        from agents.agent_testing import ElevenLabsAgentTester
        
        tester = ElevenLabsAgentTester()
        suites = tester.list_test_suites()
        return {"suites": suites}
    except Exception as e:
        return {"error": str(e)}


@router.get("/default-suite")
def get_default_test_suite() -> Dict[str, Any]:
    """Get default test suite scenarios."""
    try:
        from agents.agent_testing import create_default_test_suite
        
        scenarios = create_default_test_suite()
        return {
            "scenarios": [
                {
                    "name": s.name,
                    "messages": s.messages,
                    "expected_tool_calls": s.expected_tool_calls,
                    "expected_keywords": s.expected_keywords,
                }
                for s in scenarios
            ]
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/run-comprehensive")
def run_comprehensive_tests() -> Dict[str, Any]:
    """Run the comprehensive 10-test suite."""
    try:
        from agents.agent_testing import ElevenLabsAgentTester, TestResult
        from agents.test_suites import get_comprehensive_test_suite
        
        scenarios = get_comprehensive_test_suite()
        
        # Try to use tester, fallback to local
        tester = None
        try:
            tester = ElevenLabsAgentTester()
        except RuntimeError:
            pass
        
        if tester:
            try:
                results = tester.run_tests(scenarios=scenarios)
            except Exception:
                results = tester._run_tests_locally(scenarios)
        else:
            # Run locally
            from memory.mcp_client import MCPClient
            from memory.vector_store import VectorStore
            from agents.rag import RAGAnswerer
            
            store = VectorStore()
            mcp = MCPClient(store.similarity_search)
            rag = RAGAnswerer(mcp)
            
            results = []
            for i, scenario in enumerate(scenarios):
                test_id = f"test_{i}_{scenario.name}"
                try:
                    user_messages = [
                        msg["content"] for msg in scenario.messages
                        if msg.get("role") == "user"
                    ]
                    if not user_messages:
                        continue
                    
                    last_user_message = user_messages[-1]
                    answer = rag.answer(last_user_message)
                    response_text = answer.get("answer", "")
                    
                    tool_calls = []
                    if answer.get("sources"):
                        tool_calls.append({
                            "name": "search_knowledge_base",
                            "arguments": {"query": last_user_message},
                        })
                    
                    expected_tool_calls_met = True
                    if scenario.expected_tool_calls:
                        tool_names = [tc.get("name") for tc in tool_calls]
                        expected_tool_calls_met = all(
                            expected in tool_names
                            for expected in scenario.expected_tool_calls
                        )
                    
                    passed = expected_tool_calls_met
                    
                    results.append(TestResult(
                        test_id=test_id,
                        scenario_name=scenario.name,
                        passed=passed,
                        details={
                            "sources_count": len(answer.get("sources", [])),
                        },
                        tool_calls=tool_calls,
                        response=response_text,
                    ))
                except Exception as e:
                    results.append(TestResult(
                        test_id=test_id,
                        scenario_name=scenario.name,
                        passed=False,
                        details={},
                        tool_calls=[],
                        error=str(e),
                    ))
        
        return {
            "results": [
                {
                    "test_id": r.test_id,
                    "scenario_name": r.scenario_name,
                    "passed": r.passed,
                    "details": r.details,
                    "tool_calls": r.tool_calls,
                    "response": r.response[:200] if r.response else None,
                    "error": r.error,
                }
                for r in results
            ],
            "summary": {
                "total": len(results),
                "passed": sum(1 for r in results if r.passed),
                "failed": sum(1 for r in results if not r.passed),
                "pass_rate": sum(1 for r in results if r.passed) / len(results) * 100 if results else 0,
            }
        }
    except Exception as e:
        return {"error": str(e)}











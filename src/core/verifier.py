import time
from typing import Dict, Any, Tuple, Optional
from pydantic import BaseModel
from src.core.lattice import PermissionLattice, PermissionLevel, ToolSchema
from src.core.inspector import ParameterScopeInspector

class VerificationResult(BaseModel):
    is_intercepted: bool
    original_tool: str
    executed_tool: str
    original_permission: PermissionLevel
    executed_permission: PermissionLevel
    was_downgraded: bool
    was_blocked: bool
    latency_ms: float
    reason: str

class LeastPrivilegeVerifier:
    """
    Deterministic runtime guardrail enforcing the Principle of Least Privilege (PoLP).
    Intercepts candidate tool calls, validates parameter scopes, and performs
    capability-preserving downward projections in the permission lattice.
    """
    def __init__(self, lattice: PermissionLattice):
        self.lattice = lattice

    def verify_and_route(
        self,
        candidate_tool_name: str,
        arguments: Dict[str, Any],
        domain: str,
        required_capability: str
    ) -> Tuple[str, Dict[str, Any], VerificationResult]:
        """
        Intercepts candidate tool emission.
        Returns: (final_tool_name, final_arguments, VerificationResult)
        """
        start_time = time.perf_counter()
        candidate_tool = self.lattice.get_tool(candidate_tool_name)

        if not candidate_tool:
            latency = (time.perf_counter() - start_time) * 1000
            return (
                candidate_tool_name,
                arguments,
                VerificationResult(
                    is_intercepted=True,
                    original_tool=candidate_tool_name,
                    executed_tool="BLOCKED",
                    original_permission=PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED,
                    executed_permission=PermissionLevel.LEVEL_1_READ_SINGLE,
                    was_downgraded=False,
                    was_blocked=True,
                    latency_ms=latency,
                    reason=f"Unknown tool '{candidate_tool_name}' blocked."
                )
            )

        # 1. Deterministically infer required scope from argument payload
        required_level = ParameterScopeInspector.infer_required_scope(arguments)

        # 2. Check if candidate tool is strictly over-privileged
        if candidate_tool.permission_level.strictly_subsumes(required_level):
            # Attempt to find the minimal sufficient tool preserving capability
            minimal_tool = self.lattice.find_least_sufficient_tool(
                domain=domain,
                required_capability=required_capability,
                required_level=required_level
            )

            latency = (time.perf_counter() - start_time) * 1000

            if minimal_tool and minimal_tool.name != candidate_tool.name:
                return (
                    minimal_tool.name,
                    arguments,
                    VerificationResult(
                        is_intercepted=True,
                        original_tool=candidate_tool.name,
                        executed_tool=minimal_tool.name,
                        original_permission=candidate_tool.permission_level,
                        executed_permission=minimal_tool.permission_level,
                        was_downgraded=True,
                        was_blocked=False,
                        latency_ms=latency,
                        reason=f"Over-privileged tool '{candidate_tool.name}' downgraded to '{minimal_tool.name}'."
                    )
                )

        latency = (time.perf_counter() - start_time) * 1000
        # Compliant tool invocation
        return (
            candidate_tool.name,
            arguments,
            VerificationResult(
                is_intercepted=True,
                original_tool=candidate_tool.name,
                executed_tool=candidate_tool.name,
                original_permission=candidate_tool.permission_level,
                executed_permission=candidate_tool.permission_level,
                was_downgraded=False,
                was_blocked=False,
                latency_ms=latency,
                reason="Tool invocation conforms to least privilege."
            )
        )

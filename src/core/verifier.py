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
    Intercepts candidate tool emissions, validates parameter scopes, prevents argument smuggling,
    and performs capability-preserving downward projections in the permission lattice.
    """
    def __init__(self, lattice: PermissionLattice):
        self.lattice = lattice

    def verify_and_route(
        self,
        candidate_tool_name: str,
        arguments: Dict[str, Any],
        domain: Optional[str] = None,
        required_capability: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any], VerificationResult]:
        """
        Intercepts candidate tool emission.
        If domain or required_capability are omitted, they are extracted directly from
        the candidate tool's schema, avoiding circular evaluation dependence on benchmark labels.
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

        # Decouple from benchmark ground truth: infer domain & capability from candidate tool if not provided
        effective_domain = domain or candidate_tool.domain
        effective_capability = required_capability or candidate_tool.capability

        # 1. Deterministically infer required scope from argument payload
        required_level = ParameterScopeInspector.infer_required_scope(arguments)

        # 2. Check for Argument Smuggling / Insufficient Tool Privilege:
        # If the arguments demand higher privilege than the tool possesses, block the execution.
        if required_level.strictly_subsumes(candidate_tool.permission_level):
            latency = (time.perf_counter() - start_time) * 1000
            return (
                candidate_tool.name,
                arguments,
                VerificationResult(
                    is_intercepted=True,
                    original_tool=candidate_tool.name,
                    executed_tool="BLOCKED",
                    original_permission=candidate_tool.permission_level,
                    executed_permission=required_level,
                    was_downgraded=False,
                    was_blocked=True,
                    latency_ms=latency,
                    reason=f"Privilege mismatch: Argument payload demands {required_level.name}, but tool only has {candidate_tool.permission_level.name}."
                )
            )

        # 3. Check if candidate tool is strictly over-privileged
        if candidate_tool.permission_level.strictly_subsumes(required_level):
            # Attempt to find the minimal sufficient tool preserving capability
            minimal_tool = self.lattice.find_least_sufficient_tool(
                domain=effective_domain,
                required_capability=effective_capability,
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

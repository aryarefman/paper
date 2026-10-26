from enum import IntEnum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class PermissionLevel(IntEnum):
    """
    Mathematical representation of a privilege hierarchy (Partially Ordered Set / Lattice).
    Higher integer implies strictly greater privilege.
    """
    LEVEL_1_READ_SINGLE = 1
    LEVEL_2_READ_BATCH = 2
    LEVEL_3_WRITE_RESTRICTED = 3
    LEVEL_4_ADMIN_UNRESTRICTED = 4

    def subsumes(self, other: "PermissionLevel") -> bool:
        """Returns True if self >= other (self covers or equals other)."""
        return self.value >= other.value

    def strictly_subsumes(self, other: "PermissionLevel") -> bool:
        """Returns True if self > other (self is strictly over-privileged compared to other)."""
        return self.value > other.value

class ToolSchema(BaseModel):
    name: str
    description: str
    permission_level: PermissionLevel
    domain: str
    capability: str  # e.g., 'financial_balance', 'academic_transcript', 'filesystem', 'notification'
    parameters: Dict[str, Any]

class PermissionLattice:
    """
    Implements capability-preserving least-privilege lattice operations.
    Guarantees that downgrades preserve the exact semantic capability needed.
    """
    def __init__(self, tools: List[ToolSchema]):
        self.tools = {t.name: t for t in tools}
        self._capability_index: Dict[str, List[ToolSchema]] = {}
        for tool in tools:
            key = f"{tool.domain}:{tool.capability}"
            self._capability_index.setdefault(key, []).append(tool)

    def get_tool(self, name: str) -> Optional[ToolSchema]:
        return self.tools.get(name)

    def find_least_sufficient_tool(
        self,
        domain: str,
        required_capability: str,
        required_level: PermissionLevel
    ) -> Optional[ToolSchema]:
        """
        Finds the minimal tool in the lattice that satisfies:
        1. Exact domain and capability match.
        2. Permission level >= required_level.
        3. Minimizes privilege level.
        Prevents capability confusion (e.g. transcript vs balance).
        """
        key = f"{domain}:{required_capability}"
        candidates = [
            t for t in self._capability_index.get(key, [])
            if t.permission_level.subsumes(required_level)
        ]
        if not candidates:
            # Check domain-wide if broad administrative tool
            broad_candidates = [
                t for t in self.tools.values()
                if t.domain == domain and t.capability == required_capability and t.permission_level.subsumes(required_level)
            ]
            if not broad_candidates:
                return None
            return min(broad_candidates, key=lambda t: t.permission_level.value)

        # Return candidate tool with the lowest sufficient permission level
        return min(candidates, key=lambda t: t.permission_level.value)

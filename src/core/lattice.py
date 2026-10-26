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
    target_entity: str
    parameters: Dict[str, Any]

class PermissionLattice:
    """
    Implements least-privilege lattice operations:
    - meet (greatest lower bound)
    - join (least upper bound)
    - equivalence mapping between tool affordances
    """
    def __init__(self, tools: List[ToolSchema]):
        self.tools = {t.name: t for t in tools}
        self._domain_index: Dict[str, List[ToolSchema]] = {}
        for tool in tools:
            self._domain_index.setdefault(tool.domain, []).append(tool)

    def get_tool(self, name: str) -> Optional[ToolSchema]:
        return self.tools.get(name)

    def find_least_sufficient_tool(
        self,
        domain: str,
        target_entity: str,
        required_level: PermissionLevel
    ) -> Optional[ToolSchema]:
        """
        Finds the minimal tool in the lattice that satisfies target_entity and
        has permission_level >= required_level, minimizing privilege.
        """
        candidates = [
            t for t in self._domain_index.get(domain, [])
            if t.target_entity == target_entity and t.permission_level.subsumes(required_level)
        ]
        if not candidates:
            return None
        # Return tool with minimum permission level
        return min(candidates, key=lambda t: t.permission_level.value)

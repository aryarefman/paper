import re
from typing import Dict, Any
from src.core.lattice import PermissionLevel

class ParameterScopeInspector:
    """
    Deterministically inspects arguments to classify whether an execution
    demands single-record access, batch access, or administrative access.
    """

    WILDCARD_PATTERNS = [
        re.compile(r"^\s*\*\s*$"),
        re.compile(r"^\s*all\s*$", re.IGNORECASE),
        re.compile(r"^\s*%\s*$"),
        re.compile(r"select\s+\*\s+from", re.IGNORECASE)
    ]

    @classmethod
    def infer_required_scope(cls, arguments: Dict[str, Any]) -> PermissionLevel:
        """
        Infers the minimum sufficient permission level needed by the argument payload.
        """
        if not arguments:
            return PermissionLevel.LEVEL_1_READ_SINGLE

        for key, val in arguments.items():
            str_val = str(val).strip()

            # Check if any argument contains broad wildcards
            for pattern in cls.WILDCARD_PATTERNS:
                if pattern.search(str_val):
                    return PermissionLevel.LEVEL_2_READ_BATCH

            # Administrative raw commands
            if key in ["raw_sql_query", "command", "alert_text"]:
                if any(kw in str_val.lower() for kw in ["drop ", "delete ", "alter ", "truncate ", "rm -rf"]):
                    return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED
                if "select " in str_val.lower() and "where" not in str_val.lower():
                    return PermissionLevel.LEVEL_2_READ_BATCH

        # Standard singular identifiers (e.g. user_id="5025201048", filename="settings.json")
        id_keys = ["user_id", "student_id", "recipient_id", "filename"]
        if any(k in arguments for k in id_keys):
            return PermissionLevel.LEVEL_1_READ_SINGLE

        return PermissionLevel.LEVEL_2_READ_BATCH

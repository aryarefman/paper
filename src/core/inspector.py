import re
from typing import Dict, Any
from src.core.lattice import PermissionLevel

class ParameterScopeInspector:
    """
    Deterministically inspects arguments to classify whether an execution
    demands single-record access, legitimate batch access, write access, or administrative access.
    """

    WILDCARD_PATTERNS = [
        re.compile(r"^\s*\*\s*$"),
        re.compile(r"^\s*all\s*$", re.IGNORECASE),
        re.compile(r"^\s*%\s*$"),
        re.compile(r"select\s+\*\s+from", re.IGNORECASE)
    ]

    DESTRUCTIVE_PATTERNS = [
        re.compile(r"\bdrop\b", re.IGNORECASE),
        re.compile(r"\bdelete\b", re.IGNORECASE),
        re.compile(r"\btruncate\b", re.IGNORECASE),
        re.compile(r"\balter\b", re.IGNORECASE),
        re.compile(r"rm\s+-rf", re.IGNORECASE)
    ]

    @classmethod
    def infer_required_scope(cls, arguments: Dict[str, Any], task_intent: str = "") -> PermissionLevel:
        """
        Infers the minimum sufficient permission level needed by the argument payload.
        Handles single-record, legitimate batch, and write operations.
        """
        if not arguments:
            return PermissionLevel.LEVEL_1_READ_SINGLE

        # 1. Check for administrative or destructive commands
        for key, val in arguments.items():
            str_val = str(val).strip()
            if any(p.search(str_val) for p in cls.DESTRUCTIVE_PATTERNS):
                return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED
            if key in ["command", "raw_sql_query", "alert_text"]:
                if any(p.search(str_val) for p in cls.WILDCARD_PATTERNS):
                    return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

        # 2. Check for write operations
        if any(k in arguments for k in ["message", "log_entry", "content", "payload"]) and "filename" in arguments:
            return PermissionLevel.LEVEL_3_WRITE_RESTRICTED

        # 3. Check for legitimate batch operations (e.g. department code, plural entity arrays)
        if any(k in arguments for k in ["department_code", "group_id", "faculty_id", "directory_path"]):
            # Legitimate batch query
            return PermissionLevel.LEVEL_2_READ_BATCH

        for key, val in arguments.items():
            if isinstance(val, list) and len(val) > 1:
                return PermissionLevel.LEVEL_2_READ_BATCH
            str_val = str(val).strip()
            for pattern in cls.WILDCARD_PATTERNS:
                if pattern.search(str_val):
                    return PermissionLevel.LEVEL_2_READ_BATCH

        # 4. Singular entity identifiers -> LEVEL_1_READ_SINGLE
        single_id_keys = ["user_id", "student_id", "recipient_id", "filename", "record_id", "nrp"]
        if any(k in arguments for k in single_id_keys):
            return PermissionLevel.LEVEL_1_READ_SINGLE

        return PermissionLevel.LEVEL_1_READ_SINGLE

import re
from typing import Dict, Any
from src.core.lattice import PermissionLevel

class ParameterScopeInspector:
    """
    Deterministically inspects arguments to classify whether an execution
    demands single-record access, legitimate batch access, write access, or administrative access.
    Adheres to fail-closed security principles.
    """

    WILDCARD_PATTERNS = [
        re.compile(r"^\s*\*\s*$"),
        re.compile(r"^\s*all\s*$", re.IGNORECASE),
        re.compile(r"^\s*%\s*$"),
        re.compile(r"select\s+.*from", re.IGNORECASE)
    ]

    DESTRUCTIVE_PATTERNS = [
        re.compile(r"\bdrop\b", re.IGNORECASE),
        re.compile(r"\bdelete\b", re.IGNORECASE),
        re.compile(r"\btruncate\b", re.IGNORECASE),
        re.compile(r"\balter\b", re.IGNORECASE),
        re.compile(r"\brm\s+(-rf|-r|-f)\b", re.IGNORECASE),
        re.compile(r"\bshutdown\b", re.IGNORECASE),
        re.compile(r"\bkill\b", re.IGNORECASE)
    ]

    SQLI_PATTERNS = [
        re.compile(r"'\s*or\s+'?1'?='?1", re.IGNORECASE),
        re.compile(r"--", re.IGNORECASE),
        re.compile(r";\s*(drop|select|insert|delete|update)", re.IGNORECASE),
        re.compile(r"\bunion\s+select\b", re.IGNORECASE)
    ]

    COMMAND_KEYS = {"command", "cmd", "shell", "exec", "script", "raw_sql_query", "raw_query", "eval"}
    QUERY_KEYS = {"query", "sql", "search_query"}
    WRITE_KEYS = {"message", "log_entry", "content", "payload", "write_data", "file_content"}
    BATCH_KEYS = {"department_code", "group_id", "faculty_id", "directory_path", "batch_ids", "filter_category"}
    SINGLE_ID_KEYS = {"user_id", "student_id", "recipient_id", "filename", "record_id", "nrp", "employee_id", "account_id"}

    SAFE_ID_REGEX = re.compile(r"^[A-Za-z0-9_\-\.\/]+$")

    @classmethod
    def infer_required_scope(cls, arguments: Dict[str, Any], task_intent: str = "") -> PermissionLevel:
        """
        Infers the minimum sufficient permission level needed by the argument payload.
        Handles single-record, legitimate batch, write, and administrative operations.
        Fails safely (fail-closed) when arguments are ambiguous or malicious.
        """
        if not arguments:
            return PermissionLevel.LEVEL_1_READ_SINGLE

        # 1. Arbitrary shell/exec keys are inherently unrestricted administrative access
        for key in arguments.keys():
            if key in cls.COMMAND_KEYS:
                return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

        # 2. Check for destructive commands, SQL injection, or raw broad SQL queries
        for key, val in arguments.items():
            str_val = str(val).strip()

            if any(p.search(str_val) for p in cls.DESTRUCTIVE_PATTERNS):
                return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

            if any(p.search(str_val) for p in cls.SQLI_PATTERNS):
                return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

            # Check query keys for SQL wildcards or broad SELECT
            if key in cls.QUERY_KEYS:
                if any(p.search(str_val) for p in cls.WILDCARD_PATTERNS):
                    return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

            # Broad alert or broadcast triggers
            if key in ["alert_text", "broadcast", "recipient"]:
                if any(p.search(str_val) for p in cls.WILDCARD_PATTERNS):
                    return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

        # 3. Check for write operations
        if any(k in arguments for k in cls.WRITE_KEYS):
            return PermissionLevel.LEVEL_3_WRITE_RESTRICTED

        # 4. Check for legitimate batch operations
        for key in cls.BATCH_KEYS:
            if key in arguments:
                val = str(arguments[key]).strip()
                # Must be a valid, non-empty, safe alphanumeric identifier
                if val and cls.SAFE_ID_REGEX.match(val) and not any(p.search(val) for p in cls.WILDCARD_PATTERNS):
                    return PermissionLevel.LEVEL_2_READ_BATCH
                else:
                    # Injection attempt or wildcard in batch key -> escalate to admin
                    return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

        for key, val in arguments.items():
            if isinstance(val, list) and len(val) > 1:
                return PermissionLevel.LEVEL_2_READ_BATCH
            str_val = str(val).strip()
            for pattern in cls.WILDCARD_PATTERNS:
                if pattern.search(str_val):
                    return PermissionLevel.LEVEL_2_READ_BATCH

        # 5. Singular entity identifiers -> LEVEL_1_READ_SINGLE
        has_single_key = any(k in arguments for k in cls.SINGLE_ID_KEYS)
        if has_single_key:
            # Verify single keys are not wildcards
            for k in cls.SINGLE_ID_KEYS:
                if k in arguments:
                    val = str(arguments[k]).strip()
                    if any(p.search(val) for p in cls.WILDCARD_PATTERNS):
                        return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED
            return PermissionLevel.LEVEL_1_READ_SINGLE

        # Fail-closed: unclassified arguments demand conservative administrative oversight
        return PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED

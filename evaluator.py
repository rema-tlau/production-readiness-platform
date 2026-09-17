import os
import re


class RuleEvaluator:

    def __init__(self, files, rules):
        self.files = files
        self.rules = rules

    # ==========================================
    # MAIN EVALUATION
    # ==========================================

    def evaluate(self):

        findings = []

        for rule in self.rules:

            if not rule.get("active", True):
                continue

            result = self.evaluate_rule(rule)

            if result is not None:
                findings.append(result)

        return findings

    # ==========================================
    # RULE DISPATCHER
    # ==========================================

    def evaluate_rule(self, rule):

        check = rule["check"]

        check_methods = {

            # Security
            "hardcoded_secrets": self.check_hardcoded_secrets,
            "authentication": self.check_authentication,
            "input_validation": self.check_input_validation,
            "sensitive_logging": self.check_sensitive_logging,
            "secure_configuration": self.check_secure_configuration,

            # Backup
            "backup_documentation": self.check_backup_documentation,
            "backup_frequency": self.check_backup_frequency,
            "restore_documentation": self.check_restore_documentation,
            "important_data": self.check_important_data,
            "recovery_procedure": self.check_recovery_procedure,

            # Monitoring
            "health_endpoint": self.check_health_endpoint,
            "application_logging": self.check_application_logging,
            "error_logging": self.check_error_logging,
            "secret_logs": self.check_sensitive_logging,
            "application_status": self.check_health_endpoint,

            # Performance
            "database_queries": self.check_database_queries,
            "large_loops": self.check_large_loops,
            "performance_testing": self.check_performance_testing,
            "caching": self.check_caching,
            "resource_assumptions": self.check_resource_assumptions,

            # Operations
            "installation_instructions": self.check_installation_instructions,
            "configuration_documentation": self.check_configuration_documentation,
            "rollback_procedure": self.check_rollback_procedure,
            "health_check": self.check_health_endpoint,
            "failure_recovery": self.check_failure_recovery,
            "ownership": self.check_ownership
        }

        method = check_methods.get(check)

        if method is None:

            return self.create_finding(
                rule,
                "Rule check is not implemented yet.",
                None
            )

        return method(rule)

    # ==========================================
    # HELPER FUNCTIONS
    # ==========================================

    def all_content(self):

        content = ""

        for file in self.files:

            # Never include .env contents in analysis
            if file["name"] == ".env":
                continue

            content += "\n" + file.get("content", "")

        return content

    def file_names(self):

        return [
            file["name"].lower()
            for file in self.files
        ]

    def find_file(self, filename):

        for file in self.files:

            if file["name"].lower() == filename.lower():
                return file

        return None

    def find_keyword(self, keywords, include_env=False):

        """
        Search all scanned files for the first occurrence
        of one of the supplied keywords.

        Returns:
            file_info,
            line_number,
            evidence
        """

        if isinstance(keywords, str):
            keywords = [keywords]

        for file in self.files:

            if not include_env and file["name"] == ".env":
                continue

            content = file.get("content", "")

            if not content:
                continue

            lines = content.splitlines()

            for line_number, line in enumerate(lines, start=1):

                lower_line = line.lower()

                for keyword in keywords:

                    if keyword.lower() in lower_line:

                        evidence = self.get_evidence_context(
                            content,
                            line_number
                        )

                        return (
                            file,
                            line_number,
                            evidence
                        )

        return None, None, None

    def find_regex(self, patterns, include_env=False):

        """
        Search files using regular expressions.

        Returns:
            file_info,
            line_number,
            evidence
        """

        if isinstance(patterns, str):
            patterns = [patterns]

        for file in self.files:

            if not include_env and file["name"] == ".env":
                continue

            content = file.get("content", "")

            if not content:
                continue

            lines = content.splitlines()

            for line_number, line in enumerate(lines, start=1):

                for pattern in patterns:

                    if re.search(
                        pattern,
                        line,
                        re.IGNORECASE
                    ):

                        evidence = self.get_evidence_context(
                            content,
                            line_number
                        )

                        return (
                            file,
                            line_number,
                            evidence
                        )

        return None, None, None

    def get_evidence_context(self, content, line_number, context_lines=2):
        """
        Return a readable code snippet around the detected line.

        The detected line is marked with ">>" and a small amount
        of surrounding context is included so the finding is easier
        to understand from the dashboard.
        """

        if not content or not line_number:
            return None

        lines = content.splitlines()

        if line_number < 1 or line_number > len(lines):
            return None

        start = max(1, line_number - context_lines)
        end = min(len(lines), line_number + context_lines)

        evidence_lines = []

        for current_line in range(start, end + 1):
            prefix = ">> " if current_line == line_number else "   "
            evidence_lines.append(
                f"{prefix}Line {current_line}: {lines[current_line - 1]}"
            )

        evidence = "\n".join(evidence_lines)

        if len(evidence) > 1200:
            evidence = evidence[:1200] + "\n..."

        return evidence


    def create_finding(
        self,
        rule,
        message,
        file_path,
        line_number=None,
        evidence=None
    ):

        return {
            "rule_id": rule["id"],
            "name": rule["name"],
            "category": rule["category"],
            "severity": rule["severity"],
            "message": message,
            "file_path": file_path,
            "line_number": line_number,
            "evidence": evidence,
            "remediation": rule["remediation"],
            "status": "Open"
        }

    def create_pass(self, rule):

        return None

    # ==========================================
    # SECURITY CHECKS
    # ==========================================

    def check_hardcoded_secrets(self, rule):

        secret_patterns = [

            r'password\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'access[_-]?token\s*=\s*["\'][^"\']+["\']'

        ]

        for file in self.files:

            if file["name"] == ".env":
                continue

            content = file.get("content", "")

            for pattern in secret_patterns:

                match = re.search(
                    pattern,
                    content,
                    re.IGNORECASE
                )

                if match:

                    line_number = (
                        content[:match.start()].count("\n") + 1
                    )

                    line = content.splitlines()[line_number - 1].strip()

                    # Do not expose the actual secret
                    evidence = re.sub(
                        r'(["\'])(.*?)(\1)',
                        r'\1***REDACTED***\3',
                        line
                    )

                    return self.create_finding(
                        rule,
                        "Possible hardcoded secret detected.",
                        file["relative_path"],
                        line_number,
                        evidence
                    )

        return self.create_pass(rule)

    def check_authentication(self, rule):

        keywords = [
            "login",
            "authenticate",
            "authorization",
            "jwt",
            "session",
            "token",
            "permission"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No obvious authentication or authorization implementation was detected.",
            None
        )

    def check_input_validation(self, rule):

        keywords = [
            "validate",
            "validation",
            "sanitize",
            "wtforms",
            "marshmallow",
            "request.args",
            "request.form",
            "request.json"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No obvious input validation mechanism was detected.",
            None
        )

    def check_sensitive_logging(self, rule):

        patterns = [

            r'print\(.*password',
            r'print\(.*api[_-]?key',
            r'logging\..*\bpassword\b',
            r'logger\..*\bpassword\b'

        ]

        file, line_number, evidence = self.find_regex(patterns)

        if file:

            return self.create_finding(
                rule,
                "Possible sensitive information in logging statement.",
                file["relative_path"],
                line_number,
                evidence
            )

        return self.create_pass(rule)

    def check_secure_configuration(self, rule):

        filenames = self.file_names()

        if ".env" in filenames:

            return self.create_pass(rule)

        keywords = [
            "os.getenv",
            "os.environ"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No obvious environment-based configuration was detected.",
            None
        )

    # ==========================================
    # BACKUP CHECKS
    # ==========================================

    def check_backup_documentation(self, rule):

        keywords = [
            "backup",
            "back-up",
            "backup procedure"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No backup documentation was detected.",
            None
        )

    def check_backup_frequency(self, rule):

        keywords = [
            "daily backup",
            "weekly backup",
            "backup frequency",
            "every day",
            "every week"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No backup frequency information was detected.",
            None
        )

    def check_restore_documentation(self, rule):

        keywords = [
            "restore",
            "restoration",
            "restore procedure"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No restore procedure documentation was detected.",
            None
        )

    def check_important_data(self, rule):

        keywords = [
            "important data",
            "critical data",
            "database",
            "user data"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No clear identification of important application data was detected.",
            None
        )

    def check_recovery_procedure(self, rule):

        keywords = [
            "recovery",
            "disaster recovery",
            "recovery procedure"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No recovery procedure was detected.",
            None
        )

    # ==========================================
    # MONITORING CHECKS
    # ==========================================

    def check_health_endpoint(self, rule):

        keywords = [
            "/health"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No /health endpoint was detected.",
            None
        )

    def check_application_logging(self, rule):

        keywords = [
            "logging",
            "logger",
            "app.logger"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No application logging implementation was detected.",
            None
        )

    def check_error_logging(self, rule):

        keywords = [
            "logging",
            "logger"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        # Having exception handling is still considered
        # an indication of error handling.
        file, line_number, evidence = self.find_keyword(
            ["except"]
        )

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No obvious error logging implementation was detected.",
            None
        )

    # ==========================================
    # PERFORMANCE CHECKS
    # ==========================================

    def check_database_queries(self, rule):

        keywords = [
            "select ",
            "insert ",
            "update ",
            "execute("
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No database query implementation was detected.",
            None
        )

    def check_large_loops(self, rule):

        total_loops = 0

        first_loop_file = None
        first_loop_line = None
        first_loop_evidence = None

        for file in self.files:

            if file["name"] == ".env":
                continue

            content = file.get("content", "")

            if not content:
                continue

            lines = content.splitlines()

            for line_number, line in enumerate(
                lines,
                start=1
            ):

                stripped = line.strip()

                if (
                    stripped.startswith("for ")
                    or stripped.startswith("for(")
                    or stripped.startswith("while ")
                    or stripped.startswith("while(")
                ):

                    total_loops += 1

                    if first_loop_file is None:

                        first_loop_file = file
                        first_loop_line = line_number
                        first_loop_evidence = self.get_evidence_context(
                            content,
                            line_number
                        )

        if total_loops <= 20:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            (
                f"A large number of loops was detected "
                f"({total_loops} loops) and should be reviewed."
            ),
            first_loop_file["relative_path"]
            if first_loop_file else None,
            first_loop_line,
            first_loop_evidence
        )

    def check_performance_testing(self, rule):

        filenames = self.file_names()

        keywords = [
            "performance",
            "benchmark",
            "load_test",
            "locust",
            "timeit"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        if any(
            "test" in filename
            for filename in filenames
        ):

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No obvious performance testing was detected.",
            None
        )

    def check_caching(self, rule):

        keywords = [
            "cache",
            "caching",
            "redis",
            "memcached"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No caching implementation was detected. Review whether caching is necessary.",
            None
        )

    def check_resource_assumptions(self, rule):

        keywords = [
            "memory",
            "cpu",
            "storage",
            "resource",
            "requirements"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No obvious resource assumptions were detected.",
            None
        )

    # ==========================================
    # OPERATIONS CHECKS
    # ==========================================

    def check_installation_instructions(self, rule):

        filenames = self.file_names()

        if "readme.md" in filenames or "readme.txt" in filenames:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No README file containing installation instructions was detected.",
            None
        )

    def check_configuration_documentation(self, rule):

        filenames = self.file_names()

        if ".env" in filenames:

            return self.create_pass(rule)

        keywords = [
            "configuration",
            "environment variable"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No configuration documentation was detected.",
            None
        )

    def check_rollback_procedure(self, rule):

        keywords = [
            "rollback",
            "roll back",
            "previous version",
            "git checkout"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No rollback procedure was detected.",
            None
        )

    def check_failure_recovery(self, rule):

        keywords = [
            "restart",
            "recovery",
            "failure",
            "troubleshooting"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No failure recovery or troubleshooting instructions were detected.",
            None
        )

    def check_ownership(self, rule):

        keywords = [
            "owner",
            "maintainer",
            "responsible",
            "team"
        ]

        file, line_number, evidence = self.find_keyword(keywords)

        if file:

            return self.create_pass(rule)

        return self.create_finding(
            rule,
            "No application ownership information was detected.",
            None
        )
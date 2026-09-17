import yaml


class RuleManager:

    def __init__(self, rule_file):
        self.rule_file = rule_file
        self.rules = []

    def load_rules(self):
        with open(self.rule_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if not data or "rules" not in data:
            raise ValueError("Invalid rule file")

        self.rules = []

        for rule in data["rules"]:
            self.validate_rule(rule)

            if "active" not in rule:
                rule["active"] = True

            self.rules.append(rule)

        return self.rules

    def validate_rule(self, rule):

        required_fields = [
            "id",
            "name",
            "category",
            "severity",
            "description",
            "check",
            "remediation"
        ]

        for field in required_fields:
            if field not in rule:
                raise ValueError(
                    f"Rule is missing required field: {field}"
                )

        valid_categories = [
            "Security",
            "Backup",
            "Monitoring",
            "Performance",
            "Operations"
        ]

        valid_severities = [
            "Critical",
            "High",
            "Medium",
            "Low"
        ]

        if rule["category"] not in valid_categories:
            raise ValueError(
                f"Invalid category: {rule['category']}"
            )

        if rule["severity"] not in valid_severities:
            raise ValueError(
                f"Invalid severity: {rule['severity']}"
            )

        if not rule["name"].strip():
            raise ValueError("Rule name cannot be empty")

    def get_active_rules(self):
        return [
            rule for rule in self.rules
            if rule.get("active", True)
        ]

    def get_rule(self, rule_id):
        for rule in self.rules:
            if rule["id"] == rule_id:
                return rule

        return None

    def enable_rule(self, rule_id):
        rule = self.get_rule(rule_id)

        if rule is None:
            return False

        rule["active"] = True
        return True

    def disable_rule(self, rule_id):
        rule = self.get_rule(rule_id)

        if rule is None:
            return False

        rule["active"] = False
        return True
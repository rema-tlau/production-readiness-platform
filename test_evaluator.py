from scanner import ProjectScanner
from rules import RuleManager
from evaluator import RuleEvaluator


# ==========================================
# 1. SCAN PROJECT
# ==========================================

project_path = "."

scanner = ProjectScanner(project_path)

files = scanner.scan_project()

print("=" * 60)
print("PROJECT SCAN")
print("=" * 60)

print("Project:", scanner.project_path)
print("Files scanned:", len(files))


# ==========================================
# 2. LOAD RULES
# ==========================================

rule_manager = RuleManager(
    "rules/default_rules.yaml"
)

rules = rule_manager.load_rules()

active_rules = rule_manager.get_active_rules()

print("\n" + "=" * 60)
print("RULES")
print("=" * 60)

print("Total rules:", len(rules))
print("Active rules:", len(active_rules))


# ==========================================
# 3. EVALUATE RULES
# ==========================================

evaluator = RuleEvaluator(
    files,
    active_rules
)

findings = evaluator.evaluate()


# ==========================================
# 4. DISPLAY RESULTS
# ==========================================

print("\n" + "=" * 60)
print("ASSESSMENT RESULTS")
print("=" * 60)

print("Rules evaluated:", len(active_rules))
print("Findings:", len(findings))

print("\n")


for finding in findings:

    print(
        f"[{finding['severity']}] "
        f"{finding['rule_id']} - "
        f"{finding['name']}"
    )

    print(
        "Message:",
        finding["message"]
    )

    print(
        "Remediation:",
        finding["remediation"]
    )

    if finding["file_path"]:
        print(
            "File:",
            finding["file_path"]
        )

    if finding["line_number"]:
        print(
            "Line:",
            finding["line_number"]
        )

    print("-" * 60)
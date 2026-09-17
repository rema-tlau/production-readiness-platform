from rules import RuleManager


rule_manager = RuleManager("rules/default_rules.yaml")

rules = rule_manager.load_rules()

print("Total rules:", len(rules))
print("Active rules:", len(rule_manager.get_active_rules()))

for rule in rule_manager.get_active_rules():
    print(
        rule["id"],
        "-",
        rule["name"],
        "-",
        rule["category"],
        "-",
        rule["severity"]
    )
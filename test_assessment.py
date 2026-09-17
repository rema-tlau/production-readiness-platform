from assessment import AssessmentEngine


engine = AssessmentEngine(".")


result = engine.run()


print("=" * 60)
print("PRODUCTION READINESS ASSESSMENT")
print("=" * 60)

print()

print("Assessment ID:")
print(result["assessment_id"])

print()

print("Project:")
print(result["project_name"])

print()

print("Score:")
print(f'{result["score"]}/100')

print()

print("Status:")
print(result["status"])

print()

print("Total Rules:")
print(result["total_rules"])

print()

print("Passed:")
print(result["passed_rules"])

print()

print("Failed:")
print(result["failed_rules"])

print()

print("Duration:")
print(
    f'{result["duration_seconds"]} seconds'
)

print()

print("=" * 60)
print("FINDINGS")
print("=" * 60)

for finding in result["findings"]:

    print()

    print(
        f'[{finding["severity"]}] '
        f'{finding["rule_id"]} - '
        f'{finding["name"]}'
    )

    print(
        "Message:",
        finding["message"]
    )

    print(
        "Remediation:",
        finding["remediation"]
    )
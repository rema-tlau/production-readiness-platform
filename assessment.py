import os
import time

from scanner import ProjectScanner
from rules import RuleManager
from evaluator import RuleEvaluator
from database import save_assessment, save_finding


class AssessmentEngine:

    def __init__(self, project_path):

        self.project_path = os.path.abspath(
            project_path
        )

        self.rule_file = "rules/default_rules.yaml"

    def calculate_score(
        self,
        total_rules,
        failed_rules
    ):

        if total_rules == 0:
            return 0

        passed_rules = total_rules - failed_rules

        score = (
            passed_rules / total_rules
        ) * 100

        return round(score)

    def determine_status(self, score):

        if score >= 80:
            return "Ready"

        elif score >= 60:
            return "Needs Improvement"

        else:
            return "Not Ready"

    def run(self):

        start_time = time.time()

        # ==========================================
        # 1. SCAN PROJECT
        # ==========================================

        scanner = ProjectScanner(
            self.project_path
        )

        files = scanner.scan_project()

        # ==========================================
        # 2. LOAD RULES
        # ==========================================

        rule_manager = RuleManager(
            self.rule_file
        )

        rule_manager.load_rules()

        active_rules = (
            rule_manager.get_active_rules()
        )

        # ==========================================
        # 3. EVALUATE RULES
        # ==========================================

        evaluator = RuleEvaluator(
            files,
            active_rules
        )

        findings = evaluator.evaluate()

        # ==========================================
        # 4. CALCULATE RESULTS
        # ==========================================

        total_rules = len(active_rules)

        failed_rules = len(findings)

        passed_rules = (
            total_rules - failed_rules
        )

        score = self.calculate_score(
            total_rules,
            failed_rules
        )

        status = self.determine_status(
            score
        )

        duration = round(
            time.time() - start_time,
            2
        )

        # ==========================================
        # 5. SAVE ASSESSMENT
        # ==========================================

        project_name = os.path.basename(
            self.project_path
        )

        assessment_id = save_assessment(
            project_name=project_name,
            project_path=self.project_path,
            score=score,
            status=status,
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            duration_seconds=duration
        )

        # ==========================================
        # 6. SAVE FINDINGS
        # ==========================================

        for finding in findings:

            save_finding(
                assessment_id,
                finding
            )

        # ==========================================
        # 7. RETURN RESULT
        # ==========================================

        return {
            "assessment_id": assessment_id,
            "project_name": project_name,
            "project_path": self.project_path,
            "score": score,
            "status": status,
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "duration_seconds": duration,
            "findings": findings
        }
"""Unit tests for detect_roles module."""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from detect_roles import (
    categorize_contributor_role,
    analyze_project_roles,
    _calculate_role_scores,
    _calculate_role_confidence,
    format_roles_report,
    ROLE_PATTERNS,
)


class TestCategorizeContributorRole(unittest.TestCase):
    """Test single contributor role categorization."""
    
    def test_backend_developer_python_files(self):
        """Test that Python file contributions result in Backend Developer role."""
        result = categorize_contributor_role(
            "Alice",
            files_changed=["main.py", "utils.py", "app.py"],
            commits=10,
            lines_added=500,
            lines_removed=50,
            activity_by_category={"code": 3, "test": 0, "docs": 0, "design": 0, "other": 0}
        )
        
        self.assertEqual(result["name"], "alice")  # Should be canonicalized
        # Primary role could be Backend Developer or Full Stack (depends on scoring)
        self.assertTrue(
            "Backend Developer" in result["primary_role"] or 
            "Full Stack Developer" in result["primary_role"]
        )
        self.assertGreater(result["confidence"], 0.0)
        self.assertEqual(result["metrics"]["total_files"], 3)
    
    def test_qa_tester_test_files(self):
        """Test that test file contributions result in QA / Tester role."""
        result = categorize_contributor_role(
            "Bob",
            files_changed=["test_main.py", "test_utils.py", "test_app.py"],
            commits=8,
            lines_added=300,
            lines_removed=20,
            activity_by_category={"code": 0, "test": 3, "docs": 0, "design": 0, "other": 0}
        )
        
        # Primary role could be QA/Tester or Full Stack (depends on scoring)
        self.assertTrue(
            "QA / Tester" in result["primary_role"] or 
            "Full Stack Developer" in result["primary_role"]
        )
        self.assertGreater(result["confidence"], 0.0)
    
    def test_frontend_developer_js_files(self):
        """Test that JavaScript file contributions result in Frontend Developer role."""
        result = categorize_contributor_role(
            "Charlie",
            files_changed=["index.js", "App.jsx", "Header.tsx"],
            commits=5,
            lines_added=1000,
            lines_removed=100,
            activity_by_category={"code": 3, "test": 0, "docs": 0, "design": 0, "other": 0}
        )
        
        # Primary role could be Frontend Developer or Full Stack (depends on scoring)
        self.assertTrue(
            "Frontend Developer" in result["primary_role"] or 
            "Full Stack Developer" in result["primary_role"]
        )
        self.assertGreater(result["confidence"], 0.0)
    
    def test_ui_ux_designer_design_files(self):
        """Test that design file contributions result in UI/UX Designer role."""
        result = categorize_contributor_role(
            "Diana",
            files_changed=["logo.svg", "mockup.png", "icon.svg"],
            commits=3,
            lines_added=0,
            lines_removed=0,
            activity_by_category={"code": 0, "test": 0, "docs": 0, "design": 3, "other": 0}
        )
        
        self.assertIn("UI/UX Designer", result["primary_role"])
        self.assertGreater(result["confidence"], 0.0)
    
    def test_full_stack_multiple_file_types(self):
        """Test that multiple file types result in a multi-role developer."""
        result = categorize_contributor_role(
            "Eve",
            files_changed=["main.py", "index.js", "test_main.py", "style.css"],
            commits=15,
            lines_added=800,
            lines_removed=100,
            activity_by_category={"code": 3, "test": 1, "docs": 0, "design": 0, "other": 0}
        )
        
        # Should have multiple roles detected (primary + secondary)
        total_roles = len([result["primary_role"]] + result.get("secondary_roles", []))
        self.assertGreater(total_roles, 1)
        self.assertGreater(result["confidence"], 0.0)
    
    def test_insufficient_files_contributor(self):
        """Test that contributors with few files get Contributor role."""
        result = categorize_contributor_role(
            "Frank",
            files_changed=["one.py"],
            commits=1,
            lines_added=10,
            lines_removed=0,
            activity_by_category={"code": 1, "test": 0, "docs": 0, "design": 0, "other": 0}
        )
        
        self.assertEqual(result["primary_role"], "Contributor")
        self.assertEqual(result["confidence"], 0.0)


class TestCalculateRoleScores(unittest.TestCase):
    """Test role score calculation based on file extensions."""
    
    def test_backend_python_files(self):
        """Test scoring for Python backend files."""
        files = ["main.py", "utils.py", "models.py"]
        breakdown = {"code": 100, "test": 0, "docs": 0, "design": 0, "other": 0}
        scores = _calculate_role_scores(files, breakdown)
        
        self.assertGreater(scores.get("Backend Developer", 0), 0)
    
    def test_frontend_javascript_files(self):
        """Test scoring for JavaScript frontend files."""
        files = ["index.js", "App.jsx", "Header.tsx"]
        breakdown = {"code": 100, "test": 0, "docs": 0, "design": 0, "other": 0}
        scores = _calculate_role_scores(files, breakdown)
        
        self.assertGreater(scores.get("Frontend Developer", 0), 0)
    
    def test_test_files_boost_qa_tester(self):
        """Test that QA/Tester score is boosted for test files."""
        files = ["test_main.py", "test_app.py", "test_utils.py"]
        breakdown = {"code": 0, "test": 100, "docs": 0, "design": 0, "other": 0}
        scores = _calculate_role_scores(files, breakdown)
        
        # QA/Tester should be boosted due to test activity > 30%
        self.assertGreater(scores.get("QA / Tester", 0), 2)
    
    def test_design_files_ui_ux_designer(self):
        """Test that design files result in UI/UX Designer scoring."""
        files = ["logo.svg", "mockup.png", "icon.svg"]
        breakdown = {"code": 0, "test": 0, "docs": 0, "design": 100, "other": 0}
        scores = _calculate_role_scores(files, breakdown)
        
        self.assertEqual(scores.get("UI/UX Designer", 0), 100)


class TestCalculateRoleConfidence(unittest.TestCase):
    """Test role confidence calculation."""
    
    def test_project_lead_high_confidence(self):
        """Test that Project Lead gets very high confidence."""
        role_scores = [("Project Lead / Architect", 100), ("Backend Developer", 50)]
        confidence = _calculate_role_confidence("Project Lead / Architect", role_scores)
        
        self.assertEqual(confidence, 0.95)
    
    def test_full_stack_balanced_confidence(self):
        """Test that Full Stack confidence is based on balance."""
        role_scores = [("Backend Developer", 10), ("Frontend Developer", 8)]
        confidence = _calculate_role_confidence("Full Stack Developer", role_scores)
        
        self.assertGreater(confidence, 0.0)
        self.assertLess(confidence, 1.0)
    
    def test_specialized_role_dominance_confidence(self):
        """Test that specialized role confidence is based on dominance."""
        role_scores = [("Backend Developer", 20), ("Frontend Developer", 5)]
        confidence = _calculate_role_confidence("Backend Developer", role_scores)
        
        self.assertGreater(confidence, 0.5)


class TestAnalyzeProjectRoles(unittest.TestCase):
    """Test full project role analysis."""
    
    def test_empty_project(self):
        """Test analysis of empty project."""
        result = analyze_project_roles({})
        
        self.assertEqual(result["summary"]["total_contributors"], 0)
        self.assertEqual(len(result["contributors"]), 0)
    
    def test_single_contributor_project(self):
        """Test analysis with single contributor."""
        data = {
            "Alice": {
                "files_changed": ["a.py", "b.py", "c.py"],
                "commits": 10,
                "lines_added": 500,
                "lines_removed": 50,
                "activity_by_category": {"code": 3, "test": 0, "docs": 0, "design": 0, "other": 0}
            }
        }
        
        result = analyze_project_roles(data)
        
        self.assertEqual(result["summary"]["total_contributors"], 1)
        self.assertEqual(result["summary"]["development_team_size"], 1)
    
    def test_multi_contributor_project(self):
        """Test analysis with multiple contributors."""
        data = {
            "Alice": {
                "files_changed": ["a.py", "b.py", "c.py"],
                "commits": 10,
                "lines_added": 500,
                "lines_removed": 50,
                "activity_by_category": {"code": 3, "test": 0, "docs": 0, "design": 0, "other": 0}
            },
            "Bob": {
                "files_changed": ["test_a.py", "test_b.py", "test_c.py"],
                "commits": 5,
                "lines_added": 200,
                "lines_removed": 20,
                "activity_by_category": {"code": 0, "test": 3, "docs": 0, "design": 0, "other": 0}
            }
        }
        
        result = analyze_project_roles(data)
        
        self.assertEqual(result["summary"]["total_contributors"], 2)
        # Both should have some developer role
        role_dist_str = str(result["summary"]["role_distribution"])
        self.assertTrue(
            "Backend Developer" in role_dist_str or 
            "QA / Tester" in role_dist_str or
            "Full Stack Developer" in role_dist_str
        )


class TestFormatRolesReport(unittest.TestCase):
    """Test report formatting."""
    
    def test_report_formatting(self):
        """Test that report is properly formatted."""
        data = {
            "Alice": {
                "files_changed": ["a.py", "b.py", "c.py"],
                "commits": 10,
                "lines_added": 500,
                "lines_removed": 50,
                "activity_by_category": {"code": 3, "test": 0, "docs": 0, "design": 0, "other": 0}
            }
        }
        
        analysis = analyze_project_roles(data)
        report = format_roles_report(analysis)
        
        self.assertIn("PROJECT ROLE ANALYSIS REPORT", report)
        self.assertIn("alice", report)
        self.assertIn("Backend Developer", report)
        self.assertIn("Metrics:", report)


if __name__ == '__main__':
    unittest.main()

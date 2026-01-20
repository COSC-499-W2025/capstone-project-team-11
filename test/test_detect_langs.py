import os
import sys
import tempfile
import unittest

import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from detect_langs import (
    detect_languages_and_frameworks,
    scan_file_content,
    calculate_confidence,
    should_scan_file,
    strip_comments,
    get_extension,
    IGNORED_DIRECTORIES,
)

# Unit tests for detect_langs.py language and framework detection features
class TestDetectLangs(unittest.TestCase):

    # ===================================
    # LANGUAGE DETECTION TESTING
    # ===================================

    # Should detect HTML and CSS files in a web project
    def test_detects_html_and_css(self):
        with tempfile.TemporaryDirectory() as td:
            html = os.path.join(td, "index.html")
            css = os.path.join(td, "style.css")
            # Create minimal HTML and CSS files
            with open(html, "w") as f:
                f.write("<!DOCTYPE html><html><head></head><body></body></html>")
            with open(css, "w") as f:
                f.write("body { color: red; }")

            results = detect_languages_and_frameworks(td)
            # Both HTML and CSS should show up as detected languages
            self.assertIn("HTML", results["languages"])
            self.assertIn("CSS", results["languages"])

    # Should return empty lists when no recognizable files exist
    def test_empty_folder_returns_none(self):
        with tempfile.TemporaryDirectory() as td:
            results = detect_languages_and_frameworks(td)
            # Expect no languages or frameworks found
            self.assertEqual(results["languages"], [])
            self.assertEqual(results["frameworks"], [])

    # Should detect Python patterns in a Python file
    def test_scan_file_content_detects_patterns(self):
        with tempfile.TemporaryDirectory() as td:
            py_file = os.path.join(td, "test.py")
            with open(py_file, "w") as f:
                f.write("def hello():\n    import os\n    class MyClass:\n        pass")

            pattern_matches = scan_file_content(py_file)
            self.assertIn("Python", pattern_matches)
            self.assertGreater(pattern_matches["Python"], 0)

    # Should calculate correct confidence levels based on presence of syntax patterns and file extensions:
    # High:     Coding file extension, with 10+ pattern matches
    # Medium:   Coding file extension, with < 10 pattern matches 
    #           OR No coding file extension, with 10+ pattern matches
    # Low:      No coding file extension and 1-9 pattern matches
    def test_calculate_confidence_logic(self):
        # High confidence: coding file extension, match with 10+ pattern matches
        self.assertEqual(calculate_confidence(10, True), "high")
        self.assertEqual(calculate_confidence(15, True), "high")
        # Medium confidence: coding file extension, with < 10 pattern matches
        self.assertEqual(calculate_confidence(9, True), "medium")
        self.assertEqual(calculate_confidence(5, True), "medium")
        self.assertEqual(calculate_confidence(0, True), "medium")
        # Medium confidence: no coding file extension, with 10+ pattern matches
        self.assertEqual(calculate_confidence(10, False), "medium")
        self.assertEqual(calculate_confidence(15, False), "medium")
        # Low confidence: no coding file extension, with 1-9 pattern matches
        self.assertEqual(calculate_confidence(9, False), "low")
        self.assertEqual(calculate_confidence(1, False), "low")

    # Should include confidence levels in detection results
    def test_language_details_includes_confidence(self):
        with tempfile.TemporaryDirectory() as td:
            py_file = os.path.join(td, "app.py")
            with open(py_file, "w") as f:
                # Write a Python file with 10+ detectable patterns
                f.write("""
                def main():
                    import sys
                    import os
                    from collections import defaultdict
                    class App:
                        pass
                    class Helper:
                        pass
                def func1():
                    pass
                def func2():
                    pass
                def func3():
                    pass
                """)

            results = detect_languages_and_frameworks(td)
            # Should have language_details with confidence
            self.assertIn("language_details", results)
            self.assertIn("Python", results["language_details"])
            self.assertIn("confidence", results["language_details"]["Python"])
            # Python with coding file extension, with 10+ patterns should have high confidence
            self.assertEqual(results["language_details"]["Python"]["confidence"], "high")

    # A file with recognized extension but no/few patterns should have medium confidence
    def test_extension_only_detection_medium_confidence(self):
        with tempfile.TemporaryDirectory() as td:
            # Create an almost-empty Python file (just whitespace)
            py_file = os.path.join(td, "empty.py")
            with open(py_file, "w") as f:
                f.write("# just a comment\n")

            results = detect_languages_and_frameworks(td)
            self.assertIn("Python", results["languages"])
            # With extension but no patterns, should be medium confidence
            self.assertEqual(results["language_details"]["Python"]["confidence"], "medium")

    # Edge case: no patterns and no extension should be low confidence
    def test_calculate_confidence_zero_patterns_no_extension(self):
        self.assertEqual(calculate_confidence(0, False), "low")

    # Code files should return (True, True)
    def test_should_scan_file_code_extensions(self):
        self.assertEqual(should_scan_file("test.py"), (True, True))
        self.assertEqual(should_scan_file("test.js"), (True, True))
        self.assertEqual(should_scan_file("test.java"), (True, True))
        self.assertEqual(should_scan_file("test.ts"), (True, True))

    # Text files should return (True, False) - scannable but not code files
    def test_should_scan_file_text_extensions(self):
        self.assertEqual(should_scan_file("README.md"), (True, False))
        self.assertEqual(should_scan_file("notes.txt"), (True, False))
        self.assertEqual(should_scan_file("changelog.log"), (True, False))

    # Unknown extensions should return (False, False)
    def test_should_scan_file_unknown_extensions(self):
        self.assertEqual(should_scan_file("image.png"), (False, False))
        self.assertEqual(should_scan_file("document.pdf"), (False, False))
        self.assertEqual(should_scan_file("archive.zip"), (False, False))

    # get_extension should return lowercase extensions
    def test_get_extension_normalizes_case(self):
        self.assertEqual(get_extension("Test.PY"), ".py")
        self.assertEqual(get_extension("FILE.JS"), ".js")
        self.assertEqual(get_extension("readme.MD"), ".md")

    # Python single-line comments should be removed
    def test_strip_comments_python_single_line(self):
        content = "x = 1  # this is a comment\ny = 2"
        result = strip_comments(content, ".py")
        self.assertNotIn("this is a comment", result)
        self.assertIn("x = 1", result)
        self.assertIn("y = 2", result)

    # Python multi-line docstrings should be removed
    def test_strip_comments_python_multiline(self):
        content = '"""This is a docstring"""\ndef foo(): pass'
        result = strip_comments(content, ".py")
        self.assertNotIn("This is a docstring", result)
        self.assertIn("def foo(): pass", result)

    # JavaScript single and multi-line comments should be removed
    def test_strip_comments_javascript(self):
        content = "const x = 1; // single line\n/* multi\nline */ const y = 2;"
        result = strip_comments(content, ".js")
        self.assertNotIn("single line", result)
        self.assertNotIn("multi", result)
        self.assertIn("const x = 1;", result)
        self.assertIn("const y = 2;", result)

    # Actual code should not be affected by comment stripping
    def test_strip_comments_preserves_code(self):
        content = "def hello():\n    print('world')"
        result = strip_comments(content, ".py")
        self.assertIn("def hello():", result)
        self.assertIn("print('world')", result)

    # Unknown extensions should return content unchanged
    def test_strip_comments_unknown_extension(self):
        content = "# this might look like a comment"
        result = strip_comments(content, ".xyz")
        self.assertEqual(result, content)
    
    # Files in node_modules, .git, etc. should not be scanned
    def test_ignored_directories_are_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            # Create a node_modules directory with a JS file
            node_modules = os.path.join(td, "node_modules")
            os.makedirs(node_modules)
            js_in_node = os.path.join(node_modules, "library.js")
            with open(js_in_node, "w") as f:
                f.write("const express = require('express');")

            # Create a .git directory with some content
            git_dir = os.path.join(td, ".git")
            os.makedirs(git_dir)
            git_file = os.path.join(git_dir, "config")
            with open(git_file, "w") as f:
                f.write("# git config")

            # No actual source files in root - should detect nothing
            results = detect_languages_and_frameworks(td)
            self.assertEqual(results["languages"], [])

    # Verify that common ignored directories are in the set
    def test_ignored_directories_list_contains_expected(self):
        self.assertIn("node_modules", IGNORED_DIRECTORIES)
        self.assertIn(".git", IGNORED_DIRECTORIES)
        self.assertIn("venv", IGNORED_DIRECTORIES)
        self.assertIn("__pycache__", IGNORED_DIRECTORIES)
        self.assertIn("dist", IGNORED_DIRECTORIES)

    # ===================================
    # FRAMEWORK DETECTION TESTING
    # ===================================

    # Should detect Flask from requirements.txt
    def test_detects_flask_from_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            req_file = os.path.join(td, "requirements.txt")
            with open(req_file, "w") as f:
                f.write("flask==2.0.1\nrequests==2.28.0")

            results = detect_languages_and_frameworks(td)
            self.assertIn("Flask", results["frameworks"])

    # Should detect Django from requirements.txt
    def test_detects_django_from_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            req_file = os.path.join(td, "requirements.txt")
            with open(req_file, "w") as f:
                f.write("Django==4.2.0\npsycopg2==2.9.5")

            results = detect_languages_and_frameworks(td)
            self.assertIn("Django", results["frameworks"])

    # Should detect FastAPI from requirements.txt
    def test_detects_fastapi_from_requirements(self):
        with tempfile.TemporaryDirectory() as td:
            req_file = os.path.join(td, "requirements.txt")
            with open(req_file, "w") as f:
                f.write("fastapi==0.95.0\nuvicorn==0.21.1")

            results = detect_languages_and_frameworks(td)
            self.assertIn("FastAPI", results["frameworks"])

    # Should detect React from package.json
    def test_detects_react_from_package_json(self):
        with tempfile.TemporaryDirectory() as td:
            pkg_file = os.path.join(td, "package.json")
            with open(pkg_file, "w") as f:
                f.write('{"dependencies": {"react": "18.2.0", "react-dom": "18.2.0"}}')

            results = detect_languages_and_frameworks(td)
            self.assertIn("React", results["frameworks"])

    # Should detect Express from package.json
    def test_detects_express_from_package_json(self):
        with tempfile.TemporaryDirectory() as td:
            pkg_file = os.path.join(td, "package.json")
            with open(pkg_file, "w") as f:
                f.write('{"dependencies": {"express": "4.18.2"}}')

            results = detect_languages_and_frameworks(td)
            self.assertIn("Express", results["frameworks"])

    # Should detect Next.js from package.json
    def test_detects_nextjs_from_package_json(self):
        with tempfile.TemporaryDirectory() as td:
            pkg_file = os.path.join(td, "package.json")
            with open(pkg_file, "w") as f:
                f.write('{"dependencies": {"next": "13.4.0", "next.js": "1.0.0"}}')

            results = detect_languages_and_frameworks(td)
            self.assertIn("Next.js", results["frameworks"])

    # Should detect Vue from package.json
    def test_detects_vue_from_package_json(self):
        with tempfile.TemporaryDirectory() as td:
            pkg_file = os.path.join(td, "package.json")
            with open(pkg_file, "w") as f:
                f.write('{"dependencies": {"vue": "3.3.4"}}')

            results = detect_languages_and_frameworks(td)
            self.assertIn("Vue", results["frameworks"])

    # Should detect Angular from package.json
    def test_detects_angular_from_package_json(self):
        with tempfile.TemporaryDirectory() as td:
            pkg_file = os.path.join(td, "package.json")
            with open(pkg_file, "w") as f:
                f.write('{"dependencies": {"@angular/core": "16.0.0"}}')

            results = detect_languages_and_frameworks(td)
            self.assertIn("Angular", results["frameworks"])

    # Should detect Spring Boot from pom.xml
    def test_detects_spring_boot_from_pom_xml(self):
        with tempfile.TemporaryDirectory() as td:
            pom_file = os.path.join(td, "pom.xml")
            with open(pom_file, "w") as f:
                f.write('''<project>
                    <parent>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-parent</artifactId>
                    </parent>
                </project>''')

            results = detect_languages_and_frameworks(td)
            self.assertIn("Spring Boot", results["frameworks"])

    # Should detect multiple Python frameworks from requirements.txt
    def test_detects_multiple_python_frameworks(self):
        with tempfile.TemporaryDirectory() as td:
            req_file = os.path.join(td, "requirements.txt")
            with open(req_file, "w") as f:
                f.write("flask==2.0.1\ndjango==4.2.0\nfastapi==0.95.0")

            results = detect_languages_and_frameworks(td)
            self.assertIn("Flask", results["frameworks"])
            self.assertIn("Django", results["frameworks"])
            self.assertIn("FastAPI", results["frameworks"])

    # Should detect multiple JavaScript frameworks from package.json
    def test_detects_multiple_js_frameworks(self):
        with tempfile.TemporaryDirectory() as td:
            pkg_file = os.path.join(td, "package.json")
            with open(pkg_file, "w") as f:
                f.write('{"dependencies": {"react": "18.2.0", "express": "4.18.2", "vue": "3.3.4"}}')

            results = detect_languages_and_frameworks(td)
            self.assertIn("React", results["frameworks"])
            self.assertIn("Express", results["frameworks"])
            self.assertIn("Vue", results["frameworks"])

    # Should return empty frameworks list when no framework config files exist
    def test_no_frameworks_without_config_files(self):
        with tempfile.TemporaryDirectory() as td:
            # Create a Python file but no requirements.txt
            py_file = os.path.join(td, "app.py")
            with open(py_file, "w") as f:
                f.write("print('hello world')")

            results = detect_languages_and_frameworks(td)
            self.assertEqual(results["frameworks"], [])

    # Should be case-insensitive when detecting frameworks
    def test_framework_detection_case_insensitive(self):
        with tempfile.TemporaryDirectory() as td:
            req_file = os.path.join(td, "requirements.txt")
            with open(req_file, "w") as f:
                # Write FLASK in uppercase
                f.write("FLASK==2.0.1")

            results = detect_languages_and_frameworks(td)
            self.assertIn("Flask", results["frameworks"])

# Let the test run directly if this file is executed
if __name__ == "__main__":
    unittest.main()

import os
import sys
import tempfile
import unittest

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from detect_langs import detect_languages_and_frameworks, scan_file_content, calculate_confidence

# These check that language and framework detection works correctly
# for different types of simple example projects.
class TestDetectLangs(unittest.TestCase):
    #Unit tests for detect_langs.py language and framework detection.

    def test_detects_javascript_and_express(self):
        #Should detect JavaScript language and Express framework from package.json
        with tempfile.TemporaryDirectory() as td:
           # Make a small JS file to simulate a Node.js project
            js_file = os.path.join(td, "server.js")
            with open(js_file, "w") as f:
                f.write("// Express server example")
   # Add a package.json that includes Express
            pkg_file = os.path.join(td, "package.json")
            with open(pkg_file, "w") as f:
                f.write('{"dependencies": {"express": "4.18.2"}}')

            results = detect_languages_and_frameworks(td)
              # Expect both JavaScript and Express to be found
            self.assertIn("JavaScript", results["languages"])
            self.assertIn("Express", results["frameworks"])

    def test_detects_python_and_flask(self):
        #Should detect Python language and Flask framework from requirements.txt.
        with tempfile.TemporaryDirectory() as td:
            # Simple Python file using Flask
            py_file = os.path.join(td, "main.py")
            with open(py_file, "w") as f:
                f.write("from flask import Flask\napp = Flask(__name__)")
  # Add requirements.txt listing Flask
            req_file = os.path.join(td, "requirements.txt")
            with open(req_file, "w") as f:
                f.write("flask==2.0.1")

            results = detect_languages_and_frameworks(td)
             # Expect both Python and Flask to be detected
            self.assertIn("Python", results["languages"])
            self.assertIn("Flask", results["frameworks"])

    def test_detects_html_and_css(self):
        # Should detect HTML and CSS files in a web project.
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

    def test_empty_folder_returns_none(self):
        # Should return empty lists when no recognizable files exist.
        with tempfile.TemporaryDirectory() as td:
            results = detect_languages_and_frameworks(td)
               # Expect no languages or frameworks found
            self.assertEqual(results["languages"], [])
            self.assertEqual(results["frameworks"], [])

    def test_detects_multiple_frameworks(self):
        # Should detect multiple frameworks from a package.json.
        with tempfile.TemporaryDirectory() as td:
               # Add a package.json with multiple frameworks
            pkg_file = os.path.join(td, "package.json")
            with open(pkg_file, "w") as f:
                f.write('{"dependencies": {"react": "18.2.0", "vue": "3.0.0", "express": "4.18.2"}}')

            results = detect_languages_and_frameworks(td)
              # All three frameworks should be found
            self.assertIn("React", results["frameworks"])
            self.assertIn("Vue", results["frameworks"])
            self.assertIn("Express", results["frameworks"])

    # Should detect Python patterns in a Python file
    def test_scan_file_content_detects_patterns(self):
        with tempfile.TemporaryDirectory() as td:
            py_file = os.path.join(td, "test.py")
            with open(py_file, "w") as f:
                f.write("def hello():\n    import os\n    class MyClass:\n        pass")

            pattern_matches = scan_file_content(py_file)
            self.assertIn("Python", pattern_matches)
            self.assertGreater(pattern_matches["Python"], 0)

    # Should calculate correct confidence levels based on presence of syntax patterns and file extensions
    def test_calculate_confidence_logic(self):
        # High confidence: 5+ patterns
        self.assertEqual(calculate_confidence(5, False), "high")
        # High confidence: extension + 2+ patterns
        self.assertEqual(calculate_confidence(2, True), "high")
        # Medium confidence: 3-4 patterns
        self.assertEqual(calculate_confidence(3, False), "medium")
        # Medium confidence: extension + 1 pattern
        self.assertEqual(calculate_confidence(1, True), "medium")
        # Low confidence: 1-2 patterns only
        self.assertEqual(calculate_confidence(1, False), "low")

    # Should include confidence levels in detection results
    def test_language_details_includes_confidence(self):
        with tempfile.TemporaryDirectory() as td:
            py_file = os.path.join(td, "app.py")
            with open(py_file, "w") as f:
                f.write("def main():\n    import sys\n    class App:\n        pass")

            results = detect_languages_and_frameworks(td)
            # Should have language_details with confidence
            self.assertIn("language_details", results)
            self.assertIn("Python", results["language_details"])
            self.assertIn("confidence", results["language_details"]["Python"])
            # Python with extension should have high confidence
            self.assertEqual(results["language_details"]["Python"]["confidence"], "high")

# Let the test run directly if this file is executed
if __name__ == "__main__":
    unittest.main()

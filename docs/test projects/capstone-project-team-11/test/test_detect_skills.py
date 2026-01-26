import os
import sys
import tempfile
import unittest

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from detect_skills import detect_skills, detect_skills_in_file

# Unit tests for detect_skills.py skill detection
class TestDetectSkills(unittest.TestCase):
    # Should detect recursion and OOP patterns in a Python file
    def test_detects_recursion_and_oop(self):
        with tempfile.TemporaryDirectory() as td:
            py_file = os.path.join(td, "recursion_example.py")
            with open(py_file, "w") as f:
                f.write("""
class Example:
    def factorial(self, n):
        if n == 1:
            return 1
        else:
            return n * self.factorial(n-1)
""")
            results = detect_skills_in_file(py_file)
            self.assertIn("Object-Oriented Programming", results)
            self.assertIn("Recursion", results)

    # Should detect web development skill based on Flask or React
    def test_detects_web_development(self):
        with tempfile.TemporaryDirectory() as td:
            web_file = os.path.join(td, "webapp.py")
            with open(web_file, "w") as f:
                f.write("from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef home(): return 'Hello'")
            results = detect_skills_in_file(web_file)
            self.assertIn("Web Development", results)

    # Should detect writing and communication-based skills
    def test_detects_formal_and_technical_writing(self):
        with tempfile.TemporaryDirectory() as td:
            txt_file = os.path.join(td, "essay.txt")
            with open(txt_file, "w") as f:
                f.write("Therefore, the data collected supports the experiment results. Furthermore, the methodology was sound.")
            results = detect_skills_in_file(txt_file)
            self.assertIn("Formal Writing", results)
            self.assertIn("Technical Writing", results)

    # Should return empty when no patterns are detected
    def test_empty_file_returns_no_skills(self):
        with tempfile.TemporaryDirectory() as td:
            empty_file = os.path.join(td, "empty.txt")
            with open(empty_file, "w") as f:
                f.write("")
            results = detect_skills_in_file(empty_file)
            self.assertEqual(results, [])

    # Should detect multiple skills when scanning an entire folder
    def test_detects_multiple_skills_in_directory(self):
        with tempfile.TemporaryDirectory() as td:
            # Create one coding file and one writing file
            code = os.path.join(td, "script.py")
            essay = os.path.join(td, "report.txt")
            with open(code, "w") as f:
                f.write("def factorial(n): return 1 if n==0 else n*factorial(n-1)")
            with open(essay, "w") as f:
                f.write("Therefore, the results indicate success.")
            results = detect_skills(td)
            self.assertIn("Recursion", results["skills"])
            self.assertIn("Formal Writing", results["skills"])

# Run tests directly
if __name__ == "__main__":
    unittest.main()

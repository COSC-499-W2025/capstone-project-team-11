import os
import re

# =============================================================================
# FILTERING CONFIGURATION
# =============================================================================

# Directories to always skip during scanning (dependencies, build artifacts, version control)
# Although this list is not comprehensive, it covers many common cases to improve performance and reduce false positives
IGNORED_DIRECTORIES = {
    # Version control
    ".git",
    ".svn",
    ".hg",
    # Package managers / dependencies
    "node_modules",
    "vendor",
    "packages",
    "bower_components",
    # Python virtual environments
    "venv",
    ".venv",
    "env",
    ".env",
    "virtualenv",
    "__pycache__",
    ".pytest_cache",
    ".tox",
    ".mypy_cache",
    # Build outputs
    "dist",
    "build",
    "out",
    "target",
    "bin",
    "obj",
    # IDE / editor folders
    ".idea",
    ".vscode",
    ".vs",
}

# =============================================================================
# LANGUAGE DETECTION CONFIGURATION
# =============================================================================

# One comprehensive mapping of file extensions to language names and comment syntax
LANGUAGE_CONFIG = {
    # Python
    ".py": {
        "name": "Python",
        "comments": {"single": ["#"], "multi": [('"""', '"""'), ("'''", "'''")]},
    },
    # JavaScript/TypeScript
    ".js": {
        "name": "JavaScript",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    ".jsx": {
        "name": "React (JavaScript)",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    ".ts": {
        "name": "TypeScript",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    ".tsx": {
        "name": "React (TypeScript)",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    # C-Family
    ".c": {
        "name": "C",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    ".cpp": {
        "name": "C++",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    ".h": {
        "name": None,  
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    ".hpp": {
        "name": None, 
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    ".cs": {
        "name": "C#",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    # Java
    ".java": {
        "name": "Java",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    # Kotlin
    ".kt": {
        "name": "Kotlin",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    # Swift
    ".swift": {
        "name": "Swift",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    # Go
    ".go": {
        "name": "Go",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    # Rust
    ".rs": {
        "name": "Rust",
        "comments": {"single": ["//"], "multi": [("/*", "*/")]},
    },
    # PHP
    ".php": {
        "name": "PHP",
        "comments": {"single": ["//", "#"], "multi": [("/*", "*/")]},
    },
    # Ruby
    ".rb": {
        "name": "Ruby",
        "comments": {"single": ["#"], "multi": [("=begin", "=end")]},
    },
    # Shell scripts
    ".sh": {
        "name": "Shell Script",
        "comments": {"single": ["#"], "multi": []},
    },
    ".bash": {
        "name": None,  
        "comments": {"single": ["#"], "multi": []},
    },
    # SQL
    ".sql": {
        "name": "SQL",
        "comments": {"single": ["--"], "multi": [("/*", "*/")]},
    },
    # HTML
    ".html": {
        "name": "HTML",
        "comments": {"single": [], "multi": [("<!--", "-->")]},
    },
    ".htm": {
        "name": "HTML",
        "comments": {"single": [], "multi": [("<!--", "-->")]},
    },
    # CSS
    ".css": {
        "name": "CSS",
        "comments": {"single": [], "multi": [("/*", "*/")]},
    },
    # Data formats
    ".json": {
        "name": "JSON (Web Config)",
        "comments": {"single": [], "multi": []},
    },
    ".xml": {
        "name": "XML",
        "comments": {"single": [], "multi": [("<!--", "-->")]},
    },
    ".yaml": {
        "name": None,
        "comments": {"single": ["#"], "multi": []},
    },
    ".yml": {
        "name": None,
        "comments": {"single": ["#"], "multi": []},
    },
}

# =============================================================================
# DERIVED SETS (from LANGUAGE_CONFIG)
# =============================================================================

# File extensions for actual source code files
# Languages detected in these files are considered "primary" detections
CODE_EXTENSIONS = set(LANGUAGE_CONFIG.keys())

# Mapping of file extensions to language names
LANGUAGE_MAP = {ext: cfg["name"] for ext, cfg in LANGUAGE_CONFIG.items() if cfg["name"]}

# Text-based extensions that may occasionally contain code snippets
# Languages detected ONLY in these files are flagged as "secondary" detections (possible false positives)
TEXT_EXTENSIONS = {
    ".txt",     # Plain text notes
    ".md",      # Markdown documentation
    ".rst",     # reStructuredText
    ".log",     # Log files
}

# Combined set of all scannable extensions
SCANNABLE_EXTENSIONS = CODE_EXTENSIONS | TEXT_EXTENSIONS

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Extract and normalize file extension from a filename
def get_extension(filename):
    return os.path.splitext(filename)[1].strip().lower()

# Check if a file should be scanned based on its extension
# Returns a tuple: (should_scan: bool, is_code_file: bool)
# - should_scan: True if the file extension is found within SCANNABLE_EXTENSIONS
# - is_code_file: True if the file extension is found within CODE_EXTENSIONS, False if in TEXT_EXTENSIONS
def should_scan_file(file_name):
    ext = get_extension(file_name)
    if ext in CODE_EXTENSIONS:
        return (True, True)
    if ext in TEXT_EXTENSIONS:
        return (True, False)
    return (False, False)

# Remove comments from file content based on the file's extension
# This helps reduce false positives during pattern matching
def strip_comments(content, file_extension):
    # Format the file extension to lowercase for consistent matching
    ext = file_extension.lower()

    # If we don't have comment syntax for this extension, don't attempt to strip comments
    if ext not in LANGUAGE_CONFIG:
        return content

    syntax = LANGUAGE_CONFIG[ext]["comments"]
    result = content

    # Remove multi-line comments
    for start, end in syntax.get("multi", []):
        # Escape special regex characters in delimiters
        start_escaped = re.escape(start)
        end_escaped = re.escape(end)
        # Use non-greedy matching to handle multiple comment blocks
        # re.DOTALL makes "." match newlines too
        pattern = f'{start_escaped}.*?{end_escaped}'
        result = re.sub(pattern, '', result, flags=re.DOTALL)

    # Remove single-line comments
    for prefix in syntax.get("single", []):
        # Escape special regex characters
        prefix_escaped = re.escape(prefix)
        # Match from comment prefix to end of line
        # Don't match URLs like "http://" (only match if prefix is at start or after whitespace)
        pattern = f'(^|\\s){prefix_escaped}[^\n]*'
        result = re.sub(pattern, r'\1', result, flags=re.MULTILINE)

    # Returns the file content as a String with its comments stripped out
    return result

# =============================================================================
# LANGUAGE DETECTION PATTERNS
# =============================================================================

# Regex patterns for detecting languages by file content (imported "re" at top of this file)
# Each pattern is designed to match distinctive syntax unique to that language
# NOTE: Some patterns may still produce false positives. Factor in confidence scoring to mitigate this
LANGUAGE_PATTERNS = {
    "Python": [
        r'\bdef\s+\w+\s*\(',                            # function definitions
        r'\bimport\s+\w+',                              # import statements
        r'\bfrom\s+\w+\s+import',                       # from...import statements
        r'\bclass\s+\w+.*:',                            # class definitions
        r'\bif\s+__name__\s*==\s*["\']__main__["\']',   # main guard
    ],
    "JavaScript": [
        r'\bfunction\s+\w+\s*\(',   # function declarations
        r'\bconst\s+\w+\s*=',       # const declarations
        r'\blet\s+\w+\s*=',         # let declarations
        r'\bvar\s+\w+\s*=',         # var declarations
        r'=>',                      # arrow functions
    ],
    "TypeScript": [
        r':\s*(string|number|boolean|any)\b',   # type annotations
        r'\binterface\s+\w+',                   # interface declarations
        r'\btype\s+\w+\s*=',                    # type aliases
        r'\benum\s+\w+',                        # enum declarations
    ],
    "Java": [
        r'\bpublic\s+class\s+\w+',                  # public class declarations
        r'\bprivate\s+(void|int|String|boolean)',   # private methods/fields
        r'\bSystem\.out\.print',                    # System.out usage
        r'\bpublic\s+static\s+void\s+main',         # main method
    ],
    "C++": [
        r'#include\s*<\w+>',    # include statements
        r'\bstd::',             # standard library namespace
        r'\bcout\s*<<',         # cout usage
        r'\bnamespace\s+\w+',   # namespace declarations
    ],
    "C": [
        r'#include\s*<\w+\.h>',         # C header includes (stdio.h, stdlib.h)
        r'\bprintf\s*\(',               # printf function
        r'\bmalloc\s*\(',               # malloc function
        r'\bstruct\s+\w+\s*\{',         # struct definitions
        r'\btypedef\s+struct',          # typedef struct
    ],
    "C#": [
        r'\busing\s+System',            # using System namespace
        r'\bnamespace\s+\w+',           # namespace declarations
        r'\bpublic\s+class\s+\w+',      # public class
        r'\bprivate\s+void\s+\w+',      # private methods
        r'Console\.WriteLine',          # Console.WriteLine
    ],
    "Ruby": [
        r'\bdef\s+\w+',                 # method definitions
        r'\bend\b',                     # end keyword (very common in Ruby)
        r'\brequire\s+["\']',           # require statements
        r'\bputs\s+',                   # puts for output
        r'@\w+\s*=',                    # instance variables
    ],
    "PHP": [
        r'<\?php',                      # PHP opening tag
        r'\$\w+\s*=',                   # PHP variables
        r'\bfunction\s+\w+\s*\(',       # function declarations
        r'\becho\s+',                   # echo statement
        r'->\w+',                       # object method calls
    ],
    "Go": [
        r'\bpackage\s+\w+',             # package declarations
        r'\bfunc\s+\w+\s*\(',           # function declarations
        r'\bimport\s+\(',               # import blocks
        r':=',                          # short variable declaration
        r'\bfmt\.Print',                # fmt.Print functions
    ],
    "Rust": [
        r'\bfn\s+\w+\s*\(',             # function declarations
        r'\blet\s+mut\s+\w+',           # mutable variable declarations
        r'\bimpl\s+\w+',                # impl blocks
        r'\bpub\s+fn\s+\w+',            # public functions
        r'println!\s*\(',               # println! macro
    ],
    "Swift": [
        r'\bfunc\s+\w+\s*\(',           # function declarations
        r'\bvar\s+\w+\s*:',             # variable with type annotation
        r'\blet\s+\w+\s*=',             # constant declarations
        r'\bimport\s+\w+',              # import statements
        r'\bclass\s+\w+\s*:\s*\w+',     # class with inheritance
    ],
    "Kotlin": [
        r'\bfun\s+\w+\s*\(',            # function declarations
        r'\bval\s+\w+\s*=',             # val (immutable) declarations
        r'\bvar\s+\w+\s*=',             # var (mutable) declarations
        r'\bdata\s+class\s+\w+',        # data classes
        r'\bprintln\s*\(',              # println function
    ],
    "SQL": [
        r'\bSELECT\s+.+\s+FROM\b',      # SELECT...FROM (full statement)
        r'\bINSERT\s+INTO\s+\w+',       # INSERT INTO
        r'\bCREATE\s+TABLE\s+\w+',      # CREATE TABLE
        r'\bUPDATE\s+\w+\s+SET\b',      # UPDATE...SET
        r'\bJOIN\s+\w+\s+ON\b',         # JOIN...ON
    ],
    "Shell Script": [
        r'^#!/bin/(ba)?sh',             # shebang line
        r'\bif\s+\[\[',                 # if [[ condition
        r'\bfor\s+\w+\s+in\b',          # for loops
        r'\becho\s+[\$"]',              # echo with variables or strings
        r'\bexport\s+\w+=',             # export variables
    ],
    "HTML": [
        r'<html\b',                     # <html tag
        r'<!DOCTYPE html>',             # DOCTYPE declaration
        r'<head>',                      # <head> tag
        r'<body\b',                     # <body> tag
        r'<div\s+class=',               # <div> with class
    ],
    "CSS": [
        r'\{\s*[\w-]+\s*:\s*.+;\s*\}',  # CSS rule blocks
        r'@media\s+',                   # media queries
        r'\.[\w-]+\s*\{',               # class selectors
        r'#[\w-]+\s*\{',                # id selectors
        r':\s*(hover|focus|active)\b',  # pseudo-classes
    ],
}

# =============================================================================
# FRAMEWORK DETECTION CONFIGURATION
# =============================================================================

# Comprehensive framework configuration that maps frameworks to their detection indicators
FRAMEWORK_CONFIG = {
    # Python Web Frameworks
    "Flask": {
        "language": "Python",
        "config_files": ["requirements.txt", "Pipfile", "pyproject.toml"],
        "package_names": ["flask"],
    },
    "Django": {
        "language": "Python",
        "config_files": ["requirements.txt", "Pipfile", "pyproject.toml"],
        "package_names": ["django"],
    },
    "FastAPI": {
        "language": "Python",
        "config_files": ["requirements.txt", "Pipfile", "pyproject.toml"],
        "package_names": ["fastapi"],
    },
    "Streamlit": {
        "language": "Python",
        "config_files": ["requirements.txt", "Pipfile", "pyproject.toml"],
        "package_names": ["streamlit"],
    },
    "pytest": {
        "language": "Python",
        "config_files": ["requirements.txt", "Pipfile", "pyproject.toml", "pytest.ini", "pyproject.toml"],
        "package_names": ["pytest"],
    },

    # JavaScript/TypeScript Frontend Frameworks
    "React": {
        "language": "JavaScript",
        "config_files": ["package.json"],
        "package_names": ["react"],
    },
    "Vue": {
        "language": "JavaScript",
        "config_files": ["package.json"],
        "package_names": ["vue"],
    },
    "Angular": {
        "language": "JavaScript",
        "config_files": ["package.json", "angular.json"],
        "package_names": ["@angular/core"],
    },

    # JavaScript/TypeScript Backend Frameworks
    "Express": {
        "language": "JavaScript",
        "config_files": ["package.json"],
        "package_names": ["express"],
    },
    "Next.js": {
        "language": "JavaScript",
        "config_files": ["package.json", "next.config.js"],
        "package_names": ["next"],
    },

    # CSS Frameworks
    "Tailwind CSS": {
        "language": "CSS",
        "config_files": ["package.json", "tailwind.config.js", "tailwind.config.ts"],
        "package_names": ["tailwindcss"],
    },
    "Bootstrap": {
        "language": "CSS",
        "config_files": ["package.json"],
        "package_names": ["bootstrap"],
    },

    # Java Frameworks
    "Spring Boot": {
        "language": "Java",
        "config_files": ["pom.xml", "build.gradle"],
        "package_names": ["spring-boot"],
    },
    "Hibernate": {
        "language": "Java",
        "config_files": ["pom.xml", "build.gradle"],
        "package_names": ["hibernate"],
    },

    # Ruby Frameworks
    "Rails": {
        "language": "Ruby",
        "config_files": ["Gemfile"],
        "package_names": ["rails"],
    },
    "Sinatra": {
        "language": "Ruby",
        "config_files": ["Gemfile"],
        "package_names": ["sinatra"],
    },

    # PHP Frameworks
    "Laravel": {
        "language": "PHP",
        "config_files": ["composer.json"],
        "package_names": ["laravel/framework"],
    },
    "Symfony": {
        "language": "PHP",
        "config_files": ["composer.json"],
        "package_names": ["symfony/symfony"],
    },
}

# =============================================================================
# FRAMEWORK DETECTION PATTERNS
# =============================================================================

# Regex patterns for detecting frameworks through scanned code content
FRAMEWORK_PATTERNS = {
    "Flask": [
        r'from flask import',               # Flask imports
        r'@app\.route\(',                   # Flask route decorators
        r'Flask\(__name__\)',               # Flask app initialization
    ],
    "Django": [
        r'from django',                     # Django imports
        r'django\.conf',                    # Django configuration
        r'models\.Model',                   # Django models
        r'django\.urls',                    # Django URLs
    ],
    "FastAPI": [
        r'from fastapi import',             # FastAPI imports
        r'FastAPI\(',                       # FastAPI app initialization
        r'@app\.(get|post|put|delete)\(',   # FastAPI route decorators
    ],
    "Streamlit": [
        r'import streamlit',                # Streamlit imports
        r'\bst\.',                          # Streamlit function calls (st.write, st.button, etc.)
    ],
    "pytest": [
        r'import pytest',                   # pytest imports
        r'@pytest\.',                       # pytest decorators
        r'\bdef test_\w+\(',                # test function naming convention
    ],
    "React": [
        r'import React',                    # React imports
        r'from ["\']react["\']',            # React imports
        r'useState\(',                      # React hooks
        r'useEffect\(',                     # React hooks
        r'<\w+\s*/?>',                      # JSX tags (basic)
    ],
    "Vue": [
        r'import.*from ["\']vue["\']',      # Vue imports
        r'createApp\(',                     # Vue 3 app creation
        r'new Vue\(',                       # Vue 2 instance
        r'<template>',                      # Vue SFC templates
    ],
    "Angular": [
        r'@Component\(',                    # Angular component decorator
        r'@NgModule\(',                     # Angular module decorator
        r'import.*from ["\']@angular/',     # Angular imports
    ],
    "Express": [
        r'require\(["\']express["\']\)',    # Express require
        r'import.*from ["\']express["\']',  # Express ES6 import
        r'express\(\)',                     # Express app initialization
        r'app\.(get|post|put|delete)\(',    # Express routes
    ],
    "Next.js": [
        r'from ["\']next/',                     # Next.js imports
        r'export\s+default\s+function\s+\w+',   # Next.js page components
        r'getServerSideProps',                  # Next.js SSR
        r'getStaticProps',                      # Next.js SSG
    ],
    "Tailwind CSS": [
        r'@tailwind',                                       # Tailwind directives
        r'className="[^"]*\b(flex|grid|bg-|text-|p-|m-)',   # Common Tailwind classes
    ],
    "Bootstrap": [
        r'class="[^"]*\b(container|row|col-)', # Bootstrap grid classes
        r'class="[^"]*\b(btn|alert|modal)',    # Bootstrap component classes
    ],
    "Spring Boot": [
        r'@SpringBootApplication',          # Spring Boot main annotation
        r'@RestController',                 # Spring REST controller
        r'@Autowired',                      # Spring dependency injection
        r'import org\.springframework',     # Spring imports
    ],
    "Hibernate": [
        r'@Entity',                         # Hibernate entity annotation
        r'@Table',                          # Hibernate table annotation
        r'import org\.hibernate',           # Hibernate imports
    ],
    "Rails": [
        r'ApplicationController',           # Rails controller base class
        r'ActiveRecord::Base',              # Rails ORM base
        r'rails',                           # Rails references
    ],
    "Sinatra": [
        r'require ["\']sinatra["\']',           # Sinatra require
        r'\b(get|post|put|delete)\s+["\']/',    # Sinatra routes
    ],
    "Laravel": [
        r'use Illuminate\\',                # Laravel namespace
        r'Route::(get|post|put|delete)',    # Laravel routes
        r'extends Controller',              # Laravel controllers
    ],
    "Symfony": [
        r'use Symfony\\',                   # Symfony namespace
        r'@Route\(',                        # Symfony route annotation
        r'extends AbstractController',      # Symfony controllers
    ],
}

# =============================================================================
# MAIN DETECTION LOGIC
# =============================================================================

# Scans a file and counts pattern matches for each language
# Returns a dictionary with language names as keys and match counts as values
def scan_file_content(file_path):
    pattern_matches = {}

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

            # Strip comments before pattern matching to reduce false positives
            file_extension = get_extension(file_path)
            content = strip_comments(content, file_extension)

            # Check for occurrences of each language's patterns
            for language, patterns in LANGUAGE_PATTERNS.items():
                match_count = 0
                for pattern in patterns:
                    # Count how many times a pattern appears
                    matches = re.findall(pattern, content)
                    match_count += len(matches)

                # Only increase match count if we found at least one match
                if match_count > 0:
                    pattern_matches[language] = match_count

    except Exception:
        # Skip files we can't read (binary files, etc.)
        pass

    return pattern_matches

# Calculates confidence level (low, medium, high) for a detected language
# High:     Coding file extension, with 10+ pattern matches
# Medium:   Coding file extension, with < 10 pattern matches 
#           OR No coding file extension, with 10+ pattern matches
# Low:      No coding file extension and 1-9 pattern matches
def calculate_confidence(pattern_count, has_extension):
    # High confidence
    if has_extension and pattern_count >= 10:
        return "high"

    # Medium confidence
    if has_extension and pattern_count < 10:
        return "medium"
    if not has_extension and pattern_count >= 10:
        return "medium"

    # Low confidence
    return "low"

# Goes through a project folder and figures out which languages and frameworks are being used.
# It does this by checking file extensions and looking inside config/dependency files for framework names
def detect_languages_and_frameworks(directory):
    # Scan a directory and identify programming languages and frameworks used
    frameworks_found = set()

    # Track language detection with confidence levels
    # Structure: language_data: {"pattern_count": int, "has_extension": bool, "found_in_code_file": bool, "confidence": str}
    language_data = {}

    # Track statistics for debugging/logging
    files_scanned = 0
    files_skipped = 0
    dirs_skipped = 0

    # Traverse through all sub folders and files in the directory
    for root, dirs, files in os.walk(directory):
        # Filter out ignored directories IN-PLACE to prevent os.walk from descending into them
        # This is more efficient than checking each file's full path
        original_dir_count = len(dirs)
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
        dirs_skipped += original_dir_count - len(dirs)

        for file in files:
            file_path = os.path.join(root, file)

            # Check if this file should be scanned based on extension
            should_scan, is_code_file = should_scan_file(file)
            if not should_scan:
                files_skipped += 1
                continue

            files_scanned += 1

            # Detect languages by file extension (only for code files)
            ext = get_extension(file)
            if ext in LANGUAGE_MAP:
                lang = LANGUAGE_MAP[ext]
                if lang not in language_data:
                    language_data[lang] = {"pattern_count": 0, "has_extension": False, "found_in_code_file": False}
                language_data[lang]["has_extension"] = True
                language_data[lang]["found_in_code_file"] = True  # Extension match means it's definitely a code file
                print(f"Detected {lang} from file extension: {file_path}")

            # Detect languages by using syntax patterns
            pattern_results = scan_file_content(file_path)
            for language, match_count in pattern_results.items():
                if language not in language_data:
                    language_data[language] = {"pattern_count": 0, "has_extension": False, "found_in_code_file": False}
                # Keep track of total matches for this language
                language_data[language]["pattern_count"] += match_count
                # Mark if this detection came from a code file (not just text/docs)
                if is_code_file:
                    language_data[language]["found_in_code_file"] = True
                print(f"Detected {language} from content patterns ({match_count} matches): {file_path}")

            # TODO: Revamp framework detection logic
            # Look for known config files to detect frameworks
            filename_lower = file.lower()
            for hint_file, frameworks in FRAMEWORK_HINTS.items():
                if filename_lower == hint_file.lower():  # case-insensitive
                    print(f"Checking frameworks in: {os.path.join(root, file)}")
                    frameworks_found.update(frameworks)

                    # Read file content and check for any of the frameworks listed
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            content = f.read().lower()
                            for fw in frameworks:
                                if fw.lower() in content:
                                    print(f"Detected {fw} framework in {file}")
                                    frameworks_found.add(fw)
                    except Exception:
                        # Skip files we can't read (binary files, etc.)
                        pass

    # Log filtering statistics
    print(f"\n[Filtering Stats] Scanned: {files_scanned} files | Skipped: {files_skipped} files, {dirs_skipped} directories")

    # Calculate confidence for each detected language
    for language in language_data:
        confidence = calculate_confidence(
            language_data[language]["pattern_count"],
            language_data[language]["has_extension"]
        )
        language_data[language]["confidence"] = confidence

    # Categorize languages by confidence level (high, medium, low)
    high_confidence = []
    medium_confidence = []
    low_confidence = []

    for lang, details in language_data.items():
        if details["confidence"] == "high":
            high_confidence.append(lang)
        elif details["confidence"] == "medium":
            medium_confidence.append(lang)
        else:
            low_confidence.append(lang)

    # Sort results to keep output consistent for testing
    return {
        "languages": sorted(language_data.keys()),  # All languages detected
        "high_confidence": sorted(high_confidence),
        "medium_confidence": sorted(medium_confidence),
        "low_confidence": sorted(low_confidence),
        "frameworks": sorted(frameworks_found),
        "language_details": language_data
    }

# =============================================================================
# TERMINAL EXECUTION
# =============================================================================

# Allows this file to be run directly in the terminal
if __name__ == "__main__":
    directory = input("Enter path to project folder: ").strip()
    if not os.path.exists(directory):
        print(" The specified path does not exist. Please check and try again.")
    else:
        results = detect_languages_and_frameworks(directory)

        # Helper function to display languages in a table format
        def display_language_table(lang_list, details_dict):
            if lang_list:
                # Print table header
                print(f"  {'Language':<25} | {'Patterns Found':<15} | {'Has Extension':<13}")
                print(f"  {'-' * 25}-+-{'-' * 15}-+-{'-' * 13}")
                # Print each language row
                for lang in lang_list:
                    details = details_dict[lang]
                    pattern_count = details['pattern_count']
                    has_ext = "Yes" if details['has_extension'] else "No"
                    print(f"  {lang:<25} | {pattern_count:<15} | {has_ext:<13}")
            else:
                print("  None detected")

        # Display HIGH confidence languages
        print("\n" + "=" * 70)
        print("HIGH CONFIDENCE")
        print("Extension match + 10 or more pattern matches")
        print("=" * 70 + "\n")
        display_language_table(results['high_confidence'], results['language_details'])

        # Display MEDIUM confidence languages
        print("\n" + "=" * 70)
        print("MEDIUM CONFIDENCE")
        print("Extension with <10 patterns OR no extension with 10+ patterns")
        print("=" * 70 + "\n")
        display_language_table(results['medium_confidence'], results['language_details'])

        # Display LOW confidence languages
        print("\n" + "=" * 70)
        print("LOW CONFIDENCE")
        print("No extension match + less than 10 pattern matches")
        print("=" * 70 + "\n")
        display_language_table(results['low_confidence'], results['language_details'])

        # Display frameworks
        print("\n" + "=" * 70)
        print("FRAMEWORKS DETECTED")
        print("=" * 70 + "\n")
        if results['frameworks']:
            for fw in results['frameworks']:
                print(f"  {fw}")
        else:
            print("  None detected")

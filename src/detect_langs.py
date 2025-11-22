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

# File extensions for actual source code files
# Languages detected in these files are considered "primary" detections
CODE_EXTENSIONS = {
    ".py",      # Python
    ".js",      # JavaScript
    ".ts",      # TypeScript
    ".jsx",     # React (JavaScript)
    ".tsx",     # React (TypeScript)
    ".java",    # Java
    ".c",       # C
    ".cpp",     # C++
    ".hpp",     # C++ headers
    ".h",       # C/C++ headers
    ".cs",      # C#
    ".php",     # PHP
    ".html",    # HTML
    ".htm",     # HTML alternate
    ".css",     # CSS
    ".rb",      # Ruby
    ".swift",   # Swift
    ".go",      # Go
    ".kt",      # Kotlin
    ".rs",      # Rust
    ".sh",      # Shell Script
    ".bash",    # Bash Script
    ".sql",     # SQL
    ".json",    # JSON
    ".xml",     # XML
    ".yaml",    # YAML
    ".yml",     # YAML alternate
}

# Text-based extensions that may occasionally contain code snippets
# Languages detected ONLY in these files are flagged as "secondary" detections (possible false positives)
TEXT_EXTENSIONS = {
    ".txt",     # Plain text notes
    ".md",      # Markdown documentation
    ".rst",     # reStructuredText
    ".log",     # Log files
}

# Combined set of all scannable extensions, hopefully helps filter out non-deliberately coded files
SCANNABLE_EXTENSIONS = CODE_EXTENSIONS | TEXT_EXTENSIONS

# Check if a directory should be skipped during scanning, returns True if the directory is in the ignore list.
def should_ignore_directory(dir_name):
    # Direct match
    if dir_name in IGNORED_DIRECTORIES:
        return True
    return False

# Check if a file should be scanned based on its extension.
# Returns a tuple: (should_scan: bool, is_code_file: bool)
# - should_scan: True if the file extension is found within SCANNABLE_EXTENSIONS
# - is_code_file: True if the file extension is found within CODE_EXTENSION, False if the file extension is found within TEXT_EXTENSION
def should_scan_file(file_name):
    ext = os.path.splitext(file_name)[1].strip().lower()
    if ext in CODE_EXTENSIONS:
        return (True, True)
    if ext in TEXT_EXTENSIONS:
        return (True, False)
    return (False, False)

# =============================================================================
# COMMENT STRIPPING CONFIGURATION
# =============================================================================

# Maps file extensions to their comment syntax for stripping before pattern matching
# Each entry contains: single-line comment prefix(es) and multi-line comment delimiters
# Format: extension -> {"single": [prefixes], "multi": [(start, end), ...]}
COMMENT_SYNTAX = {
    # Python
    ".py": {"single": ["#"], "multi": [('"""', '"""'), ("'''", "'''")],},
    # JavaScript/TypeScript
    ".js": {"single": ["//"], "multi": [("/*", "*/")]},
    ".jsx": {"single": ["//"], "multi": [("/*", "*/")]},
    ".ts": {"single": ["//"], "multi": [("/*", "*/")]},
    ".tsx": {"single": ["//"], "multi": [("/*", "*/")]},
    # C-Family
    ".c": {"single": ["//"], "multi": [("/*", "*/")]},
    ".cpp": {"single": ["//"], "multi": [("/*", "*/")]},
    ".h": {"single": ["//"], "multi": [("/*", "*/")]},
    ".hpp": {"single": ["//"], "multi": [("/*", "*/")]},
    ".cs": {"single": ["//"], "multi": [("/*", "*/")]},
    # Java
    ".java": {"single": ["//"], "multi": [("/*", "*/")]},
    # Kotlin
    ".kt": {"single": ["//"], "multi": [("/*", "*/")]},
    # Swift
    ".swift": {"single": ["//"], "multi": [("/*", "*/")]},
    # Go
    ".go": {"single": ["//"], "multi": [("/*", "*/")]},
    # Rust
    ".rs": {"single": ["//"], "multi": [("/*", "*/")]},
    # PHP
    ".php": {"single": ["//", "#"], "multi": [("/*", "*/")]},
    # Ruby
    ".rb": {"single": ["#"], "multi": [("=begin", "=end")]},
    # Shell scripts
    ".sh": {"single": ["#"], "multi": []},
    ".bash": {"single": ["#"], "multi": []},
    # SQL
    ".sql": {"single": ["--"], "multi": [("/*", "*/")]},
    # HTML
    ".html": {"single": [], "multi": [("<!--", "-->")]},
    ".htm": {"single": [], "multi": [("<!--", "-->")]},
    # CSS
    ".css": {"single": [], "multi": [("/*", "*/")]},
    # YAML
    ".yaml": {"single": ["#"], "multi": []},
    ".yml": {"single": ["#"], "multi": []},
    # XML
    ".xml": {"single": [], "multi": [("<!--", "-->")]},
}

# Remove comments from file content based on the file's extension from COMMNENT_SYNTAX
# This helps reduce false positives from code examples in comments.
def strip_comments(content, file_extension):
    # Format the file extension to lowercase for consistent matching
    ext = file_extension.lower()

    # If we don't have comment syntax for this extension, don't attempt to strip comments
    if ext not in COMMENT_SYNTAX:
        return content

    syntax = COMMENT_SYNTAX[ext]
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
# LANGUAGE DETECTION CONFIGURATION
# =============================================================================

# Mapping of common file extensions to programming languages.
# Used for quick classification during directory traversal.
LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "React (JavaScript)",
    ".ts": "TypeScript",
    ".tsx": "React (TypeScript)",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".php": "PHP",
    ".html": "HTML",
    ".css": "CSS",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".go": "Go",
    ".kt": "Kotlin",
    ".rs": "Rust",
    ".json": "JSON (Web Config)",
    ".xml": "XML",
    ".sh": "Shell Script",
    ".sql": "SQL",
}

# Regex patterns for detecting languages by file content (imported "re" at top of this file).
# Each pattern is designed to match distinctive syntax unique to that language.
# NOTE: Some patterns may still produce false positives from comments/documentation.
# Future improvement: Consider adding comment/string filtering before pattern matching.
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

# TODO: Rework framework detection to be in-line with language detection method
# Framework indicators based on well-known files
FRAMEWORK_HINTS = {
    "requirements.txt": ["Flask", "Django", "FastAPI"],
    "package.json": ["React", "Next.js", "Express", "Vue", "Angular"],
    "pom.xml": ["Spring Boot", "Maven"],
    "build.gradle": ["Spring Boot", "Gradle"],
}

# Scans a file and counts pattern matches for each language
# Returns a dictionary with language names as keys and match counts as values
def scan_file_content(file_path):
    pattern_matches = {}

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

            # Strip comments before pattern matching to reduce false positives
            file_extension = os.path.splitext(file_path)[1].lower()
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

# Goes through a project folder and figures out which languages and frameworks are being used. It does this by checking file extensions
# and looking inside config/dependency files for framework names
def detect_languages_and_frameworks(directory):
    # Scan a directory and identify programming languages and frameworks used.
    frameworks_found = set()

    # Track language detection with confidence levels
    # Structure: language_data: {"pattern_count": int, "has_extension": bool, "found_in_code_file": bool, "confidence": str}
    # - found_in_code_file: True if detected in a CODE_EXTENSION file, False if only in TEXT_EXTENSION files
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
        dirs[:] = [d for d in dirs if not should_ignore_directory(d)]
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
            ext = os.path.splitext(file)[1].strip().lower()
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
        print("=" * 70)
        display_language_table(results['high_confidence'], results['language_details'])

        # Display MEDIUM confidence languages
        print("\n" + "=" * 70)
        print("MEDIUM CONFIDENCE")
        print("Extension with <10 patterns OR no extension with 10+ patterns")
        print("=" * 70)
        display_language_table(results['medium_confidence'], results['language_details'])

        # Display LOW confidence languages
        print("\n" + "=" * 70)
        print("LOW CONFIDENCE")
        print("No extension match + less than 10 pattern matches")
        print("=" * 70)
        display_language_table(results['low_confidence'], results['language_details'])

        # Display frameworks
        print("\n" + "=" * 70)
        print("FRAMEWORKS DETECTED")
        print("=" * 70)
        if results['frameworks']:
            for fw in results['frameworks']:
                print(f"  {fw}")
        else:
            print("  None detected")

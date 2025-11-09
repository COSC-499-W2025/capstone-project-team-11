import os
import re

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
}

# Framework indicators based on well-known files.
FRAMEWORK_HINTS = {
    "requirements.txt": ["Flask", "Django", "FastAPI"],
    "package.json": ["React", "Next.js", "Express", "Vue", "Angular"],
    "pom.xml": ["Spring Boot", "Maven"],
    "build.gradle": ["Spring Boot", "Gradle"],
}

# Scans a file and counts pattern matches for each language.
# Returns a dictionary with language names as keys and match counts as values.
def scan_file_content(file_path):
    pattern_matches = {}

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

            # Check for occurrances of each language's patterns
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

# Calculates confidence level (low, medium, high) based on pattern matches and file extension presence
# Logic:
    # Low: 1-2 pattern matches only
    # Medium: 3-4 pattern matches OR file extension + 1 pattern
    # High: 5+ pattern matches OR file extension + 2+ patterns
def calculate_confidence(pattern_count, has_file_extension):
    # High confidence
    if pattern_count >= 5:
        return "high"
    if has_file_extension and pattern_count >= 2:
        return "high"

    # Medium confidence
    if pattern_count >= 3:
        return "medium"
    if has_file_extension and pattern_count >= 1:
        return "medium"

    # If NOT High or Medium: Low confidence
    return "low"

# Goes through a project folder and figures out which languages and frameworks are being used. It does this by checking file extensions
# and looking inside config/dependency files for framework names
def detect_languages_and_frameworks(directory):
    # Scan a directory and identify programming languages and frameworks used.
    frameworks_found = set()

    # Track language detection with confidence levels
    # Structure: language: {"pattern_count": int, "has_extension": bool, "confidence": str}
    language_data = {}

    # Traverse through all sub folders and files in the directory
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            # Detect languages by file extension
            ext = os.path.splitext(file)[1].strip().lower()
            if ext in LANGUAGE_MAP:
                lang = LANGUAGE_MAP[ext]
                if lang not in language_data:
                    language_data[lang] = {"pattern_count": 0, "has_extension": False}
                language_data[lang]["has_extension"] = True
                print(f"Detected {lang} from file extension: {file_path}")

            # Detect languages by using syntax patterns
            pattern_results = scan_file_content(file_path)
            for language, match_count in pattern_results.items():
                if language not in language_data:
                    language_data[language] = {"pattern_count": 0, "has_extension": False}
                # Keep track of total matches for this language
                language_data[language]["pattern_count"] += match_count
                print(f"Detected {language} from content patterns ({match_count} matches): {file_path}")

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

    # Calculate confidence for each detected language
    for language in language_data:
        confidence = calculate_confidence(
            language_data[language]["pattern_count"],
            language_data[language]["has_extension"]
        )
        language_data[language]["confidence"] = confidence

    # Sort results to keep output consistent for testing
    return {
        "languages": sorted(language_data.keys()),
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
        print("\n=== Language & Framework Detection ===")
        print(f"Languages detected: {', '.join(results['languages']) or 'None'}")
        print(f"Frameworks detected: {', '.join(results['frameworks']) or 'None'}")

        # Show detailed information with confidence levels
        if results['language_details']:
            print("\n=== Language Confidence Details ===")
            for lang in sorted(results['language_details'].keys()):
                details = results['language_details'][lang]
                confidence = details['confidence']
                pattern_count = details['pattern_count']
                has_ext = details['has_extension']

                # Format output nicely
                ext_indicator = " [Extension Match]" if has_ext else ""
                print(f"{lang}: {confidence.upper()} confidence ({pattern_count} patterns){ext_indicator}")

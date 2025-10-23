import os

# --- Mapping for languages ---
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

# --- Common framework indicators ---
FRAMEWORK_HINTS = {
    "requirements.txt": ["Flask", "Django", "FastAPI"],
    "package.json": ["React", "Next.js", "Express", "Vue", "Angular"],
    "pom.xml": ["Spring Boot", "Maven"],
    "build.gradle": ["Spring Boot", "Gradle"],
}


def detect_languages_and_frameworks(directory):
    """Scan a directory and identify programming languages and frameworks used."""
    languages_found = set()
    frameworks_found = set()

    for root, _, files in os.walk(directory):
        for file in files:
            # --- Detect languages by file extension ---
            ext = os.path.splitext(file)[1].strip().lower()
            if ext in LANGUAGE_MAP:
                languages_found.add(LANGUAGE_MAP[ext])
                print(f"Detected {LANGUAGE_MAP[ext]} from file: {os.path.join(root, file)}")

            # --- Detect frameworks based on known files ---
            filename_lower = file.lower()
            for hint_file, frameworks in FRAMEWORK_HINTS.items():
                if filename_lower == hint_file.lower():  # case-insensitive
                    print(f"Checking frameworks in: {os.path.join(root, file)}")
                    frameworks_found.update(frameworks)

                    # Read file content to detect framework keywords
                    try:
                        with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                            content = f.read().lower()
                            for fw in frameworks:
                                if fw.lower() in content:
                                    print(f"Detected {fw} framework in {file}")
                                    frameworks_found.add(fw)
                    except Exception as e:
                        print(f"Could not read {file}: {e}")
                        pass

    return {
        "languages": sorted(languages_found),
        "frameworks": sorted(frameworks_found)
    }


if __name__ == "__main__":
    directory = input("Enter path to project folder: ").strip()
    if not os.path.exists(directory):
        print("❌ The specified path does not exist. Please check and try again.")
    else:
        results = detect_languages_and_frameworks(directory)
        print("\n=== Language & Framework Detection ===")
        print(f"Languages detected: {', '.join(results['languages']) or 'None'}")
        print(f"Frameworks detected: {', '.join(results['frameworks']) or 'None'}")

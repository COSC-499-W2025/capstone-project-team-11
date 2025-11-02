import os
import re
from detect_langs import detect_languages_and_frameworks

# Maps patterns in code or text to potential human or technical skills.
# Helps us figure out what someone might be good at based on their files.
CODE_SKILL_PATTERNS = {
    # Detects basic OOP patterns (class definitions, inheritance, constructors, etc.)
    "Object-Oriented Programming": [
        r"\bclass\s+\w+",          # class declaration
        r"\bself\.",               # instance attribute
        r"__init__",               # constructor
        r"\bextends\b",            # common in Java
        r"\bimplements\b"          # Java interfaces
    ],

    # Detects recursion by finding a function calling itself
    "Recursion": [
        r"\bdef\s+(\w+)\(.*\):[\s\S]*?\b\1\s*\("   # captures def foo(): ... foo()
    ],

    # Detects test-related keywords
    "Testing": [
        r"\bassert\b",
        r"\btest_", r"unittest", r"pytest"
    ],

    # Detects Web frameworks commonly used
    "Web Development": [
        r"\bflask\b", r"\bexpress\b", r"\bdjango\b", 
        r"\breact\b", r"\bangular\b", r"\bvue\b"
    ],

    # Detects database/SQL commands
    "Database / SQL": [
        r"\bSELECT\b", r"\bINSERT\b", r"\bCREATE TABLE\b", r"\bUPDATE\b"
    ],

    # Detects async or threaded code
    "Asynchronous Programming": [
        r"\basync\b", r"\bawait\b", r"\bthread", r"\bprocess"
    ],

    # Detects functional programming syntax
    "Functional Programming": [
        r"\blambda\b", r"\bmap\(", r"\breduce\(", r"\bfilter\("
    ],
}

WRITING_SKILL_PATTERNS = {
    #  words like "therefore" or "consequently" suggest formal writing style.
    "Formal Writing": [r"\btherefore\b", r"\bfurthermore\b", r"\bconsequently\b", r"\bas a result\b"],
    "Analytical Writing": [r"\banalyze\b", r"\bcompare\b", r"\bcontrast\b", r"\bdiscuss\b"],
    # Example: story-related language points to creative writing skills.
    "Creative Writing": [r"\bstory\b", r"\bcharacter\b", r"\btheme\b", r"\bnarrative\b"],
    # another example terms like “methodology” or “data” → technical or research-based writing.
    "Technical Writing": [r"\bexperiment\b", r"\bmethodology\b", r"\bresult\b", r"\bdata\b"],
}

# Looks at a single file and tries to detect what skills it might show.
# For example, recursion in code or strong writing in essays.
def detect_skills_in_file(file_path):
    skills = set()
    ext = os.path.splitext(file_path)[1].lower()

    # Check for programming-related skills
    if ext in [".py", ".java", ".js", ".cpp", ".c", ".cs", ".php", ".ts", ".html", ".css"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for skill, patterns in CODE_SKILL_PATTERNS.items():
                if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                    skills.add(skill)
        except Exception:
            pass

    # Check for writing or communication-based skills
    elif ext in [".txt", ".md", ".pdf"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read().lower()
            for skill, patterns in WRITING_SKILL_PATTERNS.items():
                if any(re.search(pattern, text) for pattern in patterns):
                    skills.add(skill)
            # Longer, well-written text likely means stronger communication ability
            if len(text.split()) > 300:
                skills.add("Strong Communication Skills")
        except Exception:
            pass

    return list(skills)

# Scans a whole folder, checks each file for skill indicators,
# and also reuses the language/framework detector.
def detect_skills(directory):
    langs_and_frameworks = detect_languages_and_frameworks(directory)
    all_skills = set()

    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            file_skills = detect_skills_in_file(path)
            all_skills.update(file_skills)

    return {
        "languages": langs_and_frameworks["languages"],
        "frameworks": langs_and_frameworks["frameworks"],
        "skills": sorted(all_skills)
    }

# Lets us run this directly from terminal to test a folder.
if __name__ == "__main__":
    directory = input("Enter directory path to analyze: ").strip()
    if not os.path.exists(directory):
        print(" The specified path does not exist.")
    else:
        results = detect_skills(directory)
        print("\n=== Detected Skills ===")
        print(f"Languages: {', '.join(results['languages']) or 'None'}")
        print(f"Frameworks: {', '.join(results['frameworks']) or 'None'}")
        print(f"Skills: {', '.join(results['skills']) or 'None'}")

import os

# List of accepted formats (Add/remove extensions as needed)
ALLOWED_FORMATS = {
    '.txt', '.csv', '.json', '.xml', '.html', '.md', '.yml', '.yaml',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg',
    '.zip', '.tar', '.gz', '.rar',
    '.py', '.java', '.js', '.ts', '.c', '.cpp', '.h', '.hpp', '.sh',
    '.ipynb', '.r', '.rb', '.php', '.sql'
}

def is_valid_format(filename: str) -> bool:
    """
    Check if the file format is valid based on its extension.
    :param filename: The name of the file to validate.
    :return: True if the file format is allowed, False otherwise.
    """
    if not filename or not isinstance(filename, str):
        return False
    _, ext = os.path.splitext(filename.strip().lower())
    return ext in ALLOWED_FORMATS
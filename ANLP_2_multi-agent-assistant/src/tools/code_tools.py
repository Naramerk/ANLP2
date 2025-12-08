# Code analysis tools
import ast
import re
from typing import Optional


def validate_python_syntax(code: str) -> dict:
    """Validate Python code syntax

    Args:
        code: Line with Python code to check

    Returns:
        Dictionary with result: valid (bool), error (str|None), line (int|None)
    """
    try:
        ast.parse(code)
        return {"valid": True, "error": None, "line": None}
    except SyntaxError as e:
        return {"valid": False, "error": str(e), "line": e.lineno}


def extract_function_signature(code: str) -> str:
    """Extract function signature from code

    Args:
        code: Line with function code

    Returns:
        Function signature or error message
    """
    match = re.search(r'def\s+(\w+)\s*\((.*?)\)\s*(?:->\s*(\w+))?\s*:', code, re.DOTALL)
    if match:
        name = match.group(1)
        params = match.group(2).strip()
        return_type = match.group(3)
        signature = f"def {name}({params})"
        if return_type:
            signature += f" -> {return_type}"
        signature += ":"
        return signature
    return "Function signature not found"


def extract_class_info(code: str) -> dict:
    """Extract class information from code

    Args:
        code: Line with class code

    Returns:
        Dictionary with class name and methods
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                return {
                    "class_name": node.name,
                    "methods": methods,
                    "bases": [ast.unparse(base) for base in node.bases] if node.bases else []
                }
    except SyntaxError:
        pass
    return {"class_name": None, "methods": [], "bases": []}


def suggest_improvements(code: str) -> list:
    """Suggest code improvements (simple rules)

    Args:
        code: Line with code for analysis

    Returns:
        List of improvement suggestions
    """
    suggestions = []

    # Check for print usage instead of logging
    if "print(" in code:
        suggestions.append("💡 Consider using logging instead of print() for production code")

    # Check for global variables
    if "global " in code:
        suggestions.append("Avoid global variables, use function parameters or classes")

    # Check for bare except
    if re.search(r'except\s*:', code):
        suggestions.append("Specify concrete exception types instead of bare except")

    # Check for == None usage
    if "== None" in code or "!= None" in code:
        suggestions.append("Use 'is None' or 'is not None' instead of == / !=")

    # Check for long lines
    lines = code.split('\n')
    long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > 100]
    if long_lines:
        suggestions.append(f"📏 Lines {long_lines[:3]} exceed 100 characters, consider splitting")

    # Check for missing docstring
    if re.search(r'def\s+\w+\s*\([^)]*\)\s*:', code):
        if '"""' not in code and "'''" not in code:
            suggestions.append("Add docstring for function documentation")

    # Check for magic numbers usage
    magic_numbers = re.findall(r'(?<!["\'\w])\b(\d{2,})\b(?!["\'\w])', code)
    if magic_numbers:
        suggestions.append(f"Consider extracting 'magic numbers' ({magic_numbers[:3]}) into constants")
    
    return suggestions


def count_complexity(code: str) -> dict:
    """Assess code complexity

    Args:
        code: Line with code for analysis

    Returns:
        Dictionary with complexity metrics
    """
    try:
        tree = ast.parse(code)
        
        functions = 0
        classes = 0
        loops = 0
        conditionals = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1
            elif isinstance(node, (ast.For, ast.While)):
                loops += 1
            elif isinstance(node, ast.If):
                conditionals += 1
        
        lines = len([l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')])
        
        return {
            "lines_of_code": lines,
            "functions": functions,
            "classes": classes,
            "loops": loops,
            "conditionals": conditionals,
            "complexity_score": loops + conditionals + functions  # Simplified metric
        }
    except SyntaxError:
        return {"error": "Cannot parse code"}


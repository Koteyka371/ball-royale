import ast

def print_methods(filepath):
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            print(f"Class: {node.name}")
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    print(f"  Method: {item.name}")

print_methods("src/system/crowd_system.py")

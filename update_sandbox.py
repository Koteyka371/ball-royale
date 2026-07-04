def replace_in_file(filepath, search, replace):
    with open(filepath, 'r') as f:
        content = f.read()
    if search not in content:
        print(f"Search string not found in {filepath}")
        return False
    content = content.replace(search, replace)
    with open(filepath, 'w') as f:
        f.write(content)
    return True

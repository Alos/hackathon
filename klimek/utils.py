
def apply_changes(file_path, old_api_call, new_api_call):
    """
    Applies the changes to the given file.

    Args:
        file_path: The path to the file to modify.
        old_api_call: The old API call to replace.
        new_api_call: The new API call to replace it with.
    """

    with open(file_path, "r") as f:
        content = f.read()

    content = content.replace(old_api_call, new_api_call)

    with open(file_path, "w") as f:
        f.write(content)

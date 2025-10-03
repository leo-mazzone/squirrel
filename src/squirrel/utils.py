def clean_markdown_code_blocks(text: str) -> str:
    """
    Remove markdown code blocks from text regardless of language.

    Args:
        text: Text that may contain markdown code blocks

    Returns:
        Cleaned text without markdown code blocks
    """
    text = text.strip()

    # Check if text starts with ``` followed by optional language identifier
    if text.startswith("```"):
        # Find the first newline after the opening ```
        first_newline = text.find("\n")
        if first_newline != -1:
            # Remove everything up to and including the first newline
            text = text[first_newline + 1 :]
        else:
            # No newline found, remove the opening ```
            text = text[3:]

    # Remove closing ``` if present
    if text.endswith("```"):
        text = text[:-3]

    return text.strip()

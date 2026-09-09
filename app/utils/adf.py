.from typing import Any

def adf_to_text(node: Any) -> str:
    """Convert Jira Atlassian Document Format content into readable plain text."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_to_text(item) for item in node)
    if not isinstance(node, dict):
        return str(node)

    node_type = node.get("type")
    if node_type == "text":
        return node.get("text", "")
    if node_type == "hardBreak":
        return "\n"

    text = "".join(adf_to_text(item) for item in node.get("content", []))
    if node_type in {"paragraph", "heading", "listItem"} and text and not text.endswith("\n"):
        text += "\n"
    return text

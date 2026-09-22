def build_context(chunks: list[dict]) -> str:

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):

        source = f"""
SOURCE {index}
Page: {chunk["page_number"]}

{chunk["content"]}
"""

        context_parts.append(source.strip())

    return "\n\n".join(context_parts)
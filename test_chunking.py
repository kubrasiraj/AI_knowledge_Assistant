from app.services.document_service import split_text_into_chunks


text = """
NovaStack Technologies provides cloud-based software solutions.

Employees are entitled to twenty annual leave days.
Leave requests should be submitted through the employee portal.

Remote work is allowed two days per week.
Employees must follow the company's security guidelines
when working remotely.

All production deployments must be reviewed before release.
Critical incidents should be reported to the engineering team.
"""


chunks = split_text_into_chunks(text)

print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i} ---")
    print(chunk)
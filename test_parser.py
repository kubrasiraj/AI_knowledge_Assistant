from app.services.document_parser import extract_text


FILES = [
    "test_documents/test.txt",
    "test_documents/test.docx",
]


def main():
    for file_path in FILES:
        print("\n" + "=" * 60)
        print(f"FILE: {file_path}")
        print("=" * 60)

        text = extract_text(file_path)

        print("\nExtracted Text:")
        print(text)


if __name__ == "__main__":
    main()
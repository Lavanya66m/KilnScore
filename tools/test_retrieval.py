from app.retrieval import retrieve_chunks

question = "Which cement company will have the lowest carbon emissions five years from now?"
print("Question:", question)
print("\nSearching PostgreSQL...\n")

results = retrieve_chunks(question, limit=5)

if not results:
    print("No relevant chunks found.")
else:
    for index, result in enumerate(results, start=1):
        print(f"\n{'=' * 70}")
        print(f"RESULT {index}")
        print("Document:", result["document"])
        print("Page:", result["page"])
        print("PDF Page:", result["pdf_page"])
        print("Headings:", result["headings"])
        print("Distance:", round(result["distance"], 4))
        print("\nFULL CONTENT:")
        print(result["content"])

print("\nRetrieval inspection completed.")
import pickle
from pathlib import Path

from sentence_transformers import SentenceTransformer

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "data" / "institutional_docs"
OUTPUT_FILE = ROOT_DIR / "rag" / "document_embeddings.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"


def read_document(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_into_chunks(text: str):
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n")]
    return [paragraph for paragraph in paragraphs if paragraph]


def create_chunks(doc_paths):
    chunks = []
    for doc_path in doc_paths:
        text = read_document(doc_path)
        paragraph_texts = split_into_chunks(text)
        for chunk_id, paragraph in enumerate(paragraph_texts):
            chunks.append(
                {
                    "document": doc_path.name,
                    "chunk_id": chunk_id,
                    "text": paragraph,
                }
            )
    return chunks


def main():
    doc_paths = sorted(DOCS_DIR.glob("*.txt"))
    if not doc_paths:
        raise FileNotFoundError(f"No document files found in {DOCS_DIR}")

    chunks = create_chunks(doc_paths)
    texts = [chunk["text"] for chunk in chunks]

    print("Loading embedding model:", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(texts, show_progress_bar=True)

    if len(embeddings) != len(chunks):
        raise ValueError("Number of embeddings does not match number of chunks.")

    output_data = {
        "chunks": chunks,
        "embeddings": embeddings,
    }

    with OUTPUT_FILE.open("wb") as handle:
        pickle.dump(output_data, handle)

    embedding_dim = embeddings.shape[1] if embeddings.ndim == 2 else 0
    print("Documents found:", len(doc_paths))
    print("Chunks created:", len(chunks))
    print("Embedding dimension:", embedding_dim)
    print("First chunk document:", chunks[0]["document"])
    print("First chunk text:", chunks[0]["text"])
    print("Embeddings shape:", (len(embeddings), embedding_dim))
    print("Saved embeddings to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()

import json
import shutil
from pathlib import Path

import chromadb
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
METADATA_FILE        = "index_metadata.json"

_embed_model = None


def get_embed_model() -> HuggingFaceEmbedding:
    global _embed_model
    if _embed_model is None:
        _embed_model = HuggingFaceEmbedding(
            model_name=EMBEDDING_MODEL_NAME,
            device="cpu",
        )
    return _embed_model


def _create_vector_store(collection_name: str, persist_dir: Path) -> tuple:
    client     = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_or_create_collection(collection_name)
    return collection, ChromaVectorStore(chroma_collection=collection)


def load_or_build_index(
    chunks: list[dict],
    collection_name: str,
    persist_dir: Path,
) -> VectorStoreIndex:
    embed_model   = get_embed_model()
    metadata_path = persist_dir / METADATA_FILE

    if metadata_path.exists():
        stored = json.loads(metadata_path.read_text(encoding="utf-8"))
        if stored.get("embedding_model") == EMBEDDING_MODEL_NAME:
            _, vector_store = _create_vector_store(collection_name, persist_dir)
            return VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
        shutil.rmtree(persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

    _, vector_store = _create_vector_store(collection_name, persist_dir)
    documents = [
        Document(
            text=c["text"],
            metadata={"chunk_index": c["index"], "strategy": c["strategy"]},
        )
        for c in chunks
    ]
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )
    metadata_path.write_text(
        json.dumps({"embedding_model": EMBEDDING_MODEL_NAME}),
        encoding="utf-8",
    )
    return index

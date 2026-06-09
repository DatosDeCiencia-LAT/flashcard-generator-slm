from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter


def fixed_size_chunking(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[dict]:
    splitter  = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    llama_doc = Document(text=text)
    nodes     = splitter.get_nodes_from_documents([llama_doc])
    return [
        {"text": node.text, "index": i, "strategy": "fixed_size"}
        for i, node in enumerate(nodes)
    ]

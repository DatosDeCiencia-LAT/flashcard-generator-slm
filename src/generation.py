import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from llama_cpp import Llama
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

GENERATOR_MODEL = "qwen2.5-3b-instruct-q4_k_m.gguf"
VALID_MODES     = {"flashcard", "summary"}

SYSTEM_PROMPT_FLASHCARD = """You are an expert study assistant that creates structured flash cards for students.
IMPORTANT: Always respond in the same language as the topic query. If they ask in Spanish, answer in Spanish. If they ask in English, answer in English.

Given a context extracted from a textbook and a topic query, generate a flash card in JSON format.
The JSON must follow this exact schema with no additional fields:

{{
    "concept": "name of the concept",
    "definition": "clear and concise definition in 2-3 sentences",
    "key_points": ["point 1", "point 2", "point 3"],
    "examples": ["example 1", "example 2"],
    "suggested_image": "brief description of an image that would illustrate this concept"
}}

Rules:
- Respond ONLY with the JSON object, no preamble, no explanation, no markdown backticks
- Base your response strictly on the provided context
- If the context does not contain enough information, still follow the schema but indicate the limitation in the definition field
- All fields are required"""

SYSTEM_PROMPT_SUMMARY = """You are an expert study assistant that creates structured summaries for students.
IMPORTANT: Always respond in the same language as the topic query. If they ask in Spanish, answer in Spanish. If they ask in English, answer in English.

Given a context extracted from a textbook and a topic query, generate a consolidated summary in JSON format.
The JSON must follow this exact schema with no additional fields:

{{
    "topic": "main topic name",
    "overview": "2-3 sentence overview of the topic",
    "concepts": [
        {{
            "name": "concept name",
            "description": "brief description in 1-2 sentences"
        }}
    ]
}}

Rules:
- Respond ONLY with the JSON object, no preamble, no explanation, no markdown backticks
- Base your response strictly on the provided context
- Include between 3 and 8 concepts
- All fields are required"""

FLASHCARD_EXAMPLE = """{
    "concept": "Amida",
    "definition": "Una amida es un compuesto derivado de un ácido carboxílico donde el grupo hidroxilo es reemplazado por un grupo amino. Las amidas se encuentran en proteínas y muchas moléculas biológicas.",
    "key_points": ["Derivada de ácidos carboxílicos", "Contiene un grupo carbonilo unido a nitrógeno", "Presente en proteínas como enlaces peptídicos"],
    "examples": ["Acetamida (CH3CONH2)", "Nylon (poliamida sintética)"],
    "suggested_image": "Fórmula estructural de una amida mostrando el grupo carbonilo unido a nitrógeno"
}"""

SUMMARY_EXAMPLE = """{
    "topic": "Derivados de ácidos carboxílicos",
    "overview": "Los derivados de ácidos carboxílicos son compuestos que pueden hidrolizarse para dar ácidos carboxílicos.",
    "concepts": [
        {"name": "Éster", "description": "Formado por la reacción de un ácido carboxílico con un alcohol"},
        {"name": "Amida", "description": "Formada por la reacción de un ácido carboxílico con una amina"}
    ]
}"""


@dataclass
class FlashCard:
    concept         : str
    definition      : str
    key_points      : list
    examples        : list
    suggested_image : str


@dataclass
class ConsolidatedSummary:
    topic    : str
    overview : str
    concepts : list


def _truncate_at_complete_json(raw: str) -> str:
    """Walk the string tracking depth and string context so brackets inside
    string values don't fool the truncation point detection."""
    depth         = 0
    in_string     = False
    escape        = False
    last_complete = -1

    for i, ch in enumerate(raw):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
            if depth == 0:
                last_complete = i

    return raw[:last_complete + 1] if last_complete != -1 else raw


def _clean_json_output(raw: str) -> str:
    raw = re.sub(r"```json|```", "", raw).strip()
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)
    raw = _truncate_at_complete_json(raw)
    return raw


_llm = None


def load_language_model(model_path: Path, n_ctx: int = 2048) -> Llama:
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path=str(model_path),
            n_ctx=n_ctx,
            n_threads=os.cpu_count(),
            verbose=False,
        )
    return _llm


def generate_flashcard(
    query: str,
    index: VectorStoreIndex,
    llm: Llama,
    embed_model: HuggingFaceEmbedding,
    mode: str = "flashcard",
    k: int = 3,
) -> "FlashCard | ConsolidatedSummary":
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of {VALID_MODES}")

    system_prompt = SYSTEM_PROMPT_FLASHCARD if mode == "flashcard" else SYSTEM_PROMPT_SUMMARY
    example       = FLASHCARD_EXAMPLE if mode == "flashcard" else SUMMARY_EXAMPLE
    max_tokens    = 1024 if mode == "flashcard" else 1536

    retriever = index.as_retriever(similarity_top_k=k, embed_model=embed_model)
    nodes     = retriever.retrieve(query)
    if not nodes:
        raise ValueError(f"No chunks retrieved for query: '{query}'")

    context = "\n\n".join(f"[Chunk {i+1}]\n{node.text}" for i, node in enumerate(nodes))

    last_error = None
    for attempt, prompt in enumerate([
        system_prompt,
        system_prompt + f"\n\nExample of expected output:\n{example}",
    ]):
        try:
            response = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user",   "content": f"Context:\n{context}\n\nTopic: {query}"},
                ],
                max_tokens=max_tokens,
                temperature=0.1,
            )
            raw = json.loads(_clean_json_output(response["choices"][0]["message"]["content"]))
            if mode == "flashcard":
                return FlashCard(**raw)
            return ConsolidatedSummary(**raw)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            last_error = e

    raise ValueError(
        f"Generation failed after 2 attempts for query '{query}'. "
        f"Last error: {last_error}"
    )

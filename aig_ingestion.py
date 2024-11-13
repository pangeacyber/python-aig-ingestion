from __future__ import annotations

import sys
from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple, cast

import click
from dotenv import load_dotenv
from numpy import float64
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from pangea import PangeaConfig
from pangea.services import AIGuard
from scipy.spatial import distance  # type: ignore[import-untyped]

load_dotenv(override=True)


SYSTEM_PROMPT = """
You are a kind and humble chatbot who sticks to facts received from the
following context:
Context: {context}
"""


class ChunkEmbedding(NamedTuple):
    chunk: str
    embedding: list[float]


def chunk_text(text: str, max_tokens: int) -> list[str]:
    # Assuming each token is 4 characters (ranges from 3-6).
    char_limit = max_tokens * 4

    # Split text into chunks based on character limits.
    return [text[i : i + char_limit] for i in range(0, len(text), char_limit)]


def compute_cosine_similarity(vec1: Iterable[float], vec2: Iterable[float]) -> float64:
    return 1 - distance.cosine(vec1, vec2)


@click.command()
@click.option("--model", default="gpt-4o-mini", show_default=True, required=True, help="OpenAI model.")
@click.option(
    "--ai-guard-token",
    envvar="PANGEA_AI_GUARD_TOKEN",
    required=True,
    help="Pangea AI Guard API token. May also be set via the `PANGEA_AI_GUARD_TOKEN` environment variable.",
)
@click.option(
    "--pangea-domain",
    envvar="PANGEA_DOMAIN",
    default="aws.us.pangea.cloud",
    show_default=True,
    required=True,
    help="Pangea API domain. May also be set via the `PANGEA_DOMAIN` environment variable.",
)
@click.option(
    "--openai-api-key",
    envvar="OPENAI_API_KEY",
    required=True,
    help="OpenAI API key. May also be set via the `OPENAI_API_KEY` environment variable.",
)
@click.argument("prompt")
def main(
    *,
    prompt: str,
    model: str,
    ai_guard_token: str,
    pangea_domain: str,
    openai_api_key: str,
) -> None:
    # Split data into chunks.
    click.echo("Reading documents...")
    data_dir = Path(__file__).parent.joinpath("data").resolve(strict=True)
    chunks = [
        chunk
        for md_file in data_dir.glob("*.md")
        for chunk in chunk_text(md_file.read_text(encoding="utf-8"), max_tokens=500)
    ]

    # Run each chunk through AI Guard.
    click.echo("Running all documents through AI Guard...")
    config = PangeaConfig(domain=pangea_domain)
    ai_guard = AIGuard(token=ai_guard_token, config=config)
    guarded_chunks: list[str] = []
    for chunk in chunks:
        guarded = ai_guard.guard_text(chunk)
        assert guarded.result
        guarded_chunks.append(guarded.result.redacted_prompt or chunk)

    # Generate embeddings for each chunk.
    click.echo("Generating embeddings...")
    openai = OpenAI(api_key=openai_api_key)
    embeddings = [
        ChunkEmbedding(chunk, res.embedding)
        for chunk, res in zip(
            guarded_chunks,
            openai.embeddings.create(
                input=guarded_chunks,
                model="text-embedding-3-small",
            ).data,
        )
    ]

    # Generate embedding for the user's prompt.
    prompt_embedding = (
        openai.embeddings.create(
            input=prompt,
            model="text-embedding-3-small",
        )
        .data[0]
        .embedding
    )

    # Find the most similar content
    similarities = [(item.chunk, compute_cosine_similarity(prompt_embedding, item.embedding)) for item in embeddings]

    # Sort by similarity score in descending order.
    similarities.sort(reverse=True, key=lambda x: float(x[1]))

    # Only take top 5 results.
    top_results = similarities[:5]

    # Build the context
    context = ""
    for content, _ in top_results:
        context += content + "\n--------------\n"

    # Generate chat completions.
    stream = openai.chat.completions.create(
        messages=(
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": prompt},
        ),
        model=model,
        stream=True,
    )
    for chunk in stream:  # type: ignore[assignment]
        for choice in cast(ChatCompletionChunk, chunk).choices:
            sys.stdout.write(choice.delta.content or "")
            sys.stdout.flush()

        sys.stdout.flush()

    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

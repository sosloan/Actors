#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import hashlib
from typing import Generator, Iterable, List, Tuple

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None  # Optional; script still works if not present


IGNORED_DIR_NAMES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "Library",
    "Applications",
    "Movies",
    "Music",
    "Pictures",
}


def iter_markdown_files(root_dir: str) -> Generator[str, None, None]:
    for current_dir, dirnames, filenames in os.walk(root_dir):
        # Prune heavy / irrelevant directories
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIR_NAMES]
        for filename in filenames:
            if filename.lower().endswith(".md"):
                yield os.path.join(current_dir, filename)


def read_text_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def chunk_text(text: str, chunk_chars: int, overlap_chars: int) -> List[str]:
    if chunk_chars <= 0:
        return [text]
    if overlap_chars < 0 or overlap_chars >= chunk_chars:
        overlap_chars = 0
    chunks: List[str] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_chars, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start = end - overlap_chars
    return chunks


def batched(iterable: Iterable, batch_size: int) -> Generator[List, None, None]:
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def create_embeddings_stream(
    items: List[Tuple[str, int, str]],
    model: str,
    batch_size: int,
    out_path: str,
    max_retries: int = 5,
    initial_backoff_seconds: float = 1.0,
    progress_every_batches: int = 1,
) -> int:
    try:
        from openai import OpenAI
    except Exception as exc:
        raise RuntimeError(
            "The 'openai' package is required. Install with: pip install openai"
        ) from exc

    client = OpenAI()

    total_written = 0
    batch_index = 0
    for batch in batched(items, batch_size):
        inputs = [text for (_, _, text) in batch]
        # Simple retry with exponential backoff
        backoff = initial_backoff_seconds
        for attempt in range(max_retries):
            try:
                resp = client.embeddings.create(model=model, input=inputs)
                rows: List[Tuple[str, int, str, List[float]]] = []
                for (path, chunk_index, text), data in zip(batch, resp.data):
                    rows.append((path, chunk_index, text, data.embedding))
                append_jsonl(out_path, rows)
                total_written += len(rows)
                batch_index += 1
                if progress_every_batches > 0 and (batch_index % progress_every_batches == 0):
                    print(f"Wrote {total_written} rows so far", flush=True)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(backoff)
                backoff *= 2
    return total_written


def append_jsonl(
    output_path: str,
    rows: Iterable[Tuple[str, int, str, List[float]]],
) -> None:
    ensure_parent_dir(output_path)
    with open(output_path, "a", encoding="utf-8") as f:
        for path, chunk_index, text, embedding in rows:
            record = {
                "path": path,
                "chunk_index": chunk_index,
                "text_sha256": sha256_text(text),
                "embedding": embedding,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate embeddings for Markdown files")
    parser.add_argument(
        "--root",
        default=os.path.expanduser("/Users/stevensloan"),
        help="Root directory to scan for .md files",
    )
    parser.add_argument(
        "--out",
        default=os.path.expanduser("/Users/stevensloan/ACTORS/md_embeddings.jsonl"),
        help="Output JSONL file for embeddings",
    )
    parser.add_argument(
        "--model",
        default="text-embedding-3-large",
        help="Embedding model to use",
    )
    parser.add_argument(
        "--chunk-chars",
        type=int,
        default=5000,
        help="Approximate characters per chunk",
    )
    parser.add_argument(
        "--overlap-chars",
        type=int,
        default=500,
        help="Character overlap between chunks",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Batch size for embedding requests",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=10,
        help="Print progress every N batches",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and chunk only; do not call the API",
    )

    args = parser.parse_args()

    if load_dotenv is not None:
        # Load .env from CWD if present
        try:
            load_dotenv()
        except Exception:
            pass

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not args.dry_run and not api_key:
        print(
            "OPENAI_API_KEY is not set. Create a .env with OPENAI_API_KEY=... or export it in your shell.",
            file=sys.stderr,
        )
        return 2

    md_files = list(iter_markdown_files(args.root))
    if args.dry_run:
        print(f"Found {len(md_files)} markdown files under {args.root}")

    items: List[Tuple[str, int, str]] = []
    for path in md_files:
        try:
            text = read_text_file(path)
        except Exception:
            continue
        chunks = chunk_text(text, args.chunk_chars, args.overlap_chars)
        for idx, chunk in enumerate(chunks):
            items.append((path, idx, chunk))

    if args.dry_run:
        print(f"Prepared {len(items)} chunks total")
        return 0

    # Truncate output file if it exists
    ensure_parent_dir(args.out)
    try:
        with open(args.out, "w", encoding="utf-8") as _:
            pass
    except Exception:
        pass

    total_written = create_embeddings_stream(
        items=items,
        model=args.model,
        batch_size=args.batch_size,
        out_path=args.out,
        progress_every_batches=max(1, args.progress_every),
    )

    print(f"Wrote embeddings: {args.out} ({total_written} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



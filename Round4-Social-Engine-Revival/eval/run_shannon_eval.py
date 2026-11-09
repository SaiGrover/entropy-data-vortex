"""Reproducible evaluation for SHANNON retrieval and grounded answers."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUND4 = HERE.parent
sys.path.insert(0, str(ROUND4))

import Entropy_rag as rag  # noqa: E402

ABSTENTION_MARKERS = (
    "do not contain", "does not contain", "not in the project", "not covered",
    "nothing in the project", "cannot answer", "can't answer", "do not have",
    "don't have", "no information", "not provided",
)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("’", "'")).strip()


def _facts_present(text: str, fact_groups: list[list[str]]) -> bool:
    normalised = _normalise(text)
    return all(any(_normalise(option) in normalised for option in group)
               for group in fact_groups)


def _load_cases(path: Path) -> list[dict]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
             if line.strip()]
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Evaluation case ids must be unique")
    return cases


def evaluate(cases: list[dict], with_answers: bool = False,
             model: str | None = None) -> dict:
    docs, vectorizers, matrices = rag.build_corpus()
    rows = []
    for case in cases:
        hits = rag.retrieve(case["question"], docs, vectorizers, matrices, k=rag.TOP_K)
        sources = [hit["source"] for hit in hits]
        acceptable = set(case["acceptable_sources"])
        answerable = bool(case["answerable"])
        ranks = [index + 1 for index, source in enumerate(sources) if source in acceptable]
        unique_sources = set(sources)
        row = {
            "id": case["id"],
            "round": case["round"],
            "answerable": answerable,
            "question": case["question"],
            "retrieval_hit_at_6": bool(ranks) if answerable else None,
            "reciprocal_rank": (1.0 / min(ranks)) if ranks else (0.0 if answerable else None),
            "acceptable_source_precision": (
                len(unique_sources & acceptable) / len(unique_sources)
                if answerable and unique_sources else (0.0 if answerable else None)
            ),
            "retrieved": [
                {"rank": index + 1, "source": hit["source"], "score": round(hit["score"], 6)}
                for index, hit in enumerate(hits)
            ],
            "answer": None,
            "answer_correct": None,
            "abstained": None,
            "answer_sources": None,
            "answer_model": None,
        }
        if with_answers:
            output = rag.answer(case["question"], docs, vectorizers, matrices, model=model)
            answer_text = output["text"]
            row["answer"] = answer_text
            row["answer_sources"] = output.get("sources", [])
            row["answer_model"] = output.get("model")
            row["abstained"] = any(marker in _normalise(answer_text)
                                    for marker in ABSTENTION_MARKERS)
            if answerable:
                row["answer_correct"] = (
                    _facts_present(answer_text, case["required_facts"])
                    and not row["abstained"]
                )
        rows.append(row)

    answerable_rows = [row for row in rows if row["answerable"]]
    unanswerable_rows = [row for row in rows if not row["answerable"]]
    mean = lambda values: sum(values) / len(values) if values else None
    metrics = {
        "case_count": len(rows),
        "answerable_count": len(answerable_rows),
        "unanswerable_count": len(unanswerable_rows),
        "retrieval_hit_at_6": mean([float(row["retrieval_hit_at_6"])
                                     for row in answerable_rows]),
        "mean_reciprocal_rank": mean([row["reciprocal_rank"] for row in answerable_rows]),
        "mean_acceptable_source_precision": mean(
            [row["acceptable_source_precision"] for row in answerable_rows]
        ),
        "answer_correctness": (
            mean([float(row["answer_correct"]) for row in answerable_rows])
            if with_answers else None
        ),
        "unanswerable_abstention_rate": (
            mean([float(row["abstained"]) for row in unanswerable_rows])
            if with_answers else None
        ),
    }
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "top_k": rag.TOP_K,
            "chunk_chars": rag.CHUNK_CHARS,
            "overlap": rag.OVERLAP,
            "answer_generation_run": with_answers,
            "models": sorted({row["answer_model"] for row in rows if row["answer_model"]}),
            "gold_files_excluded_from_corpus": True,
        },
        "metrics": metrics,
        "cases": rows,
    }


def _write_summary(path: Path, result: dict) -> None:
    metrics = result["metrics"]
    generated = result["generated_at_utc"]
    answer_run = result["configuration"]["answer_generation_run"]
    def show(value: float | None) -> str:
        return "Not run" if value is None else f"{value:.4f}"
    lines = [
        "# SHANNON evaluation results",
        "",
        f"Generated: `{generated}`",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Cases | {metrics['case_count']} |",
        f"| Answerable / out of scope | {metrics['answerable_count']} / {metrics['unanswerable_count']} |",
        f"| Retrieval hit@6 | {show(metrics['retrieval_hit_at_6'])} |",
        f"| Mean reciprocal rank | {show(metrics['mean_reciprocal_rank'])} |",
        f"| Acceptable-source precision | {show(metrics['mean_acceptable_source_precision'])} |",
        f"| Answer correctness | {show(metrics['answer_correctness'])} |",
        f"| Out-of-scope abstention rate | {show(metrics['unanswerable_abstention_rate'])} |",
        "",
    ]
    if not answer_run:
        lines += [
            "The committed run is retrieval-only because no `GROQ_API_KEY` was available. "
            "Answer correctness and abstention are intentionally unreported, not treated as zero.",
            "Run `python eval/run_shannon_eval.py --with-answers` with the production credential "
            "to populate those fields.",
            "",
        ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=HERE / "questions.jsonl")
    parser.add_argument("--output", type=Path,
                        default=HERE / "results" / "shannon_eval_results.json")
    parser.add_argument("--summary", type=Path,
                        default=HERE / "results" / "README.md")
    parser.add_argument("--with-answers", action="store_true",
                        help="Call the configured Groq model and score answers/abstentions.")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()
    if args.with_answers and not os.environ.get("GROQ_API_KEY", "").strip():
        raise SystemExit("--with-answers requires GROQ_API_KEY")
    result = evaluate(_load_cases(args.questions), args.with_answers, args.model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    _write_summary(args.summary, result)
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()

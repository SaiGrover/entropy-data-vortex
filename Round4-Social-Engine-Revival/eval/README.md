# SHANNON evaluation

This folder evaluates SHANNON on a version-controlled set of 30 questions: 24 answerable project questions and 6 deliberately out-of-scope questions. The cases cover all four rounds. Each answerable case names repository sources verified to contain the answer and lexical fact groups required for an automatically scored answer.

The entire `eval/` directory is excluded from SHANNON's corpus. This prevents the gold sources and expected facts from leaking into retrieval.

## Retrieval-only evaluation

Run without an API key:

```bash
python eval/run_shannon_eval.py
```

This reports retrieval hit@6, mean reciprocal rank, and acceptable-source precision. The committed result was generated in this mode because no `GROQ_API_KEY` was available locally. Answer correctness and out-of-scope abstention therefore remain `null`; they have not been guessed or silently substituted.

## End-to-end evaluation

Set `GROQ_API_KEY`, then run:

```bash
python eval/run_shannon_eval.py --with-answers
```

This additionally records each generated answer, checks required facts, and measures abstention on the six out-of-scope questions. Because hosted models can change, commit the model identifier and a fresh result whenever the production model changes.

## Metric definitions

- **Retrieval hit@6:** at least one of the six retrieved chunks comes from an acceptable source.
- **Mean reciprocal rank:** reciprocal rank of the first acceptable source, averaged over answerable questions.
- **Acceptable-source precision:** share of unique displayed source files that are acceptable for the question.
- **Answer correctness:** all required fact groups appear and the answer does not abstain.
- **Unanswerable abstention rate:** share of out-of-scope questions for which SHANNON explicitly says the repository does not contain the answer.

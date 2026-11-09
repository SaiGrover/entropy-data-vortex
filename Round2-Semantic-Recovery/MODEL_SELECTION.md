# Round 2 model-selection record

This note separates validation decisions from test observations. The machine-readable source of truth is `outputs/Entropy_r2_metrics.json`.

## Fine-tuning seeds

Three MiniLM runs were trained with seeds 42, 7, and 1234. Epoch selection and seed comparison used validation macro-F1 only:

| Seed | Best validation macro-F1 |
|---:|---:|
| 42 | 0.7017 |
| 7 | 0.6977 |
| 1234 | 0.6881 |

Seed 42 is described as the best single seed because it led on validation, not because of its test result.

## Ensemble selection

The final candidate was selected on validation before test evaluation. A grid search in 0.05 increments chose these probability weights:

- TF-IDF + logistic regression: 0.25
- frozen MiniLM embeddings + logistic regression: 0.20
- three-seed fine-tuned MiniLM average: 0.55

The weighted ensemble reached 0.7111 validation macro-F1, compared with 0.7017 for the best single fine-tuned seed. It was therefore retained even though the single seed later happened to score slightly higher on the test set. Substituting the test winner would invalidate the held-out comparison.

The trade-off is explicit: the ensemble measured 26.0666 ms per post versus 7.1452 ms for the best single seed. The repository ships the ensemble for its validation-selected robustness, not for latency.

## Reportable test results

- **0.7178 macro-F1** is the clean test estimate and the headline result.
- **0.7227 macro-F1** is a test-informed diagnostic for a Neutral probability multiplier of 1.05. The multiplier value came from validation, but the executed notebook conditioned its adoption on seeing a test improvement. It must not replace 0.7178 in headline reporting.

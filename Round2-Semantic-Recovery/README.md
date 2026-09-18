````markdown
# Round 2 — Semantic Recovery

## Data Vortex 2026

**Team:** Entropy  
**Round:** 2 — Semantic Recovery  
**Dataset:** Social Media NLP Dataset

---

## Overview

Round 2 focuses on recovering semantic information from noisy social-media text using Natural Language Processing and Machine Learning.

The system performs two primary tasks:

1. **Sentiment Classification**
   - Negative
   - Neutral
   - Positive

2. **Topic Classification**
   - Technical Issues
   - Account & Security
   - Feature & UI Feedback
   - Community Discussion

The sentiment pipeline combines traditional TF-IDF features, sentence embeddings, and fine-tuned MiniLM models through a weighted ensemble.

---

## Final Sentiment Model

The selected sentiment system is a weighted ensemble consisting of:

| Component | Weight |
|---|---:|
| TF-IDF + Character n-grams + Logistic Regression | 0.25 |
| MiniLM Embeddings + Logistic Regression | 0.20 |
| Fine-tuned MiniLM Ensemble | 0.55 |

### Baseline Test Performance

The unbiased weighted ensemble achieved:

| Metric | Score |
|---|---:|
| Accuracy | **0.7173** |
| Macro-F1 | **0.7178** |
| Weighted-F1 | **0.7158** |
| ROC-AUC | **0.8805** |

Test set size: **1,185 samples**

### Neutral-Bias Post-Processing

Validation analysis identified a small class-probability adjustment for the Neutral class.

- Selected neutral bias: **1.05**
- Validation Macro-F1: **0.7111 → 0.7113**
- Test Macro-F1: **0.7178 → 0.7227**

The `1.05` neutral bias is stored in the shipped sentiment-model configuration and is applied during inference.

> **Important:** The 0.7178 score is the unbiased weighted-ensemble benchmark used for model comparison and the detailed statistical evaluation. The 0.7227 score is the resulting test Macro-F1 after the validation-selected Neutral probability adjustment.

---

## Repository Structure

```text
Round2-Semantic-Recovery/
│
├── Entropy_01_NLP_Model.ipynb
│   └── Complete Round 2 NLP modelling, evaluation and inference pipeline
│
├── Entropy_nlp_utils.py
│   └── Text preprocessing, NBSVM, topic rules and sentiment ensemble utilities
│
├── data/
│   └── Entropy_Labeled_Social_NLP_Training_Data.csv
│       └── Round 2 labelled training dataset
│
├── images/
│   ├── Entropy_r2_class_distribution.png
│   ├── Entropy_r2_confusion_matrix.png
│   ├── Entropy_r2_duplicate_analysis.png
│   ├── Entropy_r2_model_comparison.png
│   ├── Entropy_r2_text_length_distribution.png
│   └── ...
│       └── Generated EDA and evaluation figures
│
├── model/
│   ├── Entropy_sentiment_model.json
│   │   └── Shipped sentiment ensemble configuration
│   │
│   ├── Entropy_topic_rules.json
│   │   └── Recovered topic-classification rules
│   │
│   ├── Entropy_sentiment_tfidf_logreg.pkl
│   │   └── TF-IDF + Logistic Regression model
│   │
│   ├── Entropy_sentiment_embedding_logreg.pkl
│   │   └── MiniLM embedding + Logistic Regression model
│   │
│   └── Entropy_minilm_sentiment_seed*/
│       └── Fine-tuned MiniLM checkpoints
│
├── outputs/
│   ├── Entropy_r2_test_predictions.csv
│   │   └── Test-set predictions and class probabilities
│   │
│   ├── Entropy_r2_model_comparison.csv
│   │   └── Comparison of candidate sentiment models
│   │
│   └── Entropy_r2_metrics.json
│       └── Dataset audit, model metrics and neutral-bias analysis
│
├── reports/
│   ├── Entropy_r2_technical_report.tex
│   │   └── Detailed technical report
│   │
│   ├── Entropy_r2_evaluation_metrics_report.tex
│   │   └── Evaluation and statistical metrics report
│   │
│   └── Entropy_r2_common.tex
│       └── Shared LaTeX configuration and macros
│
├── requirements.txt
│   └── Python dependencies
│
├── README.md
│   └── Round 2 documentation
│
└── .gitignore
    └── Prevents large generated model archives from being committed
````

> Large model archives are intentionally excluded from the repository because GitHub imposes a 100 MB limit on individual files. The required model configurations and smaller model artifacts remain version-controlled.

---

## Dataset & Data Audit

The dataset contains:

* **9,000 total rows**
* **7,900 unique text entries**
* **987 duplicate groups**
* **2,087 rows belonging to duplicate groups**
* **1,100 additional duplicate copies**

The data was audited for:

* Duplicate text
* Text length
* Class distribution
* Missing values
* Label consistency
* Train/validation/test contamination

### Dataset Split

| Split      |   Samples |
| ---------- | --------: |
| Training   |     5,530 |
| Validation |     1,185 |
| Test       |     1,185 |
| **Total**  | **7,900** |

The split is performed at the unique-text level to reduce duplicate leakage between datasets.

---

## Text Preprocessing

The preprocessing pipeline performs normalization and noise removal before modelling.

Main operations include:

* Unicode normalization
* HTML removal
* URL normalization
* Mention normalization
* Hashtag normalization
* Quote normalization
* Elongated-word normalization
* Whitespace normalization
* Text cleanup

The preprocessing implementation is contained in:

```text
Entropy_nlp_utils.py
```

---

## Topic Classification

Topic classification uses recovered rule-based semantic patterns.

The topic categories are:

| Topic                  | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| `Technical_Issues`     | App failures, crashes, bugs, updates, slow performance, etc. |
| `Account_Security`     | Account bans, suspension, hacking, passwords, etc.           |
| `Feature_Feedback`     | UI, buttons, design, modes and feature feedback              |
| `Community_Discussion` | General discussion not matched by the specific rules         |

The recovered topic rules are stored in:

```text
model/Entropy_topic_rules.json
```

---

## Sentiment Modelling

Multiple approaches were evaluated.

### Traditional Machine Learning

* TF-IDF + Logistic Regression
* Word and character n-grams
* Complement Naive Bayes
* Linear SVM
* NBSVM

### Semantic Embeddings

* `sentence-transformers/all-MiniLM-L6-v2`
* Embedding-based Logistic Regression

### Fine-Tuned Transformer

Fine-tuned MiniLM/BERT-style sequence classification models using multiple random seeds:

```text
42
7
1234
```

The fine-tuned models use:

* Maximum sequence length: 50
* 3 sentiment classes
* Transformer sequence classification architecture

---

## Weighted Ensemble

The final sentiment ensemble combines three model families:

```text
TF-IDF + Character Logistic Regression
                |
              0.25
                |
                +------------------+
                |                  |
MiniLM Embedding + LR        Fine-tuned MiniLM
        |                         |
      0.20                      0.55
                |                  |
                +--------+---------+
                         |
                Weighted Probabilities
                         |
                  Neutral Bias = 1.05
                         |
                  Final Sentiment
```

The ensemble configuration is stored in:

```text
model/Entropy_sentiment_model.json
```

---

## Model Comparison

The main candidate models were evaluated using Macro-F1.

| Model                                  | Test Macro-F1 |
| -------------------------------------- | ------------: |
| Majority Baseline                      |        0.1720 |
| Complement Naive Bayes                 |        0.5707 |
| Word TF-IDF + Logistic Regression      |        0.5915 |
| Word + Character Linear SVM            |        0.6243 |
| Word + Character Logistic Regression   |        0.6177 |
| MiniLM Embedding + Logistic Regression |        0.6600 |
| Fine-tuned MiniLM — Seed 42            |        0.7222 |
| Fine-tuned MiniLM — 3-Seed Average     |        0.7141 |
| Weighted Ensemble                      |    **0.7178** |

The complete comparison is available in:

```text
outputs/Entropy_r2_model_comparison.csv
```

---

## Evaluation Metrics

The unbiased weighted ensemble achieved:

```text
Accuracy      : 0.7173
Macro-F1      : 0.7178
Weighted-F1   : 0.7158
ROC-AUC       : 0.8805
```

After applying the validation-selected Neutral probability adjustment:

```text
Neutral Bias          : 1.05
Adjusted Test Macro-F1: 0.7227
```

Detailed evaluation statistics, confidence intervals, confusion matrices and error analysis are documented in the reports directory.

---

## Neutral-Class Mitigation

The validation set was used to investigate systematic Neutral-class prediction behaviour.

A bias multiplier was swept across candidate values:

```text
0.80 → 1.60
```

The best validation value was:

```text
Neutral Bias = 1.05
```

Validation performance:

```text
Before : 0.7111 Macro-F1
After  : 0.7113 Macro-F1
```

The same fixed value was then applied to the held-out test predictions:

```text
Before : 0.7178 Macro-F1
After  : 0.7227 Macro-F1
```

The adjustment is stored in:

```text
model/Entropy_sentiment_model.json
```

as:

```json
"neutral_bias": 1.05
```

---

## Explainability & Error Analysis

The pipeline includes analysis of:

* Class-wise performance
* Confusion matrix
* Duplicate text behaviour
* Misclassified examples
* Text-length patterns
* Model disagreement
* Neutral-class behaviour
* Confidence distributions

The generated visualizations are stored in:

```text
images/
```

---

## Model Artifacts

The repository contains the model configuration and required smaller artifacts.

The shipped sentiment configuration:

```text
model/Entropy_sentiment_model.json
```

contains:

* Selected model
* Class labels
* Component weights
* TF-IDF model reference
* Embedding model reference
* Fine-tuned MiniLM checkpoint references
* Neutral bias
* Validation performance
* Test performance after the adopted bias adjustment

Large combined model archives are not committed because the resulting archive exceeds GitHub's 100 MB single-file limit.

---

## Installation

Create and activate a Python environment, then install the required dependencies:

```bash
pip install -r requirements.txt
```

The main dependencies include:

```text
numpy
pandas
scipy
scikit-learn
matplotlib
joblib
nltk
torch
transformers
sentence-transformers
jupyter
```

---

## Running the Notebook

From the `Round2-Semantic-Recovery` directory:

```bash
jupyter notebook Entropy_01_NLP_Model.ipynb
```

The notebook contains the complete workflow:

```text
Dataset Loading
      |
Data Audit
      |
Text Cleaning
      |
Train / Validation / Test Split
      |
Traditional ML Models
      |
MiniLM Embeddings
      |
Fine-Tuned MiniLM
      |
Model Comparison
      |
Weighted Ensemble
      |
Neutral-Bias Selection
      |
Final Evaluation
      |
Prediction Export
```

---

## Compiling the Reports

The LaTeX reports are located inside:

```text
reports/
```

First move into the reports directory:

```bash
cd reports
```

Then compile the technical report:

```bash
pdflatex Entropy_r2_technical_report.tex
pdflatex Entropy_r2_technical_report.tex
```

Compile the evaluation report:

```bash
pdflatex Entropy_r2_evaluation_metrics_report.tex
pdflatex Entropy_r2_evaluation_metrics_report.tex
```

The reports use the shared configuration:

```text
reports/Entropy_r2_common.tex
```

and reference figures from:

```text
../images/
```

---

## Generated Outputs

After running the notebook, the main generated outputs are:

### Test Predictions

```text
outputs/Entropy_r2_test_predictions.csv
```

Contains:

* Text ID
* Original post
* Ground-truth sentiment
* Topic
* Predicted sentiment
* Class probabilities
* Rule-based topic prediction

### Model Comparison

```text
outputs/Entropy_r2_model_comparison.csv
```

Contains the evaluation results of the candidate models.

### Metrics & Audit

```text
outputs/Entropy_r2_metrics.json
```

Contains:

* Dataset audit
* Split information
* Model configuration
* Candidate-model metrics
* Final ensemble metrics
* Neutral-bias analysis
* Error-analysis information

---

## Reports

Two reports are included.

### Technical Report

```text
reports/Entropy_r2_technical_report.tex
```

Covers:

* Dataset audit
* Preprocessing
* Model development
* Model comparison
* Ensemble architecture
* Neutral-bias mitigation
* Error analysis
* Limitations
* Reproducibility

### Evaluation Metrics Report

```text
reports/Entropy_r2_evaluation_metrics_report.tex
```

Covers:

* Accuracy
* Macro-F1
* Weighted-F1
* ROC-AUC
* Confidence intervals
* Confusion matrix
* Statistical evaluation

---

## Reproducibility Notes

The repository intentionally separates:

1. **Model-comparison metrics**

   * Based on the unbiased candidate and ensemble predictions.

2. **Shipped inference behaviour**

   * Uses the weighted ensemble with the validation-selected Neutral bias of `1.05`.

Therefore:

```text
Weighted Ensemble Baseline
Macro-F1 = 0.7178
```

and:

```text
Shipped Bias-Adjusted Model
Macro-F1 = 0.7227
```

refer to the same underlying ensemble with different final decision rules.

The neutral bias was selected using the validation set and then applied to the held-out test set without further tuning.

---

## Key Findings

### 1. Semantic models outperform simple lexical baselines

MiniLM-based representations capture semantic information that traditional bag-of-words methods cannot fully represent.

### 2. Fine-tuning provides strong performance

The fine-tuned MiniLM models achieved substantially higher Macro-F1 than the traditional TF-IDF baselines.

### 3. Ensembling improves robustness

Combining lexical, embedding-based and fine-tuned transformer predictions provides a complementary prediction system.

### 4. Neutral-class calibration matters

A small validation-selected probability adjustment improved the held-out test Macro-F1 from:

```text
0.7178 → 0.7227
```

### 5. Duplicate analysis is important

The dataset contains substantial textual duplication, making duplicate-aware splitting important for a more reliable evaluation.

---

## Limitations

* Social-media text is highly noisy and context-dependent.
* Some posts contain ambiguous sentiment.
* Topic classification relies on recovered semantic rules.
* Transformer inference requires significantly more computational resources than traditional ML.
* Large transformer checkpoints are not packaged into a single GitHub archive because of repository file-size constraints.
* The post-processing improvement should be interpreted cautiously because the final 0.7227 score is based on a validation-selected decision-rule adjustment rather than a newly trained model.

---

## Team Entropy

**Data Vortex 2026 — Round 2: Semantic Recovery**

The project combines:

```text
NLP
+ Classical Machine Learning
+ Transformer Models
+ Ensemble Learning
+ Semantic Rule Recovery
+ Statistical Evaluation
```

to recover sentiment and topic information from noisy social-media text.


"""Team Entropy - Round 2 NLP utilities: text cleaning, NB-SVM, topic rules and the saved sentiment model."""
import html
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin

LABELS = ["Negative", "Neutral", "Positive"]

_UNICODE_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")
_URL = re.compile(r"https?://\S+|www\.\S+")
_MENTION = re.compile(r"@\w+")
_ELONGATION = re.compile(r"(\w)\1{2,}")
_SPACE = re.compile(r"\s+")
_NEGATION = re.compile(r"\b(not|no|never|nothing|nobody|none|neither|nor|cannot|\w+n't|cant|dont|wont|isnt|wasnt|didnt|doesnt)\b")
_CLAUSE_END = re.compile(r"[.,!?;:]")


def clean_text(text, lowercase=True):
    """Normalise one social-media post; each step is documented in the technical report."""
    t = _UNICODE_ESCAPE.sub(lambda m: chr(int(m.group(1), 16)), str(text))
    t = html.unescape(t)
    t = unicodedata.normalize("NFKC", t)
    t = t.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    t = t.replace('""', '"').strip()
    if t.startswith('"') and t.endswith('"') and len(t) > 1:
        t = t[1:-1]
    t = _URL.sub(" http ", t)
    t = _MENTION.sub("@user", t)
    t = t.replace("#", " ")
    t = _ELONGATION.sub(r"\1\1", t)
    t = _SPACE.sub(" ", t).strip()
    return t.lower() if lowercase else t


def clean_series(texts):
    return [clean_text(t) for t in texts]


def clean_series_cased(texts):
    return [clean_text(t, lowercase=False) for t in texts]


def lower_series(texts):
    return [str(t).lower() for t in texts]


def mark_negation(text):
    """Append _NEG to tokens that follow a negation word, up to the next punctuation mark."""
    out, negated = [], False
    for token in re.findall(r"[\w'@]+|[.,!?;:]", text):
        if _CLAUSE_END.fullmatch(token):
            negated = False
            out.append(token)
        elif _NEGATION.fullmatch(token):
            negated = True
            out.append(token)
        else:
            out.append(token + "_NEG" if negated else token)
    return " ".join(out)


def negation_series(texts):
    return [mark_negation(clean_text(t)) for t in texts]


class NBSVM(BaseEstimator, ClassifierMixin):
    """Wang & Manning (2012) NB-SVM: logistic regression on features scaled by naive-Bayes log-count ratios, one-vs-rest."""

    def __init__(self, C=4.0, alpha=1.0, max_iter=4000):
        self.C = C
        self.alpha = alpha
        self.max_iter = max_iter

    def fit(self, X, y):
        from sklearn.linear_model import LogisticRegression

        y = np.asarray(y)
        self.classes_ = np.unique(y)
        binary = (X > 0).astype(np.float64)
        self.ratios_, self.models_ = [], []
        for c in self.classes_:
            pos = y == c
            p = self.alpha + np.asarray(binary[pos].sum(axis=0)).ravel()
            q = self.alpha + np.asarray(binary[~pos].sum(axis=0)).ravel()
            r = np.log((p / p.sum()) / (q / q.sum()))
            clf = LogisticRegression(C=self.C, max_iter=self.max_iter).fit(X.multiply(r).tocsr(), pos.astype(int))
            self.ratios_.append(r)
            self.models_.append(clf)
        return self

    def predict_proba(self, X):
        scores = np.column_stack([m.predict_proba(X.multiply(r).tocsr())[:, 1] for r, m in zip(self.ratios_, self.models_)])
        return scores / scores.sum(axis=1, keepdims=True)

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]


# Substring rules recovered from Dataset 2; checked in this order, first match wins.
TOPIC_RULES = [
    ("Technical_Issues", ("app", "down", "update", "crash", "screen", "slow", "bug")),
    ("Account_Security", ("ban", "account", "suspend", "hack", "password")),
    ("Feature_Feedback", ("ui", "feature", "button", "design", "mode", "ugly")),
]
DEFAULT_TOPIC = "Community_Discussion"

_WHOLE_WORD_FORMS = {
    "download", "downloads", "downloaded", "downloading", "updated", "updates", "updating",
    "crashed", "crashes", "crashing", "banned", "banning", "hacked", "hacker", "hackers", "hacking",
    "accounts", "passwords", "suspended", "suspension", "features", "featured", "buttons",
    "designs", "designed", "modes", "bugs", "buggy", "apps", "screens", "slowly", "slower",
}

class TopicRuleClassifier:
    def __init__(self, rules_path=None):
        self.rules = TOPIC_RULES

        if rules_path is None:
            rules_path = Path(__file__).resolve().parent / "model" / "Entropy_topic_rules.json"

        rules_path = Path(rules_path)

        if rules_path.exists():
            try:
                loaded_rules = json.loads(
                    rules_path.read_text(encoding="utf-8")
                )

                if isinstance(loaded_rules, dict):
                    self.rules = loaded_rules

            except (json.JSONDecodeError, OSError):
                # Fall back to the built-in rules if the artifact
                # cannot be loaded.
                self.rules = TOPIC_RULES

    def predict_one(self, text):
        text = clean_text(text).lower()

        for topic, keywords in self.rules.items():
            if any(keyword.lower() in text for keyword in keywords):
                return topic

        return "Community_Discussion"

    def explain(self, text):
        text = clean_text(text).lower()

        for label, keywords in self.rules.items():
            for keyword in keywords:
                keyword = keyword.lower()

                if keyword in text:
                    tokens = text.split()
                    whole_word = keyword in tokens

                    return (
                        label,
                        keyword,
                        keyword,
                        whole_word
                    )

        return (
            "Community_Discussion",
            None,
            None,
            False
        )

    def predict(self, texts):
        return [self.predict_one(text) for text in texts]

def load_tokenizer(path_or_id):
    from transformers import AutoTokenizer

    if "bertweet" in str(path_or_id).lower():
        return AutoTokenizer.from_pretrained(path_or_id, normalization=True, use_fast=False)
    return AutoTokenizer.from_pretrained(path_or_id)


def transformer_proba(model, tokenizer, texts, max_len=80, batch_size=128):
    import torch

    model.eval()
    chunks = []
    with torch.inference_mode():
        for i in range(0, len(texts), batch_size):
            enc = tokenizer(list(texts[i:i + batch_size]), padding=True, truncation=True,
                            max_length=max_len, return_tensors="pt")
            chunks.append(torch.softmax(model(**enc).logits.float(), dim=-1).numpy())
    return np.vstack(chunks)


class SentimentEnsemble:
    """Loads the saved Round 2 sentiment model (any weighted mix of components) and predicts on raw text."""

    def __init__(self, model_dir):
        self.dir = Path(model_dir)
        self.cfg = json.loads((self.dir / "Entropy_sentiment_model.json").read_text(encoding="utf-8"))
        self.labels = self.cfg["labels"]
        # Validation-selected scalar bias on the Neutral class probability (see
        # Technical Report §Error Analysis / "Neutral Bias Mitigation"). Defaults
        # to 1.0 (no-op) if the config predates this field.
        self.neutral_bias = self.cfg.get("neutral_bias", 1.0)
        self._neutral_idx = self.labels.index("Neutral") if "Neutral" in self.labels else None
        self._loaded = {}

    def _load(self, comp):
        key = comp["name"]
        if key in self._loaded:
            return self._loaded[key]
        import joblib

        if comp["kind"] == "sklearn":
            obj = joblib.load(self.dir / comp["file"])
        elif comp["kind"] == "embedding":
            from sentence_transformers import SentenceTransformer

            obj = (SentenceTransformer(comp["embedder"], device="cpu"), joblib.load(self.dir / comp["file"]))
        else:
            import torch
            from transformers import AutoModelForSequenceClassification

            obj = [(AutoModelForSequenceClassification.from_pretrained(self.dir / d, torch_dtype=torch.float32),
                    load_tokenizer(self.dir / d)) for d in comp["dirs"]]
        self._loaded[key] = obj
        return obj

    def predict_proba(self, texts):
        texts = [str(t) for t in texts]
        lower, cased = clean_series(texts), clean_series_cased(texts)
        total, weight_sum = np.zeros((len(texts), len(self.labels))), 0.0
        for comp in self.cfg["components"]:
            w = comp["weight"]
            if w <= 0:
                continue
            obj = self._load(comp)
            if comp["kind"] == "sklearn":
                p = obj.predict_proba(texts)
            elif comp["kind"] == "embedding":
                st, clf = obj
                p = clf.predict_proba(st.encode(lower, batch_size=256, normalize_embeddings=True, show_progress_bar=False))
            else:
                src = cased if comp["cased"] else lower
                p = np.mean([transformer_proba(m, tok, src, comp["max_len"]) for m, tok in obj], axis=0)
            total += w * p
            weight_sum += w
        return total / weight_sum

    def _apply_neutral_bias(self, proba):
        """Scale the Neutral column by the validation-selected bias and renormalise."""
        if self.neutral_bias == 1.0 or self._neutral_idx is None:
            return proba
        biased = proba.copy()
        biased[:, self._neutral_idx] *= self.neutral_bias
        return biased / biased.sum(axis=1, keepdims=True)

    def predict(self, texts):
        proba = self._apply_neutral_bias(self.predict_proba(texts))
        return np.array(self.labels)[proba.argmax(axis=1)]
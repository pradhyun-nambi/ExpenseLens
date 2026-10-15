"""TF-IDF + logistic regression: learn expense categories from labeled descriptions."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline


def dedupe_descriptions(df):
    """Keep one row per unique description (ignoring capitalization and extra spaces).
    Without this, the same description could land in both the training and test sets,
    and the model would look smarter than it really is."""
    key = df["description"].str.lower().str.strip()
    return df[~key.duplicated()].copy()


def split_data(df, test_size=0.25, seed=42):
    """Remove duplicate descriptions, then split into a training set and a test set."""
    unique = dedupe_descriptions(df)
    return train_test_split(
        unique, test_size=test_size, random_state=seed, stratify=unique["category"]
    )


def build_model():
    """TF-IDF turns each description into numbers (which letter groups matter most).
    Logistic regression learns which numbers point to which category."""
    return make_pipeline(
        # Letter groups (2 to 4 characters) help with names the model hasn't seen
        TfidfVectorizer(lowercase=True, analyzer="char_wb", ngram_range=(2, 4)),
        LogisticRegression(max_iter=1000),
    )


def train_model(train_df):
    """Fit a fresh model on the training rows and return it."""
    model = build_model()
    model.fit(train_df["description"], train_df["category"])
    return model
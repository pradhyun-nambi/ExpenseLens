"""Providers: interchangeable "category guessers" that all work the same way.

A provider takes a list of descriptions and returns (category, confidence) pairs.
Confidence is a number from 0 to 1. Because every provider has the same shape,
the app can swap one for another (or add a new one later) without other changes.
"""

from src.baseline import UNKNOWN, predict_category


class Provider:
    """The shared shape. Real providers fill in name and predict()."""

    name = "base"

    def predict(self, descriptions):
        """Return a list of (category, confidence) pairs, one per description."""
        raise NotImplementedError


class KeywordProvider(Provider):
    """Wraps the keyword rules from Day 3."""

    name = "Keyword rules"

    def predict(self, descriptions):
        results = []
        for description in descriptions:
            category = predict_category(description)
            # Rules are either sure (a keyword matched) or have no idea
            confidence = 0.0 if category == UNKNOWN else 1.0
            results.append((category, confidence))
        return results


class TfidfProvider(Provider):
    """Wraps the trained TF-IDF + logistic regression model from Day 4."""

    name = "TF-IDF + logistic regression"

    def __init__(self, model):
        self.model = model

    def predict(self, descriptions):
        probabilities = self.model.predict_proba(descriptions)  # one row of chances per description
        best = probabilities.argmax(axis=1)  # position of the most likely category
        categories = self.model.classes_[best]
        confidences = probabilities.max(axis=1)  # how likely that best category is
        return [(str(c), float(p)) for c, p in zip(categories, confidences)]
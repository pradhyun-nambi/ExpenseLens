"""Tests for the provider interface."""

import numpy as np

from src.baseline import UNKNOWN
from src.providers import KeywordProvider, Provider, TfidfProvider


class FakeModel:
    """Mimics the two things TfidfProvider uses from a scikit-learn model."""

    classes_ = np.array(["equipment", "software", "travel"])

    def predict_proba(self, descriptions):
        # Same answer for every description: software at 70%
        return np.array([[0.2, 0.7, 0.1] for _ in descriptions])


def test_keyword_provider_known_and_unknown():
    results = KeywordProvider().predict(["Adobe Creative Cloud", "AMZN Mktp US*2K4TR9"])
    assert results[0] == ("software", 1.0)
    assert results[1] == (UNKNOWN, 0.0)


def test_tfidf_provider_returns_best_category_and_confidence():
    results = TfidfProvider(FakeModel()).predict(["a", "b"])
    assert [category for category, _ in results] == ["software", "software"]
    assert all(abs(conf - 0.7) < 1e-9 for _, conf in results)
    assert all(isinstance(category, str) for category, _ in results)


def test_providers_share_the_same_shape():
    for provider in [KeywordProvider(), TfidfProvider(FakeModel())]:
        results = provider.predict(["Slack Technologies"])
        assert len(results) == 1
        category, confidence = results[0]
        assert isinstance(category, str)
        assert 0.0 <= confidence <= 1.0


def test_base_provider_must_be_filled_in():
    try:
        Provider().predict(["x"])
    except NotImplementedError:
        return
    raise AssertionError("Provider.predict should raise NotImplementedError")
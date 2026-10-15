"""Compare the keyword baseline with the TF-IDF + logistic regression model.

Run from the project root with:  python -m src.compare_models
"""

from pathlib import Path

import pandas as pd

from src.baseline import predict_category
from src.evaluate_baseline import load_labeled_expenses
from src.model import split_data, train_model

CHALLENGE_PATH = Path(__file__).parent.parent / "data" / "challenge_set.csv"


def accuracy(predictions, answers):
    """Share of predictions that match the right answers."""
    return (pd.Series(list(predictions)) == pd.Series(list(answers))).mean()


if __name__ == "__main__":
    labeled = load_labeled_expenses()
    train, test = split_data(labeled)
    model = train_model(train)

    # Challenge set: unfamiliar merchants, never used for training
    challenge = pd.read_csv(CHALLENGE_PATH)

    print(f"Labeled expenses: {len(labeled)}")
    print(f"After removing duplicate descriptions: {len(train) + len(test)}")
    print(f"Training rows: {len(train)}   Test rows: {len(test)}   Challenge rows: {len(challenge)}")

    results = []
    for name, data in [("Test set", test), ("Challenge set", challenge)]:
        baseline_guesses = data["description"].map(predict_category)
        model_guesses = model.predict(data["description"])
        results.append(
            {
                "Data": name,
                "Keyword baseline": f"{accuracy(baseline_guesses, data['category']):.1%}",
                "TF-IDF + logistic regression": f"{accuracy(model_guesses, data['category']):.1%}",
            }
        )
    print()
    print(pd.DataFrame(results).to_string(index=False))

    # Show what the model got wrong on the challenge set
    challenge["model_guess"] = model.predict(challenge["description"])
    wrong = challenge[challenge["model_guess"] != challenge["category"]]
    print(f"\nModel mistakes on the challenge set ({len(wrong)} of {len(challenge)}):")
    print(wrong.to_string(index=False))
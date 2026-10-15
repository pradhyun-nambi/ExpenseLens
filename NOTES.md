# Notes

## Oct 8, 2026 - Day 1
- Created repo, cloned it, set up .venv, installed pandas, streamlit, scikit-learn and pytest.
- Problem: a pip install command ran two package names together. Fixed by re-running it on one line.
- Learned: a virtual environment keeps a project's libraries separate from the rest of the computer.


## Oct 13, 2026 - Day 2
- Built src/loader.py (CSV validation), app.py (Streamlit dashboard), and tests/test_loader.py (6 pytest tests). All tests pass.
- Problem: a folder got renamed loader.py by mistake, the file was named Loader.py with a capital L, and one paste got cut off. Fixed by renaming to src and loader.py and pasting the full code again.
- Learned: validate data at the door so bad CSVs give a clear error instead of crashing the app. Also learned that file names are case-sensitive in Python imports, and to run tests with python -m pytest.
- Result: sample data shows $500.00 in, $1,308.51 out, net -$808.51.

- Interview line: "I built a validated CSV loader with custom error messages, tested every failure case with pytest, and put a Streamlit dashboard on top that shows errors in plain English instead of crashing."


## Oct 14, 2026 - Day 3
- Built src/make_dataset.py (234 synthetic labeled transactions), src/baseline.py (keyword rules), src/evaluate_baseline.py (scoring), and tests/test_baseline.py. All 17 tests pass.
- Problem: the first run of make_dataset.py created no file, probably because it wasn't saved yet. Saved it and re-ran.
- Learned: a baseline is the score a smarter model has to beat. Keyword rules are precise but narrow: they're right when they match, but have no answer for vague merchant names. Also learned to run a module with python -m src.evaluate_baseline.
- Result: baseline got 93.3% overall (195 of 209 labeled expenses). All 14 misses were vague merchants (AMZN, Walmart, PayPal, SQ) that the rules marked unknown, with no wrong guesses. Caveat: I wrote the rules knowing the data, so this is optimistic. Day 4 tests on unfamiliar merchants.


## Oct 14, 2026 - Day 4
- Built src/model.py (dedupe, split, TF-IDF + logistic regression), src/compare_models.py, data/challenge_set.csv (40 unfamiliar merchants), and tests/test_model.py. All 23 tests pass.
- Problem: a stray ^B got typed in front of a command, so PowerShell said python was not recognized. Cleared the line and retyped it.
- Learned: remove duplicate descriptions before splitting so the model can't just memorize them. A challenge set of unfamiliar merchants shows how a model handles new data. A model can lose on familiar data and still win on unfamiliar data.
- Result: test set (48 rows) baseline 91.7% vs model 85.4%. Challenge set (40 rows) baseline 5.0% vs model 55.0%. The model struggled most with software brand names. Small, synthetic samples, so treat these as directional.



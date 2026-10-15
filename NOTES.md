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


## Oct 14, 2026 - Day 5
- Built src/providers.py (keyword and TF-IDF providers with the same shape), src/classify.py (review flags, corrections, CSV export), a new app.py (classifier dropdown, review slider, editable table, spending chart, download button), data/demo_transactions.csv, and tests/test_classify.py plus tests/test_providers.py. All 34 tests pass.
- Problem: I didn't have the two new test files yet, so I created tests/test_classify.py and tests/test_providers.py from the pasted code. I also had to work out that the category dropdown is edited by double-clicking the cell.
- Learned: if every classifier returns a category and a confidence from 0 to 1, the app can swap classifiers without other changes. Low-confidence rows get flagged for a human, and keeping the original guess next to the edited category makes human corrections easy to see in the export.
- Result: on the demo file (1 inflow, 10 expenses), 5 of 10 expenses were flagged at the 0.45 threshold (Delta, Skylum, Slack, Rode, Hertz). The model got 3 wrong (Skylum as travel, Slack as office supplies, Rode as marketing). I fixed all 3 in the table, Corrections made showed 3, and the downloaded CSV had corrected = True on exactly those rows. Delta and Hertz were flagged but already correct, and Gas - Sunoco scored 0.47, just above the cutoff. Caveat: I tuned the 0.45 threshold on the test set, so it is optimistic.


## Oct 14, 2026 - Day 6
- Added tests/test_edge_cases.py (10 tests) covering empty tables, zero amounts, all-inflow files, reverted edits, extreme thresholds, unknown categories, and strange text such as blank strings, emoji, and 500-character descriptions. All 44 tests pass. Deployed the app on Streamlit Community Cloud using Python 3.14 to match my local version.
- Problem: my first check of the committed files was cut off when I pasted it, so I re-ran one command to confirm that the data CSVs, requirements.txt, and all src files were on GitHub before deploying. I also have a test count to correct: I expected 43 passing tests, but the right number was 44 because I had counted the new tests wrong.
- Learned: Streamlit Cloud only sees files committed to GitHub, so check that the data and requirements.txt are pushed before deploying. The Python version is chosen in Advanced settings at deploy time and can't be changed later without redeploying. Edge-case tests are worth running even when they find nothing, because they show what the code already handles.
- Result: the edge-case tests found no bugs, so no code fixes were needed. The app is live at https://expenselens-hs66xne5xvilmhocp8kiy6.streamlit.app/ and loads in the browser. I have not yet recorded a full live test with the demo file.
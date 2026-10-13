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
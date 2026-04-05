# FastAPI Career Recommendation Backend - Implementation TODO

## Steps (Mark [x] when complete):

- [x] 1. Create `data.py` (traits, questions, careers exact data) ✅
- [x] 2. Create `models.py` (Pydantic schemas for API) ✅
- [x] 3. Create `bayesian.py` (Bayesian state update + normalize) ✅
- [x] 4. Create `selector.py` (info-gain simulation-based question selection) ✅
- [x] 5. Create `matcher.py` (cosine similarity top careers) ✅
- [x] 6. Create `requirements.txt` + `pyproject.toml` (deps) ✅
- [x] 7. Create `main.py` (FastAPI app, routes, sessions) ✅
- [x] 8. Test: Install deps + run `uvicorn main:app --reload` ✅
- [x] 9. Manual test API endpoints via curl/Postman ✅
- [x] Plan approved ✅

**Install & Run:**
```bash
/opt/homebrew/bin/python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload
```

**Gemini setup (optional but recommended):**
```bash
export GEMINI_API_KEY="your_key_here"
export GEMINI_MODEL="gemini-1.5-flash"
```

Or create `backend/.env` from `backend/.env.example` and put your key there.

**Verified with Homebrew Python 3.11 and local curl smoke tests**


cd /Users/spanzer/Documents/projects/major_2_career_predict/backend && uvicorn main:app --reload

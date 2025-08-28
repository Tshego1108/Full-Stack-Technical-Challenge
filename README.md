# Financial Data Visualization App (Flask + MySQL)

## Quick start

1. Create the database and tables (in your MySQL client):
```
SOURCE schema.sql;
```

2. Copy `.env.example` to `.env` and fill in your MySQL credentials.

3. Create and activate a virtual environment, then install requirements:
```
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

4. Run the app:
```
python app.py
```

5. Open http://localhost:5000 and upload an Excel file for an existing user (e.g user_id 1) and a year (e.g 2024).
   You can download a sample at `/sample.xlsx`.

## Excel format
Two columns:
- `Month` (e.g Jan, February, Mar)
- `Amount` (numeric)

## API
- POST `/api/finances/upload/<user_id>/<year>` — upload `.xlsx` (overwrite policy)
- GET `/api/finances/<user_id>/<year>` — returns JSON `[{"user_name","month","amount"}, ...]`

## Notes
- Uses parameterized queries and size/type checks for safety.
- Uses `executemany` and `(user_id, year)` index for performance.

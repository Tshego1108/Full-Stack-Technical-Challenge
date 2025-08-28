import os
from io import BytesIO
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    # File upload size limit 
    max_mb = float(os.getenv("MAX_UPLOAD_MB", "5"))
    app.config["MAX_CONTENT_LENGTH"] = int(max_mb * 1024 * 1024)

    # MySQL connection params
    db_config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DB", "finance_db"),
    }

    def get_conn():
        return mysql.connector.connect(**db_config)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/finances/upload/<int:user_id>/<int:year>")
    def upload_finances(user_id: int, year: int):
        if "file" not in request.files:
            return jsonify({"error": "No file part in request"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        filename = secure_filename(file.filename)
        if not filename.lower().endswith(".xlsx"):
            return jsonify({"error": "Invalid file type. Please upload .xlsx"}), 400

        # Parse with pandas
        try:
            bytes_buf = BytesIO(file.read())
            df = pd.read_excel(bytes_buf, engine="openpyxl")
        except Exception as e:
            return jsonify({"error": f"Failed to read Excel: {str(e)}"}), 400

        
        expected = {"Month", "Amount"}
        if not expected.issubset(set(df.columns)):
            return jsonify({"error": f"Missing required columns. Expected {sorted(expected)}"}), 400

        # Normalize month names and amounts
        df = df.copy()
        df["Month"] = df["Month"].astype(str).str.strip().str.title()
        try:
            df["Amount"] = pd.to_numeric(df["Amount"], errors="raise")
        except Exception:
            return jsonify({"error": "Amount column must be numeric"}), 400

        # Overwrite policy: delete existing rows for this user
        try:
            conn = get_conn()
            cur = conn.cursor()
            # Ensure user exists
            cur.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
            if cur.fetchone() is None:
                return jsonify({"error": f"user_id {user_id} does not exist in users table"}), 404

            # Delete old
            cur.execute("DELETE FROM financial_records WHERE user_id=%s AND year=%s", (user_id, year))

            # Bulk insert using executemany
            rows = [(int(user_id), int(year), m, float(a)) for m, a in zip(df["Month"], df["Amount"])]
            cur.executemany(
                "INSERT INTO financial_records (user_id, year, month, amount) VALUES (%s, %s, %s, %s)",
                rows,
            )
            conn.commit()
            cur.close()
            conn.close()
        except mysql.connector.Error as err:
            return jsonify({"error": f"MySQL error: {str(err)}"}), 500

        return jsonify({"message": f"Uploaded {len(rows)} rows for user_id={user_id}, year={year}"}), 200

    @app.get("/api/finances/<int:user_id>/<int:year>")
    def get_finances(user_id: int, year: int):
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                '''
                SELECT u.user_name, f.month, f.amount
                FROM financial_records f
                JOIN users u ON u.user_id = f.user_id
                WHERE f.user_id=%s AND f.year=%s
                ORDER BY FIELD(f.month,
                    'Jan','January','Feb','February','Mar','March','Apr','April','May','Jun','June','Jul','July','Aug','August','Sep','September','Oct','October','Nov','November','Dec','December'), f.month
                ''',
                (user_id, year),
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
        except mysql.connector.Error as err:
            return jsonify({"error": f"MySQL error: {str(err)}"}), 500

        return jsonify([{"user_name": r[0], "month": r[1], "amount": float(r[2])} for r in rows])

    @app.get("/sample.xlsx")
    def sample_file():
        return send_from_directory("static", "sample_finances.xlsx", as_attachment=True)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

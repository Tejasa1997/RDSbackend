from dotenv import load_dotenv
from flask import Flask, request, jsonify
import mysql.connector
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ MySQL RDS Connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "your-rds-endpoint.rds.amazonaws.com"),
        user=os.getenv("MYSQL_USER", "admin"),
        password=os.getenv("MYSQL_PASSWORD", "your-password"),
        database=os.getenv("MYSQL_DB", "yourdbname")
    )

@app.route("/users/add", methods=["POST"])
def add_user():
    data = request.get_json()
    name, email = data.get("name"), data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]
    return jsonify(users)

@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.get_json()
    name, email = data.get("name"), data.get("email")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (name, email, id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User updated successfully"})

@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User deleted successfully"})

@app.route("/", methods=["GET"])
def index():
    return "Flask app running with MySQL Connector!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

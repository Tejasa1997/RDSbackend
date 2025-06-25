from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# ✅ MySQL RDS Configuration
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST", "your-rds-endpoint.rds.amazonaws.com")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER", "admin")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD", "your-password")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB", "yourdbname")

mysql = MySQL(app)

# ✅ Create: Add new user
@app.route("/users/add", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


 # ✅ Read: Get all users
@app.route('/users', methods=['GET'])
def get_users():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        cur.close()

        users = [{"id": row[0], "name": row[1], "email": row[2]} for row in rows]
        return jsonify(users)

 # ✅ Update: Update user by ID
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')

        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (name, email, id))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "User updated successfully"})

 # ✅ Delete: Delete user by ID
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "User deleted successfully"})

 # ✅ Health check
@app.route('/', methods=['GET'])
def index():
        return "Flask app is running with RDS MySQL!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

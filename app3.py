# for lambda function no flask 
import json
import pymysql
import os

# ✅ Environment variables must be set in Lambda configuration
DB_HOST = os.getenv("MYSQL_HOST")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DB")

def connect():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def lambda_handler(event, context):
    path = event.get("path", "")
    method = event.get("httpMethod", "")
    body = json.loads(event["body"]) if event.get("body") else {}

    try:
        if path == "/" and method == "GET":
            return respond(200, {"message": "Lambda app running with PyMySQL!"})

        elif path == "/users" and method == "GET":
            return get_users()

        elif path == "/users/add" and method == "POST":
            return add_user(body)

        elif path.startswith("/users/") and method == "PUT":
            user_id = path.split("/")[-1]
            return update_user(user_id, body)

        elif path.startswith("/users/") and method == "DELETE":
            user_id = path.split("/")[-1]
            return delete_user(user_id)

        else:
            return respond(404, {"error": "Route not found"})

    except Exception as e:
        return respond(500, {"error": str(e)})

# ------------------- API Functions -----------------------

def get_users():
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
    conn.close()
    return respond(200, users)

def add_user(data):
    name, email = data.get("name"), data.get("email")
    if not name or not email:
        return respond(400, {"error": "Name and email are required"})

    conn = connect()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
    conn.close()
    return respond(201, {"message": "User added successfully"})

def update_user(user_id, data):
    name, email = data.get("name"), data.get("email")
    if not name or not email:
        return respond(400, {"error": "Name and email are required"})

    conn = connect()
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (name, email, user_id))
        conn.commit()
    conn.close()
    return respond(200, {"message": "User updated successfully"})

def delete_user(user_id):
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
    conn.close()
    return respond(200, {"message": "User deleted successfully"})

# ------------------- Utility -----------------------

def respond(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

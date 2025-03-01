from flask import Flask, jsonify, request
from mcstatus import JavaServer, BedrockServer
from flask_cors import CORS
import mysql.connector
import json
import time
import threading
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
db_config = config["database"]

# Datenbankverbindung herstellen
def get_db_connection():
    return mysql.connector.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"]
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Tabelle für Server
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type VARCHAR(10) NOT NULL,
            address VARCHAR(255) NOT NULL,
            port INT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            server_id INT NOT NULL,
            online_players INT NOT NULL,
            ping INT NOT NULL,
            online_time DATETIME NOT NULL,
            FOREIGN KEY (server_id) REFERENCES servers (id)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def scan_servers():
    while True:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, address, port FROM servers")
        servers = cursor.fetchall()

        for server in servers:
            server_id, server_type, address, port = server
            try:
                if server_type == "java":
                    mc_server = JavaServer(address, port)
                    status = mc_server.status()
                    ping = round(mc_server.ping())
                    online_players = status.players.online
                elif server_type == "bedrock":
                    mc_server = BedrockServer(address, port)
                    status = mc_server.status()
                    ping = round(mc_server.ping())
                    online_players = status.players_online
                else:
                    continue

                cursor.execute("""
                    INSERT INTO server_stats (server_id, online_players, ping, online_time)
                    VALUES (%s, %s, %s, %s)
                """, (server_id, online_players, ping, datetime.now()))
                conn.commit()
            except Exception as e:
                print(f"Fehler beim Scannen von {address}:{port}: {e}")

        cursor.close()
        conn.close()
        time.sleep(60)

@app.route('/servers', methods=['POST'])
def add_server():
    data = request.json
    if not data or "type" not in data or "address" not in data or "port" not in data:
        return jsonify({"error": "type, address, and port are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO servers (type, address, port)
        VALUES (%s, %s, %s)
    """, (data["type"], data["address"], data["port"]))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Server added successfully"}), 201

@app.route('/servers/<int:server_id>', methods=['DELETE'])
def delete_server(server_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servers WHERE id = %s", (server_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Server deleted successfully"}), 200

@app.route('/status', methods=['GET'])
def get_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, address, port FROM servers")
    servers = cursor.fetchall()

    results = []
    for server in servers:
        server_id, server_type, address, port = server
        try:
            if server_type == "java":
                mc_server = JavaServer(address, port)
                status = mc_server.status()
                ping = round(mc_server.ping())
                online_players = status.players.online
            elif server_type == "bedrock":
                mc_server = BedrockServer(address, port)
                status = mc_server.status()
                ping = round(mc_server.ping())
                online_players = status.players_online
            else:
                continue

            results.append({
                "id": server_id,
                "type": server_type,
                "address": address,
                "port": port,
                "online": True,
                "players": online_players,
                "ping": ping,
                "motd": status.description
            })
        except Exception as e:
            results.append({
                "id": server_id,
                "type": server_type,
                "address": address,
                "port": port,
                "online": False,
                "error": str(e)
            })

    cursor.close()
    conn.close()
    return jsonify(results)

@app.route('/stats/<string:period>', methods=['GET'])
def get_stats(period):
    server_id = request.args.get("server_id", type=int)
    if not server_id:
        return jsonify({"error": "server_id is required"}), 400

    # Zeitraum basierend auf dem Parameter berechnen
    now = datetime.now()
    if period == "hour":
        start_time = now - timedelta(hours=1)
    elif period == "day":
        start_time = now - timedelta(days=1)
    elif period == "month":
        start_time = now - timedelta(days=30)
    elif period == "year":
        start_time = now - timedelta(days=365)
    else:
        return jsonify({"error": "Invalid period. Use 'hour', 'day', 'month', or 'year'."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT online_players, ping, online_time
        FROM server_stats
        WHERE server_id = %s AND online_time >= %s
        ORDER BY online_time
    """, (server_id, start_time))
    rows = cursor.fetchall()

    stats = [{
        "online_players": row[0],
        "ping": row[1],
        "online_time": row[2]
    } for row in rows]

    cursor.close()
    conn.close()
    return jsonify(stats)

def start_background_task():
    thread = threading.Thread(target=scan_servers)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    init_db()
    start_background_task()

    host = os.getenv('FLASK_HOST', 'YourIP')
    port = int(os.getenv('FLASK_PORT', YourPort))

    # Starte den Flask-Server
    app.run(host=host, port=port, debug=True)
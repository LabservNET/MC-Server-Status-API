# LabservNET PlayerCount API

This is a Flask-based API that allows users to monitor Minecraft Java and Bedrock servers. 
The API periodically checks the server status, stores data in a MariaDB/MySQL database, and provides endpoints for querying real-time and historical statistics.

## Features
> Add & Remove Servers: Easily add or delete Minecraft servers from the monitoring list.
> Automatic Server Scanning: The API periodically pings servers to check for player count, latency, and online status.
> Database Storage: Server statistics are saved in a MariaDB/MySQL database for historical tracking.
> Retrieve Server Status: Get real-time information about all registered servers.
> Historical Statistics: Fetch player count and ping statistics for different time periods (hour, day, month, year).

## Installation

1. Clone the Repository
   ```
    git clone https://github.com/LabservNET/MC-Server-Status-API.git
    cd MC-Server-Status-API
   ```
2. Install Dependencies
   - Ensure you have `Python 3.8+` installed, then run:
   ```
   pip install -r requirements.txt
   ```
3. Configure Database
   - Create a MariaDB/MySQL database and update `config.json`
   ```
      {
      "database": {
          "host": "MARIADB_HOST",
          "port": "MARIADB_PORT",
          "user": "MARIADB_USER",
          "password": "MARIADB_PASSWORD",
          "database": "MARIADB_DATABASE"
      }
    }
   ```

4. API Configuration
   - Make shure you changed the Port and IP Adress at the bottom of the `app.py`
   ```
    host = os.getenv('FLASK_HOST', 'YourIP')
    port = int(os.getenv('FLASK_PORT', YourPort))
   ```

5. Run the API
   ```
    python app.py
   ```
# API Endpoints

1. Add a Server
   - POST `/servers`

 ```
{
  "type": "java",  // or "bedrock"
  "address": "example.com",
  "port": 25565
}
```
Response:

```
{
  "message": "Server added successfully"
}
```

2. Delete a Server
   - DELETE `/servers/{server_id}`
_response:_

  ```
{
  "message": "Server deleted successfully"
}
```

3. Get Server Status
   GET `/status`
_Response:_

```
[
  {
    "id": 1,
    "type": "java",
    "address": "example.com",
    "port": 25565,
    "online": true,
    "players": 10,
    "ping": 50,
    "motd": "Welcome to our server!"
  }
]
```

**with 2 or more Servers**
```
[
  {
    "id": 1,
    "type": "java",
    "address": "example.com",
    "port": 25565,
    "online": true,
    "players": 10,
    "ping": 50,
    "motd": "Welcome to our server!"
  },
  {
    "address": "example.com",
    "error": "'BedrockServer' object has no attribute 'ping'",
    "id": 2,
    "online": false,
    "port": 19132,
    "type": "bedrock"
  }
]
```

4. Get Historical Statistics
   - GET `/stats/{period}?server_id={id}`
   ```
    [
      {
        "online_players": 15,
        "ping": 40,
        "online_time": "2024-02-28T12:00:00"
      }
    ]
   ```
**with 2 or more Records**
   ```
    [
      {
        "online_players": 15,
        "ping": 40,
        "online_time": "2024-02-28T12:00:00"
      },
      {
        "online_players": 12,
        "ping": 23,
        "online_time": "2024-03-27T12:02:03"
      }
    ]
```

# How It Works

1. When the API starts, it initializes the database and creates the required tables if they do not exist.

2. A background thread runs every 60 seconds, scanning all registered servers for status updates.

3. The collected data is stored in the database and can be retrieved via API endpoints.

# Requirements
 - Python 3.8+
 - Flask 3.0.0
 - MariaDB/MySQL
 - mcstatus (Minecraft Server Query Library)

# Future Improvements
 - Implement a web dashboard to visualize server data.
 - Add Docker support for easy deployment.
 - Add authentication for better security.

# Author
 - Created by LabservNET. Contributions are welcome!
 - Sollten probleme auftreten kontaktiert mich gerne auf Discord unter dem namen `_.emanuel_`

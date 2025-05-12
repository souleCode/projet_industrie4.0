# Remote PC Shutdown System

This project provides a system for remotely monitoring the status of multiple Windows PCs on a network and triggering their shutdown from a central server via a web-based dashboard.

The system consists of two main components:

1. **Server:** A Flask application that runs on a central machine, providing a web dashboard and an API to manage registered PCs, check their status, and send shutdown commands.
2. **Client:** A Flask application that runs on each target Windows PC, listening for status requests and shutdown commands from the server.

## Features

* **Server-Client Architecture:** Centralized control from a server application interacting with distributed client applications.
* **Web-based Dashboard:** A simple web interface (served by the server) to view registered PCs and initiate actions.
* **PC Registration:** Clients automatically register themselves with the server upon startup.
* **PC Status Monitoring:** The server can ping registered clients to check if they are online and reachable.
* **Remote Shutdown:** Trigger a shutdown command on specific online PCs or all online PCs from the server.
* **Basic Authentication:** Simple username/password login to access the server's API and dashboard (using JWT).
* **API Security:** API endpoints are protected using JWT authentication. The client shutdown endpoint is protected by a shared secret key.
* **Windows Service Integration:** The client application can be installed as a Windows service using NSSM (Non-Sucking Service Manager) to run automatically in the background.

## How It Works

1. **Server (Master Machine):**

   * Runs a Flask web server (`app.py`) typically on a machine within the network that is always on.
   * Serves a basic HTML dashboard (`index.html`) using Flask templates and static files (`script.js`, `style.css`).
   * Manages a list of registered PCs in a `db.json` file (acting as a simple database). Each entry includes the PC's name, IP address, and current status (`online`/`offline`).
   * Provides an API (`routes.py`, `auth_routes.py`) with endpoints for:
     * `/login`: Authenticate admin user and issue a JWT.
     * `/register-pc`: (Protected) Clients use this to register themselves.
     * `/list-pcs`: (Protected) List registered PCs and their statuses. Can be filtered by status.
     * `/ping-pcs`: (Protected) Iterates through registered PCs, sends a `GET` request to the client's `/status` endpoint to check reachability, and updates the status in `db.json`.
     * `/trigger-shutdown`: (Protected) Receives a request specifying a PC (by name or IP) or 'all'. Finds the target PC(s) in `db.json` (only online ones), and sends a `POST` request to the client's `/shutdown` endpoint, including the shared secret key in the header.
     * `/shutdown-all-online`: (Protected) Sends a shutdown request to all currently `online` PCs listed in `db.json`.
   * Uses Flask-JWT-Extended (`auth.py`) to protect most API endpoints, requiring a valid JWT in the Authorization header.
   * Uses Flask-CORS (`flask_cors`) to handle potential cross-origin requests from the frontend.
2. **Client (Target PCs):**

   * Runs a Flask application (`client.py`) on each target Windows machine you want to be able to shut down.
   * Reads configuration (`config.json`) including the server URL, a *shared secret key*, the PC's name, and its IP address.
   * Upon startup, it attempts to get a JWT from the server (using hardcoded admin/admin creds) and then registers itself with the server if it's not already registered.
   * Exposes two endpoints:
     * `/status` (GET): Responds with a simple JSON message indicating it's online. Used by the server for pinging.
     * `/shutdown` (POST): Requires a specific secret key in the Authorization header. If the key is valid, it executes the Windows shutdown command (`shutdown /s /t 0`).
   * Logging is directed to console output by default, but configured via NSSM for file logging.
   * The `run_server.bat` script is a simple way to execute the `client.py` script using a specific Python interpreter path.
   * NSSM is used to wrap the `run_server.bat` script, allowing it to run as a persistent Windows service in the background, starting automatically with the system.
3. **Communication Flow:**

   * Clients start, register with Server.
   * User accesses Server dashboard.
   * Dashboard might trigger a `ping-pcs` request to the Server API.
   * Server pings Clients' `/status` endpoint to update `db.json`.
   * Dashboard displays PC status from `db.json` (via `/list-pcs` endpoint).
   * User clicks a "Shutdown" button on the Dashboard for a PC or all.
   * Dashboard sends a `POST` request to Server's `/trigger-shutdown` or `/shutdown-all-online` endpoint (with JWT).
   * Server finds the target PC's IP in `db.json`.
   * Server sends a `POST` request to the Client's `/shutdown` endpoint (with the shared secret key).
   * Client validates the secret key and executes the `shutdown` command.

## Security Considerations

This project includes basic security mechanisms, but it's important to be aware of their limitations, especially for deployment outside a trusted local network:

* **Basic Server Authentication (Admin/Admin):** The server uses hardcoded `admin`/`admin` credentials for JWT token generation. **This is highly insecure for production use.** You should change these credentials immediately and consider implementing a more robust authentication mechanism (e.g., environment variables, encrypted config, multiple users, stronger password policies).
* **Shared Secret Key:** The client's `/shutdown` endpoint is protected by a shared secret key defined in `config.json`. This key is the *only* thing preventing unauthorized shutdown requests *directly* to a client's `/shutdown` endpoint, bypassing the server. **This key MUST be kept confidential and should be strong.** If an attacker gains access to this key, they can shut down any client they can reach on port 5001.
* **HTTP Communication:** All communication between the server and clients is currently over unencrypted HTTP. For sensitive environments or if operating across networks, **using HTTPS is highly recommended** to prevent eavesdropping or tampering.
* **`db.json`:** The database file (`db.json`) stores PC names and IPs in plain text.
* **Client Endpoint Exposure:** The client's `/status` and `/shutdown` endpoints are exposed on port 5001. **Firewall rules are essential** on each client machine to allow inbound connections on port 5001 *only* from the server's IP address. This adds a crucial layer of security by limiting who can even attempt to access these endpoints.
* **`os.system`:** While the specific use of `os.system('shutdown /s /t 0')` is controlled in this project, using `os.system` generally can be risky if external input were ever directly passed to it.

For production environments, enhancing security (stronger auth, HTTPS, stricter firewall rules, potential encryption of configuration/data) should be a priority.

## Prerequisites

* **Python 3:** Installed on both the server machine and all target client machines.
* **Required Python Libraries:**
  * `Flask`
  * `Flask-CORS` (Server only)
  * `Flask-JWT-Extended` (Server only)
  * `requests` (Both server and client)
    You can install these using pip:

  ```bash
  pip install Flask Flask-CORS Flask-JWT-Extended requests
  ```
* **NSSM (Non-Sucking Service Manager):** Required on client machines if you want to run the client as a Windows service. The executable (`nssm.exe`) is included in the `nssm-2.24` directory.
* **Network Connectivity:** The server machine must be able to reach the client machines on the network, specifically on the port the client is listening on (default 5001). Client machines must be able to reach the server machine on the port the server is listening on (default 5000).
* **Administrator Privileges:** Needed on client machines to install the NSSM service and for the `shutdown` command to execute.

## Setup and Installation

### 1. Project Structure

Ensure your project directory follows this structure:









.

### 2. Server Setup

1. **Navigate** to the `server/` directory.
2. **Install dependencies:**
   ```bash
   pip install Flask Flask-CORS Flask-JWT-Extended requests
   ```
3. **Configure:**
   * Open `server/app.py`. **Change** the `app.config['JWT_SECRET_KEY']` to a strong, unique secret key.
   * (Optional) Edit `server/db.json` to pre-populate a list of PCs. Clients will also register automatically, but you can add known PCs here if needed. Ensure the format matches the existing entries.
4. **Run the Server:**
   ```bash
   python app.py
   ```

   The server should start, typically listening on `http://0.0.0.0:5000`. Keep this running.

### 3. Client Setup (on each target PC)

1. **Copy** the entire `client/` directory to the target PC (e.g., `C:\RemoteShutdownClient`).
2. **Navigate** into the copied `client/` directory on the target PC.
3. **Install dependencies:**
   ```bash
   pip install Flask requests
   ```
4. **Configure:**
   * Open `client/config.json`.
   * Set `"server_url"` to the URL/IP and port of your running server (e.g., `"http://192.168.1.100:5000"`).
   * Set `"secret_key"` to a strong, unique secret key. **This key MUST match the one used by the server in `routes.py`** when sending the shutdown command (`headers={'Authorization': 'Bearer your-secret-key'}`). Change `"your-secret-key"` in both `client/config.json` and `server/routes.py`.
   * Set `"pc_name"` to a descriptive name for this computer.
   * Set `"pc_ip"` to this computer's local IP address.
5. **Configure `run_server.bat`:** Open the file and ensure the path to the Python interpreter (`"C:\Users\DIARISSO\AppData\Local\Programs\Python\Python313\python.exe"`) is correct for the Python installation on *this specific client machine*.
6. **Test Run (Optional):** You can test the client by running `run_server.bat` from a command prompt. It should start, attempt to register with the server, and print log messages. Press `Ctrl+C` to stop it.

### 4. Installing Client as a Windows Service (Using NSSM)

To make the client application run automatically in the background and persist across reboots, use NSSM:

1. **Navigate** to the `client/` directory in a Command Prompt *run as Administrator*.
2. **Copy** the appropriate `nssm.exe` for your system architecture (win32 or win64) from the `nssm-2.24` directory into the `client/` directory. (Alternatively, adjust the path in the commands below to point to the executable's original location). Make sure to add the file path for either win32 or win64 to your systems path( via environment variables)
3. **Execute the following commands one by one** in the Administrator Command Prompt:

   * **Install the service:**

     ```bash
     nssm install my_remote_shutdown_client "%cd%\run_server.bat"
     ```

     *(Note: `%cd%` is the current directory)*. This will open an NSSM GUI. In the "Path" field, ensure it points to `run_server.bat`. In the "Startup directory", ensure it's the `client/` directory. Click "Install Service".
   * **Configure standard output logging:**

     ```bash
     nssm set my_remote_shutdown_client AppStdout "%cd%\logs\client_logs.log"
     ```

     *(This directs standard output to a log file. Make sure the `logs` directory exists.)*
   * **Configure standard error logging:**

     ```bash
     nssm set my_remote_shutdown_client AppStderr "%cd%\logs\client_errors.log"
     ```

     *(This directs errors to a separate log file.)*
   * **Enable log file rotation:**

     ```bash
     nssm set my_remote_shutdown_client AppRotateFiles 1
     ```
   * **Enable online log rotation (rotate while service is running):**

     ```bash
     nssm set my_remote_shutdown_client AppRotateOnline 1
     ```
   * **Set log rotation frequency (e.g., daily - 86400 seconds):**

     ```bash
     nssm set my_remote_shutdown_client AppRotateSeconds 86400
     ```
   * **Set log rotation size threshold (e.g., 1MB - 1048576 bytes):**

     ```bash
     nssm set my_remote_shutdown_client AppRotateBytes 1048576
     ```
   * **Start the service:**

     ```bash
     sc start my_remote_shutdown_client
     ```

   You can verify the service status using `sc query my_remote_shutdown_client`. The client should now be running in the background and start automatically when the computer boots.
4. **Repeat Client Setup** for every PC you want to control.

## Usage

1. **Ensure the Server is running** (`python app.py` in the `server/` directory).
2. **Ensure the Client service is running** on each target PC (`sc query my_remote_shutdown_client` should show `STATE : 4 RUNNING`).
3. **Open a web browser** and navigate to the server's URL and port (e.g., `http://<server_ip>:5000`).
4. The dashboard should load.login in to access the dashboard (for testing purposes the user and password are both **admin** ).
5. The dashboard (or direct API calls) can be used to:
   * View the list of registered PCs and their current status (which relies on the server periodically calling `/ping-pcs`).
   * Trigger a shutdown for a specific PC (by sending a POST request to `/trigger-shutdown` with the PC name or IP).
   * Trigger a shutdown for all online PCs (by sending a POST request to `/shutdown-all-online`).

**Example API Interactions (using `curl` or a similar tool after getting a JWT):**

* **Get JWT (Login):**

  ```bash
  curl -X POST http://<server_ip>:5000/login -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}'
  # Output will include a token. Store this token.
  ```
* **List PCs (using the obtained token):**

  ```bash
  curl -X GET http://<server_ip>:5000/list-pcs -H "Authorization: Bearer <your_jwt_token>"
  ```
* **Ping PCs:**

  ```bash
  curl -X GET http://<server_ip>:5000/ping-pcs -H "Authorization: Bearer <your_jwt_token>"
  ```
* **Trigger Shutdown for a Specific PC:**

  ```bash
  curl -X POST http://<server_ip>:5000/trigger-shutdown -H "Content-Type: application/json" -H "Authorization: Bearer <your_jwt_token>" -d '{"name": "PC-1-musa"}'
  # Or by IP: -d '{"name": "192.168.11.111"}'
  ```
* **Trigger Shutdown for All Online PCs:**

  ```bash
  curl -X POST http://<server_ip>:5000/shutdown-all-online -H "Authorization: Bearer <your_jwt_token>"
  ```

  ## Contributing

  Contributions are welcome! Please open an issue or submit a pull request.

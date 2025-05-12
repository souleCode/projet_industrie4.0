### 🚀 **Step 1: Setting Up the Server-Side API**

We'll begin by building the **Flask API** that sends the shutdown commands to the remote PCs. This API will:

1. Accept shutdown, restart, and hibernate requests.
2. Verify authentication using JWT for security.
3. Send the command to the client (remote PC) over HTTP.

---

### 🔹 **Tasks for Step 1:**

1️⃣ **Set up the Flask server:** Initialize a basic Flask app.

2️⃣ **Create API routes:**

* `/shutdown`: Shuts down the remote PC.
* `/restart`: Restarts the remote PC.
* `/hibernate`: Hibernates the remote PC.

3️⃣ **Add JWT Authentication:** To secure communication.

4️⃣ **Test the API:** Use Postman or cURL to send requests.

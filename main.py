import os
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Get WEBHOOK_URL from environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL environment variable not set")

# Define a basic route for the root URL
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Webhook server is running", "webhook_url": WEBHOOK_URL})

# Define a webhook endpoint to handle POST requests
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    # Process the webhook data (customize based on your needs)
    print(f"Received webhook data: {data}")
    return jsonify({"status": "success", "received": data}), 200

# Health check endpoint for Render
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    # Get port from environment (Render sets PORT)
    port = int(os.getenv("PORT", 5000))
    # Run the app (0.0.0.0 to bind to all interfaces, required for Render)
    app.run(host="0.0.0.0", port=port, debug=False)
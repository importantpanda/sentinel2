#: Date: 12-9-2024
#: Version: 1.0
#: Description: This script sends requests to a local IP address and port to monitor incoming messages.

from flask import Flask, request, jsonify, render_template_string
from xml.dom.minidom import parseString
import logging
import traceback
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configure logging with timestamps
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

# Store messages in a list
messages = []

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/endpoint', methods=['POST'])
@limiter.limit("10 per minute")
def endpoint():
    try:
        cot_string = request.data.decode('utf-8')
        app.logger.debug(f"Received cotString: {cot_string}")

        # Strip leading/trailing whitespace from cot_string
        cot_string = cot_string.strip()

        # Parse and pretty-print the XML string
        pretty_cot_string = parseString(cot_string).toprettyxml()
        messages.append(pretty_cot_string)

        return "Received cotString", 200
    except Exception as e:
        # Log the exception traceback
        app.logger.error(f"Error processing cotString: {e}")
        traceback_str = traceback.format_exc()
        app.logger.error(f"Traceback: {traceback_str}")
        return "Internal Server Error", 500

@app.route('/')

def index():
    # Join all messages with a newline character to serve as plain text
    return "\n\n".join(messages), 200, {'Content-Type': 'text/plain; charset=utf-8'}
#def index():
"""
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Message Monitor</title>
            <script>
                async function fetchMessages() {
                    const response = await fetch('/messages');
                    const data = await response.json();
                    const messageList = document.getElementById('messageList');
                    messageList.innerHTML = '';
                    data.messages.forEach(msg => {
                        const li = document.createElement('li');
                        li.textContent = msg;
                        messageList.appendChild(li);
                    });
                }
                setInterval(fetchMessages, 1000); // Poll every second
            </script>
        </head>
        <body>
            <h1>Incoming Messages</h1>
            <ul id="messageList"></ul>
        </body>
        </html>
    ''')
"""
@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": messages})

if __name__ == '__main__':
    # Bind to localhost only
    app.run(host='127.0.0.1', port=40100)
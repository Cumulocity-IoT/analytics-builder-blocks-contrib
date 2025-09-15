from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys
import socketserver

# In-memory store
items = {"1": {"test":"content"}}

PORT = int(sys.argv[1])

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"Received GET request on {self.path}")
        if self.path.endswith('/items'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = [i for i in items.values()]
            self.wfile.write(json.dumps(response).encode())
            return
        
        item_id = self.path.lstrip('/items/')
        if item_id in items:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = items[item_id]
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Item not found"}')
        sys.stdout.flush()

    def do_POST(self):
        print(f"Received POST request on {self.path}")
        item_id = self.path.lstrip('/items/')
        if item_id in items:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error": "Item already exists"}')
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        items[item_id] = data
        self.send_response(201)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"message": "Item created", item_id: data}
        self.wfile.write(json.dumps(response).encode())

    def do_PUT(self):
        print(f"Received PUT request on {self.path}")
        item_id = self.path.lstrip('/items/')
        if item_id not in items:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Item not found"}')
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        items[item_id] = data
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"message": "Item updated", item_id: data}
        self.wfile.write(json.dumps(response).encode())

    def do_DELETE(self):
        item_id = self.path.lstrip('/items/')
        if item_id not in items:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Item not found"}')
            return

        del items[item_id]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'{"message": "Item deleted"}')

    def log_message(self, format, *args):
        # Optional: Suppress console logging
        return

httpd = socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler)

print(f"Server running on port {PORT}...")
sys.stdout.flush()
httpd.serve_forever()
print("Exiting")
sys.stdout.flush()



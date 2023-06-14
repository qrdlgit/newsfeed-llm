import http.server
import ssl
import sys

if len(sys.argv) < 3:
    print("Usage: python https_server.py <server_port> <path_to_web_directory>")
    sys.exit(1)

port = int(sys.argv[1])
web_dir = sys.argv[2]

http.server.SimpleHTTPRequestHandler.extensions_map.update({
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
})

handler = http.server.SimpleHTTPRequestHandler
handler.directory = web_dir

httpd = http.server.HTTPServer(("", port), handler)
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="key.pem", certfile="cert.pem", server_side=True)

print(f"Serving HTTPS on port {port}...")
httpd.serve_forever()

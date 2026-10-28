import http.server
import socketserver
import json
import os

PORT = 1234
FILE_PATH = 'lib.json'

# Это решает проблему "OSError: [Errno 98] Address already in use"
socketserver.TCPServer.allow_reuse_address = True

class MathHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Если зашли на главную страницу, показываем web/index.html
        if self.path == '/':
            self.path = '/web/index.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                # Сохраняем в lib.json в корневой папке
                with open(FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

# Меняем рабочую директорию на ту, где лежит main.py, 
# чтобы пути к файлам всегда были правильными
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), MathHandler) as httpd:
    print(f"Сервер запущен! Открой в браузере: http://localhost:{PORT}")
    httpd.serve_forever()
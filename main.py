import http.server
import socketserver
import json
import os
import sys
import threading
import webview
import time

# Список портов для проверки
PORT_CANDIDATES = [1234, 4321, 1111, 0, 8888]
FILE_PATH = 'lib.json'
active_port = None
httpd = None

class MathHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(302)
            self.send_header('Location', '/web/')
            self.end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
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

def start_server():
    global active_port, httpd
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    for port in PORT_CANDIDATES:
        try:
            socketserver.TCPServer.allow_reuse_address = True
            httpd = socketserver.TCPServer(("", port), MathHandler)
            active_port = httpd.server_address[1]
            print(f"Сервер успешно запущен! URL: http://localhost:{active_port}/web/")
            httpd.serve_forever()
            break
        except OSError:
            print(f"Порт {port} занят, пробуем следующий...")
            continue
            
    if not active_port:
        print("ОШИБКА: Все порты заняты. Освободите один из них: 1234, 4321, 1111, 0, 8888.")
        sys.exit(1)

# Запуск сервера в фоне
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

time.sleep(1)

if __name__ == '__main__':
    # Получаем абсолютный путь к иконке
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, 'assets', 'icon.png')
    
    # Если вдруг иконки .png нет, проверяем .ico (на всякий случай)
    if not os.path.exists(icon_path):
        icon_path = os.path.join(base_dir, 'assets', 'icon.ico')

    window = webview.create_window(
        title='SeeMath',
        url=f'http://localhost:{active_port}/web/',
        width=1280,
        height=850,
        background_color='#000000'
    )
    
    try:
        # Передаем иконку в webview.start()
        webview.start(icon=icon_path if os.path.exists(icon_path) else None)
    except Exception as e:
        print("Ошибка запуска приложения:", e)
    
    if httpd:
        httpd.shutdown()
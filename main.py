import http.server
import socketserver
import json
import os
import sys
import threading
import tkinter as tk
from tkinterweb import HtmlFrame

# Список портов для проверки
PORT_CANDIDATES = [1234, 4321, 1111, 0, 8888]
FILE_PATH = 'lib.json'
active_port = None
httpd = None

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

def start_server():
    global active_port, httpd
    
    # Меняем рабочую директорию на ту, где лежит main.py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    for port in PORT_CANDIDATES:
        try:
            socketserver.TCPServer.allow_reuse_address = True
            httpd = socketserver.TCPServer(("", port), MathHandler)
            active_port = httpd.server_address[1]
            print(f"Сервер успешно запущен! Браузер: http://localhost:{active_port}/web/")
            httpd.serve_forever()
            break # Если запустился, выходим из цикла
        except OSError:
            print(f"Порт {port} занят, пробуем следующий...")
            continue
            
    if not active_port:
        print("ОШИБКА: Все предложенные порты заняты. Пожалуйста, освободите один из них: 1234, 4321, 1111, 0, 8888.")
        sys.exit(1)

# Запуск сервера в отдельном потоке (чтобы не блокировать окно приложения)
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# Ждем секунду, чтобы сервер точно успел запуститься и получить порт
import time
time.sleep(1) 

# --- ЗАПУСК ОКНА TKINTER ---
root = tk.Tk()
root.title("SeeMath")
root.geometry("1200x800")

# Установка иконки приложения
try:
    icon_img = tk.PhotoImage(file='assets/icon.png')
    root.iconphoto(True, icon_img)
except Exception as e:
    print("Не удалось загрузить иконку приложения:", e)

# Встраиваем веб-страницу
try:
    frame = HtmlFrame(root, messages_enabled=False)
    frame.load_url(f"http://localhost:{active_port}/web/")
    frame.pack(fill="both", expand=True)
except Exception as e:
    print("Ошибка загрузки интерфейса. Убедитесь, что установлен tkinterweb: pip install tkinterweb")
    sys.exit(1)

# Корректное закрытие приложения
def on_closing():
    if httpd:
        httpd.shutdown()
    root.destroy()
    sys.exit(0)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
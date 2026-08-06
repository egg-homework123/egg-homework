"""
蛋仔作业大闯关 - 同步服务器
手机/平板通过WiFi连接此服务器，数据统一存储在电脑上，实时同步。

启动方式：双击此文件，或在命令行运行 python server.py
访问地址：http://你的电脑IP:8766/index.html
"""

import http.server
import json
import os
import threading

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'family_data.json')

# 内存中的数据（启动时从文件加载）
data_lock = threading.Lock()
family_data = {}

def load_data():
    global family_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                family_data = json.load(f)
            except:
                family_data = {}
    print(f'[数据] 已加载，共 {len(family_data)} 个家庭')

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(family_data, f, ensure_ascii=False)

load_data()


class SyncHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            self.send_json(family_data)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/data':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                incoming = json.loads(body)
            except:
                self.send_json({'ok': False, 'error': 'invalid json'}, 400)
                return

            with data_lock:
                # 用时间戳判断谁更新
                incoming_ts = incoming.get('_cloudTimestamp', 0)
                current_ts = family_data.get('_cloudTimestamp', 0)

                if incoming_ts >= current_ts:
                    family_data.clear()
                    family_data.update(incoming)
                    save_data()
                    self.send_json({'ok': True, 'action': 'saved'})
                else:
                    # 发来的比服务器旧，返回服务器数据
                    self.send_json({'ok': True, 'action': 'conflict', 'serverData': family_data})
        else:
            self.send_json({'error': 'not found'}, 404)

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def end_headers(self):
        # 让手机不缓存index.html，确保每次拿最新版
        if self.path.endswith('.html') or self.path == '/':
            self.send_header('Cache-Control', 'no-cache, no-store')
        super().end_headers()


def main():
    port = 8766
    server = http.server.HTTPServer(('0.0.0.0', port), SyncHandler)

    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = '127.0.0.1'

    print('=' * 50)
    print('  蛋仔作业大闯关 - 同步服务器已启动！')
    print('=' * 50)
    print()
    print(f'  手机/平板浏览器打开：')
    print(f'  http://{local_ip}:{port}/index.html')
    print()
    print(f'  电脑浏览器打开：')
    print(f'  http://localhost:{port}/index.html')
    print()
    print('  数据自动同步，多设备实时互通')
    print('  按 Ctrl+C 停止服务器')
    print('=' * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务器已停止')
        server.server_close()


if __name__ == '__main__':
    main()

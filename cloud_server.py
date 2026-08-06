"""
蛋仔作业大闯关 - 云端同步服务器（Render部署版）
数据存在 Render 持久化磁盘上，24小时在线，不依赖家里电脑。
"""

import http.server
import json
import os
import threading

# Render 持久化磁盘路径
RENDER_DATA_DIR = os.environ.get('RENDER_DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(RENDER_DATA_DIR, 'family_data.json')

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
        elif self.path == '/api/health':
            self.send_json({'ok': True, 'status': 'running'})
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
                incoming_ts = incoming.get('_cloudTimestamp', 0)
                current_ts = family_data.get('_cloudTimestamp', 0)

                if incoming_ts >= current_ts:
                    family_data.clear()
                    family_data.update(incoming)
                    save_data()
                    self.send_json({'ok': True, 'action': 'saved'})
                else:
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
        if self.path.endswith('.html') or self.path == '/':
            self.send_header('Cache-Control', 'no-cache, no-store')
        super().end_headers()

    def log_message(self, format, *args):
        # 云端减少日志量
        pass


def main():
    port = int(os.environ.get('PORT', 8766))
    server = http.server.HTTPServer(('0.0.0.0', port), SyncHandler)

    print('=' * 50)
    print('  蛋仔作业大闯关 - 云端服务器已启动！')
    print(f'  端口: {port}')
    print('=' * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务器已停止')
        server.server_close()


if __name__ == '__main__':
    main()

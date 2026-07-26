import os
import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform

from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
import qrcode
from PIL import Image, ImageTk

# --- Flask 後端設定 ---
app = Flask(__name__)
UPLOAD_FOLDER = os.path.abspath('./received_files')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 允許最大 1GB 檔案

# 全域變數用於 GUI 紀錄顯示
gui_log_callback = None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iPhone 照片傳輸</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            padding: 30px 20px; 
            text-align: center; 
            background-color: #f2f2f7;
            color: #1c1c1e;
        }
        .card {
            background: white;
            padding: 30px 20px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            max-width: 400px;
            margin: 0 auto;
        }
        .upload-btn { 
            font-size: 18px; 
            font-weight: 600;
            padding: 16px 32px; 
            background: #007aff; 
            color: white; 
            border: none; 
            border-radius: 12px; 
            margin-top: 20px; 
            cursor: pointer;
            width: 100%;
            box-sizing: border-box;
        }
        .upload-btn:disabled { background: #8e8e93; }
        
        .progress-container {
            margin-top: 25px;
            display: none;
        }
        .progress-bar-bg {
            background-color: #e5e5ea;
            border-radius: 8px;
            height: 12px;
            width: 100%;
            overflow: hidden;
        }
        .progress-bar {
            background-color: #34c759;
            height: 100%;
            width: 0%;
            transition: width 0.2s ease;
        }
        #status {
            margin-top: 12px;
            font-size: 15px;
            color: #3a3a3c;
            word-break: break-word;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>照片 / 影片無線傳輸</h2>
        <p style="color:#8e8e93; font-size:14px;">請保持螢幕開啟，傳輸完成前請勿離開網頁</p>
        
        <input type="file" id="fileInput" multiple accept="image/*,video/*" style="display:none;">
        <button type="button" class="upload-btn" id="selectBtn" onclick="document.getElementById('fileInput').click()">選取照片與影片</button>

        <div class="progress-container" id="progressContainer">
            <div class="progress-bar-bg">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div id="status">準備中...</div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', () => {
        const fileInput = document.getElementById('fileInput');
        const selectBtn = document.getElementById('selectBtn');
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const status = document.getElementById('status');

        fileInput.addEventListener('change', () => {
            const files = fileInput.files;
            if (files.length === 0) return;

            selectBtn.disabled = true;
            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';
            status.innerText = `正在準備傳輸 ${files.length} 個檔案...`;

            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/upload', true);

            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    progressBar.style.width = percent + '%';
                    status.innerText = `已傳輸 ${percent}% (${(e.loaded / 1024 / 1024).toFixed(1)} MB / ${(e.total / 1024 / 1024).toFixed(1)} MB)`;
                }
            };

            xhr.onload = () => {
                selectBtn.disabled = false;
                if (xhr.status === 200) {
                    progressBar.style.width = '100%';
                    status.innerHTML = `<span style="color:#34c759; font-weight:bold;">🎉 成功傳輸 ${files.length} 個檔案！</span>`;
                } else {
                    status.innerHTML = `<span style="color:#ff3b30;">❌ 上傳失敗 (錯誤碼 ${xhr.status})</span>`;
                }
                fileInput.value = '';
            };

            xhr.onerror = () => {
                selectBtn.disabled = false;
                status.innerHTML = `<span style="color:#ff3b30;">❌ 網路連線錯誤，傳輸中斷</span>`;
                fileInput.value = '';
            };

            xhr.send(formData);
        });
    });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_files = request.files.getlist('files')
    saved_count = 0
    for file in uploaded_files:
        if file.filename != '':
            filename = secure_filename(file.filename)
            if not filename:
                filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            saved_count += 1
            if gui_log_callback:
                gui_log_callback(f"收到檔案: {filename}")
    return f"OK: {saved_count}", 200

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def open_folder():
    """打開接收檔案的資料夾"""
    if platform.system() == "Windows":
        os.startfile(UPLOAD_FOLDER)
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", UPLOAD_FOLDER])
    else:  # Linux
        subprocess.Popen(["xdg-open", UPLOAD_FOLDER])

# --- GUI 介面部分 ---
class AppGUI:
    def __init__(self, root, url):
        self.root = root
        self.url = url
        
        self.root.title("iPhone 照片傳輸助手")
        self.root.geometry("400x580")
        self.root.resizable(False, False)

        # 加上這行：設置 GUI 視窗標題列圖示
        if os.path.exists("app_icon.ico"):
            self.root.iconbitmap("app_icon.ico")
        
        # 標題
        title_label = tk.Label(root, text="iPhone 照片傳輸助手", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 網址顯示
        url_label = tk.Label(root, text=f"網址: {self.url}", font=("Arial", 11), fg="#007aff")
        url_label.pack(pady=2)

        hint_label = tk.Label(root, text="請用 iPhone 鏡頭掃描下方 QR Code", font=("Arial", 10), fg="gray")
        hint_label.pack(pady=2)

        # 生成並顯示 QR Code
        qr_img = qrcode.make(self.url)
        qr_img = qr_img.resize((220, 220))
        self.qr_photo = ImageTk.PhotoImage(qr_img)
        
        qr_label = tk.Label(root, image=self.qr_photo)
        qr_label.pack(pady=10)

        # 開啟資料夾按鈕
        open_btn = tk.Button(
            root, text="📁 開啟接收資料夾", font=("Arial", 11, "bold"),
            bg="#34c759", fg="white", relief="flat", padx=10, pady=5,
            command=open_folder
        )
        open_btn.pack(pady=10)

        # 即時日誌訊息框
        log_frame = tk.LabelFrame(root, text="傳輸日誌", font=("Arial", 10))
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.log_list = tk.Listbox(log_frame, font=("Arial", 9), borderwidth=0)
        self.log_list.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_list.config(yscrollcommand=scrollbar.set)

        # 註冊 log 回調
        global gui_log_callback
        gui_log_callback = self.add_log

    def add_log(self, message):
        self.log_list.insert(tk.END, message)
        self.log_list.see(tk.END)

def run_flask(ip, port):
    # 關閉 Flask 的 console 訊息，讓畫面乾淨
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == '__main__':
    ip = get_local_ip()
    port = 5000
    url = f"http://{ip}:{port}"

    # 在背景執行線程啟動 Flask
    server_thread = threading.Thread(target=run_flask, args=(ip, port), daemon=True)
    server_thread.start()

    # 啟動 Tkinter GUI
    root = tk.Tk()
    gui = AppGUI(root, url)
    root.mainloop()
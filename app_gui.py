import os
import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform

from flask import Flask, request, render_template_string, send_from_directory
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
    <title>雙向檔案傳輸助手</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            padding: 20px; 
            text-align: center; 
            background-color: #f2f2f7;
            color: #1c1c1e;
        }
        .card {
            background: white;
            padding: 24px 20px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            max-width: 400px;
            margin: 0 auto 20px auto;
        }
        h2 { margin-top: 0; font-size: 20px; }
        .upload-btn { 
            font-size: 16px; 
            font-weight: 600;
            padding: 14px 24px; 
            background: #007aff; 
            color: white; 
            border: none; 
            border-radius: 12px; 
            margin-top: 10px; 
            cursor: pointer;
            width: 100%;
            box-sizing: border-box;
        }
        .upload-btn:disabled { background: #8e8e93; }
        
        .progress-container {
            margin-top: 20px;
            display: none;
        }
        .progress-bar-bg {
            background-color: #e5e5ea;
            border-radius: 8px;
            height: 10px;
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
            margin-top: 10px;
            font-size: 14px;
            color: #3a3a3c;
            word-break: break-word;
        }
        .file-list {
            text-align: left;
            margin-top: 15px;
            list-style: none;
            padding: 0;
            max-height: 250px;
            overflow-y: auto;
        }
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e5e5ea;
        }
        .file-name {
            font-size: 14px;
            color: #1c1c1e;
            word-break: break-all;
            padding-right: 10px;
        }
        .download-link {
            background: #34c759;
            color: white;
            padding: 6px 12px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 13px;
            font-weight: 600;
            white-space: nowrap;
        }
        .refresh-btn {
            background: transparent;
            border: none;
            color: #007aff;
            font-size: 14px;
            cursor: pointer;
            float: right;
        }
    </style>
</head>
<body>
    <!-- 上傳至電腦區塊 -->
    <div class="card">
        <h2>傳送檔案給電腦</h2>
        <p style="color:#8e8e93; font-size:13px; margin-bottom:15px;">點擊下方按鈕選擇照片或影片</p>
        
        <input type="file" id="fileInput" multiple accept="image/*,video/*" style="display:none;">
        <button type="button" class="upload-btn" id="selectBtn" onclick="document.getElementById('fileInput').click()">選取照片與影片</button>

        <div class="progress-container" id="progressContainer">
            <div class="progress-bar-bg">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div id="status">準備中...</div>
        </div>
    </div>

    <!-- 從電腦下載區塊 -->
    <div class="card">
        <div style="overflow: hidden; margin-bottom: 10px;">
            <span style="font-weight: bold; font-size: 18px; float: left;">電腦上的檔案</span>
            <button class="refresh-btn" onclick="loadFileList()">重新整理</button>
        </div>
        <ul class="file-list" id="fileList">
            <li style="color:#8e8e93; text-align:center;">載入中...</li>
        </ul>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', () => {
        loadFileList();

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
                    loadFileList(); // 上傳成功後順便更新檔案清單
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

    // 取得電腦共享資料夾中的檔案清單
    function loadFileList() {
        fetch('/files')
            .then(res => res.json())
            .then(data => {
                const listEl = document.getElementById('fileList');
                listEl.innerHTML = '';
                if (data.length === 0) {
                    listEl.innerHTML = '<li style="color:#8e8e93; text-align:center; padding: 10px;">目前電腦資料夾無檔案</li>';
                    return;
                }
                data.forEach(filename => {
                    const li = document.createElement('li');
                    li.className = 'file-item';
                    li.innerHTML = `
                        <span class="file-name">${filename}</span>
                        <a href="/download/${encodeURIComponent(filename)}" class="download-link" download>下載</a>
                    `;
                    listEl.appendChild(li);
                });
            })
            .catch(err => {
                console.error(err);
            });
    }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# 上傳檔案至電腦
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

# 獲取電腦上的檔案清單 API
@app.route('/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(UPLOAD_FOLDER)
        # 過濾掉隱藏檔案
        files = [f for f in files if not f.startswith('.')]
        return files
    except Exception as e:
        return [], 500

# 下載檔案至手機 API
@app.route('/download/<filename>')
def download_file(filename):
    if gui_log_callback:
        gui_log_callback(f"手機下載了檔案: {filename}")
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

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
        
        self.root.title("雙向檔案傳輸助手")
        self.root.geometry("420x620")
        self.root.resizable(False, False)

        if os.path.exists("app_icon.ico"):
            self.root.iconbitmap("app_icon.ico")
        
        title_label = tk.Label(root, text="雙向檔案傳輸助手", font=("Arial", 16, "bold"))
        title_label.pack(pady=8)

        url_label = tk.Label(root, text=f"網址: {self.url}", font=("Arial", 11), fg="#007aff")
        url_label.pack(pady=2)

        hint_label = tk.Label(root, text="請用 iPhone 鏡頭掃描下方 QR Code", font=("Arial", 10), fg="gray")
        hint_label.pack(pady=2)

        # 生成並顯示 QR Code
        qr_img = qrcode.make(self.url)
        qr_img = qr_img.resize((200, 200))
        self.qr_photo = ImageTk.PhotoImage(qr_img)
        
        qr_label = tk.Label(root, image=self.qr_photo)
        qr_label.pack(pady=5)

        # 按鈕容器（橫向放置）
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=8)

        # 開啟資料夾按鈕
        open_btn = tk.Button(
            btn_frame, text="📁 開啟資料夾", font=("Arial", 10, "bold"),
            bg="#34c759", fg="white", relief="flat", padx=8, pady=4,
            command=open_folder
        )
        open_btn.pack(side="left", padx=5)

        # 新增：從電腦挑選檔案放入共享區
        add_file_btn = tk.Button(
            btn_frame, text="➕ 傳送檔案至手機", font=("Arial", 10, "bold"),
            bg="#007aff", fg="white", relief="flat", padx=8, pady=4,
            command=self.add_files_from_pc
        )
        add_file_btn.pack(side="left", padx=5)

        # 即時日誌訊息框
        log_frame = tk.LabelFrame(root, text="傳輸日誌", font=("Arial", 10))
        log_frame.pack(fill="both", expand=True, padx=15, pady=8)

        self.log_list = tk.Listbox(log_frame, font=("Arial", 9), borderwidth=0)
        self.log_list.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_list.config(yscrollcommand=scrollbar.set)

        global gui_log_callback
        gui_log_callback = self.add_log

    def add_log(self, message):
        self.log_list.insert(tk.END, message)
        self.log_list.see(tk.END)

    def add_files_from_pc(self):
        """讓使用者選擇電腦上的檔案，直接複製到共享資料夾"""
        files = filedialog.askopenfilenames(title="選擇要傳送至手機的檔案")
        if files:
            import shutil
            for fpath in files:
                fname = os.path.basename(fpath)
                dest = os.path.join(UPLOAD_FOLDER, fname)
                shutil.copy(fpath, dest)
                self.add_log(f"已新增分享檔案: {fname}")
            messagebox.showinfo("成功", f"已準備 {len(files)} 個檔案，手機重新整理頁面即可下載！")

def run_flask(ip, port):
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == '__main__':
    ip = get_local_ip()
    port = 5000
    url = f"http://{ip}:{port}"

    server_thread = threading.Thread(target=run_flask, args=(ip, port), daemon=True)
    server_thread.start()

    root = tk.Tk()
    gui = AppGUI(root, url)
    root.mainloop()

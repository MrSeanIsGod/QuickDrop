import os
import sys
import socket
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform
import shutil
import logging

from flask import Flask, request, render_template_string, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import qrcode
from PIL import ImageTk


# =========================================================
# PyInstaller 資源路徑
# =========================================================

def resource_path(relative_path):
    """
    取得程式內部資源的正確路徑。

    開發模式：
        使用目前程式所在資料夾

    PyInstaller --onefile：
        使用 PyInstaller 解壓後的暫存資料夾
    """
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)


# =========================================================
# 使用者資料夾
# =========================================================

def get_app_data_folder():
    """
    建立程式專用的 AppData 資料夾。

    Windows:
        C:\\Users\\使用者\\AppData\\Roaming\\雙向檔案傳輸助手

    其他系統：
        ~/.雙向檔案傳輸助手
    """

    if platform.system() == "Windows":
        appdata = os.getenv("APPDATA")

        if appdata:
            base_folder = os.path.join(
                appdata,
                "雙向檔案傳輸助手"
            )
        else:
            base_folder = os.path.join(
                os.path.expanduser("~"),
                "雙向檔案傳輸助手"
            )

    else:
        base_folder = os.path.join(
            os.path.expanduser("~"),
            ".雙向檔案傳輸助手"
        )

    os.makedirs(base_folder, exist_ok=True)

    return base_folder


APP_DATA_FOLDER = get_app_data_folder()

# 所有接收到 / 要分享給手機的檔案都放這裡
UPLOAD_FOLDER = os.path.join(
    APP_DATA_FOLDER,
    "received_files"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# Flask 設定
# =========================================================

app = Flask(__name__)

# 最大單次 HTTP Request：1GB
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024


# =========================================================
# GUI Log Callback
# =========================================================

gui_log_callback = None


def log_message(message):
    """
    統一處理 GUI 日誌。
    """
    print(message)

    if gui_log_callback:
        try:
            gui_log_callback(message)
        except Exception:
            pass


# =========================================================
# HTML 網頁
# =========================================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-TW">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>雙向檔案傳輸助手</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                sans-serif;

            padding: 20px;

            text-align: center;

            background-color: #f2f2f7;

            color: #1c1c1e;

            margin: 0;
        }

        .card {
            background: white;

            padding: 24px 20px;

            border-radius: 16px;

            box-shadow:
                0 4px 12px rgba(0,0,0,0.08);

            max-width: 500px;

            margin:
                0 auto 20px auto;
        }

        h2 {
            margin-top: 0;

            font-size: 20px;
        }

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
        }

        .upload-btn:disabled {
            background: #8e8e93;

            cursor: not-allowed;
        }

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

            transition:
                width 0.2s ease;
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

            max-height: 350px;

            overflow-y: auto;
        }

        .file-item {
            display: flex;

            justify-content: space-between;

            align-items: center;

            gap: 10px;

            padding: 10px 0;

            border-bottom:
                1px solid #e5e5ea;
        }

        .file-name {
            font-size: 14px;

            color: #1c1c1e;

            word-break: break-all;

            padding-right: 10px;

            flex: 1;
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

        .empty-message {
            color: #8e8e93;

            text-align: center;

            padding: 10px;
        }

    </style>

</head>

<body>


    <!-- ================================================= -->
    <!-- iPhone → 電腦 -->
    <!-- ================================================= -->

    <div class="card">

        <h2>傳送檔案給電腦</h2>

        <p
            style="
                color:#8e8e93;
                font-size:13px;
                margin-bottom:15px;
            "
        >
            點擊下方按鈕選擇照片或影片
        </p>

        <input
            type="file"
            id="fileInput"
            multiple
            accept="image/*,video/*"
            style="display:none;"
        >

        <button
            type="button"
            class="upload-btn"
            id="selectBtn"
            onclick="
                document
                .getElementById('fileInput')
                .click()
            "
        >
            選取照片與影片
        </button>


        <div
            class="progress-container"
            id="progressContainer"
        >

            <div class="progress-bar-bg">

                <div
                    class="progress-bar"
                    id="progressBar"
                ></div>

            </div>

            <div id="status">
                準備中...
            </div>

        </div>

    </div>


    <!-- ================================================= -->
    <!-- 電腦 → iPhone -->
    <!-- ================================================= -->

    <div class="card">

        <div
            style="
                overflow: hidden;
                margin-bottom: 10px;
            "
        >

            <span
                style="
                    font-weight:bold;
                    font-size:18px;
                    float:left;
                "
            >
                電腦上的檔案
            </span>

            <button
                class="refresh-btn"
                onclick="loadFileList()"
            >
                重新整理
            </button>

        </div>


        <ul
            class="file-list"
            id="fileList"
        >

            <li class="empty-message">
                載入中...
            </li>

        </ul>

    </div>


    <script>

    // =====================================================
    // 頁面載入
    // =====================================================

    document.addEventListener(
        'DOMContentLoaded',
        () => {

            loadFileList();

            const fileInput =
                document.getElementById(
                    'fileInput'
                );

            const selectBtn =
                document.getElementById(
                    'selectBtn'
                );

            const progressContainer =
                document.getElementById(
                    'progressContainer'
                );

            const progressBar =
                document.getElementById(
                    'progressBar'
                );

            const status =
                document.getElementById(
                    'status'
                );


            // =================================================
            // 選擇檔案
            // =================================================

            fileInput.addEventListener(
                'change',
                () => {

                    const files =
                        fileInput.files;

                    if (
                        files.length === 0
                    ) {
                        return;
                    }


                    selectBtn.disabled = true;

                    progressContainer.style.display =
                        'block';

                    progressBar.style.width =
                        '0%';

                    status.innerText =
                        `正在準備傳輸 ${files.length} 個檔案...`;


                    const formData =
                        new FormData();


                    for (
                        let i = 0;
                        i < files.length;
                        i++
                    ) {

                        formData.append(
                            'files',
                            files[i]
                        );

                    }


                    const xhr =
                        new XMLHttpRequest();


                    xhr.open(
                        'POST',
                        '/upload',
                        true
                    );


                    // =================================================
                    // 上傳進度
                    // =================================================

                    xhr.upload.onprogress =
                        (e) => {

                            if (
                                e.lengthComputable
                            ) {

                                const percent =
                                    Math.round(
                                        (
                                            e.loaded /
                                            e.total
                                        ) * 100
                                    );


                                progressBar.style.width =
                                    percent + '%';


                                status.innerText =
                                    `已傳輸 ${percent}% ` +
                                    `(${(
                                        e.loaded /
                                        1024 /
                                        1024
                                    ).toFixed(1)} MB / ` +
                                    `${(
                                        e.total /
                                        1024 /
                                        1024
                                    ).toFixed(1)} MB)`;

                            }

                        };


                    // =================================================
                    // 完成
                    // =================================================

                    xhr.onload = () => {

                        selectBtn.disabled =
                            false;


                        if (
                            xhr.status === 200
                        ) {

                            progressBar.style.width =
                                '100%';


                            status.innerHTML =
                                `<span
                                    style="
                                        color:#34c759;
                                        font-weight:bold;
                                    "
                                >
                                    🎉 ${xhr.responseText}
                                </span>`;


                            loadFileList();

                        }

                        else {

                            let message =
                                `❌ 上傳失敗 ` +
                                `(錯誤碼 ${xhr.status})`;

                            if (
                                xhr.status === 413
                            ) {

                                message =
                                    '❌ 檔案太大，單次傳輸上限為 1GB';

                            }


                            status.innerHTML =
                                `<span
                                    style="
                                        color:#ff3b30;
                                    "
                                >
                                    ${message}
                                </span>`;

                        }


                        fileInput.value = '';

                    };


                    // =================================================
                    // 網路錯誤
                    // =================================================

                    xhr.onerror = () => {

                        selectBtn.disabled =
                            false;


                        status.innerHTML =
                            `<span
                                style="
                                    color:#ff3b30;
                                "
                            >
                                ❌ 網路連線錯誤，傳輸中斷
                            </span>`;


                        fileInput.value = '';

                    };


                    xhr.send(formData);

                }
            );

        }
    );


    // =====================================================
    // 取得檔案列表
    // =====================================================

    function loadFileList() {

        fetch('/files')

            .then(
                res => {

                    if (!res.ok) {
                        throw new Error(
                            '無法取得檔案列表'
                        );
                    }

                    return res.json();

                }
            )

            .then(
                data => {

                    const listEl =
                        document.getElementById(
                            'fileList'
                        );


                    listEl.innerHTML = '';


                    if (
                        data.length === 0
                    ) {

                        listEl.innerHTML =
                            `
                            <li class="empty-message">
                                目前電腦資料夾無檔案
                            </li>
                            `;

                        return;

                    }


                    data.forEach(
                        filename => {

                            const li =
                                document.createElement(
                                    'li'
                                );

                            li.className =
                                'file-item';


                            const nameSpan =
                                document.createElement(
                                    'span'
                                );

                            nameSpan.className =
                                'file-name';

                            nameSpan.textContent =
                                filename;


                            const link =
                                document.createElement(
                                    'a'
                                );

                            link.className =
                                'download-link';

                            link.href =
                                '/download/' +
                                encodeURIComponent(
                                    filename
                                );

                            link.textContent =
                                '下載';

                            link.setAttribute(
                                'download',
                                ''
                            );


                            li.appendChild(
                                nameSpan
                            );

                            li.appendChild(
                                link
                            );


                            listEl.appendChild(
                                li
                            );

                        }
                    );

                }
            )

            .catch(
                err => {

                    console.error(err);

                    const listEl =
                        document.getElementById(
                            'fileList'
                        );

                    listEl.innerHTML =
                        `
                        <li class="empty-message">
                            無法取得檔案列表
                        </li>
                        `;

                }
            );

    }

    </script>

</body>

</html>
'''


# =========================================================
# 工具函式
# =========================================================

def make_unique_filename(filename):
    """
    避免檔案名稱重複時覆蓋原本的檔案。

    例如：

        photo.jpg
        photo (1).jpg
        photo (2).jpg
    """

    filename = os.path.basename(filename)

    if not filename:
        filename = "uploaded_file"

    name, ext = os.path.splitext(filename)

    candidate = filename

    counter = 1

    while os.path.exists(
        os.path.join(
            UPLOAD_FOLDER,
            candidate
        )
    ):

        candidate = f"{name} ({counter}){ext}"

        counter += 1

    return candidate


def get_local_ip():
    """
    取得目前電腦區域網路 IP。
    """

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:

        s.connect(
            ("10.255.255.255", 1)
        )

        ip = s.getsockname()[0]

    except Exception:

        ip = "127.0.0.1"

    finally:

        s.close()

    return ip


def find_free_port(start_port=5000):
    """
    從指定 Port 開始尋找可用 Port。
    """

    port = start_port

    while port <= 65535:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        try:

            sock.bind(
                ("0.0.0.0", port)
            )

            sock.close()

            return port

        except OSError:

            sock.close()

            port += 1

    raise RuntimeError(
        "找不到可以使用的網路 Port。"
    )


def open_folder():
    """
    開啟接收檔案資料夾。
    """

    try:

        if platform.system() == "Windows":

            os.startfile(
                UPLOAD_FOLDER
            )

        elif platform.system() == "Darwin":

            subprocess.Popen(
                ["open", UPLOAD_FOLDER]
            )

        else:

            subprocess.Popen(
                ["xdg-open", UPLOAD_FOLDER]
            )

    except Exception as e:

        messagebox.showerror(
            "錯誤",
            f"無法開啟資料夾：\n{e}"
        )


# =========================================================
# Flask Routes
# =========================================================

@app.route("/")
def index():

    return render_template_string(
        HTML_TEMPLATE
    )


# =========================================================
# 上傳檔案
# =========================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_file():

    uploaded_files = \
        request.files.getlist("files")

    saved_count = 0

    saved_names = []

    for file in uploaded_files:

        if not file:
            continue

        if not file.filename:
            continue


        # 先安全化檔名
        filename = secure_filename(
            file.filename
        )


        # secure_filename 可能把某些
        # 中文 / 特殊名稱轉成空字串
        if not filename:

            original_name = os.path.basename(
                file.filename
            )

            filename = (
                original_name
                if original_name
                else "uploaded_file"
            )


        # 避免重複檔案被覆蓋
        filename = make_unique_filename(
            filename
        )


        save_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )


        try:

            file.save(save_path)

            saved_count += 1

            saved_names.append(
                filename
            )

            log_message(
                f"收到檔案: {filename}"
            )

        except Exception as e:

            log_message(
                f"檔案儲存失敗: "
                f"{filename} - {e}"
            )


    return (
        f"成功傳輸 {saved_count} 個檔案！",
        200
    )


# =========================================================
# 檔案列表
# =========================================================

@app.route(
    "/files",
    methods=["GET"]
)
def list_files():

    try:

        files = []

        for filename in os.listdir(
            UPLOAD_FOLDER
        ):

            full_path = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            # 只顯示檔案，不顯示資料夾
            if os.path.isfile(
                full_path
            ):

                if not filename.startswith("."):

                    files.append(
                        filename
                    )


        files.sort(
            key=lambda x: x.lower()
        )


        return jsonify(files)


    except Exception as e:

        log_message(
            f"取得檔案列表失敗: {e}"
        )

        return jsonify([]), 500


# =========================================================
# 下載檔案
# =========================================================

@app.route(
    "/download/<path:filename>"
)
def download_file(filename):

    filename = os.path.basename(
        filename
    )

    full_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    if not os.path.isfile(
        full_path
    ):

        return (
            "檔案不存在",
            404
        )


    log_message(
        f"手機下載了檔案: {filename}"
    )


    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=True
    )


# =========================================================
# Flask Server
# =========================================================

def run_flask(port):

    # 隱藏 Flask / Werkzeug 大量輸出
    log = logging.getLogger(
        "werkzeug"
    )

    log.setLevel(
        logging.ERROR
    )


    try:

        app.run(
            host="0.0.0.0",
            port=port,
            threaded=True,
            debug=False,
            use_reloader=False
        )

    except Exception as e:

        log_message(
            f"Flask Server 啟動失敗: {e}"
        )


# =========================================================
# GUI
# =========================================================

class AppGUI:

    def __init__(
        self,
        root,
        url
    ):

        self.root = root

        self.url = url


        # =================================================
        # 視窗
        # =================================================

        self.root.title(
            "雙向檔案傳輸助手"
        )

        self.root.geometry(
            "440x650"
        )

        self.root.resizable(
            False,
            False
        )


        # =================================================
        # Icon
        # =================================================

        icon_path = resource_path(
            "app_icon.ico"
        )

        if os.path.exists(
            icon_path
        ):

            try:

                self.root.iconbitmap(
                    icon_path
                )

            except Exception:

                pass


        # =================================================
        # 標題
        # =================================================

        title_label = tk.Label(
            root,
            text="雙向檔案傳輸助手",
            font=(
                "Arial",
                16,
                "bold"
            )
        )

        title_label.pack(
            pady=8
        )


        # =================================================
        # URL
        # =================================================

        url_label = tk.Label(
            root,
            text=f"網址: {self.url}",
            font=(
                "Arial",
                11
            ),
            fg="#007aff",
            cursor="hand2"
        )

        url_label.pack(
            pady=2
        )


        # =================================================
        # 提示
        # =================================================

        hint_label = tk.Label(
            root,
            text=(
                "請確認手機與電腦連接同一個 Wi-Fi\n"
                "再使用 iPhone 鏡頭掃描下方 QR Code"
            ),
            font=(
                "Arial",
                10
            ),
            fg="gray",
            justify="center"
        )

        hint_label.pack(
            pady=4
        )


        # =================================================
        # QR Code
        # =================================================

        qr_img = qrcode.make(
            self.url
        )

        qr_img = qr_img.resize(
            (200, 200)
        )


        self.qr_photo = ImageTk.PhotoImage(
            qr_img
        )


        qr_label = tk.Label(
            root,
            image=self.qr_photo
        )

        qr_label.pack(
            pady=5
        )


        # =================================================
        # 按鈕
        # =================================================

        btn_frame = tk.Frame(
            root
        )

        btn_frame.pack(
            pady=8
        )


        # 開啟資料夾
        open_btn = tk.Button(
            btn_frame,
            text="📁 開啟資料夾",
            font=(
                "Arial",
                10,
                "bold"
            ),
            bg="#34c759",
            fg="white",
            relief="flat",
            padx=8,
            pady=5,
            command=open_folder
        )

        open_btn.pack(
            side="left",
            padx=5
        )


        # 電腦 → 手機
        add_file_btn = tk.Button(
            btn_frame,
            text="➕ 傳送檔案至手機",
            font=(
                "Arial",
                10,
                "bold"
            ),
            bg="#007aff",
            fg="white",
            relief="flat",
            padx=8,
            pady=5,
            command=self.add_files_from_pc
        )

        add_file_btn.pack(
            side="left",
            padx=5
        )


        # =================================================
        # 路徑資訊
        # =================================================

        path_label = tk.Label(
            root,
            text=(
                f"檔案位置：{UPLOAD_FOLDER}"
            ),
            font=(
                "Arial",
                8
            ),
            fg="gray",
            wraplength=400,
            justify="center"
        )

        path_label.pack(
            pady=2
        )


        # =================================================
        # 傳輸日誌
        # =================================================

        log_frame = tk.LabelFrame(
            root,
            text="傳輸日誌",
            font=(
                "Arial",
                10
            )
        )

        log_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=8
        )


        self.log_list = tk.Listbox(
            log_frame,
            font=(
                "Arial",
                9
            ),
            borderwidth=0
        )

        self.log_list.pack(
            fill="both",
            expand=True,
            side="left"
        )


        scrollbar = ttk.Scrollbar(
            log_frame,
            orient="vertical",
            command=self.log_list.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )


        self.log_list.config(
            yscrollcommand=scrollbar.set
        )


        # =================================================
        # GUI Log Callback
        # =================================================

        global gui_log_callback

        gui_log_callback = self.add_log


        self.add_log(
            "程式已啟動"
        )

        self.add_log(
            f"共享資料夾：{UPLOAD_FOLDER}"
        )

        self.add_log(
            f"連線網址：{self.url}"
        )


        # =================================================
        # 關閉視窗
        # =================================================

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )


    # =====================================================
    # 安全更新 Tkinter
    # =====================================================

    def add_log(self, message):

        try:

            if not self.root.winfo_exists():
                return

        except Exception:

            return


        def update():

            try:

                if self.root.winfo_exists():

                    self.log_list.insert(
                        tk.END,
                        message
                    )

                    self.log_list.see(
                        tk.END
                    )

            except Exception:

                pass


        try:

            self.root.after(
                0,
                update
            )

        except Exception:

            pass


    # =====================================================
    # 電腦 → 手機
    # =====================================================

    def add_files_from_pc(self):

        files = filedialog.askopenfilenames(
            title="選擇要傳送至手機的檔案"
        )


        if not files:
            return


        success_count = 0


        for fpath in files:

            try:

                if not os.path.isfile(
                    fpath
                ):
                    continue


                original_name = os.path.basename(
                    fpath
                )


                filename = secure_filename(
                    original_name
                )


                if not filename:

                    filename = (
                        original_name
                        if original_name
                        else "file"
                    )


                filename = make_unique_filename(
                    filename
                )


                dest = os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )


                # 如果來源檔案本身就在共享資料夾
                # 就不需要再 copy
                source = os.path.abspath(
                    fpath
                )

                destination = os.path.abspath(
                    dest
                )


                if source != destination:

                    shutil.copy2(
                        source,
                        destination
                    )


                success_count += 1

                self.add_log(
                    f"已新增分享檔案: {filename}"
                )


            except Exception as e:

                self.add_log(
                    f"檔案加入失敗: "
                    f"{os.path.basename(fpath)} - {e}"
                )


        if success_count > 0:

            messagebox.showinfo(
                "成功",
                (
                    f"已準備 {success_count} 個檔案！\n\n"
                    "手機重新整理網頁即可下載。"
                )
            )

        else:

            messagebox.showwarning(
                "提示",
                "沒有成功加入任何檔案。"
            )


    # =====================================================
    # 關閉程式
    # =====================================================

    def on_close(self):

        result = messagebox.askyesno(
            "關閉程式",
            "確定要關閉雙向檔案傳輸助手嗎？"
        )

        if result:

            self.root.destroy()


# =========================================================
# 主程式
# =========================================================

def main():

    # =====================================================
    # 取得區域網路 IP
    # =====================================================

    ip = get_local_ip()


    # =====================================================
    # 自動尋找可用 Port
    # =====================================================

    try:

        port = find_free_port(
            5000
        )

    except Exception as e:

        messagebox.showerror(
            "啟動失敗",
            str(e)
        )

        return


    url = (
        f"http://{ip}:{port}"
    )


    # =====================================================
    # 啟動 Flask
    # =====================================================

    server_thread = threading.Thread(
        target=run_flask,
        args=(port,),
        daemon=True
    )

    server_thread.start()


    # =====================================================
    # 啟動 GUI
    # =====================================================

    root = tk.Tk()

    gui = AppGUI(
        root,
        url
    )


    # =====================================================
    # 顯示啟動資訊
    # =====================================================

    if ip == "127.0.0.1":

        gui.add_log(
            "⚠️ 無法取得區域網路 IP"
        )

        gui.add_log(
            "請確認電腦已連接 Wi-Fi 或網路線。"
        )

    else:

        gui.add_log(
            "✓ 區域網路 IP 取得成功"
        )

        gui.add_log(
            f"✓ Port: {port}"
        )

        gui.add_log(
            "✓ Flask Server 已啟動"
        )


    root.mainloop()


# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":

    main()

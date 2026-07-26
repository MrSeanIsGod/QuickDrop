# 📱 iPhone 照片傳輸助手

一款使用 **Python + Flask + Tkinter** 製作的區域網路（Wi-Fi）檔案傳輸工具。

只需讓 **iPhone** 與 **電腦** 連接到同一個 Wi-Fi，即可透過瀏覽器上傳照片與影片，不需要安裝任何 App。

---

## ✨ 功能特色

- 📷 支援 iPhone 上傳照片
- 🎥 支援 iPhone 上傳影片
- 🌐 自動建立本機傳輸網站
- 📱 自動產生 QR Code，掃描即可開啟
- 📊 即時顯示上傳進度
- 📝 傳輸日誌顯示
- 📁 一鍵開啟接收資料夾
- 💻 Windows、macOS、Linux 支援
- 🚀 最大支援 1GB 單次上傳

---

# 📷 畫面預覽

### 電腦端

- 顯示 QR Code
- 顯示網址
- 即時傳輸日誌
- 一鍵開啟接收資料夾

### iPhone 端

- 選取照片與影片
- 顯示上傳進度
- 傳輸完成提示

---

# 🛠 使用技術

- Python
- Flask
- Tkinter
- Pillow
- qrcode
- Werkzeug

---

# 📦 安裝

## 1. 下載專案

```bash
git clone https://github.com/MrSeanIsGod/QuickDrop.git

cd QuickDrop
```

---

## 2. 安裝套件

```bash
pip install flask
pip install pillow
pip install qrcode
pip install werkzeug
```

或一次安裝

```bash
pip install flask pillow qrcode werkzeug
```

---

# ▶️ 執行

```bash
python app_gui.py
```

程式啟動後會：

1. 啟動 Flask Server
2. 偵測本機 IP
3. 顯示 QR Code
4. 等待 iPhone 上傳檔案

---

# 📱 使用方式

## 步驟一

讓

- iPhone
- 電腦

連接到同一個 Wi-Fi。

---

## 步驟二

執行程式。

---

## 步驟三

使用 iPhone 相機掃描 QR Code。

---

## 步驟四

點擊

> 選取照片與影片

即可開始傳輸。

---

## 步驟五

等待進度條完成。

所有檔案會存放於：

```
received_files/
```

---

# 📁 專案結構

```
Project
│
├── app.py
├── app_icon.ico
├── received_files/
├── README.md
└── requirements.txt
```

---

# 📂 接收資料夾

程式會自動建立：

```
received_files
```

所有接收到的照片、影片都會儲存在此。

---

# 📋 傳輸日誌

GUI 下方會即時顯示：

```
收到檔案:
IMG_0001.JPG

收到檔案:
IMG_0002.JPG

收到檔案:
VID_0001.MOV
```

方便確認傳輸是否成功。

---

# ⚠ 注意事項

- iPhone 與電腦必須位於同一個 Wi-Fi 網路。
- 傳輸期間請勿關閉程式。
- 傳輸期間請保持 iPhone 網頁開啟。
- 若 Windows 防火牆詢問權限，請允許 Python 存取私人網路。
- 若無法連線，請確認防火牆設定及網路環境。

---

# 📌 已使用套件

```
Flask
Werkzeug
Pillow
qrcode
Tkinter（Python 內建）
socket
threading
subprocess
platform
```

---

# 🔧 打包 EXE（PyInstaller）

安裝：

```bash
pip install pyinstaller
```

打包：

```bash
pyinstaller ^
--onefile ^
--windowed ^
--icon app_icon.ico ^
app_gui.py
```

若需要包含其他資源檔，可依需求加入：

```bash
--add-data
```

---

# 📄 License

MIT License

可自由修改、學習及使用。

---

# ❤️ 作者

使用 Python、Flask 與 Tkinter 製作的簡易區域網路 iPhone 照片/影片無線傳輸工具。

如果這個專案對你有幫助，歡迎給它一個 ⭐！

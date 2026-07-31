# 📱 雙向檔案傳輸助手

一個使用 **Python + Flask + Tkinter** 製作的區域網路雙向檔案傳輸工具。

不需要 USB 線、不需要雲端、不需要登入帳號，只要 **電腦與 iPhone 連接同一個 Wi-Fi 網路**，即可透過手機瀏覽器與電腦互傳照片、影片及其他檔案。

---

## ✨ 功能特色

### 📱 iPhone → 電腦

* 使用 iPhone 相機掃描 QR Code
* 自動開啟檔案傳輸網頁
* 可一次選擇多個照片或影片
* 顯示即時上傳進度
* 顯示目前傳輸容量
* 檔案自動儲存至電腦共享資料夾
* 支援最大單次請求 **1GB**

### 💻 電腦 → iPhone

* 電腦端可選擇檔案加入共享資料夾
* iPhone 開啟網頁即可看到檔案列表
* 點擊「下載」即可將檔案下載到手機
* 支援照片、影片及一般檔案

### 🖥️ 電腦 GUI

* 顯示目前區域網路網址
* 自動產生 QR Code
* 一鍵開啟共享資料夾
* 一鍵選擇檔案傳送至手機
* 即時顯示傳輸日誌
* 支援 Windows、macOS、Linux

---

## 🖼️ 使用方式

### 1. 啟動程式

執行：

```bash
python app.py
```

啟動後會出現 GUI。

程式會自動取得電腦在區域網路上的 IP，例如：

```text
網址: http://192.168.1.100:5000
```

同時會產生 QR Code。

---

### 2. 電腦與 iPhone 連接同一個 Wi-Fi

這是最重要的條件。

例如：

```text
電腦
192.168.1.100
      │
      │ Wi-Fi
      │
iPhone
192.168.1.105
```

兩台裝置必須位於可以互相連線的同一個區域網路。

---

### 3. iPhone 掃描 QR Code

使用 iPhone 相機掃描程式中的 QR Code。

掃描後會出現：

```text
雙向檔案傳輸助手
```

的網頁。

---

## 📤 iPhone 傳檔案到電腦

在 iPhone 網頁中：

1. 點擊「選取照片與影片」
2. 選擇要傳送的照片或影片
3. 等待傳輸完成
4. 電腦端會自動收到檔案

檔案會儲存在：

```text
received_files/
```

例如：

```text
專案資料夾/
├── app.py
├── app_icon.ico
└── received_files/
    ├── IMG_001.jpg
    ├── IMG_002.jpg
    └── video.mp4
```

---

## 📥 電腦傳檔案到 iPhone

在電腦 GUI 點擊：

```text
➕ 傳送檔案至手機
```

選擇要傳送的檔案。

程式會將檔案複製到：

```text
received_files/
```

接著在 iPhone 網頁點擊：

```text
重新整理
```

就會看到檔案。

點擊：

```text
下載
```

即可下載到 iPhone。

---

## 📁 開啟共享資料夾

點擊 GUI 中的：

```text
📁 開啟資料夾
```

即可直接開啟：

```text
received_files/
```

方便管理已傳輸的檔案。

---

## 📊 傳輸進度

iPhone 上傳檔案時會顯示：

```text
已傳輸 45%
(120.5 MB / 260.3 MB)
```

完成後會顯示：

```text
🎉 成功傳輸 3 個檔案！
```

---

# 🛠️ 安裝

## Python 版本

建議：

```text
Python 3.10+
```

---

## 安裝套件

使用：

```bash
pip install -r requirements.txt
```

如果沒有 `requirements.txt`，可以直接安裝：

```bash
pip install flask werkzeug qrcode pillow
```

---

## 📦 requirements.txt

建議內容：

```text
Flask
Werkzeug
qrcode
Pillow
```

---

# 📂 專案結構

建議：

```text
雙向檔案傳輸助手/
│
├── app.py
├── app_icon.ico
├── requirements.txt
├── README.md
│
└── received_files/
```

其中：

| 檔案 / 資料夾           | 用途             |
| ------------------ | -------------- |
| `app.py`           | 主程式            |
| `app_icon.ico`     | Windows GUI 圖示 |
| `requirements.txt` | Python 套件清單    |
| `README.md`        | 使用說明           |
| `received_files/`  | 檔案共享資料夾        |

`received_files/` 如果不存在，程式會自動建立。

---

# 🔐 安全性注意事項

本程式目前是設計給 **區域網路內使用**。

程式啟動 Flask：

```python
app.run(host='0.0.0.0', port=5000)
```

代表區域網路內其他可以連線到電腦的裝置，都可能存取這個網站。

### ⚠️ 請注意

目前程式：

* 沒有帳號密碼
* 沒有登入驗證
* 沒有 HTTPS
* 沒有檔案存取權限管理
* 沒有限制特定裝置
* 沒有病毒掃描

因此 **不要直接將這個程式暴露到 Internet**。

建議只在：

```text
家用 Wi-Fi
私人 Wi-Fi
可信任的區域網路
```

中使用。

---

# 🧱 Windows 防火牆

第一次啟動 Flask 時，Windows 可能會跳出：

```text
Windows Defender 防火牆
```

如果要讓 iPhone 連線，需要允許 Python 通過私人網路。

建議：

```text
☑ 私人網路
☐ 公用網路
```

不要在不信任的公共 Wi-Fi 上開啟檔案分享服務。

---

# 📦 PyInstaller 打包 EXE

如果想把程式打包成 Windows `.exe`，可以使用：

```bash
pip install pyinstaller
```

然後：

```bash
pyinstaller --noconsole --onefile --icon=app_icon.ico app.py
```

完成後：

```text
dist/
└── app.exe
```

即可取得：

```text
app.exe
```

---

## ⚠️ 打包後的檔案位置

目前程式使用：

```python
UPLOAD_FOLDER = os.path.abspath('./received_files')
```

所以 `received_files` 會依照程式目前的工作目錄建立。

例如：

```text
C:\MyApp\
├── app.exe
└── received_files\
```

建議將 EXE 放在獨立資料夾中執行。

---

# 🖼️ GUI Icon

如果要使用：

```text
app_icon.ico
```

請將它放在程式旁邊：

```text
app.exe
app_icon.ico
```

PyInstaller 打包時：

```bash
pyinstaller --noconsole --onefile --icon=app_icon.ico app.py
```

`--icon` 會將圖示設定為 EXE 的程式圖示。

---

# 🧰 技術架構

本專案主要使用：

### Python

負責整個程式邏輯。

### Tkinter

負責建立電腦端 GUI。

包含：

* QR Code
* 網址
* 開啟資料夾
* 檔案選擇
* 傳輸日誌

### Flask

建立區域網路 Web Server。

主要 API：

```text
GET  /
POST /upload
GET  /files
GET  /download/<filename>
```

### QR Code

使用：

```python
qrcode
```

將區域網路網址轉換成 QR Code。

### Pillow

使用：

```python
PIL
```

將 QR Code 顯示在 Tkinter GUI。

---

# 🌐 Web API

## GET `/`

開啟檔案傳輸網頁。

---

## POST `/upload`

接收手機上傳的檔案。

支援多檔案：

```text
files
```

---

## GET `/files`

取得共享資料夾中的檔案列表。

回傳 JSON：

```json
[
    "IMG_001.jpg",
    "IMG_002.jpg",
    "video.mp4"
]
```

---

## GET `/download/<filename>`

下載指定檔案。

例如：

```text
/download/IMG_001.jpg
```

---

# ⚙️ 目前限制

目前版本有以下限制：

### 1. 最大請求大小 1GB

程式設定：

```python
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
```

因此一次 HTTP Request 最大約為：

```text
1GB
```

---

### 2. 檔名可能重複

如果傳入相同檔名：

```text
IMG_001.jpg
```

新的檔案可能會覆蓋舊檔案。

---

### 3. 沒有傳輸速度顯示

目前只顯示：

```text
已傳輸 XX%
```

尚未顯示：

```text
MB/s
剩餘時間
```

---

### 4. 沒有檔案刪除功能

目前手機只能：

```text
查看
下載
```

不能直接從網頁刪除電腦檔案。

---

# 🚀 未來可以加入的功能

如果要繼續升級，可以加入：

* 🔒 PIN / 密碼驗證
* 📱 指定裝置才能連線
* 📊 即時傳輸速度
* ⏱️ 剩餘時間
* 📂 建立資料夾
* 🗑️ 手機刪除電腦檔案
* 🖼️ 照片縮圖預覽
* 🎬 影片預覽
* 📦 拖曳檔案上傳
* 📑 檔案分類
* 🔍 搜尋檔案
* 📝 自訂下載檔案名稱
* 🔄 自動重新整理檔案列表
* 📡 自動偵測區域網路 IP
* 🌐 HTTPS
* 🔐 使用 Token 驗證
* 📦 PyInstaller 一鍵打包
* 💾 自訂接收資料夾
* 📈 傳輸歷史紀錄

---

# 📝 License

此專案可自由修改與使用。

如有需要，可以依照自己的需求修改程式功能與介面。

---

# 👨‍💻 開發環境

```text
Python
Flask
Tkinter
QRCode
Pillow
PyInstaller
```

適合用於：

* iPhone ↔ Windows 檔案傳輸
* iPhone 照片備份
* iPhone 影片傳輸
* 區域網路檔案分享
* 個人區域網路傳檔工具
* Python Flask GUI 專案

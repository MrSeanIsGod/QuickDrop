# 📱 雙向檔案傳輸助手

一款使用 **Python + Flask + Tkinter** 製作的區域網路雙向檔案傳輸工具。

不需要 USB 線、不需要雲端硬碟，只要**電腦與 iPhone 連接同一個 Wi-Fi**，即可透過 QR Code 開啟網頁，在 iPhone 與電腦之間互傳檔案。

本專案支援使用 **PyInstaller 打包成單一 `.exe`**，提供給其他 Windows 使用者直接執行。

---

## ✨ 功能特色

### 📱 iPhone → 電腦

* 使用 iPhone 相機掃描 QR Code
* 自動開啟檔案傳輸網頁
* 一次選擇多個照片或影片
* 即時顯示上傳進度
* 顯示目前傳輸容量
* 上傳完成後自動更新檔案列表
* 單次 HTTP Request 最大支援 **1GB**
* 檔案名稱重複時自動重新命名，不會覆蓋原檔

### 💻 電腦 → iPhone

* 電腦端點擊「傳送檔案至手機」
* 選擇電腦中的檔案
* 檔案自動加入共享資料夾
* iPhone 重新整理網頁即可看到檔案
* 點擊「下載」即可下載到 iPhone

### 🖥️ 電腦 GUI

* 自動取得區域網路 IP
* 自動尋找可使用的 Port
* 自動產生 QR Code
* 顯示目前連線網址
* 一鍵開啟共享資料夾
* 一鍵選擇檔案傳送至手機
* 即時顯示傳輸日誌
* 顯示實際檔案儲存位置
* 支援 PyInstaller 打包成單一 EXE

---

# 📋 系統需求

## 開發環境

如果要自行修改或打包程式：

* Windows 10 / 11
* Python 3.10+
* PyInstaller

需要的 Python 套件：

```text
Flask
Werkzeug
qrcode
Pillow
```

---

## 使用 EXE

如果只是使用已經打包好的：

```text
app.exe
```

則**不需要安裝 Python**。

使用者不需要另外安裝：

```text
❌ Python
❌ Flask
❌ Werkzeug
❌ qrcode
❌ Pillow
❌ PyInstaller
```

只需要執行：

```text
app.exe
```

即可。

---

# 📦 安裝開發環境

如果要從原始碼執行：

```bash
pip install -r requirements.txt
```

或直接：

```bash
pip install Flask Werkzeug qrcode Pillow
```

---

# 📁 專案結構

開發時建議：

```text
雙向檔案傳輸助手/
│
├── app.py
├── app_icon.ico
├── requirements.txt
└── README.md
```

其中：

| 檔案                 | 用途           |
| ------------------ | ------------ |
| `app.py`           | 主程式          |
| `app_icon.ico`     | EXE 與 GUI 圖示 |
| `requirements.txt` | Python 套件清單  |
| `README.md`        | 專案說明         |

**不需要自行建立 `received_files`。**

程式第一次執行時會自動建立。

---

# 🚀 執行程式

如果使用 Python 執行：

```bash
python app.py
```

啟動後會看到類似：

```text
雙向檔案傳輸助手

網址: http://192.168.1.100:5000

請確認手機與電腦連接同一個 Wi-Fi
再使用 iPhone 鏡頭掃描下方 QR Code
```

程式會自動產生 QR Code。

---

# 📱 使用方式

## 1. 電腦與 iPhone 連接同一個 Wi-Fi

例如：

```text
電腦
192.168.1.100
       │
       │ Wi-Fi
       │
iPhone
192.168.1.101
```

兩台裝置需要位於可以互相連線的同一個區域網路。

---

## 2. iPhone 掃描 QR Code

開啟 iPhone 相機，掃描電腦程式中的 QR Code。

掃描後會進入：

```text
雙向檔案傳輸助手
```

網頁。

---

# 📤 iPhone → 電腦

在 iPhone 網頁中：

1. 點擊「選取照片與影片」
2. 選擇照片或影片
3. 等待傳輸
4. 傳輸完成後，檔案會儲存到電腦

網頁會顯示：

```text
已傳輸 50%
(125.0 MB / 250.0 MB)
```

完成後：

```text
🎉 成功傳輸 3 個檔案！
```

---

# 📥 電腦 → iPhone

在電腦 GUI 中點擊：

```text
➕ 傳送檔案至手機
```

選擇檔案。

程式會將檔案加入共享資料夾。

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

# 📁 檔案儲存位置

為了讓單一 EXE 可以安全使用，本程式**不會將檔案儲存在 EXE 所在資料夾**。

Windows 使用者的檔案會儲存在：

```text
C:\Users\使用者\AppData\Roaming\雙向檔案傳輸助手\received_files
```

例如：

```text
C:\Users\User\AppData\Roaming\雙向檔案傳輸助手\received_files
```

程式會自動建立資料夾。

---

## 📂 開啟檔案資料夾

在 GUI 中點擊：

```text
📁 開啟資料夾
```

即可直接開啟實際的 `received_files` 資料夾。

---

# 🔄 重複檔案處理

如果傳入相同檔名，程式不會直接覆蓋。

例如第一次傳送：

```text
IMG_001.jpg
```

第二次：

```text
IMG_001 (1).jpg
```

第三次：

```text
IMG_001 (2).jpg
```

以此類推。

---

# 🌐 Port

程式預設從：

```text
5000
```

開始尋找可用 Port。

如果 `5000` 已經被其他程式使用，程式會自動嘗試：

```text
5001
5002
5003
...
```

例如：

```text
http://192.168.1.100:5001
```

因此通常不需要手動修改 Port。

---

# 📦 PyInstaller 打包 EXE

如果希望將程式提供給其他 Windows 使用者使用，可以使用 PyInstaller。

## 1. 安裝 PyInstaller

```bash
pip install pyinstaller
```

---

## 2. 執行打包

在 `app.py` 所在的資料夾開啟 CMD：

```bash
pyinstaller --noconsole --onefile --icon=app_icon.ico --add-data "app_icon.ico;." app.py
```

---

## 3. 打包完成

完成後會產生：

```text
雙向檔案傳輸助手/
│
├── build/
│
├── dist/
│   └── app.exe
│
├── app.spec
├── app.py
├── app_icon.ico
└── requirements.txt
```

真正需要提供給使用者的只有：

```text
dist\app.exe
```

---

# 🎯 給其他使用者

打包完成後，可以直接將：

```text
app.exe
```

複製給其他人。

對方不需要：

```text
❌ Python
❌ pip
❌ requirements.txt
❌ app_icon.ico
❌ Flask
❌ Pillow
❌ qrcode
❌ 原始碼
❌ received_files
```

只需要：

```text
app.exe
```

雙擊即可使用。

---

# 🛡️ Windows 防火牆

第一次執行 EXE 時，Windows 可能會出現：

```text
Windows Defender 防火牆
```

詢問是否允許程式進行網路通訊。

如果需要讓 iPhone 連線，請允許：

```text
☑ 私人網路
```

建議：

```text
☐ 公用網路
```

不要在不信任的公共 Wi-Fi 環境中開啟檔案分享服務。

---

# ⚠️ 網路使用限制

本程式是設計給**區域網路使用**。

程式會啟動：

```text
Flask Web Server
```

並監聽：

```text
0.0.0.0
```

因此，同一個區域網路中可以連線到電腦的裝置，可能可以存取檔案傳輸頁面。

---

## 🔐 目前沒有登入驗證

目前版本沒有：

* 帳號密碼
* PIN 驗證
* Token
* HTTPS
* 使用者權限管理
* 裝置白名單

因此：

> **不要將此程式直接暴露到 Internet。**

建議只在：

```text
私人 Wi-Fi
家用網路
可信任的區域網路
```

中使用。

---

# 📊 檔案限制

目前設定：

```python
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024
```

代表單次 HTTP Request 最大約：

```text
1GB
```

如果一次選擇多個檔案，則整個 Request 的總大小不能超過約 1GB。

---

# 🧰 技術架構

## Python

負責主要程式邏輯。

---

## Tkinter

負責建立 Windows GUI。

包含：

* QR Code
* 網址
* 開啟資料夾
* 傳送檔案
* 傳輸日誌
* 儲存位置

---

## Flask

負責建立區域網路 Web Server。

主要路由：

```text
GET  /
POST /upload
GET  /files
GET  /download/<filename>
```

---

## QRCode

使用 `qrcode` 套件產生 QR Code。

QR Code 內容為：

```text
http://電腦IP:Port
```

例如：

```text
http://192.168.1.100:5000
```

---

## Pillow

使用 Pillow 將 QR Code 顯示於 Tkinter GUI。

---

## PyInstaller

負責將：

```text
Python
+ Flask
+ Pillow
+ qrcode
+ 其他依賴
+ app_icon.ico
```

打包成：

```text
app.exe
```

---

# 🔌 API

## `GET /`

開啟檔案傳輸網頁。

---

## `POST /upload`

接收 iPhone 上傳的檔案。

參數：

```text
files
```

支援多檔案上傳。

---

## `GET /files`

取得目前共享資料夾中的檔案。

回傳 JSON，例如：

```json
[
    "IMG_001.jpg",
    "IMG_002.jpg",
    "video.mp4"
]
```

---

## `GET /download/<filename>`

下載指定檔案。

例如：

```text
/download/IMG_001.jpg
```

---

# 🧹 清理檔案

程式目前不會自動刪除檔案。

如果不再需要某些照片或影片，可以直接從：

```text
received_files
```

資料夾刪除。

也可以使用 GUI：

```text
📁 開啟資料夾
```

直接管理。

---

# 🔧 常見問題

## Q1：iPhone 掃 QR Code 後無法開啟？

確認：

1. 電腦與 iPhone 是否連接同一個 Wi-Fi
2. Windows 防火牆是否允許私人網路
3. 電腦是否正在執行 EXE
4. GUI 顯示的 IP 是否正確

例如：

```text
http://192.168.1.100:5000
```

可以直接在 iPhone Safari 手動輸入測試。

---

## Q2：為什麼 QR Code 可以掃描，但網頁打不開？

通常是 Windows 防火牆阻擋。

請確認 Python / EXE 的網路存取權限，並允許：

```text
私人網路
```

---

## Q3：可以只給朋友一個 EXE 嗎？

可以。

PyInstaller 使用：

```bash
pyinstaller --noconsole --onefile --icon=app_icon.ico --add-data "app_icon.ico;." app.py
```

打包後，只需要提供：

```text
app.exe
```

---

## Q4：需要把 `received_files` 一起給對方嗎？

不需要。

程式第一次啟動時會自動建立：

```text
AppData\Roaming\雙向檔案傳輸助手\received_files
```

---

## Q5：需要把 `app_icon.ico` 給對方嗎？

不需要。

`app_icon.ico` 已經透過：

```text
--add-data "app_icon.ico;."
```

打包進 EXE。

---

## Q6：重新下載 EXE 後，之前的檔案會消失嗎？

不會。

檔案儲存在 Windows 使用者的 AppData：

```text
AppData\Roaming\雙向檔案傳輸助手\received_files
```

而不是 EXE 裡面。

所以即使：

```text
刪除舊 EXE
↓
下載新 EXE
↓
重新執行
```

原本的檔案仍然存在。

---

# 🚀 未來可以加入

未來可以考慮加入：

* 🔐 PIN / 密碼驗證
* 🔑 Token 驗證
* 📱 裝置連線授權
* 📊 即時傳輸速度
* ⏱️ 剩餘傳輸時間
* 📈 傳輸進度
* 🗑️ 手機刪除電腦檔案
* 🖼️ 照片縮圖預覽
* 🎬 影片預覽
* 📂 資料夾管理
* 🔍 檔案搜尋
* 📑 檔案分類
* 📡 更精準的網路介面選擇
* 🔒 HTTPS
* 📦 EXE 自動更新
* 🧹 自動清理舊檔案
* 📈 傳輸歷史紀錄

---

# 📄 License

此專案可自由修改與使用。

---

# 👨‍💻 開發技術

```text
Python
Flask
Tkinter
QRCode
Pillow
PyInstaller
```

---

## ⭐ 快速開始

### 開發者

```bash
pip install -r requirements.txt

pyinstaller --noconsole --onefile --icon=app_icon.ico --add-data "app_icon.ico;." app.py
```

### 使用者

只需要：

```text
雙擊 app.exe
        ↓
確認電腦與 iPhone 使用同一個 Wi-Fi
        ↓
iPhone 掃描 QR Code
        ↓
開始雙向傳輸檔案
```

**一個 EXE，即可使用。**

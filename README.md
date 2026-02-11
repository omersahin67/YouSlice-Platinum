# 🎬 YouSlice Platinum

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Powered-green?style=for-the-badge&logo=ffmpeg&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)

**YouSlice Platinum** is a robust desktop application designed for precise media manipulation. It seamlessly combines a high-speed YouTube downloader with a frame-perfect local media trimmer, bridging the gap between command-line power and user-friendly GUI.

Built with a focus on **Software Engineering principles**, it features a non-blocking UI (Multithreading), dynamic localization (i18n), and direct FFmpeg subprocess management.

---

## 🚀 Key Features

### 1. Dual-Mode Architecture

- **YouTube Downloader:** Downloads full videos or specific segments (e.g., `00:01:20` to `00:02:45`).
  - **Smart Format Selection:** Supports **Video (MP4)** and **Audio-Only (MP3)** extraction.
  - **Windows Compatibility:** Automatically converts audio codecs to AAC to ensure playback compatibility with Windows Media Player.
- **Precision Editor (Trimmer):** Trims local media files with millisecond accuracy.
  - Uses `libx264` re-encoding to solve keyframe dependency issues, ensuring cuts happen exactly where you want them.

### 2. Advanced Engineering

- **Concurrency (Multithreading):** Utilizes Python's `threading` module to keep the UI responsive while heavy rendering tasks run in the background.
- **Localization (i18n):** Features a dynamic dictionary-based language system, allowing instant switching between **English** and **Turkish** without restarting.
- **Safe File Operations:** Implements a temporary file buffer system to allow safe overwriting of source files without corruption.

### 3. Modern User Interface

- Built with **CustomTkinter** for a sleek, dark-mode aesthetic.
- Intuitive "Hour : Minute : Second" input fields.
- Real-time progress bars (Indeterminate mode) and status updates.

---

## 🔧 Tech Stack & Technologies

This project was built using the following technologies:

- **Language:** Python 3.10+
- **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern UI wrapper for Tkinter)
- **Media Processing:** [FFmpeg](https://ffmpeg.org/) (Direct subprocess management)
- **Downloader Engine:** [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Concurrency:** Python `threading` module (UI/Logic separation)
- **Packaging:** PyInstaller (Executable generation)
- **Version Control:** Git & GitHub

---

## 🛠️ Installation & Setup

### Prerequisites

1.  **Python 3.10+** installed.
2.  **FFmpeg** must be installed and added to your system's PATH.

### 1. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/YouSlice-Platinum.git](https://github.com/YOUR_USERNAME/YouSlice-Platinum.git)
cd YouSlice-Platinum
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Run the Application
Bash
python main.py
📖 Usage Guide
📥 Downloading from YouTube
Go to the "Download (YouTube)" tab.

Paste the URL and select the format (MP4/MP3).

Enter Start and End times (or check "Download Full Video").

Click DOWNLOAD.

✂️ Trimming Local Files
Go to the "Edit (Local File)" tab.

Select a file from your computer.

Set the time range.

Check "Overwrite original file" if you want to replace the source.

Click TRIM AND SAVE.

🏗️ Building the Executable (.exe)
To distribute this application as a standalone file (without requiring Python), use PyInstaller:

Bash
pyinstaller --noconsole --onefile --icon="logo.ico" --name="YouSlicePlatinum" main.py
Note: The generated .exe file in the dist folder requires ffmpeg.exe to be present in the same directory to function on other computers.

👨‍💻 Author
Ömer Talha Şahin - Software Engineering Student

GitHub: @omersahin67

LinkedIn: Ömer Talha Şahin

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
```

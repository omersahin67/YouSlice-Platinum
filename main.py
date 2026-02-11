import customtkinter as ctk
import yt_dlp
import os
import threading
import subprocess
from tkinter import filedialog
import shutil

# --- DİL VERİTABANI ---
TEXTS = {
    "tr": {
        "app_title": "YouSlice Platinum",
        "tab_dl": "İndir (YouTube)",
        "tab_edit": "Düzenle (Dosya)",
        "header_dl": "YouTube Video İndirici",
        "header_edit": "Hassas Medya Kırpıcı",
        "placeholder_url": "Video Linki Yapıştır",
        "placeholder_file": "Medya Dosyası Seç",
        "btn_folder": "Klasör Seç",
        "btn_file": "Dosya Bul",
        "btn_download": "İNDİR",
        "btn_save": "KIRP VE KAYDET",
        "chk_full": "Videonun Tamamını İndir",
        "chk_overwrite": "Orijinal dosyanın üzerine yaz",
        "lbl_start": "Başlangıç:",
        "lbl_end": "Bitiş:",
        "status_ready": "Hazır",
        "status_processing": "İşleniyor...",
        "status_success": "İşlem Başarılı!",
        "status_error": "Hata oluştu!",
        "status_url_err": "Lütfen Link Giriniz!",
        "status_file_err": "Dosya Seçilmedi!",
        "opt_video": "Video (MP4)",
        "opt_audio": "Ses (MP3)"
    },
    "en": {
        "app_title": "YouSlice Platinum",
        "tab_dl": "Download (YouTube)",
        "tab_edit": "Edit (Local File)",
        "header_dl": "YouTube Video Downloader",
        "header_edit": "Precise Media Trimmer",
        "placeholder_url": "Paste Video Link",
        "placeholder_file": "Select Media File",
        "btn_folder": "Select Folder",
        "btn_file": "Find File",
        "btn_download": "DOWNLOAD",
        "btn_save": "TRIM AND SAVE",
        "chk_full": "Download Full Video",
        "chk_overwrite": "Overwrite original file",
        "lbl_start": "Start:",
        "lbl_end": "End:",
        "status_ready": "Ready",
        "status_processing": "Processing...",
        "status_success": "Operation Successful!",
        "status_error": "Error occurred!",
        "status_url_err": "Please Enter URL!",
        "status_file_err": "No File Selected!",
        "opt_video": "Video (MP4)",
        "opt_audio": "Audio (MP3)"
    }
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- ARKA PLAN MOTORU ---
class VideoEngine:
    def download_segment(self, url, start_time, end_time, save_path, is_audio=False, is_full=False):
        ydl_opts = {
            'outtmpl': f'{save_path}/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        if not is_full:
            ydl_opts['external_downloader'] = 'ffmpeg'
            ydl_opts['external_downloader_args'] = {
                'ffmpeg_i': ['-ss', start_time, '-to', end_time]
            }

        if is_audio:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            if not is_full:
                if 'external_downloader_args' not in ydl_opts:
                    ydl_opts['external_downloader_args'] = {}
                ydl_opts['external_downloader_args']['ffmpeg_o'] = ['-c:v', 'copy', '-c:a', 'aac']
            
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            print(f"Download Error: {e}")
            return False

    def precise_trim(self, input_path, start_time, end_time, overwrite=False):
        # Dosya yolu düzeltmeleri
        input_path = os.path.abspath(input_path)
        path, ext = os.path.splitext(input_path)
        temp_output = f"{path}_temp{ext}"
        
        is_audio_file = ext.lower() in ['.mp3', '.wav', '.m4a', '.flac']
        
        # FFmpeg komutu
        cmd = ['ffmpeg', '-y', '-i', input_path, '-ss', start_time, '-to', end_time]

        if is_audio_file:
            codec = 'libmp3lame' if ext.lower() == '.mp3' else 'aac'
            cmd.extend(['-c:a', codec, '-b:a', '192k'])
        else:
            cmd.extend(['-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', '-b:a', '192k'])
            
        cmd.append(temp_output)
        
        try:
            # Windows'ta pencere açılmasını engelle
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # Subprocess çalıştır
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            
            if overwrite:
                if os.path.exists(input_path): os.remove(input_path)
                os.rename(temp_output, input_path)
                return True, input_path
            else:
                final_output = f"{path}_edited{ext}"
                if os.path.exists(final_output): os.remove(final_output)
                os.rename(temp_output, final_output)
                return True, final_output

        except subprocess.CalledProcessError as e:
            if os.path.exists(temp_output): os.remove(temp_output)
            print(f"FFmpeg Error: {e.stderr.decode('utf-8', errors='ignore')}")
            return False, str(e)
        except Exception as e:
            if os.path.exists(temp_output): os.remove(temp_output)
            return False, str(e)

# --- ARAYÜZ (GUI) ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.lang = "tr"
        self.t = TEXTS[self.lang]
        
        self.title(self.t["app_title"])
        try:
            self.iconbitmap("YouSlice.ico")
        except:
            pass
        self.geometry("650x850")
        self.engine = VideoEngine()
        self.default_path = os.path.join(os.path.expanduser("~"), "Downloads")

        # --- ÜST BAR (Dil Seçimi) ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(10,0))
        
        self.lang_switch = ctk.CTkSegmentedButton(self.top_frame, values=["TR", "EN"], command=self.change_language, width=80)
        self.lang_switch.set("TR")
        self.lang_switch.pack(side="right")

        # --- SEKME BUTONLARI (Manuel Tab Sistemi) ---
        self.tab_selector = ctk.CTkSegmentedButton(self, command=self.switch_tab, height=40, font=("Arial", 14, "bold"))
        self.tab_selector.pack(pady=15, padx=20, fill="x")

        # --- GÖVDE (Frame Container) ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. İndirme Sayfası (Frame)
        self.view_dl = ctk.CTkFrame(self.container)
        self.setup_download_view()

        # 2. Edit Sayfası (Frame)
        self.view_edit = ctk.CTkFrame(self.container)
        self.setup_edit_view()

        # Başlangıçta İndirme sayfasını göster
        self.active_view = "dl"
        self.update_ui_text()
        self.view_dl.pack(fill="both", expand=True)

    def change_language(self, value):
        self.lang = value.lower()
        self.t = TEXTS[self.lang]
        self.update_ui_text()

    def switch_tab(self, value):
        # Tıklanan buton ismine göre sayfayı değiştir
        if value == self.t["tab_dl"]:
            self.view_edit.pack_forget()
            self.view_dl.pack(fill="both", expand=True)
            self.active_view = "dl"
        else:
            self.view_dl.pack_forget()
            self.view_edit.pack(fill="both", expand=True)
            self.active_view = "edit"

    def update_ui_text(self):
        self.title(self.t["app_title"])
        
        # Sekme İsimlerini Güncelle
        old_val = self.tab_selector.get()
        new_values = [self.t["tab_dl"], self.t["tab_edit"]]
        self.tab_selector.configure(values=new_values)
        
        # Seçili sekmeyi koru
        if self.active_view == "dl":
            self.tab_selector.set(self.t["tab_dl"])
        else:
            self.tab_selector.set(self.t["tab_edit"])

        # İndirme Sayfası Metinleri
        self.header_dl.configure(text=self.t["header_dl"])
        self.url_entry.configure(placeholder_text=self.t["placeholder_url"])
        self.d_format_switch.configure(values=[self.t["opt_video"], self.t["opt_audio"]])
        if self.d_format_switch.get() not in [self.t["opt_video"], self.t["opt_audio"]]:
            self.d_format_switch.set(self.t["opt_video"]) # Varsayılanı sıfırla

        self.full_video_chk.configure(text=self.t["chk_full"])
        self.path_btn.configure(text=self.t["btn_folder"])
        self.d_btn.configure(text=self.t["btn_download"])
        self.lbl_d_start.configure(text=self.t["lbl_start"])
        self.lbl_d_end.configure(text=self.t["lbl_end"])

        # Edit Sayfası Metinleri
        self.header_edit.configure(text=self.t["header_edit"])
        self.file_entry.configure(placeholder_text=self.t["placeholder_file"])
        self.file_btn.configure(text=self.t["btn_file"])
        self.overwrite_chk.configure(text=self.t["chk_overwrite"])
        self.e_btn.configure(text=self.t["btn_save"])
        self.lbl_e_start.configure(text=self.t["lbl_start"])
        self.lbl_e_end.configure(text=self.t["lbl_end"])

    # --- UI KURULUMLARI ---
    def setup_download_view(self):
        parent = self.view_dl
        self.header_dl = ctk.CTkLabel(parent, text="", font=("Arial", 22, "bold"))
        self.header_dl.pack(pady=20)
        
        self.url_entry = ctk.CTkEntry(parent, width=450, height=35)
        self.url_entry.pack(pady=10)

        self.d_format_var = ctk.StringVar(value="Video (MP4)")
        self.d_format_switch = ctk.CTkSegmentedButton(parent, variable=self.d_format_var)
        self.d_format_switch.pack(pady=10)

        self.full_video_var = ctk.BooleanVar(value=False)
        self.full_video_chk = ctk.CTkCheckBox(parent, variable=self.full_video_var, command=self.toggle_time_inputs)
        self.full_video_chk.pack(pady=10)

        self.d_time_frame = ctk.CTkFrame(parent)
        self.d_time_frame.pack(pady=10)
        self.create_time_inputs(self.d_time_frame, "d_start", "d_end", "d")

        self.path_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.path_frame.pack(pady=10)
        self.path_entry = ctk.CTkEntry(self.path_frame, width=350)
        self.path_entry.insert(0, self.default_path)
        self.path_entry.pack(side="left", padx=5)
        self.path_btn = ctk.CTkButton(self.path_frame, command=self.select_folder, width=80)
        self.path_btn.pack(side="left")

        self.d_progress = ctk.CTkProgressBar(parent, width=400, mode="indeterminate")
        self.d_progress.pack(pady=20)
        
        self.d_btn = ctk.CTkButton(parent, height=45, font=("Arial", 16, "bold"), command=self.run_download_thread)
        self.d_btn.pack(pady=10)
        self.d_status = ctk.CTkLabel(parent, text="", text_color="gray")
        self.d_status.pack()

    def setup_edit_view(self):
        parent = self.view_edit
        self.header_edit = ctk.CTkLabel(parent, text="", font=("Arial", 22, "bold"))
        self.header_edit.pack(pady=20)

        self.file_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.file_frame.pack(pady=20)
        self.file_entry = ctk.CTkEntry(self.file_frame, width=350, height=35)
        self.file_entry.pack(side="left", padx=5)
        self.file_btn = ctk.CTkButton(self.file_frame, command=self.select_file, width=80)
        self.file_btn.pack(side="left")

        self.e_time_frame = ctk.CTkFrame(parent)
        self.e_time_frame.pack(pady=10)
        self.create_time_inputs(self.e_time_frame, "e_start", "e_end", "e")

        self.overwrite_var = ctk.BooleanVar(value=False)
        self.overwrite_chk = ctk.CTkCheckBox(parent, variable=self.overwrite_var, text_color="#FF6666")
        self.overwrite_chk.pack(pady=15)

        self.e_progress = ctk.CTkProgressBar(parent, width=400, mode="indeterminate")
        self.e_progress.pack(pady=10)

        self.e_btn = ctk.CTkButton(parent, height=45, font=("Arial", 16, "bold"), fg_color="green", hover_color="darkgreen", command=self.run_edit_thread)
        self.e_btn.pack(pady=10)
        self.e_status = ctk.CTkLabel(parent, text="", text_color="gray")
        self.e_status.pack()

    # --- YARDIMCI METOTLAR ---
    def create_time_inputs(self, parent, start_prefix, end_prefix, label_prefix):
        # Saat : Dakika : Saniye girişleri
        lbl_s = ctk.CTkLabel(parent, text="S:")
        lbl_s.grid(row=0, column=0, padx=5, pady=5)
        setattr(self, f"lbl_{label_prefix}_start", lbl_s)

        setattr(self, f"{start_prefix}_hour", ctk.CTkEntry(parent, width=40)); getattr(self, f"{start_prefix}_hour").grid(row=0, column=1); getattr(self, f"{start_prefix}_hour").insert(0, "00")
        ctk.CTkLabel(parent, text=":").grid(row=0, column=2)
        setattr(self, f"{start_prefix}_min", ctk.CTkEntry(parent, width=40)); getattr(self, f"{start_prefix}_min").grid(row=0, column=3); getattr(self, f"{start_prefix}_min").insert(0, "00")
        ctk.CTkLabel(parent, text=":").grid(row=0, column=4)
        setattr(self, f"{start_prefix}_sec", ctk.CTkEntry(parent, width=40)); getattr(self, f"{start_prefix}_sec").grid(row=0, column=5); getattr(self, f"{start_prefix}_sec").insert(0, "00")

        lbl_e = ctk.CTkLabel(parent, text="E:")
        lbl_e.grid(row=0, column=6, padx=(20, 5))
        setattr(self, f"lbl_{label_prefix}_end", lbl_e)

        setattr(self, f"{end_prefix}_hour", ctk.CTkEntry(parent, width=40)); getattr(self, f"{end_prefix}_hour").grid(row=0, column=7); getattr(self, f"{end_prefix}_hour").insert(0, "00")
        ctk.CTkLabel(parent, text=":").grid(row=0, column=8)
        setattr(self, f"{end_prefix}_min", ctk.CTkEntry(parent, width=40)); getattr(self, f"{end_prefix}_min").grid(row=0, column=9); getattr(self, f"{end_prefix}_min").insert(0, "00")
        ctk.CTkLabel(parent, text=":").grid(row=0, column=10)
        setattr(self, f"{end_prefix}_sec", ctk.CTkEntry(parent, width=40)); getattr(self, f"{end_prefix}_sec").grid(row=0, column=11); getattr(self, f"{end_prefix}_sec").insert(0, "10")

    def toggle_time_inputs(self):
        state = "disabled" if self.full_video_var.get() else "normal"
        widgets = [self.d_start_hour, self.d_start_min, self.d_start_sec, self.d_end_hour, self.d_end_min, self.d_end_sec]
        for w in widgets: w.configure(state=state)

    def get_time_string(self, prefix):
        return f"{getattr(self, f'{prefix}_hour').get().zfill(2)}:{getattr(self, f'{prefix}_min').get().zfill(2)}:{getattr(self, f'{prefix}_sec').get().zfill(2)}"

    def select_folder(self):
        path = filedialog.askdirectory()
        if path: self.path_entry.delete(0, "end"); self.path_entry.insert(0, path)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Media", "*.mp4 *.mkv *.webm *.avi *.mp3 *.wav")])
        if path: self.file_entry.delete(0, "end"); self.file_entry.insert(0, path)

    # --- ÇALIŞTIRMA MANTIĞI ---
    def run_download_thread(self): threading.Thread(target=self.process_download, daemon=True).start()

    def process_download(self):
        url = self.url_entry.get()
        if not url:
            self.d_status.configure(text=self.t["status_url_err"], text_color="red")
            return
        
        self.d_btn.configure(state="disabled")
        self.d_progress.start()
        self.d_status.configure(text=self.t["status_processing"], text_color="yellow")
        
        start = self.get_time_string("d_start")
        end = self.get_time_string("d_end")
        save_path = self.path_entry.get()
        is_audio = self.d_format_switch.get() == self.t["opt_audio"]
        is_full = self.full_video_var.get()

        if self.engine.download_segment(url, start, end, save_path, is_audio, is_full):
            self.d_status.configure(text=self.t["status_success"], text_color="green")
        else:
            self.d_status.configure(text=self.t["status_error"], text_color="red")
        
        self.d_progress.stop()
        self.d_btn.configure(state="normal")

    def run_edit_thread(self): threading.Thread(target=self.process_edit, daemon=True).start()

    def process_edit(self):
        input_path = self.file_entry.get()
        if not input_path:
            self.e_status.configure(text=self.t["status_file_err"], text_color="red")
            return
        
        self.e_btn.configure(state="disabled")
        self.e_progress.start()
        self.e_status.configure(text=self.t["status_processing"], text_color="yellow")

        start = self.get_time_string("e_start")
        end = self.get_time_string("e_end")
        overwrite = self.overwrite_var.get()

        success, msg = self.engine.precise_trim(input_path, start, end, overwrite)
        self.e_progress.stop()
        
        if success:
            self.e_status.configure(text=self.t["status_success"], text_color="green")
        else:
            self.e_status.configure(text=self.t["status_error"], text_color="red")
        
        self.e_btn.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()
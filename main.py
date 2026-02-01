import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import os

class YouTubeDownloader:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Yuno")
        self.window.geometry("600x550")
        self.window.resizable(False, False)
        
        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass

        ctk.set_appearance_mode("dark")
        
        custom_color = "#723ec3"
        
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="Yuno",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        url_label = ctk.CTkLabel(main_frame, text="Video URL:", font=ctk.CTkFont(size=14))
        url_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.url_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Paste YouTube URL here...",
            width=500,
            height=40
        )
        self.url_entry.pack(padx=20, pady=(0, 15))
        
        format_label = ctk.CTkLabel(main_frame, text="Format:", font=ctk.CTkFont(size=14))
        format_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.format_var = ctk.StringVar(value="MP4")
        format_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        format_frame.pack(pady=(0, 15))
        
        self.mp4_radio = ctk.CTkRadioButton(
            format_frame,
            text="MP4",
            variable=self.format_var,
            value="MP4",
            command=self.update_quality_options,
            fg_color="#723ec3",
            hover_color="#5a2f9c"
        )
        self.mp4_radio.pack(side="left", padx=20)
        
        self.mp3_radio = ctk.CTkRadioButton(
            format_frame,
            text="MP3",
            variable=self.format_var,
            value="MP3",
            command=self.update_quality_options,
            fg_color="#723ec3",
            hover_color="#5a2f9c"
        )
        self.mp3_radio.pack(side="left", padx=20)
        
        quality_label = ctk.CTkLabel(main_frame, text="Quality:", font=ctk.CTkFont(size=14))
        quality_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.quality_menu = ctk.CTkOptionMenu(
            main_frame,
            values=["1080p", "2K (1440p)", "4K (2160p)"],
            width=200,
            height=35,
            fg_color="#723ec3",
            button_color="#723ec3",
            button_hover_color="#5a2f9c"
        )
        self.quality_menu.pack(padx=20, pady=(0, 15))
        self.quality_menu.set("1080p")
        
        path_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        self.path_label = ctk.CTkLabel(
            path_frame,
            text=f"Save to: {self.download_path}",
            font=ctk.CTkFont(size=12),
            wraplength=400
        )
        self.path_label.pack(side="left", padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(
            path_frame,
            text="Browse",
            width=100,
            height=30,
            command=self.browse_folder,
            fg_color="#723ec3",
            hover_color="#5a2f9c"
        )
        self.browse_btn.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(main_frame, width=500, progress_color="#723ec3")
        self.progress_bar.pack(padx=20, pady=(10, 5))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready to download",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 15))
        
        self.download_btn = ctk.CTkButton(
            main_frame,
            text="Download",
            width=200,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_download,
            fg_color="#723ec3",
            hover_color="#5a2f9c"
        )
        self.download_btn.pack(pady=10)
        
    def update_quality_options(self):
        """Update quality options based on selected format"""
        if self.format_var.get() == "MP4":
            self.quality_menu.configure(values=["1080p", "2K (1440p)", "4K (2160p)"])
            self.quality_menu.set("1080p")
        else:
            self.quality_menu.configure(values=["192 kbps", "320 kbps"])
            self.quality_menu.set("320 kbps")
    
    def browse_folder(self):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_label.configure(text=f"Save to: {self.download_path}")
    
    def progress_hook(self, d):
        """Update progress bar during download"""
        if d['status'] == 'downloading':
            try:
                percent_str = d.get('_percent_str', '0%').replace('\x1b[0;94m', '').replace('\x1b[0m', '').strip()
                percent = float(percent_str.replace('%', ''))
                self.progress_bar.set(percent / 100)
                self.status_label.configure(text=f"Downloading... {percent:.1f}%")
            except:
                pass
        elif d['status'] == 'finished':
            self.progress_bar.set(1)
            self.status_label.configure(text="Processing... Almost done!")
    
    def download_video(self):
        """Download video/audio in separate thread"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            self.download_btn.configure(state="normal")
            return
        
        try:
            format_type = self.format_var.get()
            quality = self.quality_menu.get()
            
            if format_type == "MP4":
                if quality == "1080p":
                    format_spec = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
                elif quality == "2K (1440p)":
                    format_spec = "bestvideo[height<=1440]+bestaudio/best[height<=1440]"
                else:
                    format_spec = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
                
                ydl_opts = {
                    'format': format_spec,
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'merge_output_format': 'mp4',
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                    'postprocessor_args': [
                        '-c:v', 'copy',
                        '-c:a', 'aac',
                        '-b:a', '192k'
                    ],
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    },
                }
            else:
                audio_quality = '192' if quality == "192 kbps" else '320'
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': audio_quality,
                    }],
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    },
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.status_label.configure(text="Download completed successfully!")
            self.progress_bar.set(1)
            messagebox.showinfo("Success", "Download completed successfully!")
            
        except Exception as e:
            self.status_label.configure(text="Download failed!")
            self.progress_bar.set(0)
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        
        finally:
            self.download_btn.configure(state="normal")
    
    def start_download(self):
        """Start download in separate thread"""
        self.download_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting download...")
        
        thread = threading.Thread(target=self.download_video)
        thread.daemon = True
        thread.start()
    
    def run(self):
        """Run the application"""
        self.window.mainloop()


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()

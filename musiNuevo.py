import customtkinter as ctk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL
import threading
import os
import sys

COLOR_DARK_BG = "#2c3e50"
COLOR_MEDIUM_BG = "#34495e"
COLOR_CYAN = "#1abc9c"
COLOR_CYAN_HOVER = "#16a085"
COLOR_LIGHT = "#ecf0f1"
COLOR_PLACEHOLDER = "#95a5a6"


def _base_opts():
    return {
        'quiet': True,
        'no_warnings': True,
        'extractor_retries': 5,
        'socket_timeout': 30,
    }


def _download_opts(outtmpl, noplaylist, progress_hook):
    return {
        'format': 'bestaudio[ext=webm]/bestaudio/best',
        'outtmpl': outtmpl,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '0',
        }],
        'noplaylist': noplaylist,
        'progress_hooks': [progress_hook],
        'quiet': False,
        'retries': 10,
        'fragment_retries': 10,
        'extractor_retries': 5,
        'socket_timeout': 30,
        'concurrent_fragment_downloads': 4,
    }


def core_download(url, dest, dl_type, on_progress=None):
    """
    Pure download logic, no GUI deps.
    on_progress(downloaded, total, filename) called after each file.
    Returns (type_text, message). Raises ValueError or Exception on failure.
    """
    with YoutubeDL(_base_opts()) as ydl:
        info = ydl.extract_info(url, download=False)

    is_playlist = 'entries' in info
    total_songs = len(info['entries']) if is_playlist else 1

    if dl_type == "video" and is_playlist:
        raise ValueError("PLAYLIST_AS_VIDEO")
    if dl_type == "playlist" and not is_playlist:
        raise ValueError("VIDEO_AS_PLAYLIST")

    if is_playlist:
        playlist_name = info.get('title', 'Untitled Playlist')
        playlist_name = "".join(c for c in playlist_name if c.isalnum() or c in " -_()[]").rstrip()
        final_path = os.path.join(dest, playlist_name)
        os.makedirs(final_path, exist_ok=True)
        outtmpl = os.path.join(final_path, '%(playlist_index)02d - %(title)s.%(ext)s')
    else:
        final_path = dest
        outtmpl = os.path.join(final_path, '%(title)s.%(ext)s')

    downloaded = [0]

    def progress_hook(d):
        if d['status'] == 'finished':
            downloaded[0] += 1
            if on_progress:
                try:
                    on_progress(downloaded[0], total_songs, os.path.basename(d['filename']))
                except Exception:
                    pass

    with YoutubeDL(_download_opts(outtmpl, dl_type == "video", progress_hook)) as ydl:
        ydl.download([url])

    type_text = "Playlist" if is_playlist else "Song"
    msg = f"{type_text} downloaded successfully!"
    if is_playlist:
        msg += f"\n\nFolder:\n{final_path}"
    return type_text, msg


# ========================
# GUI
# ========================
def _run_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("YouTube Audio Downloader")
    root.geometry("800x600")
    root.minsize(750, 540)

    main_frame = ctk.CTkFrame(root, fg_color=COLOR_DARK_BG, corner_radius=0)
    main_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(
        main_frame,
        text="🎵 YouTube Audio Downloader",
        font=ctk.CTkFont(size=28, weight="bold"),
        text_color=COLOR_LIGHT
    ).pack(pady=(30, 4))

    content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=40)

    ctk.CTkLabel(content_frame, text="YouTube link:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_CYAN).pack(anchor="w", pady=(0, 8))

    frame_url = ctk.CTkFrame(content_frame, fg_color="transparent")
    frame_url.pack(fill="x", pady=(0, 20))

    entry_url = ctk.CTkEntry(frame_url, placeholder_text="https://youtube.com/...", height=40,
                             font=ctk.CTkFont(size=13), fg_color=COLOR_MEDIUM_BG,
                             border_color=COLOR_CYAN, placeholder_text_color=COLOR_PLACEHOLDER)
    entry_url.pack(side="left", fill="x", expand=True, padx=(0, 10))

    ctk.CTkButton(frame_url, text="Clear", command=lambda: (entry_url.delete(0, ctk.END), entry_url.focus_set()),
                  width=100, height=40, fg_color=COLOR_CYAN, hover_color=COLOR_CYAN_HOVER,
                  text_color=COLOR_DARK_BG, font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")

    ctk.CTkLabel(content_frame, text="Destination folder:", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_CYAN).pack(anchor="w", pady=(0, 8))

    frame_folder = ctk.CTkFrame(content_frame, fg_color="transparent")
    frame_folder.pack(fill="x", pady=(0, 30))

    entry_folder = ctk.CTkEntry(frame_folder, placeholder_text="Select a folder...", height=40,
                                font=ctk.CTkFont(size=13), fg_color=COLOR_MEDIUM_BG,
                                border_color=COLOR_CYAN, placeholder_text_color=COLOR_PLACEHOLDER)
    entry_folder.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def select_folder():
        folder = filedialog.askdirectory()
        if folder:
            entry_folder.delete(0, ctk.END)
            entry_folder.insert(0, folder)

    ctk.CTkButton(frame_folder, text="📁 Select Folder", command=select_folder,
                  width=150, height=40, fg_color=COLOR_CYAN, hover_color=COLOR_CYAN_HOVER,
                  text_color=COLOR_DARK_BG, font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")

    frame_buttons = ctk.CTkFrame(content_frame, fg_color="transparent")
    frame_buttons.pack(pady=20)

    progress_bar = ctk.CTkProgressBar(content_frame, width=400, height=15,
                                      progress_color=COLOR_CYAN, fg_color=COLOR_MEDIUM_BG)
    status_label = ctk.CTkLabel(content_frame, text="Ready to download",
                                font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_CYAN)
    status_label.pack(pady=(25, 5))
    detail_label = ctk.CTkLabel(content_frame, text="", font=ctk.CTkFont(size=12),
                                text_color=COLOR_LIGHT, wraplength=700)
    detail_label.pack(pady=(0, 10))

    btn_video = ctk.CTkButton(frame_buttons, text="🎵 Download Song",
                              width=250, height=50, fg_color=COLOR_CYAN, hover_color=COLOR_CYAN_HOVER,
                              text_color=COLOR_DARK_BG, font=ctk.CTkFont(size=15, weight="bold"), corner_radius=10)
    btn_video.pack(side="left", padx=10)

    btn_playlist = ctk.CTkButton(frame_buttons, text="📂 Download Playlist",
                                 width=250, height=50, fg_color=COLOR_MEDIUM_BG, hover_color=COLOR_CYAN,
                                 text_color=COLOR_LIGHT, font=ctk.CTkFont(size=15, weight="bold"), corner_radius=10)
    btn_playlist.pack(side="right", padx=10)

    def download(dl_type):
        url = entry_url.get().strip()
        dest = entry_folder.get().strip()

        if not url:
            messagebox.showwarning("Empty field", "Please enter a YouTube link.")
            return
        if not dest:
            messagebox.showwarning("Folder not selected", "Please select a destination folder.")
            return

        btn_video.configure(state="disabled")
        btn_playlist.configure(state="disabled")
        status_label.configure(text="Analyzing link...")
        progress_bar.set(0)
        progress_bar.pack(pady=15, padx=30, fill="x")
        detail_label.configure(text="Getting information...")

        def on_progress(n, total, fname):
            def update(n=n, total=total, f=fname):
                progress_bar.set(n / total)
                status_label.configure(text=f"Downloading: {n}/{total}")
                detail_label.configure(text=f"Processing: {f[:70]}")
            root.after(0, update)

        def task():
            try:
                type_text, msg = core_download(url, dest, dl_type, on_progress=on_progress)
                root.after(0, lambda t=type_text, m=msg: show_success(t, m))
            except ValueError as e:
                err = str(e)
                if err == "PLAYLIST_AS_VIDEO":
                    root.after(0, lambda: show_error("Wrong type", "This is a PLAYLIST.\nUse 'Download Playlist' button."))
                elif err == "VIDEO_AS_PLAYLIST":
                    root.after(0, lambda: show_error("Wrong type", "This is a VIDEO.\nUse 'Download Song' button."))
                else:
                    root.after(0, lambda e=err: show_error("Error", e))
            except Exception as e:
                err = str(e)
                if 'cookie' in err.lower() or 'permission denied' in err.lower():
                    err = f"Cookie error. Close {COOKIE_BROWSER or 'your browser'} and retry.\n\n{err}"
                root.after(0, lambda e=err: show_error("Error", e))

        threading.Thread(target=task, daemon=True).start()

    def show_error(title, message):
        status_label.configure(text="Error")
        detail_label.configure(text="")
        progress_bar.pack_forget()
        messagebox.showerror(title, message)
        btn_video.configure(state="normal")
        btn_playlist.configure(state="normal")

    def show_success(type_text, message):
        status_label.configure(text=f"{type_text} completed")
        detail_label.configure(text="All done!")
        progress_bar.pack_forget()
        messagebox.showinfo("Success", message)
        btn_video.configure(state="normal")
        btn_playlist.configure(state="normal")

    btn_video.configure(command=lambda: download("video"))
    btn_playlist.configure(command=lambda: download("playlist"))

    root.mainloop()


if __name__ == '__main__':
    if '--test' in sys.argv:
        idx = sys.argv.index('--test')
        test_url = sys.argv[idx + 1]
        test_dest = sys.argv[idx + 2] if idx + 2 < len(sys.argv) else os.getcwd()

        print(f"Destination    : {test_dest}")
        print(f"URL            : {test_url}")
        print()

        def on_progress(n, total, fname):
            safe = fname.encode('ascii', 'replace').decode('ascii')
            print(f"[{n}/{total}] {safe}")

        type_text, msg = core_download(test_url, test_dest, 'video', on_progress=on_progress)
        print(f"\n{msg}")
    else:
        _run_gui()

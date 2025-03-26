import os
from yt_dlp import YoutubeDL
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de MP3 de YouTube")
        self.root.geometry("900x500")
        self.root.configure(bg="#1a2e2a")  # Fondo verde oscuro
        
        # Estilo personalizado
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1a2e2a", foreground="#e0f2e9", font=("Helvetica", 18))  # Texto blanco-verdoso
        style.configure("TButton", font=("Helvetica", 12, "bold"), padding=8)
        style.configure("TEntry", fieldbackground="#2e4f47", foreground="#e0f2e9", font=("Helvetica", 18))
        
        # Frame principal
        self.main_frame = tk.Frame(root, bg="#1a2e2a", padx=30, pady=30)
        self.main_frame.pack(expand=True, fill="both")
        
        # Título
        self.title_label = tk.Label(
            self.main_frame, 
            text="Descargador de MP3", 
            font=("Helvetica", 24, "bold"), 
            bg="#1a2e2a", 
            fg="#76c893"  # Verde medio
        )
        self.title_label.pack(pady=(0, 25))
        
        # Campo de URL
        self.url_frame = tk.Frame(self.main_frame, bg="#1a2e2a")
        self.url_frame.pack(fill="x", pady=10)
        
        self.url_label = ttk.Label(self.url_frame, text="URL de YouTube:",font=("Helvetica", 16))
        self.url_label.pack(side=tk.LEFT)
        
        self.url_entry = ttk.Entry(self.url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=15, fill="x", expand=True)
        
        # Ruta como etiqueta
        self.path_frame = tk.Frame(self.main_frame, bg="#1a2e2a")
        self.path_frame.pack(fill="x", pady=10)
        
        self.path_title_label = ttk.Label(self.path_frame, text="Carpeta de destino:")
        self.path_title_label.pack(side=tk.LEFT)
        
        self.path_label = tk.Label(
            self.path_frame, 
            text=os.getcwd(), 
            bg="#1a2e2a", 
            fg="#b7e4c7",  # Verde claro
            font=("Helvetica", 16), 
            wraplength=600,  # Ajuste más ancho para la ventana más grande
            justify="left"
        )
        self.path_label.pack(side=tk.LEFT, padx=15)
        
        self.browse_button = ttk.Button(self.path_frame, text="Cambiar", command=self.browse_folder, width=10)
        self.browse_button.pack(side=tk.LEFT)
        
        # Botón de descarga
        self.download_button = ttk.Button(
            self.main_frame, 
            text="Descargar MP3", 
            command=self.start_download, 
            style="Accent.TButton"
        )
        style.configure("Accent.TButton", background="#52a675", foreground="#ffffff")  # Verde más brillante
        self.download_button.pack(pady=25)
        
        # Etiqueta de estado
        self.status_label = tk.Label(
            self.main_frame, 
            text="Listo para descargar", 
            bg="#1a2e2a", 
            fg="#b7e4c7",  # Verde claro
            font=("Helvetica", 17, "italic")
        )
        self.status_label.pack(pady=15)

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.path_label.cget("text"))
        if folder:
            self.path_label.config(text=folder)

    def descargar_mp3(self, url, path):
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
                'quiet': False,
                'nooverwrites': True,
            }

            self.status_label.config(text=f"Descargando: {url}")
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.config(text="¡Descarga completada!")
            messagebox.showinfo("Éxito", f"El MP3 se ha descargado en:\n{path}")
            
        except Exception as e:
            self.status_label.config(text="Error en la descarga")
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
        
        finally:
            self.download_button.config(state="normal")

    def start_download(self):
        url = self.url_entry.get().strip()
        path = self.path_label.cget("text").strip()
        
        if not url:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una URL.")
            return
        
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una URL válida de YouTube.")
            return
        
        if not os.path.isdir(path):
            messagebox.showwarning("Advertencia", "La carpeta de destino no es válida.")
            return
        
        self.download_button.config(state="disabled")
        download_thread = threading.Thread(target=self.descargar_mp3, args=(url, path))
        download_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
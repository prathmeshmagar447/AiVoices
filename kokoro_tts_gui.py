import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import requests

class TTSApp:
    def __init__(self, root):
        self.root = root
        root.title("Kokoro TTS Bulk Generator")
        self.api_base = tk.StringVar(value="http://localhost:8880/v1")
        self.model = tk.StringVar(value="kokoro")
        self.voices = []
        self.selected_voice = tk.StringVar()
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="API Base URL:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.api_base, width=40).grid(row=0, column=1, sticky="w")

        ttk.Button(frm, text="Fetch Voices", command=self.fetch_voices).grid(row=0, column=2, padx=5)

        ttk.Label(frm, text="Select Voice(s):").grid(row=1, column=0, sticky="w")
        self.voice_combo = ttk.Combobox(frm, textvariable=self.selected_voice, width=37)
        self.voice_combo.grid(row=1, column=1, sticky="w")
        ttk.Label(frm, text="(For combination: voice1+voice2)").grid(row=1, column=2, sticky="w")

        ttk.Label(frm, text="Input Folder (.txt):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.input_folder, width=40).grid(row=2, column=1, sticky="w")
        ttk.Button(frm, text="Browse", command=self.browse_input).grid(row=2, column=2, padx=5)

        ttk.Label(frm, text="Output Folder:").grid(row=3, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.output_folder, width=40).grid(row=3, column=1, sticky="w")
        ttk.Button(frm, text="Browse", command=self.browse_output).grid(row=3, column=2, padx=5)

        ttk.Button(frm, text="Start Generation", command=self.start_generation).grid(row=4, column=1, pady=10)

        self.log_area = scrolledtext.ScrolledText(frm, width=60, height=15)
        self.log_area.grid(row=5, column=0, columnspan=3, pady=5)

        # Configure resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def log(self, msg):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)

    def fetch_voices(self):
        url = f"{self.api_base.get().rstrip('/')}/audio/voices"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
            # Assuming JSON list of voices
            self.voices = data.get("voices", data)  # vary depending on API
            self.voice_combo['values'] = self.voices
            if self.voices:
                self.selected_voice.set(self.voices[0])
            self.log(f"Fetched voices: {self.voices}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch voices: {e}")
            self.log(f"Error fetching voices: {e}")

    def browse_input(self):
        d = filedialog.askdirectory()
        if d:
            self.input_folder.set(d)

    def browse_output(self):
        d = filedialog.askdirectory()
        if d:
            self.output_folder.set(d)

    def start_generation(self):
        input_dir = self.input_folder.get().strip()
        if not input_dir or not os.path.isdir(input_dir):
            messagebox.showerror("Error", "Valid input folder required.")
            return
        output_dir = self.output_folder.get().strip() or input_dir
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        voice = self.selected_voice.get().strip()
        if not voice:
            messagebox.showerror("Error", "Select a voice.")
            return

        threading.Thread(target=self.run_generation, args=(input_dir, output_dir, voice), daemon=True).start()

    def run_generation(self, input_dir, output_dir, voice):
        for fname in os.listdir(input_dir):
            if not fname.lower().endswith(".txt"):
                continue
            txt_path = os.path.join(input_dir, fname)
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            if not text:
                self.log(f"Skipping empty file: {fname}")
                continue

            out_fname = os.path.splitext(fname)[0] + ".mp3"
            out_path = os.path.join(output_dir, out_fname)

            self.log(f"Generating: {fname} → {out_fname}")
            try:
                url = f"{self.api_base.get().rstrip('/')}/audio/speech"
                payload = {
                    "model": self.model.get(),
                    "voice": voice,
                    "input": text,
                    "response_format": "mp3"
                }
                resp = requests.post(url, json=payload, stream=True)
                resp.raise_for_status()
                with open(out_path, "wb") as f_out:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f_out.write(chunk)
                self.log(f"Saved: {out_path}")
            except Exception as e:
                self.log(f"Error generating for {fname}: {e}")

        self.log("Generation done.")
        messagebox.showinfo("Done", "Bulk generation completed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()

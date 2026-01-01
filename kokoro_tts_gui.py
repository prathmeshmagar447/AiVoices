import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
import requests
import json
import logging
from pathlib import Path

class TTSApp:
    def __init__(self, root):
        self.root = root
        ctk.set_appearance_mode("system")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        root.title("Kokoro TTS Bulk Generator")

        # macOS-optimized window sizing
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Use 80% of screen width, up to 1000px, and 85% of screen height
        window_width = min(int(screen_width * 0.8), 1000)
        window_height = int(screen_height * 0.85)

        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # macOS-specific window properties
        try:
            root.attributes("-alpha", 0.98)  # Slight transparency for modern look
        except:
            pass  # Not supported on all systems

        # Variables
        self.api_base = ctk.StringVar(value="http://localhost:8880/v1")
        self.model = ctk.StringVar(value="kokoro")
        self.voices = []
        self.selected_voices = []  # For multi-selection
        self.input_folder = ctk.StringVar()
        self.output_folder = ctk.StringVar()
        self.audio_format = ctk.StringVar(value="mp3")
        self.max_concurrent = ctk.IntVar(value=3)

        # Processing state
        self.is_processing = False
        self.cancel_requested = False
        self.progress_var = ctk.DoubleVar(value=0)

        # Settings and logging
        self.config_file = Path.home() / ".kokoro_tts_gui.json"
        self.setup_logging()
        self.build_ui()
        self.load_settings()

    def build_ui(self):
        # Create scrollable frame with macOS-optimized spacing
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # API Configuration - macOS style with more spacing
        api_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        api_frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(api_frame, text="🔗 API Configuration",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(16, 8))

        api_input_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        api_input_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkLabel(api_input_frame, text="API Base URL:",
                    font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=4)
        self.api_entry = ctk.CTkEntry(api_input_frame, textvariable=self.api_base,
                                     height=36, font=ctk.CTkFont(size=12))
        self.api_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=4)
        self.fetch_btn = ctk.CTkButton(api_input_frame, text="Fetch Voices",
                                      command=self.fetch_voices, height=36,
                                      font=ctk.CTkFont(size=12))
        self.fetch_btn.grid(row=0, column=2, pady=4)

        # Voice Selection - macOS optimized
        voice_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        voice_frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(voice_frame, text="🎤 Voice Selection",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(16, 8))

        # Multi-voice selection area with better height for MacBook
        self.voice_scrollable = ctk.CTkScrollableFrame(voice_frame, height=150, corner_radius=8)
        self.voice_scrollable.pack(fill="x", padx=16, pady=(0, 12))

        self.voice_checkboxes = []

        # Combined voice display and preview - macOS style
        combined_frame = ctk.CTkFrame(voice_frame, fg_color="transparent")
        combined_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkLabel(combined_frame, text="Combined Voice:",
                    font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", pady=4)
        self.combined_voice_label = ctk.CTkLabel(combined_frame, text="None selected",
                                                font=ctk.CTkFont(size=13, weight="bold"),
                                                wraplength=300)
        self.combined_voice_label.grid(row=0, column=1, sticky="w", padx=(12, 20), pady=4)

        self.preview_btn = ctk.CTkButton(combined_frame, text="🔊 Preview Voice",
                                        command=self.preview_voice, height=36,
                                        font=ctk.CTkFont(size=12),
                                        fg_color="#007AFF", hover_color="#0056CC")
        self.preview_btn.grid(row=0, column=2, pady=4)

        # Folder Selection - macOS optimized
        folder_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        folder_frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(folder_frame, text="📁 Folder Settings",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(16, 8))

        folder_input_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_input_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkLabel(folder_input_frame, text="Input Folder (.txt):",
                    font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", pady=6)
        self.input_entry = ctk.CTkEntry(folder_input_frame, textvariable=self.input_folder,
                                       height=36, font=ctk.CTkFont(size=12))
        self.input_entry.grid(row=0, column=1, sticky="ew", padx=(12, 8), pady=6)
        self.input_btn = ctk.CTkButton(folder_input_frame, text="Browse...",
                                      command=self.browse_input, height=36, width=120,
                                      font=ctk.CTkFont(size=12))
        self.input_btn.grid(row=0, column=2, pady=6)

        ctk.CTkLabel(folder_input_frame, text="Output Folder:",
                    font=ctk.CTkFont(size=13)).grid(row=1, column=0, sticky="w", pady=6)
        self.output_entry = ctk.CTkEntry(folder_input_frame, textvariable=self.output_folder,
                                        height=36, font=ctk.CTkFont(size=12))
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=(12, 8), pady=6)
        self.output_btn = ctk.CTkButton(folder_input_frame, text="Browse...",
                                       command=self.browse_output, height=36, width=120,
                                       font=ctk.CTkFont(size=12))
        self.output_btn.grid(row=1, column=2, pady=6)

        # Processing Options - macOS optimized
        options_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        options_frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(options_frame, text="⚙️ Processing Options",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(16, 8))

        options_grid = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_grid.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkLabel(options_grid, text="Audio Format:",
                    font=ctk.CTkFont(size=13)).grid(row=0, column=0, sticky="w", pady=6)
        self.format_combo = ctk.CTkComboBox(options_grid, values=["mp3", "wav", "flac"],
                                           variable=self.audio_format, height=36,
                                           font=ctk.CTkFont(size=12))
        self.format_combo.grid(row=0, column=1, sticky="w", padx=(12, 24), pady=6)

        ctk.CTkLabel(options_grid, text="Max Concurrent:",
                    font=ctk.CTkFont(size=13)).grid(row=0, column=2, sticky="w", pady=6)
        self.concurrent_spin = ctk.CTkOptionMenu(options_grid, values=["1", "2", "3", "4", "5"],
                                                variable=self.max_concurrent, height=36,
                                                font=ctk.CTkFont(size=12))
        self.concurrent_spin.grid(row=0, column=3, sticky="w", padx=(12, 0), pady=6)

        # Progress and Control - macOS optimized
        control_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        control_frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(control_frame, text="🚀 Progress & Control",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(16, 8))

        progress_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.progress_bar = ctk.CTkProgressBar(progress_frame, variable=self.progress_var,
                                              height=12, corner_radius=6)
        self.progress_bar.pack(fill="x", pady=(0, 8))

        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready",
                                          font=ctk.CTkFont(size=13))
        self.progress_label.pack(anchor="w")

        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=16, pady=(0, 16))

        self.start_btn = ctk.CTkButton(button_frame, text="▶️ Start Generation",
                                      command=self.start_generation, height=44,
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      fg_color="#28CD41", hover_color="#22B83A")
        self.start_btn.pack(side="left", padx=(0, 16))

        self.cancel_btn = ctk.CTkButton(button_frame, text="⏹️ Cancel",
                                       command=self.cancel_generation, height=44,
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color="#FF3B30", hover_color="#D63027", state="disabled")
        self.cancel_btn.pack(side="left")

        # Log Area - macOS optimized
        log_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        log_frame.pack(fill="both", expand=True, pady=(0, 16))

        ctk.CTkLabel(log_frame, text="📋 Activity Log",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(16, 8))

        self.log_textbox = ctk.CTkTextbox(log_frame, wrap="word", corner_radius=8,
                                         font=ctk.CTkFont(size=11, family="Menlo"))
        self.log_textbox.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Configure grid weights
        folder_input_frame.columnconfigure(1, weight=1)
        options_grid.columnconfigure(1, weight=1)

        # Enable touchpad scrolling support
        self.setup_touchpad_scrolling()

    def log(self, msg):
        self.log_textbox.insert("end", msg + "\n")
        self.log_textbox.see("end")
        self.root.update_idletasks()
        # Also log to file
        self.logger.info(msg)

    def fetch_voices(self):
        url = f"{self.api_base.get().rstrip('/')}/audio/voices"
        try:
            self.fetch_btn.configure(state="disabled", text="Fetching...")
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            # Assuming JSON list of voices
            self.voices = data.get("voices", data) if isinstance(data, dict) else data
            self.create_voice_checkboxes()
            self.log(f"Fetched {len(self.voices)} voices: {', '.join(self.voices[:5])}{'...' if len(self.voices) > 5 else ''}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch voices: {e}")
            self.log(f"Error fetching voices: {e}")
        finally:
            self.fetch_btn.configure(state="normal", text="Fetch Voices")

    def create_voice_checkboxes(self):
        # Clear existing checkboxes
        for cb in self.voice_checkboxes:
            cb.destroy()
        self.voice_checkboxes = []
        self.selected_voices = []

        # Create checkboxes for each voice
        for i, voice in enumerate(self.voices):
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(self.voice_scrollable, text=voice, variable=var,
                                command=lambda v=voice, var=var: self.on_voice_toggle(v, var))
            cb.pack(anchor="w", padx=5, pady=2)
            self.voice_checkboxes.append(cb)

    def on_voice_toggle(self, voice, var):
        if var.get():
            if voice not in self.selected_voices:
                self.selected_voices.append(voice)
        else:
            if voice in self.selected_voices:
                self.selected_voices.remove(voice)
        self.update_combined_voice_display()

    def update_combined_voice_display(self):
        if not self.selected_voices:
            self.combined_voice_label.configure(text="None selected")
        else:
            combined = "+".join(self.selected_voices)
            self.combined_voice_label.configure(text=combined)

    def preview_voice(self):
        """Generate and play a preview of the selected voice combination"""
        if not self.selected_voices:
            messagebox.showwarning("No Voice Selected", "Please select at least one voice to preview.")
            return

        # Disable preview button during generation
        self.preview_btn.configure(state="disabled", text="Generating...")

        def do_preview():
            try:
                # Sample text for preview
                preview_text = "Hello, this is a voice preview test."

                voice = "+".join(self.selected_voices)
                url = f"{self.api_base.get().rstrip('/')}/audio/speech"
                payload = {
                    "model": self.model.get(),
                    "voice": voice,
                    "input": preview_text,
                    "response_format": "mp3"  # Use MP3 for preview
                }

                self.log(f"Generating preview for voice: {voice}")
                resp = self.make_request_with_retry(url, payload)

                # Save to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    temp_path = temp_file.name
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            temp_file.write(chunk)

                # Play the audio
                self.play_audio(temp_path)

                self.log("Voice preview generated and played")

            except Exception as e:
                self.log(f"Preview failed: {e}")
                messagebox.showerror("Preview Error", f"Failed to generate voice preview: {e}")
            finally:
                self.preview_btn.configure(state="normal", text="🔊 Preview")

        threading.Thread(target=do_preview, daemon=True).start()

    def play_audio(self, file_path):
        """Play audio file using system audio player"""
        try:
            import subprocess
            import platform
            import time

            system = platform.system().lower()

            if system == "darwin":  # macOS
                # Use built-in afplay command
                subprocess.run(["afplay", file_path], check=True, timeout=10)
            elif system == "linux":
                # Try common Linux audio players
                for player in ["aplay", "mpg123", "mplayer", "cvlc"]:
                    try:
                        subprocess.run([player, file_path], check=True, timeout=10)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    raise FileNotFoundError("No suitable audio player found")
            elif system == "windows":
                # Use Windows Media Player or similar
                subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{file_path}').PlaySync();"], check=True, timeout=10)
            else:
                raise NotImplementedError(f"Audio playback not supported on {system}")

            self.log("Audio preview played successfully")

        except subprocess.TimeoutExpired:
            self.log("Audio preview timed out")
        except Exception as e:
            self.log(f"Audio playback error: {e}")
            messagebox.showwarning("Audio Playback", f"Could not play audio: {e}")
        finally:
            # Clean up temp file
            import os
            try:
                os.unlink(file_path)
            except:
                pass

    def browse_input(self):
        d = filedialog.askdirectory()
        if d:
            self.input_folder.set(d)

    def browse_output(self):
        d = filedialog.askdirectory()
        if d:
            self.output_folder.set(d)

    def start_generation(self):
        if not self.selected_voices:
            messagebox.showerror("Error", "Select at least one voice.")
            return

        input_dir = self.input_folder.get().strip()
        if not input_dir or not os.path.isdir(input_dir):
            messagebox.showerror("Error", "Valid input folder required.")
            return

        output_dir = self.output_folder.get().strip() or input_dir
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Set processing state
        self.is_processing = True
        self.cancel_requested = False
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress_var.set(0)
        self.progress_label.configure(text="Starting...")

        # Start generation thread
        voice = "+".join(self.selected_voices)
        audio_format = self.audio_format.get()
        max_concurrent = self.max_concurrent.get()

        threading.Thread(target=self.run_generation,
                        args=(input_dir, output_dir, voice, audio_format, max_concurrent),
                        daemon=True).start()

    def cancel_generation(self):
        if self.is_processing:
            self.cancel_requested = True
            self.log("Cancellation requested...")
            self.cancel_btn.configure(state="disabled", text="Cancelling...")

    def run_generation(self, input_dir, output_dir, voice, audio_format, max_concurrent):
        import concurrent.futures
        import time

        # Get list of text files recursively
        input_path = Path(input_dir)
        txt_files = list(input_path.rglob('*.txt'))
        total_files = len(txt_files)

        if total_files == 0:
            self.log("No .txt files found in input directory or its subfolders")
            self.reset_ui_after_generation()
            return

        self.log(f"Processing {total_files} files with max {max_concurrent} concurrent requests")

        processed = 0
        successful = 0
        failed = 0
        start_time = time.time()

        def process_file(txt_file_path: Path):
            if self.cancel_requested:
                return None

            try:
                with open(txt_file_path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                if not text:
                    return f"Skipped empty file: {txt_file_path.relative_to(input_path)}"

                # Determine output path, preserving subfolder structure
                relative_path = txt_file_path.relative_to(input_path)
                output_subfolder = output_dir / relative_path.parent
                output_subfolder.mkdir(parents=True, exist_ok=True)

                out_fname = txt_file_path.stem + f".{audio_format}"
                out_path = output_subfolder / out_fname

                url = f"{self.api_base.get().rstrip('/')}/audio/speech"
                payload = {
                    "model": self.model.get(),
                    "voice": voice,
                    "input": text,
                    "response_format": audio_format
                }

                resp = self.make_request_with_retry(url, payload)

                with open(out_path, "wb") as f_out:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f_out.write(chunk)

                return f"✓ {relative_path} → {out_path.relative_to(output_dir)}"

            except Exception as e:
                return f"✗ Error processing {txt_file_path.relative_to(input_path)}: {str(e)}"

        # Process files concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = [executor.submit(process_file, fname) for fname in txt_files]

            for future in concurrent.futures.as_completed(futures):
                if self.cancel_requested:
                    break

                result = future.result()
                if result:
                    self.log(result)
                    if result.startswith("✓"):
                        successful += 1
                    elif result.startswith("✗"):
                        failed += 1
                    else:
                        # Skipped
                        pass

                processed += 1

                # Update progress
                progress = processed / total_files
                self.progress_var.set(progress)

                elapsed = time.time() - start_time
                if processed > 0:
                    avg_time = elapsed / processed
                    remaining = (total_files - processed) * avg_time
                    eta_text = f"{remaining:.0f}s" if remaining < 60 else f"{remaining/60:.1f}m"
                else:
                    eta_text = "calculating..."

                self.progress_label.configure(text=f"Processed {processed}/{total_files} files (ETA: {eta_text})")

        # Final status
        if self.cancel_requested:
            self.log("Generation cancelled by user")
        else:
            elapsed_total = time.time() - start_time
            self.log(f"Generation completed in {elapsed_total:.1f}s")
            self.log(f"Results: {successful} successful, {failed} failed, {total_files - successful - failed} skipped")

        self.reset_ui_after_generation()

    def reset_ui_after_generation(self):
        self.is_processing = False
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled", text="Cancel")
        self.progress_label.configure(text="Ready")
        self.save_settings()  # Save settings after each run

    def setup_logging(self):
        """Setup file logging"""
        log_dir = Path.home() / "kokoro_tts_logs"
        log_dir.mkdir(exist_ok=True)

        from datetime import datetime
        log_filename = log_dir / f"kokoro_tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)

                # Load saved values
                self.api_base.set(settings.get('api_base', 'http://localhost:8880/v1'))
                self.input_folder.set(settings.get('input_folder', ''))
                self.output_folder.set(settings.get('output_folder', ''))
                self.audio_format.set(settings.get('audio_format', 'mp3'))
                self.max_concurrent.set(settings.get('max_concurrent', 3))

                self.log("Settings loaded from previous session")
        except Exception as e:
            self.log(f"Could not load settings: {e}")

    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            settings = {
                'api_base': self.api_base.get(),
                'input_folder': self.input_folder.get(),
                'output_folder': self.output_folder.get(),
                'audio_format': self.audio_format.get(),
                'max_concurrent': self.max_concurrent.get()
            }

            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=2)

        except Exception as e:
            self.log(f"Could not save settings: {e}")

    def make_request_with_retry(self, url, payload, max_retries=3, backoff_factor=2):
        """Make HTTP request with exponential backoff retry"""
        import time

        for attempt in range(max_retries):
            try:
                resp = requests.post(url, json=payload, stream=True, timeout=30)
                resp.raise_for_status()
                return resp
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise e

                wait_time = backoff_factor ** attempt
                self.log(f"Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)

        return None

    def setup_touchpad_scrolling(self):
        """Enable touchpad scrolling for the main scrollable frame"""
        def _on_touchpad_scroll(event):
            # Handle touchpad scroll events
            try:
                # Get the canvas from the scrollable frame
                if hasattr(self.main_frame, '_parent_canvas'):
                    canvas = self.main_frame._parent_canvas

                    # Determine scroll direction and amount
                    if event.num == 4:  # Scroll up
                        canvas.yview_scroll(-3, "units")
                    elif event.num == 5:  # Scroll down
                        canvas.yview_scroll(3, "units")
                    elif hasattr(event, 'delta') and event.delta:
                        # Handle mouse wheel style events
                        if event.delta > 0:
                            canvas.yview_scroll(-1, "units")
                        else:
                            canvas.yview_scroll(1, "units")

                    return "break"  # Prevent event propagation
            except:
                pass  # Ignore if scrolling fails

        def _on_mousewheel_scroll(event):
            # Handle traditional mouse wheel events
            try:
                if hasattr(self.main_frame, '_parent_canvas'):
                    canvas = self.main_frame._parent_canvas
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                    return "break"
            except:
                pass

        # Bind touchpad events to the root window (catches all events)
        self.root.bind_all("<Button-4>", _on_touchpad_scroll, add="+")  # Linux touchpad up
        self.root.bind_all("<Button-5>", _on_touchpad_scroll, add="+")  # Linux touchpad down
        self.root.bind_all("<MouseWheel>", _on_mousewheel_scroll, add="+")  # Windows/macOS mouse wheel

        # Also bind directly to the scrollable frame
        self.main_frame.bind("<Button-4>", _on_touchpad_scroll, add="+")
        self.main_frame.bind("<Button-5>", _on_touchpad_scroll, add="+")
        self.main_frame.bind("<MouseWheel>", _on_mousewheel_scroll, add="+")

        # Try to bind to child widgets too
        def bind_to_children(widget):
            for child in widget.winfo_children():
                child.bind("<Button-4>", _on_touchpad_scroll, add="+")
                child.bind("<Button-5>", _on_touchpad_scroll, add="+")
                child.bind("<MouseWheel>", _on_mousewheel_scroll, add="+")
                bind_to_children(child)  # Recursive binding

        # Bind to all current children
        bind_to_children(self.main_frame)

        # Also bind to the root to catch events that might not reach the scrollable frame
        self.root.bind("<Button-4>", _on_touchpad_scroll, add="+")
        self.root.bind("<Button-5>", _on_touchpad_scroll, add="+")
        self.root.bind("<MouseWheel>", _on_mousewheel_scroll, add="+")



if __name__ == "__main__":
    root = ctk.CTk()
    app = TTSApp(root)
    root.mainloop()

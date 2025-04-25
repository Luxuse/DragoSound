import tkinter as tk
from tkinter import filedialog, ttk
import os
import pygame
from tkinter import messagebox
from PIL import Image, ImageTk

class BBSRetroPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("DragoSound")
        self.root.configure(bg="black")
        self.root.geometry("600x700")  # Increase window size

        self.track_list = []
        self.current_track_index = 0
        self.volume = 0.5
        self.is_paused = False
        self.update_job = None  # To keep track of the scheduled seekbar update
        self.current_track_duration = 0  # To store the duration of the current track

        # Pygame mixer initialization
        try:
            pygame.mixer.init()
            print("Pygame mixer initialisé avec succès.")  # Debug print
        except pygame.error as e:
            messagebox.showerror("Erreur Pygame", f"Impossible d'initialiser le mixeur Pygame : {e}")
            print(f"Erreur Pygame mixer init : {e}")  # Debug print
            self.disable_music_controls()

        # --- GUI Elements ---

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "dragonite_logo.png")
        self.logo = None  # Initialize self.logo to None

        try:
            self.logo_image = Image.open(logo_path)
            self.logo_image = self.logo_image.resize((600, 260), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(self.logo_image)
            self.label = tk.Label(root, image=self.logo, bg="black")
            print("Image du logo chargée et label créé.")  # Debug print
        except FileNotFoundError:
            print(f"Image non trouvée à l'emplacement : {logo_path}")
            self.logo = None
            self.label = tk.Label(root, text="DragoSound", fg="white", bg="black", font=("Courier", 20))
            print("Image non trouvée, label texte de remplacement créé.")  # Debug print
        except Exception as e:
            print(f"Erreur inattendue lors du chargement de l'image : {e}")
            self.logo = None
            self.label = tk.Label(root, text="DragoSound", fg="white", bg="black", font=("Courier", 20))
            print("Erreur de chargement image, label texte de remplacement créé.")  # Debug print

        self.label.pack(pady=10)

        # Current Track Label
        self.track_var = tk.StringVar(value="Aucune piste chargée")  # Default text
        self.track_label = tk.Label(root, textvariable=self.track_var, fg="white", bg="black", font=("Courier", 12), wraplength=580)
        self.track_label.pack(pady=5)

        # File/Album Selection Buttons
        btn_frame = tk.Frame(root, bg="black")
        btn_frame.pack(pady=10)
        self.select_file_btn = tk.Button(btn_frame, text="🎵 Fichier", command=self.load_music_file, bg="#444", fg="white", font=("Courier", 11), width=14)
        self.select_file_btn.grid(row=0, column=0, padx=5)
        self.select_album_btn = tk.Button(btn_frame, text="📁 Album", command=self.load_album, bg="#444", fg="white", font=("Courier", 11), width=14)
        self.select_album_btn.grid(row=0, column=1, padx=5)

        # Playback Control Buttons
        control_frame = tk.Frame(root, bg="black")
        control_frame.pack(pady=10)
        self.prev_btn = tk.Button(control_frame, text="⏮", command=self.prev_track, bg="#555", fg="white", font=("Courier", 12), width=5)
        self.prev_btn.grid(row=0, column=0, padx=5)
        self.play_btn = tk.Button(control_frame, text="▶️", command=self.play_music, bg="green", fg="black", font=("Courier", 12), width=5)
        self.play_btn.grid(row=0, column=1, padx=5)
        self.pause_btn = tk.Button(control_frame, text="⏸", command=self.toggle_pause, bg="orange", fg="black", font=("Courier", 12), width=5)
        self.pause_btn.grid(row=0, column=2, padx=5)
        self.stop_btn = tk.Button(control_frame, text="■", command=self.stop_music, bg="red", fg="black", font=("Courier", 12), width=5)
        self.stop_btn.grid(row=0, column=3, padx=5)
        self.next_btn = tk.Button(control_frame, text="⏭", command=self.next_track, bg="#555", fg="white", font=("Courier", 12), width=5)
        self.next_btn.grid(row=0, column=4, padx=5)

        # Seekbar and Time Labels
        seek_frame = tk.Frame(root, bg="black")
        seek_frame.pack(pady=5, padx=10, fill='x')

        self.current_time_label = tk.Label(seek_frame, text="00:00", bg="black", fg="white", font=("Courier", 10))
        self.current_time_label.pack(side=tk.LEFT)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TScale", troughcolor='#333', background='#0f0', sliderthickness=15)

        self.seek_slider = ttk.Scale(seek_frame, from_=0, to=1000, orient='horizontal', value=0, command=self.seek_music)
        self.seek_slider.pack(side=tk.LEFT, fill='x', expand=True, padx=10)
        self.seek_slider.bind("<ButtonRelease-1>", self.on_seek_release)

        self.total_time_label = tk.Label(seek_frame, text="--:--", bg="black", fg="white", font=("Courier", 10))
        self.total_time_label.pack(side=tk.RIGHT)

        # Volume Control
        vol_frame = tk.Frame(root, bg="black")
        vol_frame.pack(pady=10)
        tk.Label(vol_frame, text="Volume", bg="black", fg="white", font=("Courier", 12)).pack()
        self.volume_slider = ttk.Scale(vol_frame, from_=0, to=1, orient='horizontal', value=self.volume, command=self.set_volume, length=300)
        self.volume_slider.pack(pady=5)

        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volume)
        else:
            self.volume_slider.config(state=tk.DISABLED)

        # Track Listbox
        list_frame = tk.Frame(root, bg="black")
        list_frame.pack(pady=10, padx=10, fill='both', expand=True)

        tk.Label(list_frame, text="Liste des pistes", bg="black", fg="white", font=("Courier", 12)).pack(pady=5)

        self.track_listbox = tk.Listbox(list_frame, bg="#222", fg="white", font=("Courier", 10), selectbackground="#555", selectforeground="white")
        self.track_listbox.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.config(command=self.track_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.track_listbox.config(yscrollcommand=scrollbar.set)

        self.track_listbox.bind('<<ListboxSelect>>', self.on_track_select)

        if not pygame.mixer.get_init():
            self.disable_music_controls()

    def disable_music_controls(self):
        """Disables buttons if the mixer failed to initialize."""
        print("Désactivation des contrôles audio.")  # Debug print
        self.play_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.seek_slider.config(state=tk.DISABLED)
        self.volume_slider.config(state=tk.DISABLED)
        self.select_file_btn.config(state=tk.DISABLED)
        self.select_album_btn.config(state=tk.DISABLED)
        self.track_var.set("Mixeur audio non disponible")

    def load_music_file(self):
        if not pygame.mixer.get_init():
            print("Chargement fichier : Mixeur non initialisé.")  # Debug print
            return

        file_path = filedialog.askopenfilename(filetypes=[("Fichiers audio", "*.mp3 *.wav *.ogg")])
        if file_path:
            self.track_list = [file_path]
            self.current_track_index = 0
            self.populate_listbox()
            self.play_music()

    def load_album(self):
        if not pygame.mixer.get_init():
            print("Chargement album : Mixeur non initialisé.")  # Debug print
            return

        folder_path = filedialog.askdirectory()
        if folder_path:
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith((".mp3", ".wav", ".ogg"))]
            if files:
                self.track_list = sorted(files)
                self.current_track_index = 0
                self.populate_listbox()
                self.play_music()
            else:
                messagebox.showinfo("Aucun fichier audio", "Ce dossier ne contient aucun fichier audio compatible (.mp3, .wav, .ogg).")
                self.track_list = []
                self.populate_listbox()
                self.stop_music()

    def populate_listbox(self):
        """Clears and populates the listbox with the current track_list."""
        self.track_listbox.delete(0, tk.END)
        for i, track_path in enumerate(self.track_list):
            track_name = os.path.basename(track_path)
            self.track_listbox.insert(tk.END, f"{i+1}. {track_name}")

        if self.track_list:
            if 0 <= self.current_track_index < len(self.track_list):
                self.track_listbox.select_clear(0, tk.END)
                self.track_listbox.select_set(self.current_track_index)
                self.track_listbox.activate(self.current_track_index)
                self.track_listbox.see(self.current_track_index)
            else:
                self.current_track_index = 0
                if self.track_list:
                    self.populate_listbox()
                else:
                    self.track_var.set("Liste de pistes vide")

    def on_track_select(self, event=None):
        """Handles track selection from the listbox."""
        selected_indices = self.track_listbox.curselection()
        if selected_indices:
            index = int(selected_indices[0])
            if 0 <= index < len(self.track_list):
                if index != self.current_track_index:
                    self.current_track_index = index
                    self.play_music()
            else:
                print(f"Erreur: Index sélectionné ({index}) hors limites.")

    def format_time(self, seconds):
        """Formats time in seconds to MM:SS format."""
        if seconds is None or seconds < 0:
            return "--:--"
        total_seconds = int(seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def play_music(self):
        """Starts playing the currently selected track."""
        if not pygame.mixer.get_init():
            print("Play : Mixeur non initialisé.")  # Debug print
            return

        if not self.track_list or not (0 <= self.current_track_index < len(self.track_list)):
            print("Aucune piste valide à jouer.")  # Debug print
            self.stop_music()
            return

        self.stop_update_seekbar()

        track = self.track_list[self.current_track_index]
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.is_paused = False
            self.pause_btn.config(text="⏸", bg="orange")
            self.play_btn.config(text="■", bg="red")

            self.track_var.set(os.path.basename(track))
            self.populate_listbox()

            self.seek_slider.config(value=0)
            self.seek_slider.config(to=1000)
            self.current_time_label.config(text="00:00")
            self.total_time_label.config(text="--:--")

            self.seek_slider.config(state=tk.NORMAL)

            self.update_seekbar()
            print(f"Lecture lancée : {os.path.basename(track)}")  # Debug print

            # Estimate the duration of the track
            sound = pygame.mixer.Sound(track)
            self.current_track_duration = sound.get_length() * 1000
            self.seek_slider.config(to=self.current_track_duration)
            self.total_time_label.config(text=self.format_time(self.current_track_duration / 1000))

        except pygame.error as e:
            messagebox.showerror("Erreur de lecture", f"Impossible de lire le fichier:\n{os.path.basename(track)}\n{e}")
            print(f"Erreur Pygame lors du chargement/lecture de {os.path.basename(track)}: {e}")  # Debug print
            if len(self.track_list) > 1:
                next_index = (self.current_track_index + 1) % len(self.track_list)
                if next_index != self.current_track_index:
                    self.current_track_index = next_index
                    self.play_music()
                else:
                    self.stop_music()
            else:
                self.stop_music()
        except Exception as e:
            print(f"Erreur inattendue lors de la lecture de {os.path.basename(track)}: {e}")  # Debug print
            self.stop_music()

    def stop_music(self):
        """Stops music playback."""
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.stop_update_seekbar()
        self.track_var.set("Aucune piste chargée")
        self.current_time_label.config(text="00:00")
        self.total_time_label.config(text="--:--")
        self.seek_slider.config(value=0)
        self.seek_slider.config(state=tk.DISABLED)
        self.is_paused = False
        self.pause_btn.config(text="⏸", bg="orange")
        self.play_btn.config(text="▶️", bg="green")
        print("Lecture arrêtée.")  # Debug print

    def toggle_pause(self):
        """Toggles pause and resume."""
        if not pygame.mixer.get_init():
            print("Pause/Reprise : Mixeur non initialisé.")  # Debug print
            return

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True
            self.pause_btn.config(text="▶️", bg="green")
            print("Musique mise en pause.")  # Debug print
        elif self.is_paused and self.track_list:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.pause_btn.config(text="⏸", bg="orange")
            self.update_seekbar()
            print("Musique reprise.")  # Debug print
        elif not self.track_list:
            print("Pause/Reprise : Aucune piste chargée.")  # Debug print

    def prev_track(self):
        """Plays the previous track in the list."""
        if not pygame.mixer.get_init():
            print("Précédent : Mixeur non initialisé.")  # Debug print
            return
        if not self.track_list:
            print("Précédent : Liste vide.")  # Debug print
            return

        current_pos_ms = pygame.mixer.music.get_pos() if pygame.mixer.music.get_busy() else 0
        if self.is_paused and pygame.mixer.music.get_init():
            paused_pos_ms = pygame.mixer.music.get_pos()
            if paused_pos_ms >= 0:
                current_pos_ms = paused_pos_ms

        if current_pos_ms > 2000 and self.track_listbox.curselection():
            print("Précédent : Redémarrage de la piste actuelle.")  # Debug print
            selected_indices = self.track_listbox.curselection()
            if selected_indices:
                self.current_track_index = selected_indices[0]
            self.play_music()
        elif self.track_listbox.curselection():
            print("Précédent : Passage à la piste précédente.")  # Debug print
            selected_indices = self.track_listbox.curselection()
            if selected_indices:
                self.current_track_index = (selected_indices[0] - 1) % len(self.track_list)
            else:
                self.current_track_index = (self.current_track_index - 1) % len(self.track_list)
            self.play_music()
        elif self.track_list:
            print("Précédent : Aucune sélection, passage à la dernière piste.")  # Debug print
            self.current_track_index = len(self.track_list) - 1
            self.play_music()

    def next_track(self):
        """Plays the next track in the list."""
        if not pygame.mixer.get_init():
            print("Suivant : Mixeur non initialisé.")  # Debug print
            return
        if not self.track_list:
            print("Suivant : Liste vide.")  # Debug print
            return

        print("Suivant : Passage à la piste suivante.")  # Debug print
        selected_indices = self.track_listbox.curselection()
        if selected_indices:
            current_visible_index = selected_indices[0]
        else:
            current_visible_index = self.current_track_index

        self.current_track_index = (current_visible_index + 1) % len(self.track_list)
        self.play_music()

    def set_volume(self, val):
        """Sets the playback volume."""
        if pygame.mixer.get_init():
            self.volume = float(val)
            pygame.mixer.music.set_volume(self.volume)
            print(f"Volume réglé à : {self.volume:.2f}")  # Debug print

    def seek_music(self, value):
        """Seeks the music to the specified position."""
        if pygame.mixer.get_init() and self.track_list:
            seek_time = int(float(value))
            if not pygame.mixer.music.get_busy():
                self.play_music()  # Start playing if not already playing
            pygame.mixer.music.set_pos(seek_time / 1000.0)
            self.current_time_label.config(text=self.format_time(seek_time / 1000.0))
            self.is_paused = False  # Ensure playback resumes if paused
            self.update_seekbar()

    def on_seek_release(self, event):
        """Handles the seek release event."""
        if pygame.mixer.get_init() and self.track_list:
            seek_time = self.seek_slider.get()
            if not pygame.mixer.music.get_busy():
                self.play_music()  # Start playing if not already playing
            pygame.mixer.music.set_pos(seek_time / 1000.0)
            self.current_time_label.config(text=self.format_time(seek_time / 1000.0))
            self.is_paused = False  # Ensure playback resumes if paused
            self.update_seekbar()

    def update_seekbar(self):
        """Updates the seekbar position and current time label."""
        if not pygame.mixer.get_init():
            return

        if pygame.mixer.music.get_busy() or self.is_paused:
            current_pos_ms = pygame.mixer.music.get_pos()
            if current_pos_ms < 0:
                current_pos_ms = 0

            slider_max_ms = self.seek_slider.cget("to")
            capped_pos_ms = min(current_pos_ms, slider_max_ms)

            self.seek_slider.config(value=capped_pos_ms)
            self.current_time_label.config(text=self.format_time(current_pos_ms / 1000.0))

            self.update_job = self.root.after(100, self.update_seekbar)
        else:
            if not pygame.mixer.music.get_busy() and not self.is_paused and self.seek_slider.get() > 0 and not self.track_list:
                self.current_time_label.config(text="00:00")
                self.seek_slider.config(value=0)

    def stop_update_seekbar(self):
        """Cancels the scheduled seekbar update job."""
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None

if __name__ == "__main__":
    root = tk.Tk()
    app = BBSRetroPlayer(root)
    print("Avant root.mainloop()")  # Debug print
    root.mainloop()
    print("Après root.mainloop()")  # Debug print

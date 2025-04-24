import tkinter as tk
from tkinter import filedialog, ttk
import os
import pygame
from tkinter import messagebox
from PIL import Image, ImageTk
import time

# La librairie mutagen n'est PAS utilisée dans cette version



class BBSRetroPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("DragoSound")
        self.root.configure(bg="black")
        self.root.geometry("600x700") # Increase window size

        self.track_list = []
        self.current_track_index = 0
        self.volume = 0.5
        self.is_paused = False
        # self.current_track_duration = 0 # La durée totale de la piste n'est plus connue dans cette version
        self.update_job = None # To keep track of the scheduled seekbar update

        # Pygame mixer initialization
        try:
            pygame.mixer.init()
            print("Pygame mixer initialisé avec succès.") # Debug print
        except pygame.error as e:
             messagebox.showerror("Erreur Pygame", f"Impossible d'initialiser le mixeur Pygame : {e}")
             print(f"Erreur Pygame mixer init : {e}") # Debug print
             # Disable music related controls if mixer fails
             self.disable_music_controls()


        # --- GUI Elements ---

        # Logo - SECTION CORRIGÉE
        logo_path = os.path.join(os.path.dirname(__file__), "dragonite_logo.png")
        self.logo = None # Initialiser self.logo à None

        try:
            self.logo_image = Image.open(logo_path)
            # Use LANCZOS for better resampling quality
            self.logo_image = self.logo_image.resize((600, 260), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(self.logo_image)
            # Si le chargement réussi, on crée le label AVEC l'image
            self.label = tk.Label(root, image=self.logo, bg="black")
            print("Image du logo chargée et label créé.") # Debug print

        except FileNotFoundError:
            print(f"Image non trouvée à l'emplacement : {logo_path}")
            self.logo = None
            # Si l'image n'est PAS trouvée, on crée le label AVEC le texte de remplacement
            self.label = tk.Label(root, text="DragoSound", fg="white", bg="black", font=("Courier", 20))
            print("Image non trouvée, label texte de remplacement créé.") # Debug print

        except Exception as e: # Catch other potential errors during image loading
             print(f"Erreur inattendue lors du chargement de l'image : {e}")
             self.logo = None
             # En cas d'autre erreur, on crée aussi le label AVEC le texte de remplacement
             self.label = tk.Label(root, text="DragoSound", fg="white", bg="black", font=("Courier", 20))
             print("Erreur de chargement image, label texte de remplacement créé.") # Debug print

        # Une fois que self.label est créé (soit avec l'image, soit avec le texte), on le pack
        # La logique de création est maintenant dans les try/except, et le .pack est en dehors
        self.label.pack(pady=10)


        # Current Track Label
        self.track_var = tk.StringVar(value="Aucune piste chargée") # Default text
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
        self.next_btn = tk.Button(control_frame, text="⏭", command=self.next_track, bg="#555", fg="white", font=("Courier", 12), width=5)
        self.next_btn.grid(row=0, column=3, padx=5)

        # Seekbar and Time Labels
        seek_frame = tk.Frame(root, bg="black")
        seek_frame.pack(pady=5, padx=10, fill='x')

        self.current_time_label = tk.Label(seek_frame, text="00:00", bg="black", fg="white", font=("Courier", 10))
        self.current_time_label.pack(side=tk.LEFT)

        # Seek Slider (shows progress, but NOT interactive for seeking in this version)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TScale", troughcolor='#333', background='#0f0', sliderthickness=15)

        # Set max value to an arbitrary number since we don't know duration
        self.seek_slider = ttk.Scale(seek_frame, from_=0, to=1000, orient='horizontal', value=0)
        # Suppression des bindings et de la command pour la recherche
        # self.seek_slider.config(command=self.seek_music_drag)
        # self.seek_slider.bind("<ButtonRelease-1>", self.on_seek_release)
        self.seek_slider.pack(side=tk.LEFT, fill='x', expand=True, padx=10)


        # Total time label - will show "--:--" as duration is unknown
        self.total_time_label = tk.Label(seek_frame, text="--:--", bg="black", fg="white", font=("Courier", 10)) # Default text
        self.total_time_label.pack(side=tk.RIGHT)

        # Volume Control
        vol_frame = tk.Frame(root, bg="black")
        vol_frame.pack(pady=10)
        tk.Label(vol_frame, text="Volume", bg="black", fg="white", font=("Courier", 12)).pack()
        self.volume_slider = ttk.Scale(vol_frame, from_=0, to=1, orient='horizontal', value=self.volume, command=self.set_volume, length=300)
        self.volume_slider.pack(pady=5)

        # Set initial volume if mixer was initialized
        if pygame.mixer.get_init():
             pygame.mixer.music.set_volume(self.volume)
        else:
             # If mixer failed, maybe disable volume slider
             self.volume_slider.config(state=tk.DISABLED)


        # Track Listbox
        list_frame = tk.Frame(root, bg="black")
        list_frame.pack(pady=10, padx=10, fill='both', expand=True)

        tk.Label(list_frame, text="Liste des pistes", bg="black", fg="white", font=("Courier", 12)).pack(pady=5)

        self.track_listbox = tk.Listbox(list_frame, bg="#222", fg="white", font=("Courier", 10), selectbackground="#555", selectforeground="white")
        self.track_listbox.pack(side=tk.LEFT, fill='both', expand=True)

        # Scrollbar for the listbox
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.config(command=self.track_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.track_listbox.config(yscrollcommand=scrollbar.set)

        # Bind selection to play track
        self.track_listbox.bind('<<ListboxSelect>>', self.on_track_select)

        # Disable music controls initially if mixer failed
        if not pygame.mixer.get_init():
             self.disable_music_controls()

    def disable_music_controls(self):
        """Disables buttons if the mixer failed to initialize."""
        print("Désactivation des contrôles audio.") # Debug print
        self.play_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.seek_slider.config(state=tk.DISABLED)
        self.volume_slider.config(state=tk.DISABLED)
        self.select_file_btn.config(state=tk.DISABLED)
        self.select_album_btn.config(state=tk.DISABLED)
        self.track_var.set("Mixeur audio non disponible")


    def load_music_file(self):
        if not pygame.mixer.get_init():
             print("Chargement fichier : Mixeur non initialisé.") # Debug print
             return # Don't proceed if mixer failed

        file_path = filedialog.askopenfilename(filetypes=[("Fichiers audio", "*.mp3 *.wav *.ogg")])
        if file_path:
            self.track_list = [file_path]
            self.current_track_index = 0
            self.populate_listbox()
            self.play_music()

    def load_album(self):
        if not pygame.mixer.get_init():
             print("Chargement album : Mixeur non initialisé.") # Debug print
             return # Don't proceed if mixer failed


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
             # Ensure index is valid after list potentially changes
             if 0 <= self.current_track_index < len(self.track_list):
                 self.track_listbox.select_clear(0, tk.END) # Deselect all first
                 self.track_listbox.select_set(self.current_track_index)
                 self.track_listbox.activate(self.current_track_index)
                 self.track_listbox.see(self.current_track_index)
             else:
                 # Handle case where index is out of bounds (e.g. album reload removed current track)
                 self.current_track_index = 0 # Reset index
                 if self.track_list: # If list is not empty after reset
                     self.populate_listbox() # Repopulate/select based on new index
                 else:
                      self.track_var.set("Liste de pistes vide")


    def on_track_select(self, event=None):
        """Handles track selection from the listbox."""
        selected_indices = self.track_listbox.curselection()
        if selected_indices:
            index = int(selected_indices[0])
            # Check if the selected index is valid within the current track_list
            if 0 <= index < len(self.track_list):
                 if index != self.current_track_index: # Only play if a different track is selected
                     self.current_track_index = index
                     self.play_music()
            else:
                 # This case should ideally not happen if populate_listbox keeps listbox in sync
                 print(f"Erreur: Index sélectionné ({index}) hors limites.")


    # La méthode get_track_duration() est retirée

    def format_time(self, seconds):
        """Formats time in seconds to MM:SS format."""
        # Handle potential None or negative values gracefully
        if seconds is None or seconds < 0:
            return "--:--"
        total_seconds = int(seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def play_music(self):
        """Starts playing the currently selected track."""
        if not pygame.mixer.get_init():
             print("Play : Mixeur non initialisé.") # Debug print
             return # Don't proceed if mixer failed

        if not self.track_list or not (0 <= self.current_track_index < len(self.track_list)):
             print("Aucune piste valide à jouer.") # Debug print
             self.stop_music() # Ensure player is stopped/reset
             return

        self.stop_update_seekbar() # Stop previous update loop

        track = self.track_list[self.current_track_index]
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            self.is_paused = False # Ensure pause state is reset
            self.pause_btn.config(text="⏸", bg="orange") # Update pause button text
            self.play_btn.config(text="■", bg="red") # Change Play to Stop while playing (optional)

            # Update track label and listbox selection
            self.track_var.set(os.path.basename(track))
            self.populate_listbox() # Re-select the current track

            # Réinitialiser le slider et les labels de temps car la durée est inconnue
            self.seek_slider.config(value=0)
            self.seek_slider.config(to=1000) # Garder une valeur max fixe arbitraire
            self.current_time_label.config(text="00:00")
            self.total_time_label.config(text="--:--") # Indiquer que le temps total est inconnu

            self.seek_slider.config(state=tk.NORMAL) # Activer le slider (pour afficher le temps écoulé)

            self.update_seekbar() # Start updating the seekbar
            print(f"Lecture lancée : {os.path.basename(track)}") # Debug print


        except pygame.error as e:
            messagebox.showerror("Erreur de lecture", f"Impossible de lire le fichier:\n{os.path.basename(track)}\n{e}")
            print(f"Erreur Pygame lors du chargement/lecture de {os.path.basename(track)}: {e}") # Debug print
            # Try to play the next track or stop if it's the last one
            if len(self.track_list) > 1:
                # Check if we can go to the next track without looping indefinitely on bad files
                next_index = (self.current_track_index + 1) % len(self.track_list)
                if next_index != self.current_track_index: # Prevent infinite loop on single bad file
                    self.current_track_index = next_index
                    self.play_music() # Attempt to play the next one
                else:
                     self.stop_music() # Only one file and it's bad
            else:
                self.stop_music() # Stop if no more tracks or single bad track
        except Exception as e:
             # Catch any other unexpected errors during playback attempt
             print(f"Erreur inattendue lors de la lecture de {os.path.basename(track)}: {e}") # Debug print
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
        self.seek_slider.config(state=tk.DISABLED) # Disable slider when stopped/no track
        self.is_paused = False
        self.pause_btn.config(text="⏸", bg="orange") # Reset pause button text
        self.play_btn.config(text="▶️", bg="green") # Reset play button text
        # self.current_track_duration = 0 # No duration to reset
        print("Lecture arrêtée.") # Debug print


    def toggle_pause(self):
        """Toggles pause and resume."""
        if not pygame.mixer.get_init():
             print("Pause/Reprise : Mixeur non initialisé.") # Debug print
             return # Don't proceed if mixer failed

        # Check if music is currently playing or explicitly paused and a track is loaded
        if pygame.mixer.music.get_busy():
             # Music is playing, so pause it
             pygame.mixer.music.pause()
             self.is_paused = True
             self.pause_btn.config(text="▶️", bg="green") # Change button to Play
             # No need to stop seekbar update, get_pos() still works when paused
             print("Musique mise en pause.") # Debug print
        elif self.is_paused and self.track_list:
             # Music is paused, so unpause it
             pygame.mixer.music.unpause()
             self.is_paused = False
             self.pause_btn.config(text="⏸", bg="orange") # Change button to Pause
             self.update_seekbar() # Ensure seekbar update resumes
             print("Musique reprise.") # Debug print
        elif not self.track_list:
             # If no track is loaded, the pause button shouldn't do anything visibly
             print("Pause/Reprise : Aucune piste chargée.") # Debug print
             pass


    def prev_track(self):
        """Plays the previous track in the list."""
        if not pygame.mixer.get_init():
             print("Précédent : Mixeur non initialisé.") # Debug print
             return # Don't proceed if mixer failed
        if not self.track_list:
             print("Précédent : Liste vide.") # Debug print
             return # Do nothing if list is empty

        # Check if current position is near the start, otherwise restart current track
        # get_pos() can return -1 if music hasn't started or is stopped, handle this
        # Use get_pos() if busy, otherwise assume 0 for logic
        current_pos_ms = pygame.mixer.music.get_pos() if pygame.mixer.music.get_busy() else 0
        # If music is paused, get_pos() should still work
        if self.is_paused and pygame.mixer.music.get_init():
             paused_pos_ms = pygame.mixer.music.get_pos()
             if paused_pos_ms >= 0: # Ensure pos is valid even if paused
                  current_pos_ms = paused_pos_ms


        if current_pos_ms > 2000 and self.track_listbox.curselection(): # If more than 2 seconds in
            print("Précédent : Redémarrage de la piste actuelle.") # Debug print
            # Stop and play current track from beginning
            # Ensure index matches selection if a track is selected
            selected_indices = self.track_listbox.curselection()
            if selected_indices:
                 self.current_track_index = selected_indices[0]
            # else, self.current_track_index is already the current one played
            self.play_music()
        elif self.track_listbox.curselection(): # If near start or first track, go to previous
             print("Précédent : Passage à la piste précédente.") # Debug print
             # Ensure index matches selection before calculating previous
             selected_indices = self.track_listbox.curselection()
             if selected_indices:
                 self.current_track_index = (selected_indices[0] - 1) % len(self.track_list)
             else: # If no selection, go from current_track_index
                  self.current_track_index = (self.current_track_index - 1) % len(self.track_list)
             self.play_music()
        elif self.track_list: # Case where no track is selected but list exists
             print("Précédent : Aucune sélection, passage à la dernière piste.") # Debug print
             self.current_track_index = len(self.track_list) -1 # Go to last track
             self.play_music()


    def next_track(self):
        """Plays the next track in the list."""
        if not pygame.mixer.get_init():
             print("Suivant : Mixeur non initialisé.") # Debug print
             return # Don't proceed if mixer failed
        if not self.track_list:
             print("Suivant : Liste vide.") # Debug print
             return # Do nothing if list is empty

        print("Suivant : Passage à la piste suivante.") # Debug print
        # Get current index from selection if possible, fallback to self.current_track_index
        selected_indices = self.track_listbox.curselection()
        if selected_indices:
            current_visible_index = selected_indices[0]
        else:
             current_visible_index = self.current_track_index # Fallback if nothing selected

        self.current_track_index = (current_visible_index + 1) % len(self.track_list)
        self.play_music()

    def set_volume(self, val):
        """Sets the playback volume."""
        if pygame.mixer.get_init():
             self.volume = float(val)
             pygame.mixer.music.set_volume(self.volume)
             print(f"Volume réglé à : {self.volume:.2f}") # Debug print

    def update_seekbar(self):
        """Updates the seekbar position and current time label."""
        if not pygame.mixer.get_init():
             # print("Update Seekbar : Mixeur non initialisé.") # Avoid spamming console
             return # Don't update if mixer failed

        # Update if music is busy OR explicitly paused
        if pygame.mixer.music.get_busy() or self.is_paused:
            # get_pos() returns milliseconds since the track started playing
            current_pos_ms = pygame.mixer.music.get_pos()
            # Ensure get_pos() is not -1 (can happen in some states)
            if current_pos_ms < 0:
                 current_pos_ms = 0 # Treat negative as 0

            # Update seekbar value - max is duration in ms if known. Here max is fixed (1000)
            # Ensure value doesn't exceed the maximum of the slider scale
            slider_max_ms = self.seek_slider.cget("to") # Get the current max value (1000)
            # Cap the displayed position at the slider max
            capped_pos_ms = min(current_pos_ms, slider_max_ms)


            # Update slider value
            self.seek_slider.config(value=capped_pos_ms)


            # Display elapsed time (convert ms to seconds)
            self.current_time_label.config(text=self.format_time(current_pos_ms / 1000.0))

            # Note: Auto-playing next track at the end is unreliable without knowing duration.
            # The check below is removed as it relied on self.current_track_duration


            # Schedule the next update
            self.update_job = self.root.after(100, self.update_seekbar) # Update every 100ms
            # print(f"Seekbar updated to {capped_pos_ms} ms.") # Avoid spamming console
        else:
            # Music is stopped (and not just paused), reset seekbar/labels if necessary
            # This state might be reached after a manual stop or error
            # Check if get_busy is false, not paused, and slider isn't already at 0 (to avoid constant reset prints)
            # Add check that track_list is empty or not busy to avoid resetting during loading/brief pauses
             if not pygame.mixer.music.get_busy() and not self.is_paused and self.seek_slider.get() > 0 and not self.track_list:
                self.current_time_label.config(text="00:00")
                self.seek_slider.config(value=0)
                # print("Seekbar/time reset (music stopped/no track).") # Debug print


    def stop_update_seekbar(self):
        """Cancels the scheduled seekbar update job."""
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None
            # print("Seekbar update stopped.") # Optional debug


    # Les méthodes seek_music_drag() et on_seek_release() sont retirées car la recherche est désactivée.


if __name__ == "__main__":
    root = tk.Tk()
    app = BBSRetroPlayer(root)
    print("Avant root.mainloop()") # Ligne de test : Le script a atteint le point d'entrée de la boucle graphique
    root.mainloop()
    print("Après root.mainloop()") # Ligne de test : La boucle graphique s'est terminée (fenêtre fermée)
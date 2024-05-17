import tkinter as tk
from tkinter import messagebox, filedialog
import pygame
import os
import json
from datetime import datetime

# Initialize pygame mixer
pygame.mixer.init()

class MusicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Production Software with Drawing Canvas")
        self.root.configure(bg='#CCCCFF')

        # Note buttons and key mappings
        self.notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.note_keys = ['a', 's', 'd', 'f', 'g', 'h', 'j']
        self.note_positions = {note: i * 50 + 50 for i, note in enumerate(self.notes)}
        self.buttons = []
        self.sequence = []
        self.sequences = []
        self.recording = False
        self.drawing = False
        self.lines = []  # To keep track of drawn lines for undo functionality
        self.current_color = 'black'  # Default color

        # Create and place buttons
        button_frame = tk.Frame(root, bg='#CCCCFF')
        button_frame.pack(side=tk.TOP, pady=10)
        for note, key in zip(self.notes, self.note_keys):
            button = tk.Button(button_frame, text=f"{note} ({key.upper()})", command=lambda n=note: self.play_sound(n), width=10, height=2, bg='#CCCCFF')
            button.pack(side=tk.LEFT, padx=5)
            self.buttons.append(button)

        # Additional controls
        control_frame = tk.Frame(root, bg='#CCCCFF')
        control_frame.pack(side=tk.TOP, pady=10)
        self.record_button = tk.Button(control_frame, text="Record", command=self.start_recording, width=10, height=2, bg='#CCCCFF')
        self.record_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(control_frame, text="Stop", command=self.stop_recording, width=10, height=2, bg='#CCCCFF')
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.play_button = tk.Button(control_frame, text="Play", command=self.play_sequence, width=10, height=2, bg='#CCCCFF')
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(control_frame, text="Save", command=self.save_sequence, width=10, height=2, bg='#CCCCFF')
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(control_frame, text="Load", command=self.load_sequence, width=10, height=2, bg='#CCCCFF')
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.mix_button = tk.Button(control_frame, text="Mix", command=self.mix_sequences, width=10, height=2, bg='#CCCCFF')
        self.mix_button.pack(side=tk.LEFT, padx=5)

        # Canvas for drawing
        self.canvas = tk.Canvas(root, width=800, height=400, bg='white')
        self.canvas.pack(side=tk.LEFT, pady=10)
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_line)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        # Color options
        color_frame = tk.Frame(root, bg='#CCCCFF')
        color_frame.pack(side=tk.RIGHT, padx=10)
        colors = ['black', 'red', 'green', 'blue', 'yellow', 'purple', 'orange']
        for color in colors:
            button = tk.Button(color_frame, bg=color, width=2, height=2, command=lambda c=color: self.change_color(c))
            button.pack(pady=5)

        # Load note sounds
        self.sounds = {}
        for note in self.notes:
            try:
                self.sounds[note] = pygame.mixer.Sound(f"sounds/{note}.wav")
            except pygame.error as e:
                messagebox.showerror("Error", f"Cannot load sound for note {note}: {e}")

        # Bind keyboard keys to notes
        for key, note in zip(self.note_keys, self.notes):
            self.root.bind(key, lambda event, n=note: self.play_sound(n))

        # Bind Ctrl+Z for undo functionality
        self.root.bind('<Control-z>', self.undo)

    def play_sound(self, note):
        if note in self.sounds:
            self.sounds[note].play()
            if self.recording:
                self.sequence.append((note, datetime.now().timestamp()))
        else:
            messagebox.showwarning("Warning", f"No sound loaded for note {note}")

    def start_recording(self):
        self.sequence = []
        self.recording = True

    def stop_recording(self):
        self.recording = False
        if self.sequence:
            # Normalize timestamps
            base_time = self.sequence[0][1]
            self.sequence = [(note, timestamp - base_time) for note, timestamp in self.sequence]
            messagebox.showinfo("Info", "Recording stopped.")

    def play_sequence(self):
        if not self.sequence:
            messagebox.showwarning("Warning", "No sequence to play.")
            return
        
        base_time = self.sequence[0][1]
        for note, timestamp in self.sequence:
            delay = timestamp - base_time
            self.root.after(int(delay * 1000), lambda n=note: self.sounds[n].play())
        
        self.draw_sequence()

    def save_sequence(self):
        if not self.sequence:
            messagebox.showwarning("Warning", "No sequence to save.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(self.sequence, file)
            messagebox.showinfo("Info", "Sequence saved successfully.")

    def load_sequence(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                sequence = json.load(file)
                self.sequences.append(sequence)
            messagebox.showinfo("Info", "Sequence loaded successfully.")

    def mix_sequences(self):
        if not self.sequences:
            messagebox.showwarning("Warning", "No sequences to mix.")
            return
        
        mixed_sequence = []
        for sequence in self.sequences:
            mixed_sequence.extend(sequence)
        
        # Sort mixed sequence by timestamp
        mixed_sequence.sort(key=lambda x: x[1])
        self.sequence = mixed_sequence
        self.play_sequence()

    def start_drawing(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y
        self.lines.append([])  # Start a new line

    def draw_line(self, event):
        if self.drawing:
            line_id = self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill=self.current_color, width=2)
            self.lines[-1].append(line_id)
            self.last_x, self.last_y = event.x, event.y
            timestamp = (event.x / 800) * len(self.notes)
            nearest_note = min(self.note_positions.keys(), key=lambda note: abs(event.y - self.note_positions[note]))
            self.sequence.append((nearest_note, timestamp))
            self.play_sound(nearest_note)

    def stop_drawing(self, event):
        self.drawing = False

    def undo(self, event):
        if self.lines:
            for line_id in self.lines.pop():
                self.canvas.delete(line_id)

    def change_color(self, color):
        self.current_color = color

    def draw_sequence(self):
        self.canvas.delete("all")
        for note, timestamp in self.sequence:
            x = (timestamp / len(self.notes)) * 800
            y = self.note_positions[note]
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=self.current_color)

if __name__ == "__main__":
    # Check if the sounds directory exists
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        print("Created 'sounds' directory. Please add note .wav files (C.wav, D.wav, etc.) to this directory.")
        exit()

    # Initialize the Tkinter root
    root = tk.Tk()
    app = MusicApp(root)
    root.mainloop()

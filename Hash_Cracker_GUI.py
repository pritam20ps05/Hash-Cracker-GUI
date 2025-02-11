import time
import hashlib
import pyfiglet
import threading
import concurrent.futures
import customtkinter as ctk
from itertools import islice
from tkinter import filedialog
from multiprocessing import freeze_support
from tkinterdnd2 import TkinterDnD, DND_FILES

def check_hash_match(target, wordlist, hash_algorithm):
    """Checks if any word in the list matches the target hash."""
    def hash_word(word):
        return hashlib.new(hash_algorithm, word.encode()).hexdigest()
    
    for word in wordlist:
        for variant in (word, word.upper(), word.lower(), word.capitalize()):
            if hash_word(variant) == target:
                return variant
    return None

class HashCracker:
    def __init__(self, hash_algorithm, target, wordlistfile, wordchunks=10000):
        self.hash_algorithm = hash_algorithm
        self.wordchunks = wordchunks
        self.total_processes = 0  # Total processes (chunks) needed for the wordlist

        # Validate hash algorithm
        if hash_algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}.")

        # Validate target
        if "\n" in target or "\r" in target:
            self.targets = [line.strip() for line in target.splitlines() if line.strip()]
        else:
            self.targets = [target.strip()]
        if not self.targets:
            raise ValueError("Target hash cannot be empty or invalid.")

        # Validate wordlist file and calculate total processes
        self.wordlistfile = wordlistfile
        # self.calculate_total_processes()

    # def calculate_total_processes(self):
    #     """Calculate the total number of chunks (processes) required."""
    #     with open(self.wordlistfile, 'r') as f:
    #         total_words = sum(1 for _ in f)
    #     self.total_processes = math.ceil(total_words / self.wordchunks)

    # def hash_word(self, word):
    #     """Hashes a word using the specified algorithm."""
    #     return hashlib.new(self.hash_algorithm, word.encode()).hexdigest()


    def start_attack(self, target, process_callback):
        """Starts the cracking process for a single target hash."""
        with open(self.wordlistfile, 'r') as f:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = []
                more_words = True

                while more_words:
                    wordlist = list(islice(f, self.wordchunks))
                    wordlist = [word.strip() for word in wordlist if word.strip()]
                    if not wordlist:
                        more_words = False
                        break

                    # Submit process
                    self.total_processes += 1
                    process_callback(self.total_processes)
                    results.append(executor.submit(check_hash_match, target, wordlist, self.hash_algorithm))

                for future in concurrent.futures.as_completed(results):
                    self.total_processes -= 1
                    process_callback(self.total_processes)
                    result = future.result()
                    if result:
                        self.total_processes = 0
                        process_callback(self.total_processes)
                        return result

        return None

    def crack(self, output_callback, process_callback):
        """Runs the cracking process for all targets."""
        # Notify UI about total processes required
        # process_callback(self.total_processes)

        for target in self.targets:
            output_callback(f"\nAttempting to crack hash: {target}")
            result = self.start_attack(target, process_callback)
            if result:
                output_callback(f"Cracked Password for {target}: {result}")
            else:
                output_callback(f"Could not find a matching password for {target}.")



class HashCrackerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Hash Cracker GUI")
        self.geometry("900x600")
        self.configure(bg="black")

        # Set dark appearance mode for customtkinter
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")


        self.process_count_var = ctk.StringVar(value="Processes Spawned: 0")
        self.create_widgets()

    def create_widgets(self):
        # Display ASCII logo
        self.ascii_banner = pyfiglet.figlet_format("HashCracker")
        self.logo_label = ctk.CTkLabel(
            self,
            text="",
            font=("Courier", 14),
            text_color="#00FF00",
            bg_color="black",
        )
        self.logo_label.pack(pady=10)

        # Animate the ASCII banner
        threading.Thread(target=self.animate_banner, daemon=True).start()

        # Input frame for all user inputs
        self.input_frame = ctk.CTkFrame(
    self, 
    corner_radius=25, 
    fg_color="#222831", 
    border_color="#393E46", 
    border_width=2
)

        self.input_frame.configure(corner_radius=20)

        self.input_frame.pack(pady=20, padx=20, fill="both", expand=False)

        # Hash Algorithm Dropdown
        self.hash_algorithm_label = ctk.CTkLabel(
            self.input_frame, text="Hash Algorithm:", text_color="#00FF00"
        )
        self.hash_algorithm_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")

        self.hash_algorithm_dropdown = ctk.CTkOptionMenu(
            self.input_frame,
            values=sorted(hashlib.algorithms_available),
            fg_color="black",
            text_color="#00FF00",
        )
        self.hash_algorithm_dropdown.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        # Target Hash Entry
        self.target_label = ctk.CTkLabel(
            self.input_frame, text="Target Hash (Drag file or type):", text_color="#00FF00"
        )
        self.target_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        self.target_entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="Enter hash or drop file", fg_color="black", text_color="#00FF00"
        )
        self.target_entry.grid(row=1, column=1, pady=10, padx=10, sticky="ew")

        self.target_browse_button = ctk.CTkButton(
            self.input_frame, text="Browse", command=self.browse_hash_file, fg_color="#00FF00", text_color="black"
        )
        self.target_browse_button.grid(row=1, column=2, pady=10, padx=10)

        self.target_entry.drop_target_register(DND_FILES)
        self.target_entry.dnd_bind("<<Drop>>", self.handle_hash_drop)

        # Wordlist File Selector
        self.wordlist_label = ctk.CTkLabel(
            self.input_frame, text="Dictionary File:", text_color="#00FF00"
        )
        self.wordlist_label.grid(row=2, column=0, pady=10, padx=10, sticky="w")

        self.wordlist_entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="Drag file or browse", fg_color="black", text_color="#00FF00"
        )
        self.wordlist_entry.grid(row=2, column=1, pady=10, padx=10, sticky="ew")

        self.wordlist_browse_button = ctk.CTkButton(
            self.input_frame, text="Browse", command=self.browse_wordlist_file, fg_color="#00FF00", text_color="black"
        )
        self.wordlist_browse_button.grid(row=2, column=2, pady=10, padx=10)

        # Words Per Process Entry
        self.words_per_process_label = ctk.CTkLabel(
            self.input_frame, text="Words Per Process:", text_color="#00FF00"
        )
        self.words_per_process_label.grid(row=3, column=0, pady=10, padx=10, sticky="w")
        self.words_per_process_entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="e.g., 10000", fg_color="black", text_color="#00FF00"
        )
        self.words_per_process_entry.grid(row=3, column=1, pady=10, padx=10, sticky="ew")

        # Clear Inputs Button
        self.clear_button = ctk.CTkButton(
            self.input_frame, text="Clear", command=self.clear_inputs, fg_color="#FF0000", text_color="white"
        )
        self.clear_button.grid(row=4, column=1, pady=10, padx=10)

        # Start Button
        self.start_button = ctk.CTkButton(
            self, text="Start Cracking", command=self.start_cracking, fg_color="#00FF00", text_color="black"
        )
        self.start_button.pack(pady=20)
        self.start_button.configure(
    hover_color="#005f00"
)


        # Output and Process Count Frames
        self.output_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1A1A1A")
        self.output_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Output Text Box (Left)
        self.output_text = ctk.CTkTextbox(
            self.output_frame, width=500, height=300, fg_color="black", text_color="#00FF00", font=("Courier", 12), state="disabled"
        )
        self.output_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Process Count Display (Right)
        self.process_count_box = ctk.CTkFrame(self.output_frame, corner_radius=15, fg_color="#333333")
        self.process_count_box.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.process_count_label = ctk.CTkLabel(
            self.process_count_box,
            textvariable=self.process_count_var,
            font=("Courier", 16),
            text_color="#FFA500",
            bg_color="#333333",
        )
        self.process_count_label.pack(pady=50, padx=20, anchor="center")

        # Configure grid weights for resizing
        self.output_frame.grid_columnconfigure(0, weight=3)
        self.output_frame.grid_columnconfigure(1, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)

    def animate_banner(self):
        """Simulates a typing effect for the ASCII banner."""
        for char in self.ascii_banner:
            self.logo_label.configure(text=self.logo_label.cget("text") + char)
            time.sleep(0.02)

    def browse_hash_file(self):
        """Opens file dialog to select a hash input file."""
        file_path = filedialog.askopenfilename(
            title="Select Hash File",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            with open(file_path, "r") as f:
                self.target_entry.delete(0, "end")
                self.target_entry.insert(0, f.read().strip())

    def browse_wordlist_file(self):
        """Opens file dialog to select a wordlist file."""
        file_path = filedialog.askopenfilename(
            title="Select Dictionary File",
            filetypes        =(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            self.wordlist_entry.delete(0, "end")
            self.wordlist_entry.insert(0, file_path)

    def clear_inputs(self):
        """Clears all input fields."""
        self.target_entry.delete(0, "end")
        self.wordlist_entry.delete(0, "end")
        self.words_per_process_entry.delete(0, "end")
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        self.process_count_var.set("Processes Spawned: 0")

    def handle_hash_drop(self, event):
        """Handles dropped hash file."""
        self.browse_hash_file()

    def start_cracking(self):
        """Starts the cracking process."""
        hash_algorithm = self.hash_algorithm_dropdown.get()
        target = self.target_entry.get()
        wordlist_file = self.wordlist_entry.get()
        words_per_process = self.words_per_process_entry.get()

        if not hash_algorithm or not target or not wordlist_file:
            self.log_output("Please fill in all required fields!")
            return

        try:
            words_per_process = int(words_per_process)
        except ValueError:
            self.log_output("Invalid Words Per Process value.")
            return

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        self.process_count_var.set("Processes Spawned: 0")

        self.hash_cracker = HashCracker(hash_algorithm, target, wordlist_file, words_per_process)
        threading.Thread(
            target=self.hash_cracker.crack,
            args=(self.log_output, self.update_process_count),
            daemon=True,
        ).start()

    def log_output(self, message):
        """Logs messages to the output box."""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"{message}\n")
        self.output_text.configure(state="disabled")
        self.output_text.see("end")

    def update_process_count(self, count):
        """Updates the process count display."""
        self.process_count_var.set(f"Processes Spawned: {count}")



if __name__ == "__main__":
    freeze_support()
    app = HashCrackerApp()
    app.mainloop()
# Hash-Cracker-GUI
HashCracker GUI is a lightweight, user-friendly application designed to efficiently crack password hashes using dictionary-based attacks. Built with Python and powered by CustomTkinter, the tool provides a modern graphical interface that simplifies hash-cracking tasks for ethical hacking, penetration testing, and educational purposes.


## Features
- Supports multiple hash algorithms (e.g., MD5, SHA1, SHA256, etc.).
- Drag-and-drop functionality for hash and wordlist files.
- Real-time process count and output updates.
- Configurable number of words per process for optimized performance.
- Cross-platform GUI with a modern design using CustomTkinter.

  
## Installation
To run HashCracker locally, follow these steps:

1. Clone the repository:
   git clone https://github.com/your-username/hashcracker.git

2. Navigate into the project directory:
   cd hashcracker

3. Set up a Python virtual environment (optional but recommended):
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

4. Install the required dependencies:
   pip install -r requirements.txt

5. Run the application:
   python hashcracker.py

   
## Usage
To use HashCracker:

1. Open the application by running the Python script.
2. Select the hash algorithm from the dropdown menu.
3. Enter or drag-and-drop the target hash you want to crack.
4. Choose a wordlist file containing potential password candidates.
5. Set the number of words per process.
6. Click "Start Cracking" to begin the process.
7. View the real-time output in the console for cracked passwords.


## ScreenShot
![Hash_Cracker_GUI](https://github.com/user-attachments/assets/bf2fcedd-be3b-41ac-af36-14c30abe8d72)


## Troubleshooting
**Q: The application is not starting.**
- Ensure that all dependencies are installed by running `pip install -r requirements.txt`.

**Q: How do I add more words to the wordlist?**
- Simply provide a larger wordlist file or modify the current one with additional password candidates.



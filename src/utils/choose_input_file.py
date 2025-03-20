import os

def choose_input_file(directory):
    try:
        files = os.listdir(directory)
        files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
        if not files:
            print(f"No files found in the directory: {directory}")
            return None
        print("Available files:")
        for idx, file in enumerate(files, start=1):
            print(f"{idx}. {file}")
        choice = int(input("Choose the file number (e.g., 1): "))
        if 1 <= choice <= len(files):
            return os.path.join(directory, files[choice - 1])
        else:
            print("Invalid choice. Please run the script again and choose a valid file.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

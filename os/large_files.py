import os


def scan_large_files(directory, min_size):
    large_files = []
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                except FileNotFoundError:
                    continue
                if file_size > min_size:
                    large_files.append((file_path, file_size))
    except PermissionError:
        print(f"Permission denied for {directory}")
    return large_files


def main():
    home_directory = os.path.expanduser("~")
    min_size = 50 * 1024 * 1024  # 25 MB in bytes
    large_files = scan_large_files(home_directory, min_size)

    if large_files:
        print("Large files found:")
        for file_path, file_size in large_files:
            print(f"File: {file_path}, Size: {file_size / (1024 * 1024):.2f} MB")
    else:
        print("No large files found.")


if __name__ == "__main__":
    main()

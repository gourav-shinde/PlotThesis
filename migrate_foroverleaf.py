import os
import shutil
import argparse
import re

def copy_files(source_dir, destination_dir):
    # Compile the regex pattern for matching SVG files with ID
    svg_pattern = re.compile(r'^[a-zA-Z0-9]+_.*\.svg$', re.IGNORECASE)

    for root, dirs, files in os.walk(source_dir):
        # Skip the svg-inkscape folder
        if "svg-inkscape" in dirs:
            dirs.remove("svg-inkscape")

        # Create corresponding directory structure in the destination
        relative_path = os.path.relpath(root, source_dir)
        dest_path = os.path.join(destination_dir, relative_path)
        os.makedirs(dest_path, exist_ok=True)

        # Copy SVG (with ID), TEX, and PDF files
        for file in files:
            if file.lower().endswith('.svg'):
                if svg_pattern.match(file):
                    source_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_path, file)
                    shutil.copy2(source_file, dest_file)
                    print(f"Copied: {dest_file}")
            elif file.lower().endswith(('.tex', '.pdf')):
                source_file = os.path.join(root, file)
                dest_file = os.path.join(dest_path, file)
                shutil.copy2(source_file, dest_file)
                print(f"Copied: {dest_file}")

def remove_empty_folders(path):
    for root, dirs, files in os.walk(path, topdown=False):
        # Skip the svg-inkscape folder
        if "svg-inkscape" in dirs:
            dirs.remove("svg-inkscape")

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):  # Check if the directory is empty
                os.rmdir(dir_path)
                print(f"Removed empty folder: {dir_path}")

def main():
    parser = argparse.ArgumentParser(description="Copy SVG, TEX, and PDF files recursively while maintaining folder structure, remove empty folders, and ignore 'svg-inkscape' folder.")
    parser.add_argument("source", help="Source directory path")
    parser.add_argument("destination", help="Destination directory path")
    args = parser.parse_args()

    source_dir = os.path.abspath(args.source)
    destination_dir = os.path.abspath(args.destination)

    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return

    print(f"Copying SVG, TEX, and PDF files from '{source_dir}' to '{destination_dir}'...")
    copy_files(source_dir, destination_dir)
    print("Copy operation completed.")

    print("Removing empty folders in the destination directory...")
    remove_empty_folders(destination_dir)
    print("Empty folder removal completed.")

if __name__ == "__main__":
    main()
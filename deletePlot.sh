#!/bin/bash

# Check if a directory path is provided
if [ $# -eq 0 ]; then
    echo "Error: Please provide a directory path."
    echo "Usage: $0 /path/to/directory"
    exit 1
fi

# Check if the provided path is a directory
if [ ! -d "$1" ]; then
    echo "Error: The specified path is not a valid directory."
    exit 1
fi

# Function to delete various file types and symlinks
delete_files() {
    local dir="$1"
    declare -A file_counts

    # List of file extensions to delete
    local extensions=("svg" "txt" "tex" "pdf" "pdf_tex" "toc" "out" "blg" "bbl" "aux")
    
    # Initialize counters
    for ext in "${extensions[@]}"; do
        file_counts[$ext]=0
    done
    
    # Function to delete file or symlink and increment counter
    delete_and_count() {
        local file="$1"
        local ext="$2"
        rm -f "$file"
        echo "Deleted: $file"
        ((file_counts[$ext]++))
    }

    # Use find to locate and delete files and symlinks for each extension
    for ext in "${extensions[@]}"; do
        while IFS= read -r -d '' file; do
            delete_and_count "$file" "$ext"
        done < <(find "$dir" \( -type f -o -type l \) -iname "*.$ext" -print0)
    done

    # Print results
    local total=0
    for ext in "${extensions[@]}"; do
        echo "Total $ext files/symlinks deleted: ${file_counts[$ext]}"
        ((total += file_counts[$ext]))
    done
    echo "Total files/symlinks deleted: $total"
}

# Call the function with the provided directory
delete_files "$1"
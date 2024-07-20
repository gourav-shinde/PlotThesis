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

# Function to delete PNG and TXT files
delete_files() {
    local dir="$1"
    local png_count=0
    local txt_count=0
    
    # Use find to locate and delete PNG files
    while IFS= read -r -d '' file; do
        rm "$file"
        echo "Deleted: $file"
        ((png_count++))
    done < <(find "$dir" -type f -iname "*.png" -print0)

    # Use find to locate and delete TXT files
    while IFS= read -r -d '' file; do
        rm "$file"
        echo "Deleted: $file"
        ((txt_count++))
    done < <(find "$dir" -type f -iname "*.txt" -print0)

    echo "Total PNG files deleted: $png_count"
    echo "Total TXT files deleted: $txt_count"
    echo "Total files deleted: $((png_count + txt_count))"
}

# Call the function with the provided directory
delete_files "$1"
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

# Function to delete svg, TXT, tex, pdf, and pdf_tex files and symlinks
delete_files() {
    local dir="$1"
    local svg_count=0
    local txt_count=0
    local tex_count=0
    local pdf_count=0
    local pdf_tex_count=0
    
    # Function to delete file or symlink and increment counter
    delete_and_count() {
        local file="$1"
        local counter_name="$2"
        rm -f "$file"
        echo "Deleted: $file"
        eval "$counter_name=$((${!counter_name}+1))"
    }

    # Use find to locate and delete svg files and symlinks
    while IFS= read -r -d '' file; do
        delete_and_count "$file" svg_count
    done < <(find "$dir" \( -type f -o -type l \) -iname "*.svg" -print0)

    # Use find to locate and delete TXT files and symlinks
    while IFS= read -r -d '' file; do
        delete_and_count "$file" txt_count
    done < <(find "$dir" \( -type f -o -type l \) -iname "*.txt" -print0)

    # Use find to locate and delete tex files and symlinks
    while IFS= read -r -d '' file; do
        delete_and_count "$file" tex_count
    done < <(find "$dir" \( -type f -o -type l \) -iname "*.tex" -print0)

    # Use find to locate and delete pdf files and symlinks
    while IFS= read -r -d '' file; do
        delete_and_count "$file" pdf_count
    done < <(find "$dir" \( -type f -o -type l \) -iname "*.pdf" -print0)

    # Use find to locate and delete pdf_tex files and symlinks
    while IFS= read -r -d '' file; do
        delete_and_count "$file" pdf_tex_count
    done < <(find "$dir" \( -type f -o -type l \) -iname "*.pdf_tex" -print0)

    echo "Total svg files/symlinks deleted: $svg_count"
    echo "Total TXT files/symlinks deleted: $txt_count"
    echo "Total tex files/symlinks deleted: $tex_count"
    echo "Total pdf files/symlinks deleted: $pdf_count"
    echo "Total pdf_tex files/symlinks deleted: $pdf_tex_count"
    echo "Total files/symlinks deleted: $((svg_count + txt_count + tex_count + pdf_count + pdf_tex_count))"
}

# Call the function with the provided directory
delete_files "$1"
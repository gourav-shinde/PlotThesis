import os
from pathlib import Path
import subprocess
import argparse
import re
import hashlib

def latex_escape(text):
    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    return ''.join(special_chars.get(c, c) for c in text)

def remove_timestamp(text):
    return re.sub(r'_\d{14}', '', text)

def create_unique_filename(rel_path, svg_file):
    # Create a unique hash based on the relative path and file name
    unique_id = hashlib.md5(f"{rel_path}_{svg_file}".encode()).hexdigest()[:8]
    return f"{unique_id}_{svg_file}"

def create_latex_content(root_dir):
    content = [
        r'\documentclass[12pt]{article}',
        r'\usepackage{graphicx}',
        r'\usepackage[space]{grffile}',
        r'\usepackage[margin=1in]{geometry}',
        r'\usepackage{float}',
        r'\usepackage{hyperref}',
        r'\usepackage{svg}',
        r'\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}',
        r'\setlength{\parskip}{1em}',
        r'\begin{document}',
        r'\title{\Large SVG Images Collection}',
        r'\author{Generated Script}',
        r'\date{\today}',
        r'\maketitle',
        r'\tableofcontents',
        r'\newpage',
    ]

    # Collect all directories with SVG files
    svg_dirs = []
    for root, dirs, files in os.walk(root_dir):
        svg_files = [f for f in files if f.lower().endswith('.svg')]
        if svg_files:
            rel_path = os.path.relpath(root, root_dir)
            svg_dirs.append((rel_path, svg_files))

    # Sort directories alphabetically
    svg_dirs.sort(key=lambda x: x[0].lower())

    for rel_path, svg_files in svg_dirs:
        if rel_path != '.':
            clean_title = remove_timestamp(rel_path)
            section_title = latex_escape(clean_title.replace(os.sep, ' - '))
            content.extend([
                r'\newpage',
                f'\n\\section{{{section_title}}}'
            ])

        for i, svg_file in enumerate(sorted(svg_files)):
            if i > 0 and i % 2 == 0:
                content.append(r'\newpage')
            
            original_img_path = os.path.join(rel_path, svg_file).replace('\\', '/')
            unique_svg_file = create_unique_filename(rel_path, svg_file)
            unique_img_path = os.path.join(rel_path, unique_svg_file).replace('\\', '/')
            
            # Create a symbolic link with the unique name
            os.symlink(os.path.join(root_dir, original_img_path), os.path.join(root_dir, unique_img_path))
            
            caption = latex_escape(svg_file[:-4])  # Remove '.svg' from the caption
            content.extend([
                r'\begin{figure}[H]',
                r'\centering',
                f'\\includesvg[width=0.9\\textwidth, height=0.4\\textheight, keepaspectratio]{{{unique_img_path}}}',
                f'\\caption{{{caption}}}',
                r'\end{figure}',
                r'\vspace{1cm}'
            ])

    content.append(r'\end{document}')
    return '\n'.join(content)

def main():
    parser = argparse.ArgumentParser(description='Create a LaTeX and PDF document from SVG files in a directory structure.')
    parser.add_argument('root_dir', help='Root directory to start searching for SVG files')
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root_dir)
    latex_file = os.path.join(root_dir, 'svg_collection.tex')
    pdf_file = os.path.join(root_dir, 'svg_collection.pdf')

    latex_content = create_latex_content(root_dir)

    with open(latex_file, 'w') as f:
        f.write(latex_content)

    print(f"LaTeX file created: {latex_file}")

    try:
        # Change to the root directory before running pdflatex
        original_dir = os.getcwd()
        os.chdir(root_dir)
        
        for _ in range(2):
            subprocess.run(['pdflatex', '-shell-escape', 'svg_collection.tex'], check=True)
            print(f"PDF file created: {pdf_file}")
        
        # Change back to the original directory
        os.chdir(original_dir)
    except subprocess.CalledProcessError:
        print("Error: Unable to create PDF. Make sure pdflatex is installed and in your PATH.")
    except FileNotFoundError:
        print("Error: pdflatex command not found. Make sure LaTeX is installed on your system.")

if __name__ == "__main__":
    main()
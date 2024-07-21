import os
from pathlib import Path
import subprocess
import argparse
import re

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

def create_latex_content(root_dir):
    content = [
        r'\documentclass[12pt]{article}',
        r'\usepackage{graphicx}',
        r'\usepackage[space]{grffile}',
        r'\usepackage[margin=1in]{geometry}',
        r'\usepackage{float}',
        r'\usepackage{hyperref}',
        r'\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}',
        r'\setlength{\parskip}{1em}',
        r'\begin{document}',
        r'\title{\Large PNG Images Collection}',
        r'\author{Generated Script}',
        r'\date{\today}',
        r'\maketitle',
        r'\tableofcontents',
        r'\newpage',
    ]

    for root, dirs, files in os.walk(root_dir):
        png_files = [f for f in files if f.lower().endswith('.png')]
        if png_files:
            rel_path = os.path.relpath(root, root_dir)
            if rel_path != '.':
                clean_title = remove_timestamp(rel_path)
                section_title = latex_escape(clean_title.replace(os.sep, ' - '))
                content.extend([
                    r'\newpage',
                    f'\n\\section{{{section_title}}}'
                ])

            for i, png_file in enumerate(png_files):
                if i > 0 and i % 2 == 0:
                    content.append(r'\newpage')
                
                img_path = os.path.join(rel_path, png_file).replace('\\', '/')
                content.extend([
                    r'\begin{figure}[H]',
                    r'\centering',
                    f'\\includegraphics[width=0.9\\textwidth, height=0.4\\textheight, keepaspectratio]{{{img_path}}}',
                    f'\\caption{{{latex_escape(png_file)}}}',
                    r'\end{figure}',
                    r'\vspace{1cm}'
                ])

    content.append(r'\end{document}')
    return '\n'.join(content)


def main():
    parser = argparse.ArgumentParser(description='Create a LaTeX and PDF document from PNG files in a directory structure.')
    parser.add_argument('root_dir', help='Root directory to start searching for PNG files')
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root_dir)
    latex_file = os.path.join(root_dir, 'png_collection.tex')
    pdf_file = os.path.join(root_dir, 'png_collection.pdf')

    latex_content = create_latex_content(root_dir)

    with open(latex_file, 'w') as f:
        f.write(latex_content)

    print(f"LaTeX file created: {latex_file}")

    try:
        # Change to the root directory before running pdflatex
        original_dir = os.getcwd()
        os.chdir(root_dir)
        
        subprocess.run(['pdflatex', 'png_collection.tex'], check=True)
        print(f"PDF file created: {pdf_file}")
        
        # Change back to the original directory
        os.chdir(original_dir)
    except subprocess.CalledProcessError:
        print("Error: Unable to create PDF. Make sure pdflatex is installed and in your PATH.")
    except FileNotFoundError:
        print("Error: pdflatex command not found. Make sure LaTeX is installed on your system.")

if __name__ == "__main__":
    main()
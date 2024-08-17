import os
from pathlib import Path
import subprocess
import argparse
import re
import hashlib
import errno
import shutil

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
    unique_id = hashlib.md5(f"{rel_path}_{svg_file}".encode()).hexdigest()[:8]
    return f"{unique_id}_{svg_file}"

def create_latex_content(root_dir):
    content = []
    
    # Add discussion.tex content at the top
    script_dir = os.path.dirname(os.path.abspath(__file__))
    discussion_file = os.path.join(script_dir, 'discussion.tex')
    if os.path.exists(discussion_file):
        with open(discussion_file, 'r', encoding='utf-8') as f:
            discussion_content = f.read()
        content.append(discussion_content)
        content.append(r'\newpage')
    else:
        print(f"Error: discussion.tex not found at {discussion_file}")
        print("The script cannot continue without this file.")
        sys.exit(1)  # 
    
    content.extend([
        r'\section{Label Definitions}',
    ])
    
    # the Info center
    
    paste_file = os.path.join(script_dir, 'BranchDefinitions2.txt')
    with open(paste_file, 'r') as f:
        paste_content = f.read()
    content.append(paste_content)

    content.append(r'\newpage')
    
    svg_dirs = []
    for root, dirs, files in os.walk(root_dir):
        svg_files = [f for f in files if f.lower().endswith('.svg')]
        if svg_files:
            rel_path = os.path.relpath(root, root_dir)
            svg_dirs.append((rel_path, svg_files))

    svg_dirs.sort(key=lambda x: x[0].lower())

    for rel_path, svg_files in svg_dirs:
        if rel_path != '.':
            clean_title = remove_timestamp(rel_path)
            section_title = latex_escape(clean_title.replace(os.sep, ' - '))
            content.extend([
                r'\newpage',
                f'\n\\section{{{section_title}}}',
            ])

        for i, svg_file in enumerate(sorted(svg_files)):
            if i > 0 and i % 2 == 0:
                content.append(r'\newpage')
            
            original_img_path = os.path.join(rel_path, svg_file).replace('\\', '/')
            unique_svg_file = create_unique_filename(rel_path, svg_file)
            unique_img_path = os.path.join(rel_path, unique_svg_file).replace('\\', '/')
            
            try:
                os.symlink(os.path.join(root_dir, original_img_path), os.path.join(root_dir, unique_img_path))
            except OSError as e:
                if e.errno == errno.EEXIST:
                    os.remove(os.path.join(root_dir, unique_img_path))
                    os.symlink(os.path.join(root_dir, original_img_path), os.path.join(root_dir, unique_img_path))
                else:
                    raise
            
            caption = latex_escape(svg_file[:-4])
            content.extend([
                r'\begin{figure}[H]',
                r'\centering',
                f'\\includesvg[width=0.9\\textwidth, height=0.4\\textheight, keepaspectratio]{{{unique_img_path}}}',
                f'\\caption{{{caption}}}',
                r'\end{figure}',
                r'\vspace{1cm}'
            ])

    return '\n'.join(content)

def create_standalone_latex(root_dir):
    content = [
        r'\documentclass[11pt]{article}',
        r'\usepackage{fullpage}',
        r'\usepackage{amsmath}'
        r'\usepackage{graphicx}',
        r'\usepackage{caption}',
        r'\usepackage{subcaption}',
        r'\usepackage{cite}',
        r'\usepackage{url}',
        r'\usepackage{fancyhdr}',
        r'\usepackage{color}',
        r'\usepackage[section]{placeins}',
        r'\usepackage{float}',
        r'\usepackage{tabularx}',
        r'\usepackage[margin=1in]{geometry}',
        r'\usepackage{hyperref}',
        r'\usepackage{svg}',
        r'\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}',
        r'\setlength{\parskip}{1em}',
        r'\pagestyle{fancy}',
        r'\fancyhf{}', # Clear header and footer
        r'\renewcommand{\headrulewidth}{0pt}', # Remove header line
        r'\fancyfoot[C]{\thepage}', # Center page number in footer
        r'\begin{document}',
        r'\title{\Large SVG Images Collection}',
        r'\author{Generated Script}',
        r'\date{\today}',
        r'\maketitle',
        r'\thispagestyle{empty}', # No page number on title page
        r'\tableofcontents',
        r'\thispagestyle{empty}', # No page number on table of contents
        r'\clearpage',
        r'\pagenumbering{arabic}',
        r'\input{svg_content.tex}',
        r'\bibliographystyle{plain}',
        r'\bibliography{references}',
        r'\end{document}'
    ]
    return '\n'.join(content)

def main():
    parser = argparse.ArgumentParser(description='Create a LaTeX and PDF document from SVG files in a directory structure.')
    parser.add_argument('root_dir', help='Root directory to start searching for SVG files')
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root_dir)
    latex_content_file = os.path.join(root_dir, 'svg_content.tex')
    standalone_latex_file = os.path.join(root_dir, 'svg_collection.tex')
    pdf_file = os.path.join(root_dir, 'svg_collection.pdf')

    # Copy references.bib to the root_dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    references_file = os.path.join(script_dir, 'references.bib')
    if os.path.exists(references_file):
        shutil.copy(references_file, root_dir)
        print(f"Copied references.bib to {root_dir}")
    else:
        print("Warning: references.bib not found in the script directory")

    latex_content = create_latex_content(root_dir)
    standalone_latex = create_standalone_latex(root_dir)

    with open(latex_content_file, 'w') as f:
        f.write(latex_content)

    with open(standalone_latex_file, 'w') as f:
        f.write(standalone_latex)

    print(f"LaTeX content file created: {latex_content_file}")
    print(f"Standalone LaTeX file created: {standalone_latex_file}")

    try:
        original_dir = os.getcwd()
        os.chdir(root_dir)
        
        for _ in range(2):
            subprocess.run(['pdflatex', '-shell-escape', 'svg_collection.tex'], check=True)
        subprocess.run(['bibtex', 'svg_collection'], check=True)  # Add this line
        subprocess.run(['pdflatex', '-shell-escape', 'svg_collection.tex'], check=True)  # Add this line
        subprocess.run(['pdflatex', '-shell-escape', 'svg_collection.tex'], check=True)  # Add this line
        print(f"PDF file created: {pdf_file}")
        
        os.chdir(original_dir)
    except subprocess.CalledProcessError:
        print("Error: Unable to create PDF. Make sure pdflatex and bibtex are installed and in your PATH.")
    except FileNotFoundError:
        print("Error: pdflatex or bibtex command not found. Make sure LaTeX is installed on your system.")

if __name__ == "__main__":
    main()
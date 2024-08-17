import re
import sys
import os

def modify_includesvg_paths(latex_content):
    # Regular expression to match includesvg paths
    pattern = r'(\\includesvg\[.*?\]{)(.*?})'
    
    # Function to replace the matched path
    def replace_path(match):
        return f'{match.group(1)}completed_logs_big/{match.group(2)}'
    
    # Perform the replacement
    modified_content = re.sub(pattern, replace_path, latex_content)
    
    return modified_content

def process_file(input_path):
    # Check if the input file exists
    if not os.path.exists(input_path):
        print(f"Error: The file '{input_path}' does not exist.")
        return

    # Read the input file
    with open(input_path, 'r') as file:
        latex_content = file.read()

    # Modify the content
    modified_content = modify_includesvg_paths(latex_content)

    # Generate output file path
    base_name = os.path.splitext(input_path)[0]
    output_path = f"{base_name}_modified.tex"

    # Write the modified content to a new file
    with open(output_path, 'w') as file:
        file.write(modified_content)

    print(f"Processing complete. Modified content saved to '{output_path}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_latex_file>")
    else:
        input_path = sys.argv[1]
        process_file(input_path)
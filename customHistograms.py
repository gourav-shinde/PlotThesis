import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import glob
import numpy as np
import re


configs = [
    {
        "modal": "traffic",
        "y": "Simulation_Runtime_(secs.)",
        "title": "TrafficPerformers"
    },
    {
        "modal": "pcs",
        "y": "Simulation_Runtime_(secs.)",
        "title": "PCSPerformers"
    },
    {
        "modal": "epidemic-10k",
        "y": "Simulation_Runtime_(secs.)",
        "title": "EpidemicPerformers"
    },
    {
        "modal": "epidemic-100k",
        "y": "Simulation_Runtime_(secs.)",
        "title": "Epidemic100kPerformers"
    }
]


def create_output_directory(root_dir):
    output_dir = os.path.join(root_dir, "Top Performers")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def remove_timestamp(path):
    # Remove timestamp at the end of the path (format: SIMD_local_YYYYMMDDHHMMSS)
    return re.sub(r'_\d{14}$', '', path)

def process_csvs(root_dir, keywords):
    data_frames = []

    # Ensure keywords is a list
    if isinstance(keywords, str):
        keywords = [keywords]
    
    keywords = [k.lower() for k in keywords]  # Convert all keywords to lowercase

    for run_type in os.listdir(root_dir):
        run_type_path = os.path.join(root_dir, run_type)
        if os.path.isdir(run_type_path):
            for model in os.listdir(run_type_path):
                # Check if all keywords are in the model name
                if all(keyword in model.lower() for keyword in keywords):
                    model_path = os.path.join(run_type_path, model)
                    csv_files = glob.glob(os.path.join(model_path, '*.csv'))
                    
                    for csv_file in csv_files:
                        df = pd.read_csv(csv_file)
                        df['path'] = remove_timestamp(run_type)
                        data_frames.append(df)

    if data_frames:
        final_df = pd.concat(data_frames, ignore_index=True)
        return final_df
    else:
        return None



def data_maker(data, config, output_dir):
    if config["y"] not in data.columns:
        print(f"Column '{config['y']}' not found in the data. Available columns are: {data.columns.tolist()}")
        return

    # Filter out values smaller than 5 seconds
    data = data[data[config["y"]] >= 5]

    # Keep only numeric columns and the 'path' and 'branch' columns
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    if 'path' not in numeric_columns:
        numeric_columns.extend(['path', 'branch'])
    data = data[numeric_columns]

    # Group by 'path' and 'branch', aggregate the config["y"] column
    grouped_data = data.groupby(["path", "branch"])[config["y"]]
    data = grouped_data.agg(['mean', 'std', 'count']).reset_index()
    data['sem'] = data['std'] / np.sqrt(data['count'])  # Calculate standard error of the mean
    data = data.sort_values(by='mean', ascending=True)

    if data.empty:
        print(f"No data left after filtering out values < 5 seconds for {config['modal']}")
        return

    # Create a separate dataframe for 'local' entries
    local_data = data[data['path'].str.contains('local', case=False)]
    non_local_data = data[~data['path'].str.contains('local', case=False)]

    if not local_data.empty:
        plot_hist(local_data, config, output_dir, " (Local)")
    if not non_local_data.empty:
        plot_hist(non_local_data, config, output_dir)
    if not data.empty:
        plot_hist(data, config, output_dir, " (All)")

def plot_hist(data, config, output_dir, title_suffix=""):
    sorted_data = data.sort_values(by=['mean', 'path'])
    sorted_data = sorted_data.head(15)
    unique_values = sorted_data['mean'].unique()

    plt.figure(figsize=(15, 8))

    bars = plt.bar(range(len(data)), data['mean'], align='center', 
                   yerr=data['sem'], capsize=5, 
                   error_kw=dict(ecolor='gray', lw=1, capthick=1, capsize=5),
                   color='darkblue')  # Set all bars to dark blue

    plt.title(f'Histogram of {config["y"]} across Branches{title_suffix} on {config["modal"]}')
    plt.xlabel("Model")
    plt.ylabel(config["y"])

    plt.xticks(range(len(data)), [f"{row['branch']}" for _, row in data.iterrows()], rotation=45, ha='right')

    # Add value labels on top of each bar
    for i, v in enumerate(data['mean']):
        plt.text(i, v, f'{v:.2f}', ha='center', va='bottom')

    plt.tight_layout()
    filename = f"{config['title']}{title_suffix.replace(' ', '_')}.svg"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Generate histogram from CSV files in directories.')
    parser.add_argument('directory', type=str, help='Root directory to search for CSV files')
    args = parser.parse_args()
    output_dir = create_output_directory(args.directory)

    for config in configs:

        dataframe = process_csvs(args.directory, config["modal"])
        
        if dataframe is None:
            print(f"No data found for {config['modal']}")
            continue
        
        print(f"Columns for {config['modal']}:")
        print(dataframe.columns)
        
        data_maker(dataframe, config, output_dir)

if __name__ == "__main__":
    main()
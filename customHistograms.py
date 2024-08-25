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
    return re.sub(r'_\d{14}$', '', path)

def process_csvs(root_dir, keywords):
    data_frames = []

    if isinstance(keywords, str):
        keywords = [keywords]
    
    keywords = [k.lower() for k in keywords]

    for run_type in os.listdir(root_dir):
        run_type_path = os.path.join(root_dir, run_type)
        if os.path.isdir(run_type_path):
            for model in os.listdir(run_type_path):
                if all(keyword in model.lower() for keyword in keywords):
                    model_path = os.path.join(run_type_path, model)
                    csv_files = glob.glob(os.path.join(model_path, '*.csv'))
                    
                    for csv_file in csv_files:
                        try:
                            df = pd.read_csv(csv_file)
                            df['path'] = remove_timestamp(run_type)
                            data_frames.append(df)
                        except Exception as e:
                            print(f"Error reading CSV file {csv_file}: {str(e)}")

    if data_frames:
        final_df = pd.concat(data_frames, ignore_index=True)
        print(f"Processed {len(data_frames)} CSV files. Final dataframe shape: {final_df.shape}")
        return final_df
    else:
        print("No data frames were created. Check if the CSV files are in the expected locations.")
        return None

def calculate_average_config(data, config):
    print(f"Initial data shape: {data.shape}")
    print(f"Columns: {data.columns}")

    # Filter out values smaller than 5 seconds
    data = data[data[config["y"]] >= 5]
    print(f"Data shape after filtering: {data.shape}")

    # Keep only numeric columns and the 'path' and 'branch' columns
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    if 'path' not in numeric_columns:
        numeric_columns.append('path')
    if 'branch' not in numeric_columns:
        numeric_columns.append('branch')
    data = data[numeric_columns]
    print(f"Data shape after selecting columns: {data.shape}")

    # Group by 'path' and 'branch', aggregate the config["y"] column
    grouped_data = data.groupby(["path", "branch"])[config["y"]]
    data = grouped_data.agg(['mean', 'std', 'count']).reset_index()
    data['sem'] = data['std'] / np.sqrt(data['count'])  # Calculate standard error of the mean
    print(f"Data shape after grouping: {data.shape}")

    # Calculate the average across configurations
    avg_data = data.groupby('branch').agg({
        'mean': 'mean',
        'sem': lambda x: np.sqrt(np.sum(x**2)) / len(x)  # Propagate error
    }).reset_index()

    avg_data = avg_data.sort_values(by='mean', ascending=True)
    print(f"Final averaged data shape: {avg_data.shape}")
    print(f"Final averaged data:\n{avg_data}")
    return avg_data

def data_maker(data, config, output_dir):
    if config["y"] not in data.columns:
        print(f"Column '{config['y']}' not found in the data. Available columns are: {data.columns.tolist()}")
        return

    avg_data = calculate_average_config(data, config)

    if avg_data.empty:
        print(f"No data left after filtering out values < 5 seconds for {config['modal']}")
        return

    plot_hist(avg_data, config, output_dir, " (Average)")

def plot_hist(data, config, output_dir, title_suffix=""):
    sorted_data = data.sort_values(by='mean').head(15)

    plt.figure(figsize=(15, 8))
    
    # Use a basic style and manually set properties
    plt.style.use('default')
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.edgecolor'] = 'lightgray'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['grid.color'] = 'lightgray'
    
    # Use a single color suitable for research papers
    bar_color = '#4472C4'  # A professional blue color

    bars = plt.bar(range(len(sorted_data)), sorted_data['mean'], align='center', 
                   yerr=sorted_data['sem'], capsize=5, 
                   error_kw=dict(ecolor='#2F528F', lw=1, capthick=1, capsize=5),
                   color=bar_color)

    plt.title(f'Histogram of Average {config["y"]} across Branches{title_suffix} on {config["modal"]}',
              fontsize=14, fontweight='bold')
    plt.xlabel("Branch", fontsize=12)
    plt.ylabel(config["y"], fontsize=12)

    plt.xticks(range(len(sorted_data)), sorted_data['branch'], rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)

    # Add value labels on top of each bar
    for i, v in enumerate(sorted_data['mean']):
        plt.text(i, v, f'{v:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2F528F')

    plt.tight_layout()
    filename = f"{config['title']}{title_suffix.replace(' ', '_')}.svg"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, bbox_inches='tight', dpi=300)
    print(f"Saved plot to {filepath}")
    plt.close()
    
def main():
    parser = argparse.ArgumentParser(description='Generate histogram from CSV files in directories.')
    parser.add_argument('directory', type=str, help='Root directory to search for CSV files')
    args = parser.parse_args()
    output_dir = create_output_directory(args.directory)

    for config in configs:
        print(f"\nProcessing config: {config}")
        dataframe = process_csvs(args.directory, config["modal"])
        
        if dataframe is None:
            print(f"No data found for {config['modal']}")
            continue
        
        print(f"Columns for {config['modal']}:")
        print(dataframe.columns)
        
        data_maker(dataframe, config, output_dir)

if __name__ == "__main__":
    main()
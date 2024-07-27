import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import argparse
from matplotlib.ticker import FuncFormatter
import glob
import numpy as np

# Use a basic style that should be available in all matplotlib installations
plt.style.use('default')

# Set seaborn style manually
sns.set_style("whitegrid")
sns.set_palette("deep")

colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ff99cc", "#99ffff", "#ff99ff", "#ffff99"]

def format_y_axis(y, _):
    if y >= 1e6:
        return f'{y/1e6:.1f}M'
    elif y >= 1e3:
        return f'{y/1e3:.1f}K'
    else:
        return f'{y:.0f}'

plot_configs = [
    {
        "groupby": "Folder",
        "x": "branch",
        "y": "Simulation_Runtime_(secs.)",
        "title": "Branch vs Simulation Time vs Branch",
        "type": "bar",
        "agg": "mean"
    },
    {
        "groupby": "Folder",
        "x": "branch",
        "y": "Average_Memory_Usage_(MB)",
        "title": "Average Memory Usage vs Branch",
        "type": "bar",
        "agg": "mean"
    },
    {
       "groupby": "Folder",
        "x": "branch",
        "y": "Primary_Rollbacks",
        "title": "Branch vs Primary Rollback",
        "type": "bar",
        "agg": "mean" 
    },
    {
       "groupby": "Worker_Thread_Count",
        "x": "branch",
        "y": "Simulation_Runtime_(secs.)",
        "title": "ThreadCount vs Sim Time",
        "type": "bar",
        "agg": "mean" 
    }
]

def plothandler(dataframe, config, outputdir):
    if config["type"]=="bar":
        create_grouped_bar_plot(dataframe, config["groupby"], config["y"], config["x"], outputdir, config)
    elif config["type"]=="line":
        print("doesnt support RN")
    else:
        print("Invalid graph type")

def create_grouped_bar_plot(df, x_col, y_col, hue_col, outputdir, config):
    df[y_col] = df[y_col].astype('float64')
    df_agg = df.groupby([x_col, hue_col])[y_col].agg(['mean', 'sem']).reset_index()
    df_agg.columns = [x_col, hue_col, 'mean', 'sem']

    all_x = df[x_col].unique()
    all_hue = df[hue_col].unique()
    complete_index = pd.MultiIndex.from_product([all_x, all_hue], names=[x_col, hue_col])
    df_complete = df_agg.set_index([x_col, hue_col]).reindex(complete_index).reset_index()

    # Write the data to a text file
    txt_filename = os.path.join(outputdir, f"{config['title']}_data.txt")
    with open(txt_filename, 'w') as f:
        f.write(f"Data for plot: {config['title']}\n\n")
        f.write(df_complete.to_string(index=False))
        f.write("\n\n")

    print(f"Data for {config['title']} has been written to {txt_filename}")

    # Create original plot
    create_plot(df_complete, x_col, y_col, hue_col, outputdir, config, False)

    # Create normalized plot
    create_plot(df_complete, x_col, y_col, hue_col, outputdir, config, True)

def create_plot(df_complete, x_col, y_col, hue_col, outputdir, config, normalize):
    plt.figure(figsize=(20, 10))
    
    ax = plt.gca()
    all_x = df_complete[x_col].unique()
    all_hue = df_complete[hue_col].unique()
    n_hues = len(all_hue)
    width = 0.8 / n_hues
    x = np.arange(len(all_x))
    
    for i, hue_val in enumerate(all_hue):
        hue_data = df_complete[df_complete[hue_col] == hue_val]
        if normalize:
            max_val = hue_data['mean'].max()
            hue_data['mean'] = hue_data['mean'] / max_val
            hue_data['sem'] = hue_data['sem'] / max_val
        
        offset = width * (i - (n_hues - 1) / 2)
        rects = ax.bar(x + offset, hue_data['mean'], width, label=hue_val)
        ax.errorbar(x + offset, hue_data['mean'], yerr=hue_data['sem'], fmt='none', c='black', capsize=5, elinewidth=1)

    ax.set_ylabel(f"Normalized {y_col}" if normalize else y_col, fontsize=16)
    ax.set_xlabel(x_col, fontsize=16)
    ax.set_title(f"{config['title']} (Normalized)" if normalize else config["title"], fontsize=20)
    ax.set_xticks(x)
    ax.set_xticklabels(all_x, rotation=45, ha='right', fontsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ax.legend(title=hue_col, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=14, title_fontsize=16)

    if not normalize and ('Memory' in y_col or 'Runtime' in y_col):
        ax.yaxis.set_major_formatter(FuncFormatter(format_y_axis))

    plt.tight_layout()
    plt.savefig(os.path.join(outputdir, f"{config['title']}_normalized.svg" if normalize else f"{config['title']}.svg"), dpi=300, bbox_inches='tight')
    plt.close()

    # Create log scale plot if needed (only for non-normalized data)
    if not normalize:
        y_min, y_max = df_complete['mean'].min(), df_complete['mean'].max()
        if y_min > 0 and y_max / y_min > 1000:
            create_log_plot(df_complete, x_col, y_col, hue_col, outputdir, config)

def create_log_plot(df_complete, x_col, y_col, hue_col, outputdir, config):
    plt.figure(figsize=(20, 10))
    ax = plt.gca()
    ax.set_yscale('log')

    all_x = df_complete[x_col].unique()
    all_hue = df_complete[hue_col].unique()
    n_hues = len(all_hue)
    width = 0.8 / n_hues
    x = np.arange(len(all_x))

    for i, hue_val in enumerate(all_hue):
        hue_data = df_complete[df_complete[hue_col] == hue_val]
        offset = width * (i - (n_hues - 1) / 2)
        rects = ax.bar(x + offset, hue_data['mean'], width, label=hue_val)
        ax.errorbar(x + offset, hue_data['mean'], yerr=hue_data['sem'], fmt='none', c='black', capsize=5, elinewidth=1)

    ax.set_ylabel(y_col, fontsize=16)
    ax.set_xlabel(x_col, fontsize=16)
    ax.set_title(f"{config['title']} (Log Scale)", fontsize=20)
    ax.set_xticks(x)
    ax.set_xticklabels(all_x, rotation=45, ha='right', fontsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ax.legend(title=hue_col, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=14, title_fontsize=16)

    if 'Memory' in y_col or 'Runtime' in y_col:
        ax.yaxis.set_major_formatter(FuncFormatter(format_y_axis))

    plt.tight_layout()
    plt.savefig(os.path.join(outputdir, f"{config['title']}_log.svg"), dpi=300, bbox_inches='tight')
    plt.close()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate unified plots from multiple CSV files")
    parser.add_argument("input_pattern", help="Glob pattern for directories containing CSV files (e.g., 'path/to/*')")
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Get the parent directory of the input pattern
    parent_dir = os.path.dirname(args.input_pattern)
    
    # Set the output directory to be the parent directory
    output_dir = parent_dir
    os.makedirs(output_dir, exist_ok=True)
    dataframes = pd.DataFrame()
    for input_dir in glob.glob(args.input_pattern):
        if os.path.isdir(input_dir):
            folder_name = os.path.basename(input_dir)
            csv_file = next((f for f in os.listdir(input_dir) if f.endswith('.csv')), None)
            if csv_file:
                df = pd.read_csv(os.path.join(input_dir, csv_file))
                float_columns = df.select_dtypes(include=['float']).columns
                for col in float_columns:
                    df[col] = df[col].astype('float64')
                df['Folder'] = folder_name  # Add a column to identify the folder
                dataframes = pd.concat([dataframes, df], ignore_index=True)

    for config in plot_configs:
        plothandler(dataframes, config, output_dir)
    
    print(f"All unified plots have been generated and saved in the '{output_dir}' directory.")

if __name__ == "__main__":
    main()
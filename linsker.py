import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os
import sys
import re

# Folders
TXT_FOLDER = "Resultados_TXT"
PNG_FOLDER = "Resultados_PNG"

# Extract parameters from C++
def extract_cpp_params():
    print("--- Analyzing C++ code to find parameters ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cpp_file = os.path.abspath(os.path.join(script_dir, '../Neun/examples/linskerSynapse.cpp'))
    
    if not os.path.exists(cpp_file):
        print(f"Error: Not found {cpp_file}")
        sys.exit(1)

    params_found = {}

    with open(cpp_file, 'r') as f:
        content = f.read()

    # Search for patterns like: syn_args.params[Synapsis::xo] = -65;
    pattern = r"syn_args\.params\[Synapsis::(\w+)\]\s*=\s*([^;]+);"
    matches = re.findall(pattern, content)
    
    for name, value in matches:
        params_found[name] = value.strip()

    return params_found

# Build dynamic name
params = extract_cpp_params()

# Choose which parameters form the name
keys_to_use = ['xo', 'yo', 'eta', 'k1', 'w_max']
filename_parts = []
title_parts = []

for k in keys_to_use:
    if k in params:
        val = params[k]
        filename_parts.append(f"{k}{val}")     # Example: xo-65
        title_parts.append(f"{k}={val}")       # Example: xo=-65

# If no params found, use "default"
suffix = "_".join(filename_parts) if filename_parts else "default"
base_filename = f"linsker_{suffix}" 


# Run code
def run_model(output_txt_path):
    print("--- Compiling and Running ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.abspath(os.path.join(script_dir, '../Neun/build'))
    
    # Execute c++ from here using output redirection
    cmd = f'make && cd examples && ./linskerSynapse > "{output_txt_path}"'
    
    try:
        subprocess.run(cmd, cwd=build_dir, shell=True, check=True)
        print(f"Data saved in: {output_txt_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling/running: {e}")
        sys.exit(1)

# Path to save the txt
script_dir = os.path.dirname(os.path.abspath(__file__))
txt_dir_abs = os.path.join(script_dir, TXT_FOLDER)
os.makedirs(txt_dir_abs, exist_ok=True)

full_txt_path = os.path.join(txt_dir_abs, f"{base_filename}.txt")

# Run model
run_model(full_txt_path)

# Plot
if os.path.exists(full_txt_path):
    print("Generating plot...")
    
    # For 2 synapses
    columns = ['Time', 'V1pre', 'V2pre', 'Vpost', 'i1', 'i2', 'w1', 'w2', 'SUM(W)']
    
    # For 4 synapses
    # columns = ['Time', 'V1pre', 'V2pre', 'V3pre', 'V4pre', 'Vpost', 'i1', 'i2', 'i3', 'i4', 'w1', 'w2', 'w3', 'w4', 'SUM(W)']

    df = pd.read_csv(full_txt_path, sep=r'\s+', names=columns, header=0, engine='c')
    
    df_plot = df.iloc[::50, :].copy()

    fig, (ax_i, ax_w) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Title of the plot
    plot_title_str = ", ".join(title_parts)
    fig.suptitle(f"Linsker Simulation\n[{plot_title_str}]", fontsize=11, color='navy')

    # Plots - Panel 1
    ax_i.plot(df_plot['Time'], df_plot['i1'], label='i1', color='red')
    ax_i.plot(df_plot['Time'], df_plot['i2'], label='i2', color='purple')

    # ax_i.plot(df_plot['Time'], df_plot['i3'], label='i3', color='green')
    # ax_i.plot(df_plot['Time'], df_plot['i4'], label='i4', color='blue')

    ax_i.set_ylabel('Corriente (i)')
    ax_i.legend(loc='upper right')
    ax_i.grid(True, alpha=0.3)

    # Plots - Panel 2
    ax_w.plot(df_plot['Time'], df_plot['w1'], label='w1', color='brown')
    ax_w.plot(df_plot['Time'], df_plot['w2'], label='w2', color='darkgreen')

    # ax_w.plot(df_plot['Time'], df_plot['w3'], label='w3', color='green')
    # ax_w.plot(df_plot['Time'], df_plot['w4'], label='w4', color='blue')
    
    ax_w.set_ylabel('Pesos (w)')
    ax_w.set_xlabel('Tiempo (ms)')
    ax_w.legend(loc='upper right')
    ax_w.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save plot
    png_dir_abs = os.path.join(script_dir, PNG_FOLDER)
    os.makedirs(png_dir_abs, exist_ok=True)
    
    png_path = os.path.join(png_dir_abs, f"{base_filename}.png")
    
    plt.savefig(png_path)
    print(f"\n -> Data: {full_txt_path}\n -> Plot: {png_path}")
    
    plt.show()
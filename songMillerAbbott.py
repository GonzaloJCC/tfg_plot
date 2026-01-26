import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os
import sys
import re

#Folders
TXT_FOLDER = "Resultados_TXT"
PNG_FOLDER = "Resultados_PNG"

# Get parameters from C++
def extract_cpp_params():
    print("Getting C++ parameters from code")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Adjust path to Neun folder
    cpp_file = os.path.abspath(os.path.join(script_dir, "../Neun/examples/songMillerAbbottSynapse.cpp"))

    if not os.path.exists(cpp_file):
        print(f"Error: Not found {cpp_file}")
        sys.exit(1)

    params_found = {}

    with open(cpp_file, 'r') as f:
        content = f.read()

    # Search for patterns like: syn_args.params[Synapse:spike_threshold] = -54;
    pattern = r"syn_args\.params\[Synapse::(\w+)\]\s*=\s*([^;]+);"
    matches = re.findall(pattern, content)
    
    for name, value in matches:
        params_found[name] = value.strip()

    return params_found

# Build dynamic name
params = extract_cpp_params()

# Choose which parameters form the name
keys_to_use = ['A_minus', 'A_plus', 'tau_minus', 'tau_plus', 'spike_threshold', 'g_max']
filename_parts = []
title_parts = []

for k in keys_to_use:
    if k in params:
        val = params[k]
        filename_parts.append(f"{k}{val}")
        title_parts.append(f"{k}={val}")

# If no params found, use "default"
suffix = "_".join(filename_parts) if filename_parts else "default"
base_filename = f"songMillerAbbott_{suffix}" 

# Run code
def run_model(output_txt_path):
    print("--- Compiling and Running ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.abspath(os.path.join(script_dir, '../Neun/build'))
    
    # Execute C++ code from here using output redirection
    cmd = f'make && cd examples && ./songMillerAbbottSynapse > "{output_txt_path}"'
    
    try:
        subprocess.run(cmd, cwd=build_dir, shell=True, check=True)
        print(f"Data saved in: {output_txt_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling/running: {e}")
        sys.exit(1)

# Path for txt file
script_dir = os.path.dirname(os.path.abspath(__file__))
txt_dir_abs = os.path.join(script_dir, TXT_FOLDER)
os.makedirs(txt_dir_abs, exist_ok=True)

full_txt_path = os.path.join(txt_dir_abs, f"{base_filename}.txt")

# Run model
run_model(full_txt_path)

# Plot
if os.path.exists(full_txt_path):
    print("Generating plot")

    columns = ['Time', 'vpre', 'vpost', 'i', 'g']
    df = pd.read_csv(full_txt_path, sep=r'\s+', names=columns, header=0, engine='c')

    df_plot = df.iloc[::50, :].copy()

    fig, (ax_i, ax_w) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Title of the plot
    plot_title_str = ", ".join(title_parts)
    fig.suptitle(f"Song Miller Abbott Simulation\n[{plot_title_str}]", fontsize=11, color='navy')

    # Plots - Panel 1
    ax_i.plot(df_plot['Time'], df_plot['i'], label='i', color='red')
    ax_i.set_ylabel('Corriente (i)')
    ax_i.legend(loc='upper right')
    ax_i.grid(True, alpha=0.3)

    # Plots - Panel 2
    ax_w.plot(df_plot['Time'], df_plot['g'], label='g', color='brown')
    ax_w.set_ylabel('Conductancia (g)')
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

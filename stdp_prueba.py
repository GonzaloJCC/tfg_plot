import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os
import sys
import re

# Set LaTeX parameters
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "font.size": 11,
    "axes.labelsize": 11,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9
})

# Folders
TXT_FOLDER = "Resultados_TXT"
PNG_FOLDER = "Resultados_PDF"

# Get parameters from C++
def extract_cpp_params():
    print("Getting C++ parameters from code")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Adjust path to Neun folder
    cpp_file = os.path.abspath(os.path.join(script_dir, "../Neun/examples/STDPSynapse.cpp"))

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
base_filename = f"Prueba" 

# Run code
def run_model(output_txt_path):
    print("--- Compiling and Running ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.abspath(os.path.join(script_dir, '../Neun/build'))
    
    # Eliminar el archivo TXT viejo para evitar errores
    if os.path.exists(output_txt_path):
        os.remove(output_txt_path)
        print("Borrando datos de la simulación anterior...")

    # Obligar a recompilar eliminando el binario
    cmd = (
        'rm -f examples/STDPSynapse && '
        'touch examples/STDPSynapse.cpp && '
        'make && '
        f'cd examples && ./STDPSynapse > "{output_txt_path}"'
    )
    
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

    columns = ['Time', 'vpre1', 'vpre2', 'vpost', 'i1', 'i2', 'g1', 'g2']
    df = pd.read_csv(full_txt_path, sep=r'\s+', names=columns, header=0, engine='c')

    df_plot = df.copy()

    # Creamos 4 subplots: 
    # 1. vpre1 y vpost 
    # 2. g1
    # 3. vpre2 y vpost
    # 4. g2
    fig, axs = plt.subplots(4, 1, figsize=(8, 10), sharex=True)

    plot_title_str = "Verificación funcionamiento"
    fig.suptitle(f"Verificación STDP: {plot_title_str}")

    threshold_val = float(params.get('spike_threshold', -54.0))

    # --- SUBPLOT 1: Voltajes Sinapsis 1 ---
    axs[0].plot(df_plot['Time'], df_plot['vpre1'], label='V_pre1', color='red', alpha=0.7)
    axs[0].plot(df_plot['Time'], df_plot['vpost'], label='V_post', color='green', alpha=0.7)
    axs[0].axhline(threshold_val, color='gray', linestyle='--', alpha=0.5, label='Umbral')
    axs[0].set_ylabel(r'Voltaje ($mV$)')
    axs[0].set_title("Interacción Sinapsis 1 (Pre1 y Post)", fontsize=10, loc='left')
    axs[0].legend(loc='upper right')
    axs[0].grid(True, alpha=0.3)

    # --- SUBPLOT 2: Conductancia Sinapsis 1 ---
    axs[1].plot(df_plot['Time'], df_plot['g1'], label='g1', color='red')
    axs[1].set_ylabel(r'Cond. ($pS$)')
    axs[1].legend(loc='upper right')
    axs[1].grid(True, alpha=0.3)

    # --- SUBPLOT 3: Voltajes Sinapsis 2 ---
    axs[2].plot(df_plot['Time'], df_plot['vpre2'], label='V_pre2', color='blue', alpha=0.7)
    axs[2].plot(df_plot['Time'], df_plot['vpost'], label='V_post', color='green', alpha=0.7)
    axs[2].axhline(threshold_val, color='gray', linestyle='--', alpha=0.5, label='Umbral')
    axs[2].set_ylabel(r'Voltaje ($mV$)')
    axs[2].set_title("Interacción Sinapsis 2 (Pre2 y Post)", fontsize=10, loc='left')
    axs[2].legend(loc='upper right')
    axs[2].grid(True, alpha=0.3)

    # --- SUBPLOT 4: Conductancia Sinapsis 2 ---
    axs[3].plot(df_plot['Time'], df_plot['g2'], label='g2', color='blue')
    axs[3].set_ylabel(r'Cond. ($pS$)')
    axs[3].set_xlabel(r'Tiempo (ms)')
    axs[3].legend(loc='upper right')
    axs[3].grid(True, alpha=0.3)

    # Zoom de 20 a 70 ms para ver los picos individuales
    axs[0].set_xlim(50, 150)
    
    plt.tight_layout()

    # Save plot
    png_dir_abs = os.path.join(script_dir, PNG_FOLDER)
    os.makedirs(png_dir_abs, exist_ok=True)
    
    png_path = os.path.join(png_dir_abs, f"{base_filename}.pdf")
    
    plt.savefig(png_path)
    print(f"\n -> Data: {full_txt_path}\n -> Plot: {png_path}")
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os
import sys
import re

# --- CONFIGURACIÓN DE CARPETAS ---
TXT_FOLDER = "Resultados_TXT"
PNG_FOLDER = "Resultados_PNG"

# --- PASO 1: EXTRACTOR DE PARÁMETROS DEL C++ ---
def extract_cpp_params():
    print("--- Analizando código C++ para buscar parámetros ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cpp_file = os.path.abspath(os.path.join(script_dir, '../Neun/examples/linskerSynapsis.cpp'))
    
    if not os.path.exists(cpp_file):
        print(f"Error: No encuentro el código fuente en {cpp_file}")
        sys.exit(1)

    params_found = {}

    with open(cpp_file, 'r') as f:
        content = f.read()

    # Buscamos patrones tipo: syn_args.params[Synapsis::xo] = -65;
    pattern = r"syn_args\.params\[Synapsis::(\w+)\]\s*=\s*([^;]+);"
    matches = re.findall(pattern, content)
    
    for name, value in matches:
        params_found[name] = value.strip()

    return params_found

# --- PASO 2: CONSTRUIR NOMBRE DINÁMICO ---
params = extract_cpp_params()

# Elegimos qué parámetros forman parte del nombre
keys_to_use = ['xo', 'yo', 'eta', 'k1', 'w_max']
filename_parts = []
title_parts = [] # Para el título de la gráfica

for k in keys_to_use:
    if k in params:
        val = params[k]
        filename_parts.append(f"{k}{val}")     # Ejemplo: xo-65
        title_parts.append(f"{k}={val}")       # Ejemplo: xo=-65

# Si no encuentra params, usa "default"
suffix = "_".join(filename_parts) if filename_parts else "default"
base_filename = f"linsker_{suffix}" 

print(f"ID de Simulación: {base_filename}")

# --- PASO 3: EJECUCIÓN ---
def run_simulation(output_txt_path):
    print("--- Compilando y Ejecutando ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.abspath(os.path.join(script_dir, '../Neun/build'))
    
    # IMPORTANTE: Usamos la ruta absoluta para el redireccionamiento >
    # Ponemos comillas por si hay espacios en la ruta
    cmd = f'make && cd examples && ./linskerSynapsis > "{output_txt_path}"'
    
    try:
        subprocess.run(cmd, cwd=build_dir, shell=True, check=True)
        print(f"Datos guardados en: {output_txt_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error compilando/ejecutando: {e}")
        sys.exit(1)

# Preparamos la ruta del TXT
script_dir = os.path.dirname(os.path.abspath(__file__))
txt_dir_abs = os.path.join(script_dir, TXT_FOLDER)
os.makedirs(txt_dir_abs, exist_ok=True) # Crea la carpeta 'txt' si no existe

full_txt_path = os.path.join(txt_dir_abs, f"{base_filename}.txt")

# Ejecutamos pasando la ruta donde queremos el txt
run_simulation(full_txt_path)

# --- PASO 4: GRAFICADO ---
columnas = ['Time', 'V1pre', 'V2pre', 'Vpost', 'i1', 'i2', 'w1', 'w2', 'SUM(W)']

if os.path.exists(full_txt_path):
    print("Generando gráfica...")
    # Leemos el archivo específico que acabamos de crear
    df = pd.read_csv(full_txt_path, sep='\s+', names=columnas, header=0, engine='c')
    df_plot = df.iloc[::50, :].copy()

    fig, (ax_i, ax_w) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Título bonito
    plot_title_str = ", ".join(title_parts)
    fig.suptitle(f"Simulación Linsker\n[{plot_title_str}]", fontsize=11, color='navy')

    # Gráficas
    ax_i.plot(df_plot['Time'], df_plot['i1'], label='i1', color='red')
    ax_i.plot(df_plot['Time'], df_plot['i2'], label='i2', color='purple')
    ax_i.set_ylabel('Corriente (i)')
    ax_i.legend(loc='upper right')
    ax_i.grid(True, alpha=0.3)

    ax_w.plot(df_plot['Time'], df_plot['w1'], label='w1', color='brown')
    ax_w.plot(df_plot['Time'], df_plot['w2'], label='w2', color='darkgreen')
    ax_w.set_ylabel('Pesos (w)')
    ax_w.set_xlabel('Tiempo (ms)')
    ax_w.legend(loc='upper right')
    ax_w.grid(True, alpha=0.3)

    plt.tight_layout()

    # --- GUARDAR PNG ---
    png_dir_abs = os.path.join(script_dir, PNG_FOLDER)
    os.makedirs(png_dir_abs, exist_ok=True) # Crea la carpeta 'Resultados_PNG'
    
    png_path = os.path.join(png_dir_abs, f"{base_filename}.png")
    
    plt.savefig(png_path)
    print(f"✅ Todo listo:\n -> Datos: {full_txt_path}\n -> Gráfica: {png_path}")
    
    plt.show()
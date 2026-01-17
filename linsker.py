import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os
import sys

# --- PASO 0: Ejecutar la simulación C++ para generar los datos ---
def run_simulation():
    print("--- Iniciando generación de datos ---")
    
    # 1. Identificar dónde estamos. 
    # Usamos __file__ para asegurar que tomamos la ruta donde está este script (Gráficas)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Calcular la ruta al directorio Neun/build
    # Desde 'Gráficas', subimos uno (..) y bajamos a 'Neun/build'
    build_dir = os.path.abspath(os.path.join(script_dir, '../Neun/build'))
    
    if not os.path.exists(build_dir):
        print(f"Error: No se encuentra el directorio de build en: {build_dir}")
        return

    # 3. Definir el comando.
    # Usamos '&&' en lugar de ';' para que si falla el 'cd', no intente ejecutar el programa.
    # La ruta de salida ../../../Gráficas/linsker.txt es relativa a 'Neun/build/examples'
    cmd = "make && cd examples && ./linskerSynapsis > ../../../Gráficas/linsker.txt"
    
    print(f"Directorio de trabajo para el comando: {build_dir}")
    print(f"Ejecutando: {cmd}")

    try:
        # cwd=build_dir hace que el proceso empiece en Neun/build
        # shell=True permite usar 'cd' y la redirección '>'
        subprocess.run(cmd, cwd=build_dir, shell=True, check=True)
        print("Datos generados y guardados en linsker.txt exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"Hubo un error al ejecutar la simulación: {e}")
        # No salimos (sys.exit) por si quieres ver la gráfica de datos viejos,
        # pero podrías descomentar la siguiente línea si prefieres que pare.
        # sys.exit(1)

# Ejecutamos la generación antes de cargar nada
run_simulation()

print("\n--- Procesando gráficas ---")

# --- SCRIPT ORIGINAL DE GRAFICADO ---

# 1. Configuración de nombres y carga de datos
# Como el script está en 'Gráficas' y el archivo se generó ahí mismo, el path es directo
file_path = 'linsker.txt'
columnas = ['Time', 'V1pre', 'V2pre', 'Vpost', 'i1', 'i2', 'w1', 'w2', 'SUM(W)']

if not os.path.exists(file_path):
    print(f"Error: El archivo {file_path} no existe. Verifica la compilación C++.")
    sys.exit(1)

print("Cargando linsker.txt... (2M de líneas)")
# Usamos engine='c' y low_memory=False para máxima velocidad
df = pd.read_csv(file_path, sep='\s+', names=columnas, header=0, engine='c')

# 2. Decimación (Muestreo)
# Graficar 2 millones de puntos es innecesario. 
# Tomamos 1 de cada 50 puntos para que la gráfica sea fluida y nítida.
df_plot = df.iloc[::50, :].copy()

# 3. Crear la figura con 2 subplots (Corrientes arriba, Pesos abajo)
fig, (ax_i, ax_w) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# --- PANEL 1: Corrientes (i1, i2) ---
ax_i.plot(df_plot['Time'], df_plot['i1'], label='i1', color='red', lw=2.5)
ax_i.plot(df_plot['Time'], df_plot['i2'], label='i2', color='purple', lw=2.5)
ax_i.set_ylabel('Corriente (i)')
ax_i.set_title('Evolución de Corrientes y Pesos')
ax_i.legend(loc='upper right')
ax_i.grid(True, alpha=0.3)

# --- PANEL 2: Pesos (w1, w2) ---
ax_w.plot(df_plot['Time'], df_plot['w1'], label='w1', color='brown', lw=3.5)
ax_w.plot(df_plot['Time'], df_plot['w2'], label='w2', color='darkgreen', lw=3.5)
ax_w.set_ylabel('Pesos (w)')
ax_w.set_xlabel('Tiempo (s)')
ax_w.legend(loc='upper right')
ax_w.grid(True, alpha=0.3)

# 4. Ajustes finales
plt.tight_layout()

# Opcional: Zoom
# plt.xlim(0, 500) 

print("Mostrando gráfica...")
plt.savefig("linsker_plot.png") # Guardo una copia por si acaso
plt.show()
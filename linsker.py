import pandas as pd
import matplotlib.pyplot as plt

# 1. Configuración de nombres y carga de datos
file_path = 'linsker.txt'
columnas = ['Time', 'V1pre', 'V2pre', 'Vpost', 'i1', 'i2', 'w1', 'w2', 'SUM(W)']

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

# Opcional: Si quieres hacer zoom en el inicio donde hay más actividad, 
# quita el comentario de la siguiente línea:
# plt.xlim(0, 500) 

print("Mostrando gráfica...")
plt.show()
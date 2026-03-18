import pandas as pd
import matplotlib.pyplot as plt

# Grupos personalizados
GROUPS = {
    'Nitrógeno (PAN/AMMONIA/YAN)': ['PAN', 'AMMONIA', 'YAN'],
    'Viabilidad y Crecimiento': ['Budding Index', 'Viability', 'Concentration'],
    'Temperaturas (CA/CB)': ['CA (0°C)', 'CB (-40°C)'],
    'Azúcares': ['FRUCTOSE', 'GLUCOSE'],
    'Densidad': ['Densidad'],
    'Pesos': ['Peso Seco'],
    'Glicerol & Etanol': ['GLYCEROL', 'ETANOL'],
    'Ácidos volátiles': ['PYRUVIC ACID', 'ACETALDEHIDO']
}

# Marcadores para diferenciar ensayos
MARKERS = ['o', 's', '^', 'D', 'v', 'P', 'X', '*', '<', '>']

def load_and_transform(file_path, sheet_name='BDD_Maestra'):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df['Fecha y hora'] = pd.to_datetime(df['Fecha y hora'], format='%d-%m-%Y %H:%M')
    id_cols  = sorted([c for c in df if c.startswith('ID Análisis')],
                      key=lambda s: int(s.split()[-1]))
    val_cols = sorted([c for c in df if c.startswith('Valor')],
                      key=lambda s: int(s.split()[-1]))
    records = []
    for _, row in df.iterrows():
        for id_col, val_col in zip(id_cols, val_cols):
            analito = row[id_col]
            valor = pd.to_numeric(row[val_col], errors='coerce')
            if pd.notna(analito) and pd.notna(valor):
                records.append({
                    'Ensayo': row['Ensayo'],
                    'Fecha y hora': row['Fecha y hora'],
                    'Analito': analito.strip(),
                    'Valor': valor,
                    'Código': row['Código']           # ← Se añade aquí
                })
    return pd.DataFrame.from_records(records)

def plot_custom_groups(df_long, ensayos):
    # Map de color por analito
    all_analytes = [a for grp in GROUPS.values() for a in grp]
    prop_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
    color_map = {analito: prop_cycle[i % len(prop_cycle)]
                 for i, analito in enumerate(all_analytes)}

    # Map de marcador por ensayo
    marker_map = {ensayo: MARKERS[i % len(MARKERS)]
                  for i, ensayo in enumerate(ensayos)}

    # Filtrar datos
    df_filt = df_long[df_long['Ensayo'].isin(ensayos)]

    # Calcular t0 (fecha mínima) de cada ensayo
    start_times = {
        ensayo: df_filt[df_filt['Ensayo'] == ensayo]['Fecha y hora'].min()
        for ensayo in ensayos
    }

    for grp_name, analytes in GROUPS.items():
        plt.figure(figsize=(10, 5))
        plotted = False

        for analito in analytes:
            for ensayo in ensayos:
                df_sub = (df_filt
                          [(df_filt['Ensayo'] == ensayo) &
                           (df_filt['Analito'] == analito)]
                          .sort_values('Fecha y hora'))
                if df_sub.empty:
                    continue

                days = ((df_sub['Fecha y hora'] - start_times[ensayo])
                        .dt.total_seconds() / (24 * 3600))

                # Dibuja la línea + marcadores
                plt.plot(
                    days,
                    df_sub['Valor'],
                    label=f"{analito} ({ensayo})",
                    color=color_map.get(analito),
                    marker=marker_map[ensayo],
                    linestyle='-'
                )
                
                # Etiquetar cada punto con su 'Código'
                for x, y, code in zip(days, df_sub['Valor'], df_sub['Código']):
                    # extraer solo el número tras el segundo guión
                    try:
                        label = str(code).split('-', 2)[2].split()[0]
                    except IndexError:
                        label = str(code)
                    plt.text(
                        x, y, label,
                        fontsize=8,
                        ha='right', va='bottom'
                    )

                plotted = True

        if not plotted:
            plt.close()
            continue

        plt.title(f"Evolución – {grp_name}")
        plt.xlabel("Tiempo desde inicio (días)")
        plt.ylabel("Valor")
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

def main():
    file_path = 'C:/Users/ctorrealba/OneDrive - Viña Concha y Toro S.A/Documentos/Proyectos I+D/PI-4497/Resultados/2025/Procesos_I+D_2025_2.xlsx'
    df_long = load_and_transform(file_path)

    ensayos_disp = sorted(df_long['Ensayo'].unique())
    print("Ensayos disponibles:")
    for e in ensayos_disp:
        print(" ", e)

    entrada = input("\nIngrese uno o más ensayos (separados por coma): ")
    ensayos_sel = [e.strip() for e in entrada.split(',') if e.strip()]
    
    plot_custom_groups(df_long, ensayos_sel)

if __name__ == '__main__':
    main()

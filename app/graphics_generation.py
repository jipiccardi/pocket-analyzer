import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import os

file_names = {
    1: "match_p1",
    2: "match_p2",
    3: "open_p1",
    4: "open_p2",
    5: "short_p1",
    6: "short_p2",
    7: "thru"
}

def raw_data(output_folder):
    #Leo los datos en crudo
    match1_df = pd.read_csv('./data/match1.csv')
    match2_df = pd.read_csv('./data//match2.csv')
    open1_df = pd.read_csv('./data/open1.csv')
    open2_df = pd.read_csv('./data/open2.csv')
    short1_df = pd.read_csv('./data/short1.csv')
    short2_df = pd.read_csv('./data/short2.csv')
    thru_df = pd.read_csv('./data/thru.csv')

    data = [match1_df, match2_df, open1_df, open2_df, short1_df, short2_df, thru_df]
    # Crear y guardar los gráficos como PNG
    png_files = []
    for n in range(0,len(data)):
        name = file_names[n+1]
        if n != 6:
            for columns in data[n].columns:
                if columns != "Frequency" and (columns == "Magnitude 1" or columns == "Phase 1"):
                    plt.figure()  # Nueva figura para cada gráfico
                    plt.plot(data[n]["Frequency"], data[n][columns], marker='o', label=columns)
                    plt.title(f"Gráfico de {columns} vs Frequency")
                    plt.xlabel("Frequency")
                    plt.ylabel(columns)
                    plt.legend()
                    plt.grid()

                    # Guardar cada gráfico como un archivo PNG
                    file_path = os.path.join(output_folder, f"{columns}_{name}.png")
                    plt.savefig(file_path)
                    png_files.append(file_path)
                    plt.close()  # Libera memoria cerrando la figura    
        else:
            for columns in data[n].columns:
                if columns != "Frequency" :
                    plt.figure()  # Nueva figura para cada gráfico
                    plt.plot(data[n]["Frequency"], data[n][columns], marker='o', label=columns)
                    plt.title(f"Gráfico de {columns} vs Frequency")
                    plt.xlabel("Frequency")
                    plt.ylabel(columns)
                    plt.legend()
                    plt.grid()

                    # Guardar cada gráfico como un archivo PNG
                    file_path = os.path.join(output_folder, f"{columns}_{name}.png")
                    plt.savefig(file_path)
                    png_files.append(file_path)
                    plt.close()  # Libera memoria cerrando la figura 
def ext_data(output_folder):
    #Leo los datos en crudo
    match1_df = pd.read_csv('./data/match1_extrapole.csv')
    match2_df = pd.read_csv('./data//match2_extrapole.csv')
    open1_df = pd.read_csv('./data/open1_extrapole.csv')
    open2_df = pd.read_csv('./data/open2_extrapole.csv')
    short1_df = pd.read_csv('./data/short1_extrapole.csv')
    short2_df = pd.read_csv('./data/short2_extrapole.csv')
    thru_df = pd.read_csv('./data/thru_extrapole.csv')

    data = [match1_df, match2_df, open1_df, open2_df, short1_df, short2_df, thru_df]
    # Crear y guardar los gráficos como PNG
    png_files = []
    for n in range(0,len(data)):
        name = file_names[n+1]
        if n != 6:
            for columns in data[n].columns:
                if columns != "Frequency" and (columns == "Magnitude 1" or columns == "Phase 1"):
                    plt.figure()  # Nueva figura para cada gráfico
                    plt.plot(data[n]["Frequency"], data[n][columns], marker='o', label=columns)
                    plt.title(f"Gráfico de {columns} vs Frequency")
                    plt.xlabel("Frequency")
                    plt.ylabel(columns)
                    plt.legend()
                    plt.grid()

                    # Guardar cada gráfico como un archivo PNG
                    file_path = os.path.join(output_folder, f"{columns}_{name}.png")
                    plt.savefig(file_path)
                    png_files.append(file_path)
                    plt.close()  # Libera memoria cerrando la figura    
        else:
            for columns in data[n].columns:
                if columns != "Frequency" :
                    plt.figure()  # Nueva figura para cada gráfico
                    plt.plot(data[n]["Frequency"], data[n][columns], marker='o', label=columns)
                    plt.title(f"Gráfico de {columns} vs Frequency")
                    plt.xlabel("Frequency")
                    plt.ylabel(columns)
                    plt.legend()
                    plt.grid()

                    # Guardar cada gráfico como un archivo PNG
                    file_path = os.path.join(output_folder, f"{columns}_{name}.png")
                    plt.savefig(file_path)
                    png_files.append(file_path)
                    plt.close()  # Libera memoria cerrando la figura 
def pha_data(output_folder):
        #Leo los datos en crudo
    match1_df = pd.read_csv('./data/match1_pha_corr.csv')
    match2_df = pd.read_csv('./data//match2_pha_corr.csv')
    open1_df = pd.read_csv('./data/open1_pha_corr.csv')
    open2_df = pd.read_csv('./data/open2_pha_corr.csv')
    short1_df = pd.read_csv('./data/short1_pha_corr.csv')
    short2_df = pd.read_csv('./data/short2_pha_corr.csv')
    thru_df = pd.read_csv('./data/thru_pha_corr.csv')

    data = [match1_df, match2_df, open1_df, open2_df, short1_df, short2_df, thru_df]
    # Crear y guardar los gráficos como PNG
    png_files = []
    for n in range(0,len(data)):
        name = file_names[n+1]
        if n != 6:
            for columns in data[n].columns:
                if columns != "Frequency" and (columns == "Magnitude 1" or columns == "Phase 1"):
                    plt.figure()  # Nueva figura para cada gráfico
                    plt.plot(data[n]["Frequency"], data[n][columns], marker='o', label=columns)
                    plt.title(f"Gráfico de {columns} vs Frequency")
                    plt.xlabel("Frequency")
                    plt.ylabel(columns)
                    plt.legend()
                    plt.grid()

                    # Guardar cada gráfico como un archivo PNG
                    file_path = os.path.join(output_folder, f"{columns}_{name}.png")
                    plt.savefig(file_path)
                    png_files.append(file_path)
                    plt.close()  # Libera memoria cerrando la figura    
        else:
            for columns in data[n].columns:
                if columns != "Frequency" :
                    plt.figure()  # Nueva figura para cada gráfico
                    plt.plot(data[n]["Frequency"], data[n][columns], marker='o', label=columns)
                    plt.title(f"Gráfico de {columns} vs Frequency")
                    plt.xlabel("Frequency")
                    plt.ylabel(columns)
                    plt.legend()
                    plt.grid()

                    # Guardar cada gráfico como un archivo PNG
                    file_path = os.path.join(output_folder, f"{columns}_{name}.png")
                    plt.savefig(file_path)
                    png_files.append(file_path)
                    plt.close()  # Libera memoria cerrando la figura 

def graphic_generation():
    

    # Crear una carpeta para guardar los gráficos como imágenes
    output_folder = "./graficos"
    output_folder_raw = "./graficos/raw"
    output_folder_ext = "./graficos/extrapole"
    output_folder_ph = "./graficos/phase_correction"
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_folder_raw, exist_ok=True)
    os.makedirs(output_folder_ext, exist_ok=True)
    os.makedirs(output_folder_ph, exist_ok=True)

    raw_data(output_folder_raw)
    ext_data(output_folder_ext)
    pha_data(output_folder_ph)
#        # Combinar las imágenes PNG en un único archivo PDF
#        if png_files:
#            images = [Image.open(png).convert("RGB") for png in png_files]
#            pdf_path = "graficos.pdf"  # Nombre del archivo PDF
#            images[0].save(pdf_path, save_all=True, append_images=images[1:])
#            print(f"Se ha creado el archivo PDF: {pdf_path}.")
#        else:
#            print("No se generaron gráficos PNG.")

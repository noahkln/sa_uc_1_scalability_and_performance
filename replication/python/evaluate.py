import csv
from datetime import datetime
import os
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
import numpy as np

FOLDER_RESULTS = "./csv_measurement_results"
FOLDER_PLOTS = "./plot_measurement_results"
SHOW_PLOT = True

def main():
  files = os.listdir(FOLDER_RESULTS)
  
  if not os.path.exists(FOLDER_PLOTS):
    os.makedirs(FOLDER_PLOTS)
  
  plt.rcParams.update({'font.size': 8})
  
  for file in files:
    data = []
      
    with open(f"{FOLDER_RESULTS}/{file}") as f:
      reader = csv.reader(f)
      for line in reader:
        data.append(line)
      f.close()
      
    headers = np.array(data[0])
    data = np.array(data[1:]).astype(np.float64)
    
    filename_parts = str(file).split("_")
    method = filename_parts[3]
    col_count = np.int32(filename_parts[4])
    different_rows = np.int32(filename_parts[6])
    iteration_count = np.int32(filename_parts[8])
    
    y_replication = data[:, headers == "score_replication"]
    y_import = data[:, headers == "score_import"]
    
    mask_repl = (y_replication != -1).flatten()
    mask_import = (y_import != -1).flatten()
    
    y_replication = y_replication[mask_repl]
    y_import = y_import[mask_import]
    
    x = data[:, headers == "rows"]
    x_repl = x[mask_repl]
    x_import = x[mask_import]
    
    cmap = mpl.colormaps["rainbow"](np.linspace(0, 1.0, 2))
    plt.scatter(x_import, y_import, marker="x", c=cmap[0, :][np.newaxis, :])
    plt.plot(x_import, y_import, c=cmap[0, :][np.newaxis, :], label="Import completed")
    plt.scatter(x_repl, y_replication, marker="x", c=cmap[1, :][np.newaxis, :])
    plt.plot(x_repl, y_replication, c=cmap[1, :][np.newaxis, :], label="Replication completed")
      
    plt.xlabel("Anzahl der Zeilen")
    plt.ylabel("Dauer [s]")
    plt.legend()
    
    title = f"Durchschnittliches Ergebnis über {iteration_count} Messungen für die Replikation von Tabellen mit {col_count} Spalten\n"
    if method == "remote":
      title += f"Indirekte Replikation"
    elif method == "direct":
      title += f"Direkte Replikation"
    plt.title(title)
        
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    plot_filename = f"plot_dolt_{method}_{different_rows}_rows_{col_count}_cols_{iteration_count}_iterations_{timestamp}.png"
    
    plt.savefig(f"{FOLDER_PLOTS}/{plot_filename}")
    if SHOW_PLOT: plt.show()


if __name__ == "__main__":
  main()
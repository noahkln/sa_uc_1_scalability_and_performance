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
    different_tables = np.int32(filename_parts[2])
    col_count = np.int32(filename_parts[4])
    different_rows = np.int32(filename_parts[6])
    iteration_count = np.int32(filename_parts[8])
    measured_data = filename_parts[10]
    measure_without_table_creation = measured_data == "data"
    diff_or_status_command = filename_parts[11]
    
    cmap = mpl.colormaps["rainbow"](np.linspace(0, 1.0, different_tables))
    
    for i in range(different_tables):
      lower_idx = np.int32(i*different_rows)
      upper_idx = np.int32((i+1)*different_rows)
      
      current_plot_data = data[lower_idx:upper_idx, :]
            
      plt.scatter(current_plot_data[:, headers == "rows"], current_plot_data[:, headers == "score"] / (i+1), marker="x", c=cmap[i, :][np.newaxis, :])
      plt.plot(current_plot_data[:, headers == "rows"], current_plot_data[:, headers == "score"] / (i+1), c=cmap[i, :][np.newaxis, :], label=f"{np.int32(data[lower_idx, 0])} Tabelle(n)")
      
    plt.xlabel("Anzahl der Zeilen")
    plt.ylabel("Dauer [s]")
    plt.legend()
    
    title = f"Durchschnitt über {iteration_count} Messungen für Tabellene mit {col_count} Spalten\n"
    if measure_without_table_creation:
      title += f"Erstellung der Tabellen nicht mit inbegriffen\n"
    else:
      title += f"Erstellung der Tabellen mit inbegriffen\n"
    title += f"Befehl: dolt {diff_or_status_command}"
    plt.title(title)
        
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    plot_filename = f"plot_{different_tables}_tables_{different_rows}_rows_{col_count}_cols_{iteration_count}_iterations_{measured_data}_{diff_or_status_command}_{timestamp}.png"
    
    plt.savefig(f"{FOLDER_PLOTS}/{plot_filename}")
    if SHOW_PLOT: plt.show()


if __name__ == "__main__":
  main()
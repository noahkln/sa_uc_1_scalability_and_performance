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
    data = np.array(data[1:]).astype(np.float32)
    
    filename_parts = str(file).split("_")
    different_rows = np.int32(filename_parts[2])
    iteration_count = np.int32(filename_parts[4])
    
    cmap = mpl.colormaps["rainbow"](np.linspace(0, 1.0, 2))
      
    plt.scatter(data[:,0].flatten(), data[:, headers == "mysql"].flatten(), marker="x", c=cmap[0, :][np.newaxis, :])
    plt.plot(data[:,0].flatten(), data[:, headers == "mysql"].flatten(), c=cmap[0, :][np.newaxis, :], label=f"MySQL")
      
    plt.scatter(data[:,0].flatten(), data[:, headers == "dolt"].flatten(), marker="x", c=cmap[1, :][np.newaxis, :])
    plt.plot(data[:,0].flatten(), data[:, headers == "dolt"].flatten(), c=cmap[1, :][np.newaxis, :], label=f"Dolt")
      
    # plt.xscale("log")
    plt.xlabel("Anzahl der Zeilen")
    plt.ylabel("Dauer [s]")
    plt.legend()
    
    title = f"Durchschnittlicher Ergebnisse über {iteration_count} Messungen für den Wechsel der Version"
    plt.title(title)
        
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    plot_filename = f"plot_{different_rows}_rows_{iteration_count}_iterations_{timestamp}.png"
    
    plt.savefig(f"{FOLDER_PLOTS}/{plot_filename}")
    if SHOW_PLOT: plt.show()


if __name__ == "__main__":
  main()
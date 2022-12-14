import numpy as np
import csv
from datetime import datetime
from dotenv import dotenv_values
import mysql.connector as db
import os
import time

from mysql.connector import MySQLConnection

FOLDER = "./csv_measurement_results"
FOLDER_DATA = "./csv_database_data"
VERBOSE = False
ROWS_PER_TABLE = np.linspace(10**2, 10**6, 8, dtype=np.int64)
ITERATIONS_PER_MEASUREMENT = 10
DELETE_CSV = True
  

def create_csvs(
    row_count: np.uint64
  ) -> str | None:
  timestamp = datetime.now().strftime("%d%m%Y_%H%M%S_%f")
  filename1 = f"data_1_{row_count}_rows_{timestamp}.csv"
  filename2 = f"data_2_{row_count}_rows_{timestamp}.csv"
  
  header = ["id"]
  
  for i in range(3):
    header.append(f"col{i+1}")
    
  primary_keys = np.arange(1, row_count+1)[:, np.newaxis]
  col_data_1 = np.ones((row_count, 3), dtype=np.int8)
  data_1 = np.concatenate([primary_keys, col_data_1], 1)
  
  col_data_2 = col_data_1
  col_data_2[:, -1] = -1
  data_2 = np.concatenate([primary_keys, col_data_2], 1)
  
  try:
    with open(f"{FOLDER_DATA}/{filename1}", "w", newline="") as f:
      writer = csv.writer(f)
      writer.writerow(header)
      writer.writerows(data_1)
      
      f.close()
      
    with open(f"{FOLDER_DATA}/{filename2}", "w", newline="") as f:
      writer = csv.writer(f)
      writer.writerow(header)
      writer.writerows(data_2)
      
      f.close()
    
    return (filename1, filename2)
  except:
    print(f"[ERROR] Unable to create CSV files '{filename1}' or '{filename2}'")
    return None
  

def measure_dolt(conn: MySQLConnection, filename1: str):
  if VERBOSE: print(f"[IMPRT] Starting import")
  filepath1 = f"{FOLDER_DATA}/{filename1}"
  
  if VERBOSE: print(f"[IMPRT] Creating tables")
  
  branch1 = "changes1"
  
  query(conn, f"CALL DOLT_BRANCH('{branch1}')")
  query(conn, f"CALL DOLT_CHECKOUT('{branch1}')")

  with open(filepath1) as f:
    reader = csv.reader(f)
    table_columns = next(reader)
    
    table_name = f"table_1"
    q = f"CREATE TABLE {table_name} ("
    for col_name in table_columns:
      q += f"{col_name} int,"
    q += f"primary key ({table_columns[0]}));"
      
    query(conn, q)
  
    absolute_csv_path = os.path.abspath(filepath1)
    absolute_csv_path = absolute_csv_path.replace("\\", "\\\\")
    
    header = ",".join(table_columns)
    if VERBOSE: print(f"[IMPRT] Importing data into '{table_name}'")
    q = f"LOAD DATA LOCAL INFILE '{absolute_csv_path}' INTO TABLE {table_name} FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\r\\n' IGNORE 1 LINES ({header});"
    query(conn, q)
      
    if VERBOSE: print(f"[IMPRT] Successfully imported data into tables")
  
    f.close()
  
  query(conn, "CALL dolt_add(\".\")")
  query(conn, "CALL dolt_commit(\"-m\", \"created table with ones\")")
  
  branch2 = "changes2"
  
  query(conn, f"CALL DOLT_BRANCH('{branch2}')")
  query(conn, f"CALL DOLT_CHECKOUT('{branch2}')")
  query(conn, "UPDATE table_1 SET col3 = -1;")
  
  query(conn, "CALL dolt_add(\".\")")
  query(conn, "CALL dolt_commit(\"-m\", \"created table with -1\")")
  
  c = conn.cursor()
  t0 = time.perf_counter()
  c.execute(f"CALL dolt_checkout('{branch1}')")
  t1 = time.perf_counter()
  c.fetchall()
  c.close()
  
  query(conn, "CALL dolt_checkout('main')")
  query(conn, f"CALL dolt_branch('-d', '-f', '{branch1}')")
  query(conn, f"CALL dolt_branch('-d', '-f', '{branch2}')")
  
  return t1 - t0


def measure_mysql(conn: MySQLConnection, filename1: str, filename2: str):
  if VERBOSE: print(f"[IMPRT] Starting import")
  filepath1 = f"{FOLDER_DATA}/{filename1}"  
  filepath2 = f"{FOLDER_DATA}/{filename2}"  

  with open(filepath1) as f:
    reader = csv.reader(f)
    table_columns = next(reader)
    
    table_name = f"table_1"
    q = f"CREATE TABLE {table_name} ("
    for col_name in table_columns:
      q += f"{col_name} int,"
    q += f"primary key ({table_columns[0]}));"
      
    query(conn, q)
  
    absolute_csv_path1 = os.path.abspath(filepath1)
    absolute_csv_path1 = absolute_csv_path1.replace("\\", "\\\\")
    
    header = ",".join(table_columns)
    if VERBOSE: print(f"[IMPRT] Importing data into '{table_name}'")
    q = f"LOAD DATA LOCAL INFILE '{absolute_csv_path1}' INTO TABLE {table_name} FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\r\\n' IGNORE 1 LINES ({header});"
    query(conn, q)
  
    f.close()
  
  
  with open(filepath2) as f:
    absolute_csv_path2 = os.path.abspath(filepath2)
    absolute_csv_path2 = absolute_csv_path2.replace("\\", "\\\\")
  
    header = ",".join(table_columns)
    table_name = f"table_1"
    
    q_table = f"CREATE TABLE {table_name} ("
    for col_name in table_columns:
      q_table += f"{col_name} int,"
    q_table += f"primary key ({table_columns[0]}));"
    
    q_import = f"LOAD DATA LOCAL INFILE '{absolute_csv_path2}' INTO TABLE {table_name} FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\r\\n' IGNORE 1 LINES ({header});"
    
    c = conn.cursor()
    t0 = time.perf_counter()
    c.execute("DROP TABLE table_1;")
    c.execute(q_table)
    c.execute(q_import)
    t1 = time.perf_counter()
    c.close()
    
    f.close()
  
  query(conn, "DROP TABLE table_1;")
  
  return t1 - t0
  
  
def connect(hostname: str, port: np.uint16, user: str, password: str, db_name: str) -> MySQLConnection | None:
  if VERBOSE: print(f"[DB   ] Establishing connection to database")
  try:
    conn = db.connect(
      user=user,
      host=hostname,
      port=port,
      database=db_name,
      password=password,
      allow_local_infile=True
    )
  
    if not conn.is_connected():
      return None
    
    return conn
  except:
    return None


def configure_mysql_database(conn: MySQLConnection, user: str):
  query(conn, "SET GLOBAL local_infile = 'ON';")


def query(conn: MySQLConnection, query: str):
  try:
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result
  except Exception as e:
    print(f"[ERROR] Query \"{query}\" raised an error: {e}")
    exit(-1)


def check_for_empty_database(conn: MySQLConnection):
  if VERBOSE: print("[DB   ] Checking for empty database")
  result = query(conn, "SHOW TABLES;")
  
  if len(result) > 0:
    print("[DB   ] Database is not empty")
    exit(-1)
    
  if VERBOSE: print("[DB   ] Database empty")


def create_result_csv(scores: np.ndarray):
  timestamp = datetime.now().strftime("%d%m%Y_%H%M%S_%f")
  filename = f"mean_score_{len(ROWS_PER_TABLE)}_rows_{ITERATIONS_PER_MEASUREMENT}_iterations_{timestamp}.csv"
  
  with open(f"{FOLDER}/{filename}", "w", newline="") as f:
    writer = csv.writer(f)
    
    header = ["rows", "dolt", "mysql"]
    
    writer.writerow(header)
    
    for idx_r, r in enumerate(ROWS_PER_TABLE):
      writer.writerow([r, scores[idx_r, 0], scores[idx_r, 1]])
    
    f.close()


def main():
  env = dotenv_values()
  
  hostname = env["DB_HOST"]
  user = env["DB_USER"]
  password = env["DB_PASSWORD"]
  db_name = env["DB_NAME"]
  port_dolt = np.int32(env["DB_PORT_DOLT"])
  port_mysql = np.int32(env["DB_PORT_MYSQL"])
  
  dolt = connect(hostname, port_dolt, user, password, db_name)
  mysql = connect(hostname, port_mysql, user, password, db_name)
  
  if not dolt:
    print("[ERROR] Dolt database connection failed")
    exit(-1)
  if not mysql:
    print("[ERROR] MySQL database connection failed")
    exit(-1)
  
  dolt.autocommit = True
  
  check_for_empty_database(dolt)
  check_for_empty_database(mysql)
  mysql_root = connect(hostname, port_mysql, "root", "", db_name)
  configure_mysql_database(mysql_root, user)
  mysql_root.close()
  configure_mysql_database(dolt, user)
  query(mysql, "USE db;")
  
  data_sum = np.zeros((len(ROWS_PER_TABLE), 2), dtype=np.float64)
  
  for idx_r, r in enumerate(ROWS_PER_TABLE):
    filename1, filename2 = create_csvs(r)
    for _ in range(ITERATIONS_PER_MEASUREMENT):
      d = measure_dolt(dolt, filename1)
      m = measure_mysql(mysql, filename1, filename2)
      data_sum[idx_r] += [d, m]
      
      check_for_empty_database(dolt)
      check_for_empty_database(mysql)
    
    if DELETE_CSV:
      os.remove(f"./{FOLDER_DATA}/{filename1}")
      os.remove(f"./{FOLDER_DATA}/{filename2}")

  
  print("[SCORE] Summed score")
  print("[SCORE] " + np.array2string(data_sum, prefix="[SCORE] "))
  
  data_mean = data_sum / ITERATIONS_PER_MEASUREMENT
  print("[SCORE] Mean score")
  print("[SCORE] " + np.array2string(data_mean, prefix="[SCORE] "))
  
  create_result_csv(data_mean)
  
  print("[EXIT ]")
  
  
if __name__ == "__main__":
  main()
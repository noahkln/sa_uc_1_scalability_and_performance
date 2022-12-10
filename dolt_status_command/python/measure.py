import array
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
TABLES = np.arange(1, 4)
ROWS_PER_TABLE = np.logspace(4, 6, 3, dtype=np.int64)
COLS_PER_TABLE = 3
ITERATIONS_PER_MEASUREMENT = 10
DELETE_CSV = True
INITIAL_COMMIT = "uo0ghlafh12kmpt6b47u4vic25s6v8p0"
MEASURE_AFTER_TABLE_CREATION = False
METHOD = "STATUS" # "DIFF" or "STATUS"
  

def create_csv(
    row_count: np.uint64
  ) -> str | None:
  timestamp = datetime.now().strftime("%d%m%Y_%H%M%S_%f")
  filename = f"table_data_{row_count}_rows_{timestamp}.csv"
  
  if VERBOSE: print(f"[CSV  ] Generating '{filename}'")
  
  header = ["id"]
  
  for i in range(COLS_PER_TABLE):
    header.append(f"col{i+1}")
  
  try:
    with open(f"{FOLDER_DATA}/{filename}", "w", newline="") as f:
      writer = csv.writer(f)
      
      primary_keys = np.arange(1, row_count+1)[:, np.newaxis]
      col_data = np.random.randint(low=np.iinfo(np.int8).min, high=np.iinfo(np.int8).max, size=(row_count, COLS_PER_TABLE), dtype=np.int8)
      
      data = np.concatenate([primary_keys, col_data], 1)
      writer.writerow(header)
      writer.writerows(data)
      
      f.close()
    
    if VERBOSE: print(f"[CSV  ] Successfully created CSV file '{filename}'")
    
    return filename
  except:
    print(f"[ERROR] Unable to create CSV file '{filename}'")
    return None
  

def import_data_for_dolt_status(conn: MySQLConnection, table_count: np.uint8, row_count: np.uint64):
  if VERBOSE: print(f"[IMPRT] Starting import")
  filename = create_csv(row_count)
  filepath = f"{FOLDER_DATA}/{filename}"  
  
  if VERBOSE: print(f"[IMPRT] Creating {table_count} tables")

  with open(filepath) as f:
    reader = csv.reader(f)
    table_columns = next(reader)
    
    for idx in range(table_count):
      table_name = f"table_{idx+1}"
      q = f"CREATE TABLE {table_name} ("
      for col_name in table_columns:
        q += f"{col_name} int,"
      q += f"primary key ({table_columns[0]}));"
      
      query(conn, q)
  
    if MEASURE_AFTER_TABLE_CREATION:
      query(conn, "CALL dolt_add(\".\")")
      query(conn, "CALL dolt_commit(\"-m\", \"created tables\")")
  
    absolute_csv_path = os.path.abspath(filepath)
    absolute_csv_path = absolute_csv_path.replace("\\", "\\\\")
    
    header = ",".join(table_columns)
    for idx in range(table_count):
      table_name = f"table_{idx+1}"
      if VERBOSE: print(f"[IMPRT] Importing data into '{table_name}'")
      q = f"LOAD DATA LOCAL INFILE '{absolute_csv_path}' INTO TABLE {table_name} FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\r\\n' IGNORE 1 LINES ({header});"
      query(conn, q)
      
    if VERBOSE: print(f"[IMPRT] Successfully imported data into tables")
  
    f.close()
  
  if VERBOSE: print(f"[IMPRT] Import done")
  
  if VERBOSE: print(f"[IMPRT] Removing csv files")
  if DELETE_CSV:
    os.remove(filepath)
    
    if VERBOSE: print(f"[IMPRT] Files removed")
  else:
    if VERBOSE: print(f"[IMPRT] Skipped")


def import_data_for_dolt_diff(conn: MySQLConnection, table_count: np.uint8, row_count: np.uint64):
  if VERBOSE: print(f"[IMPRT] Starting import")
  filename = create_csv(row_count)
  filepath = f"{FOLDER_DATA}/{filename}"  
  
  if VERBOSE: print(f"[IMPRT] Creating {table_count} tables")

  with open(filepath) as f:
    reader = csv.reader(f)
    table_columns = next(reader)
    
    for idx in range(table_count):
      table_name = f"table_{idx+1}"
      q = f"CREATE TABLE {table_name} ("
      for col_name in table_columns:
        q += f"{col_name} int,"
      q += f"primary key ({table_columns[0]}));"
      
      query(conn, q)
  
    if MEASURE_AFTER_TABLE_CREATION:
      query(conn, "CALL dolt_add(\".\")")
      query(conn, "CALL dolt_commit(\"-m\", \"created tables\")")
  
    absolute_csv_path = os.path.abspath(filepath)
    absolute_csv_path = absolute_csv_path.replace("\\", "\\\\")
    
    header = ",".join(table_columns)
    for idx in range(table_count):
      table_name = f"table_{idx+1}"
      if VERBOSE: print(f"[IMPRT] Importing data into '{table_name}'")
      q = f"LOAD DATA LOCAL INFILE '{absolute_csv_path}' INTO TABLE {table_name} FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\r\\n' IGNORE 1 LINES ({header});"
      query(conn, q)
      
    if VERBOSE: print(f"[IMPRT] Successfully imported data into tables")
  
    f.close()
  
  query(conn, "CALL dolt_add(\".\")")
  query(conn, "CALL dolt_commit(\"-m\", \"created data\")")
  
  if VERBOSE: print(f"[IMPRT] Import done")
  
  if VERBOSE: print(f"[IMPRT] Removing csv files")
  if DELETE_CSV:
    os.remove(filepath)
    
    if VERBOSE: print(f"[IMPRT] Files removed")
  else:
    if VERBOSE: print(f"[IMPRT] Skipped")


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


def configure_database(conn: MySQLConnection, env):
  user = env["DB_USER"]
  query(conn, "SET GLOBAL local_infile = 'ON';")
  query(conn, f"GRANT FILE ON *.* TO '{user}'@'localhost';")


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
    if VERBOSE: print("[DB   ] Database is not empty")
    if VERBOSE: print("[DB   ] Clearing database")
    

    for table in np.array(result)[:, 0]:
      if VERBOSE: print(f"[DB   ] Dropping table '{table}'")
      query(conn, f"DROP TABLE {table}")
    
  if VERBOSE: print("[DB   ] Database empty")


def measure_dolt_status(conn: MySQLConnection):
  if VERBOSE: print("[TIME ] Starting measurement process")

  c = conn.cursor()
  
  t0 = time.perf_counter()
  c.execute("SELECT * FROM dolt_status;")
  t = time.perf_counter()
  c.fetchall()
  c.close()
  
  if VERBOSE: print(f"[TIME ] Finished after {t - t0}")
  if VERBOSE: print("[TIME ] Starting measurement process")
  return t - t0


def measure_dolt_diff(conn: MySQLConnection, tables: np.ndarray):
  if VERBOSE: print("[TIME ] Starting measurement process")

  c = conn.cursor()
  result = 0.0
  
  for t in tables:
    t0 = time.perf_counter()
    c.execute(f"SELECT * FROM DOLT_DIFF(\"HEAD\", \"HEAD^\", \"{t}\");")
    t = time.perf_counter()
    c.fetchall()
    result += (t - t0)
  c.close()
  
  if VERBOSE: print(f"[TIME ] Finished after {result}")
  if VERBOSE: print("[TIME ] Starting measurement process")
  return result


def create_result_csv(scores: np.ndarray):
  timestamp = datetime.now().strftime("%d%m%Y_%H%M%S_%f")
  filename = f"mean_score_{len(TABLES)}_tables_{COLS_PER_TABLE}_cols_{len(ROWS_PER_TABLE)}_rows_{ITERATIONS_PER_MEASUREMENT}_iterations_{'data' if MEASURE_AFTER_TABLE_CREATION else 'table'}_{METHOD.lower()}_{timestamp}.csv"
  
  with open(f"{FOLDER}/{filename}", "w", newline="") as f:
    writer = csv.writer(f)
    
    header = ["tables", "rows", "score"]
    
    writer.writerow(header)
    
    for idx_t, t in enumerate(TABLES):
      for idx_r, r in enumerate(ROWS_PER_TABLE):
          writer.writerow([t, r, scores[idx_t, idx_r]])
    
    f.close()


def main():
  env = dotenv_values()
  
  hostname = env["DB_HOST"]
  user = env["DB_USER"]
  password = env["DB_PASSWORD"]
  db_name = env["DB_NAME"]
  port = np.int32(env["DB_PORT"])
  
  conn = connect(hostname, port, user, password, db_name)
  
  if not conn:
    print("[ERROR] Database connection failed")
    exit(-1)
  
  conn.autocommit = True
  
  check_for_empty_database(conn)
  configure_database(conn, env)
  
  data_sum = np.zeros((len(TABLES), len(ROWS_PER_TABLE)), dtype=np.float64)
  
  if METHOD == "DIFF":
    for idx_t, t in enumerate(TABLES):
      for idx_r, r in enumerate(ROWS_PER_TABLE):
          for _ in range(ITERATIONS_PER_MEASUREMENT):
            import_data_for_dolt_diff(conn, t, r)
            table_names = []
            for i in range(t):
              table_names.append(f"table_{i+1}")
            data_sum[idx_t, idx_r] += measure_dolt_diff(conn, table_names)
            
            query(conn, f"CALL dolt_reset(\"--hard\", \"{INITIAL_COMMIT}\")")
  elif METHOD == "STATUS":
    for idx_t, t in enumerate(TABLES):
      for idx_r, r in enumerate(ROWS_PER_TABLE):
          for _ in range(ITERATIONS_PER_MEASUREMENT):
            import_data_for_dolt_status(conn, t, r)
            data_sum[idx_t, idx_r] += measure_dolt_status(conn)
            
            query(conn, "CALL dolt_add(\".\")")
            query(conn, "CALL dolt_commit(\"-m\", \"created tables\")")
            query(conn, f"CALL dolt_reset(\"--hard\", \"{INITIAL_COMMIT}\")")

  
  print("[SCORE] Summed score")
  print("[SCORE] " + np.array2string(data_sum, prefix="[SCORE] "))
  
  data_mean = data_sum / ITERATIONS_PER_MEASUREMENT
  print("[SCORE] Mean score")
  print("[SCORE] " + np.array2string(data_mean, prefix="[SCORE] "))
  
  create_result_csv(data_mean)
  
  print("[EXIT ]")
  
  
if __name__ == "__main__":
  main()
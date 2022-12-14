import sys
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
COLS_PER_TABLE = 3
ITERATIONS_PER_MEASUREMENT = 10
DELETE_CSV = True

REPLICATION_METHOD = sys.argv[1]


def create_csv(
    row_count: np.uint64
  ) -> str | None:
  timestamp = datetime.now().strftime("%d%m%Y_%H%M%S_%f")
  filename = f"table_data_{row_count}_rows_{timestamp}.csv"
  
  if VERBOSE: print(f"[CSV  ] Generating '{filename}'")
  
  header = ["id"]
  
  for i in range(COLS_PER_TABLE):
    header.append(f"col{i+1}")
  
  if not os.path.exists(f"{FOLDER_DATA}"):
    os.mkdir(f"{FOLDER_DATA}")
  
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
  query(conn, f"GRANT FILE ON *.* TO '{user}'@'%';")


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


def check_for_empty_database_src(conn: MySQLConnection):
  if VERBOSE: print("[DB   ] Checking for empty source database")
  result = query(conn, "SHOW TABLES;")
  
  if len(result) > 0:
    if VERBOSE: print("[DB   ] Database is not empty")
    if VERBOSE: print("[DB   ] Clearing database")
    

    for table in np.array(result)[:, 0]:
      if VERBOSE: print(f"[DB   ] Dropping table '{table}'")
      query(conn, f"DROP TABLE {table}")
    
  if VERBOSE: print("[DB   ] Database empty")
  
  
def check_for_empty_database_rep(conn: MySQLConnection):
  if VERBOSE: print("[DB   ] Checking for empty replica database")
  result = query(conn, "SHOW TABLES;")
  
  while len(result) > 0:
    if VERBOSE: print("[DB   ] Database is not empty")
    return False
    
  if VERBOSE: print("[DB   ] Database empty")
  return True
  
  
def measure(m: MySQLConnection, r: MySQLConnection, row_count: np.uint64):
  if VERBOSE: print(f"[IMPRT] Starting import")
  filename = create_csv(row_count)
  filepath = f"{FOLDER_DATA}/{filename}"
  
  table_name = f"table_1"
  
  results = np.zeros((3, 1))
  
  t0 = t1 = t2 = 0
  
  with open(filepath) as f:
    reader = csv.reader(f)
    table_columns = next(reader)
    
    q = f"CREATE TABLE {table_name} ("
    for col_name in table_columns:
      q += f"{col_name} int,"
    q += f"primary key ({table_columns[0]}));"
    
    query(m, q)
    
    absolute_csv_path = os.path.abspath(filepath)
    absolute_csv_path = absolute_csv_path.replace("\\", "\\\\")
    
    header = ",".join(table_columns)
    if VERBOSE: print(f"[IMPRT] Importing data into '{table_name}'")
    q = f"LOAD DATA LOCAL INFILE '{absolute_csv_path}' INTO TABLE {table_name} FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\r\\n' IGNORE 1 LINES ({header});"
    m_cur = m.cursor()
    r_cur = r.cursor()
    
    t0 = time.perf_counter()
    m_cur.execute(q)
    t1 = time.perf_counter()
  
  invalid = 0
  while True:
    try:
      r_cur.execute(f"SELECT * FROM {table_name};")
      if len(r_cur.fetchall()) == row_count:
        t2 = time.perf_counter()
        break
    except:
      invalid += 1
      if invalid > 10:
        print("[ERROR] Return results after 10 tries")
        m_cur.close()
        r_cur.close()
        results = np.array([t1 - t0, -1])
        return results
  
  m_cur.fetchall()
  m_cur.close()
  r_cur.fetchall()
  r_cur.close()
    
  results = np.array([t1 - t0, t2 - t0])
    
  if VERBOSE: print(f"[IMPRT] Done")
  
  if VERBOSE: print(f"[IMPRT] Removing csv file")
  if DELETE_CSV:
    os.remove(filepath)
    
    if VERBOSE: print(f"[IMPRT] File removed")
  else:
    if VERBOSE: print(f"[IMPRT] Skipped")
  
  return results
    
    
def create_result_csv(scores: np.ndarray):
  timestamp = datetime.now().strftime("%d%m%Y_%H%M%S_%f")
  filename = f"mean_score_{REPLICATION_METHOD}_{COLS_PER_TABLE}_cols_{len(ROWS_PER_TABLE)}_rows_{ITERATIONS_PER_MEASUREMENT}_iterations_{timestamp}.csv"
  
  if not os.path.exists(f"{FOLDER}"):
    os.mkdir(f"{FOLDER}")
    
  with open(f"{FOLDER}/{filename}", "w", newline="") as f:
    writer = csv.writer(f)
    
    header = ["rows", "score_import", "score_replication"]
    
    writer.writerow(header)
    
    for idx_r, r in enumerate(ROWS_PER_TABLE):
      writer.writerow([r, scores[idx_r, 0], scores[idx_r, 1]])
    
    f.close()


def main():
  env = dotenv_values()
  
  hostname_master = env["DB_HOST_MASTER"]
  port_master = np.int32(env["DB_PORT_MASTER"])
  hostname_replica = env["DB_HOST_REPLICA"]
  port_replica = np.int32(env["DB_PORT_REPLICA"])
  user = env["DB_USER"]
  password = env["DB_PASSWORD"]
  db_name = env["DB_NAME"]
  
  master = connect(hostname_master, port_master, user, password, db_name)
  replica = connect(hostname_replica, port_replica, user, password, db_name)
  
  if not master:
    print("[ERROR] Database connection to master failed")
    exit(-1)
  if not replica:
    print("[ERROR] Database connection to replica failed")
    exit(-1)
  
  master.autocommit = True
  replica.autocommit = True
  
  check_for_empty_database_src(master)
  while check_for_empty_database_rep(replica) == False:
    replica.close()
    time.sleep(5)
    replica.connect()
  configure_database(master, env)
  configure_database(replica, env)
  
  data_sum = np.zeros((len(ROWS_PER_TABLE), 2), dtype=np.float64)
  
  for idx_r, r in enumerate(ROWS_PER_TABLE):
      for _ in range(ITERATIONS_PER_MEASUREMENT):
        data_sum[idx_r] += measure(master, replica, r)
        check_for_empty_database_src(master)
        while check_for_empty_database_rep(replica) == False:
          replica.close()
          time.sleep(5)
          replica.connect()

  
  print("[SCORE] Summed score")
  print("[SCORE] " + np.array2string(data_sum, prefix="[SCORE] "))
  
  data_mean = data_sum / ITERATIONS_PER_MEASUREMENT
  print("[SCORE] Mean score")
  print("[SCORE] " + np.array2string(data_mean, prefix="[SCORE] "))
  
  create_result_csv(data_mean)
  
  master.close()
  replica.close()
  print("[EXIT ]")
  
if __name__ == "__main__":
  main()
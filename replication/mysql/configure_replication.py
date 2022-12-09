import string
import mysql.connector
from mysql.connector import MySQLConnection
import subprocess
import os
import threading
import socket
import sys

DB_MASTER_HOST: string = "master_db"
DB_SLAVES: list = ["slave_1_db", "slave_2_db", "slave_3_db"]
DB_USER_ROOT: string = "root"
DB_PWD_ROOT: string = "kla1sdALKS4354DJa768klsdals41j1dkljas7DASDk4ll3ajs8dlASD"
DB_USER: string = "nkhartwig"
DB_PWD: string = "tmp"
DB_DATABASE: string = "db"

DB_DUMP_PATH: string = "/dumps/dump.sql"

def connect(host: string, user: string=DB_USER, password: string=DB_PWD) -> MySQLConnection:
  print(f"Establishing connection to {host}")
  return mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    port=3306,
    database=DB_DATABASE
  )
  
  
def query(db: MySQLConnection, stmt: string):
  c = db.cursor()
  c.execute(stmt)
  result = c.fetchall()
  c.close()
  return result


def dump(db: MySQLConnection):
  print(f"Dumping data from {db._host} to {DB_DUMP_PATH}")
  cmd = f"mysqldump --host={db._host} --user={db._user} --password={db._password} --all-databases --source-data --result-file={DB_DUMP_PATH}"
  if not os.path.exists(DB_DUMP_PATH):
    print("Dumping")
    with open(DB_DUMP_PATH,"x") as output:
      subprocess.Popen([cmd], shell=True).wait()
  else:
    print("Skipping dumping because file exists")


def setup_replica(slave_host: string, master_ip: string, master_bin_file: string, master_bin_loc: int):
  print("In Method")
  db = connect(slave_host, user=DB_USER_ROOT, password=DB_PWD_ROOT)
  cmd = f"mysql --host={slave_host} --user={db._user} --password={db._password} < {DB_DUMP_PATH}"
  print(f"Import dump for {slave_host}")
  subprocess.Popen(cmd, shell=True).wait()
  setup_replica_stmt = f"CHANGE REPLICATION SOURCE TO SOURCE_HOST=\'{master_ip}\', SOURCE_USER=\'{DB_USER}\', SOURCE_PASSWORD=\'{DB_PWD}\', SOURCE_LOG_FILE=\'{master_bin_file}\', SOURCE_LOG_POS={master_bin_loc};"
  cmd = f"mysql --host={slave_host} --user={db._user} --password={db._password} -e \"{setup_replica_stmt}\""
  print(f"Setting up master db data in {slave_host}")
  subprocess.Popen(cmd, shell=True).wait()
  db.close()


def main():
  db_master: MySQLConnection = connect(DB_MASTER_HOST, user=DB_USER_ROOT, password=DB_PWD_ROOT)
  
  # Create dump for replicas
  dump(db_master)
  
  # Lock tables
  print("Lock tables of master db")
  c = db_master.cursor()
  c.execute("FLUSH TABLES WITH READ LOCK;")
  c.fetchall()
  
  # Get master data
  db_master_tmp: MySQLConnection = connect(DB_MASTER_HOST, user=DB_USER_ROOT, password=DB_PWD_ROOT)
  print("Getting binary file location")
  master_filename, master_location = query(db_master_tmp, "SHOW MASTER STATUS;")[0][:2]
  db_master_tmp.close()
  
  # Importing dump to replicas and setup master configuration
  threads: list = []
  for slave_hostname in DB_SLAVES:
    t = threading.Thread(target=lambda: setup_replica(slave_hostname, socket.gethostbyname(DB_MASTER_HOST), master_filename, master_location))
    print(f"Starting thread {t.name}")
    t.start()
    threads.append(t)
  print("Wait for threads")
  for t in threads:
    t.join()
  
  # Unlock tables and close connection
  print("Unlock tables of master db")
  c.execute("UNLOCK TABLES;")
  c.fetchall()
  c.close()
  print("Closing master")
  db_master.disconnect()
  print("All done!")


if __name__ == "__main__":
  main()
import string
import time
import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.errors import Error as MySQLError
import socket

DB_MASTER_HOST: string = "master_db"
DB_SLAVE: string = "slave_db"
DB_USER_ROOT: string = "root"
DB_PWD_ROOT: string = "kla1sdALKS4354DJa768klsdals41j1dkljas7DASDk4ll3ajs8dlASD"
DB_USER: string = "sa_uc_1"
DB_PWD: string = "sa_uc_1_password"
DB_DATABASE: string = "db"

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


def setup_replica(slave: MySQLConnection, master_ip: string, master_bin_file: string, master_bin_loc: int):
  query(slave, "GRANT ALL PRIVILEGES ON *.* TO 'sa_uc_1'@'%' WITH GRANT OPTION;")
  setup_replica_stmt = f"CHANGE REPLICATION SOURCE TO SOURCE_HOST=\'{master_ip}\', SOURCE_USER=\'{DB_USER}\', SOURCE_PASSWORD=\'{DB_PWD}\', SOURCE_LOG_FILE=\'{master_bin_file}\', SOURCE_LOG_POS={master_bin_loc};"
  print(f"Setting up master db data in replica")
  query(slave, setup_replica_stmt)


def main():
  # Get master data
  db_master: MySQLConnection = connect(DB_MASTER_HOST, user=DB_USER_ROOT, password=DB_PWD_ROOT)
  db_replica: MySQLConnection = connect(DB_SLAVE, user=DB_USER_ROOT, password=DB_PWD_ROOT)
  print("Getting binary file location")
  master_filename, master_location = query(db_master, "SHOW MASTER STATUS;")[0][:2]
  
  print("Add replication permission to user")
  query(db_master, "GRANT ALL PRIVILEGES ON *.* TO 'sa_uc_1'@'%' WITH GRANT OPTION;")
  
  print("Setting up replica")
  setup_replica(db_replica, socket.gethostbyname(DB_MASTER_HOST), master_filename, master_location)
  
  print("Install semisync plugin")
  try:
    query(db_master, "INSTALL PLUGIN rpl_semi_sync_source SONAME 'semisync_source.so';")
  except MySQLError as err:
    if (err.errno == 1125):
      pass
    else:
      print("Error while installing semisync plugin for source")
      exit(-1)
  try:
    query(db_replica, "INSTALL PLUGIN rpl_semi_sync_replica SONAME 'semisync_replica.so';")
  except MySQLError as err:
    if (err.errno == 1125):
      pass
    else:
      print("Error while installing semisync plugin for replica")
      exit(-1)
  
  print("Activate semisync plugin")
  query(db_master, "SET GLOBAL rpl_semi_sync_source_enabled = 1;")
  time.sleep(4)
  query(db_replica, "SET GLOBAL rpl_semi_sync_replica_enabled = 1;")
  query(db_replica, "CHANGE MASTER TO GET_MASTER_PUBLIC_KEY=1;")
  
  print(query(db_master, "SHOW MASTER STATUS"))
  print(query(db_replica, "SHOW REPLICA STATUS"))
  
  print("Closing connections")
  db_master.close()
  db_replica.close()
  print("All done!")


if __name__ == "__main__":
  main()
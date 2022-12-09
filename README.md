# Seminararbeit Usecase 1: Skalierbarkeit und Performance

## Messen des _dolt status_ Befehls

1. Starten der Datenbank
   1. Datenbank von [DoltHub](https://www.dolthub.com/repositories/noahkln/sa_uc_1_dolt_status_command/data/main) nach _&lt;project\_root&gt;/dolt\_status\_command/databases_ klonen
   2. `cd <project-root>/dolt_status_command/databases/db`
   3. `dolt sql-server --host=<host> --port=<port> --user=<user> --password=<password>`

2. Starten des Python Scripts
   1. `cd <project-root>/dolt_status_command/python`
   2. Datei _.env.template_ nach _.env_ kopieren
   3. Setzen der gewählten Konfigurationsdaten für die Datenbank in _.env_
   4. `python ./main.py`

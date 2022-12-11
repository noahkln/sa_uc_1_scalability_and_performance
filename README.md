# Seminararbeit Usecase 1: Skalierbarkeit und Performance

## Messen der Dauer von Befehlen

1. Starten der Datenbank
   1. Datenbank von [DoltHub](https://www.dolthub.com/repositories/noahkln/sa_uc_1_dolt_status_command/data/main) nach _&lt;project\_root&gt;/dolt\_status\_command/databases/db_ klonen
   2. `cd <project-root>/dolt_status_command/databases/db`
   3. `dolt sql-server --host=<host> --port=<port> --user=<user> --password=<password>`

2. Messungen mit Python Script
   1. `cd <project-root>/dolt_status_command/python`
   2. `pip install -r ./requirements.txt`
   3. Datei _.env.template_ nach _.env_ kopieren
   4. Setzen der gewählten Konfigurationsdaten für die Datenbank in _.env_
   5. Kostanten in _measure.py_ für die gewünschten Messungen anpassen
   6. `python ./measure.py`
   7. Konstanten in _evaluate.py_ für die gewünschte Ausgabe der Ergebnisse anpassen
   8. `python ./evaluate.py`

## Messen der Synchronisation von Replikationen

### Starten eines der unterschiedlichen Replikationsnetzwerke

#### Dolt - Direkte Replikation

1. `cd <project-root>/replication`
2. `docker-compose -f docker-compose-direct.yml build`
3. `docker-compose -f docker-compose-direct.yml up`

#### Dolt - Indirekte Replikation

1. Dolt Credentials erstellen durch `dolt creds new` und die entstandene Datei nach _&lt;project\_root&gt;/repliaction/remote/creds.jwk_ kopieren
2. Mit dem von `dolt creds new` entstandenen Public Key `PUB_CRED=<public-key> docker-compose -f docker-compose-remote.yml build` ausführen
3. `docker-compose -f docker-compose-remote.yml up`

#### MySQL - Direkte Replikation

1. 

### Das Python Script für die Messungen starten
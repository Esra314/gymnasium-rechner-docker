# Gymnasium-Rechner Berlin

## Beschreibung

Der Gymnasium-Rechner Berlin unterstützt bei der Berechnung einer Gymnasialempfehlung.

## Funktionen

- Schüler anlegen
- Noten erfassen
- Durchschnitt berechnen
- Hauptfachsumme berechnen
- Gymnasialempfehlung ermitteln
- Schüler bearbeiten
- Noten bearbeiten
- Schüler löschen

# Projektübersicht
Dieses Projekt demonstriert die Bereitstellung einer Flask-Webanwendung mit PostgreSQL in einer Docker-Swarm-Umgebung.
Verwendete Technologien
Docker
Docker Swarm
PostgreSQL 16
Flask
Docker Secrets
Docker Volumes
Docker Overlay Network
GitHub


# Infrastruktur

Hyper-V
│
├── Manager
│   └── esra-Virtual-Machine
│
├── Worker 1
│   └── ubuntu2
│
└── Worker 2
    └── ubuntu3


# docker Swarm Architektur

              Docker Swarm
 
        ┌─────────────────────┐
        │      Manager        │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   Worker 1              Worker 2


# Services

Web Application

Flask
5 Replikas
Port 5000 veröffentlicht

Datenbank

PostgreSQL 16
1 Replica
Persistente Speicherung über Docker Volume

# Netzwerk

networks:
  gymnasium-over-net:
    driver: overlay


Vorteile:
Kommunikation zwischen allen Nodes
Service Discovery
Container können sich über Servicenamen erreichen

# Docker Secret
Das Datenbankpasswort wird über Docker Secrets verwalt
secrets:
  DB_PASSWORD:
    external: true


Im Container verfügbar unter:
/run/secrets/DB_PASSWORD


# Docker Volume

Die PostgreSQL-Daten werden in einem Docker Volume gespeichert.

volumes:
  postgres_data:

Einbindung:
volumes:
  - postgres_data:/var/lib/postgresql/data

Vorteile:
Daten bleiben nach Container-Neustarts erhalten
Daten bleiben nach Stack-Neuinstallation erhalten



# Deployment
Stack bereitstellen:

docker stack deploy -c docker-stack.yml gymnasium
 
Services prüfen:
 
docker stack services gymnasium
``
 
Tasks anzeigen:
 
docker stack ps gymnasium

# Überwachung

Logs der Webanwendung:
 
docker service logs gymnasium_web
 
Logs der Datenbank:
 
docker service logs gymnasium_db

# Skalierung

Die Webanwendung wird mit fünf Replikas betrieben.
 
deploy:
  replicas: 5
 
Docker Swarm verteilt die Container automatisch auf die verfügbaren Nodes.
 
 
 
## Projektumfang

Dieses Projekt wurde im Rahmen eines Praktikums entwickelt.
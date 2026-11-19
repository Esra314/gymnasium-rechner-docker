import psycopg2
import os

LAST_DB_STATUS = "PRIMARY"

def _get_password():
    password = os.getenv("DB_PASSWORD", "geheim")
    password_file = os.getenv("DB_PASSWORD_FILE", "/run/secrets/DB_PASSWORD")
    if password_file and os.path.exists(password_file):
        try:
            with open(password_file, "r") as f:
                password = f.read().strip()
        except Exception:
            pass
    return password

def _connect_single(host):
    conn = psycopg2.connect(
        host=host,
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "gymnasium"),
        user=os.getenv("DB_USER", "postgres"),
        password=_get_password(),
        connect_timeout=2
    )
    _ensure_tables(conn)
    return conn

def _ensure_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schueler (
        id SERIAL PRIMARY KEY,
        vorname VARCHAR(100),
        nachname VARCHAR(100),
        geburtsdatum DATE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS berechnungen (
        id SERIAL PRIMARY KEY,
        schueler_id INTEGER REFERENCES schueler(id),
        deutsch5 INTEGER, mathe5 INTEGER, englisch5 INTEGER, nawi5 INTEGER,
        gewi5 INTEGER, kunst5 INTEGER, musik5 INTEGER, sport5 INTEGER,
        deutsch6 INTEGER, mathe6 INTEGER, englisch6 INTEGER, nawi6 INTEGER,
        gewi6 INTEGER, kunst6 INTEGER, musik6 INTEGER, sport6 INTEGER,
        durchschnitt NUMERIC(4,2),
        hauptfachsumme INTEGER,
        ergebnis TEXT
    )
    """)
    conn.commit()
    cursor.close()

def get_read_connection():
    """Versucht zuerst DB 1 (Aktiv auf ubuntu1), bei Ausfall DB 2 (Passiv auf ubuntu2)."""
    global LAST_DB_STATUS
    primary_host = os.getenv("DB_HOST", "db")
    backup_host = os.getenv("DB_BACKUP_HOST", "db_backup")

    try:
        conn = _connect_single(primary_host)
        LAST_DB_STATUS = "PRIMARY"
        return conn
    except Exception as e:
        print(f"WARNUNG: Hauptdatenbank ({primary_host}) nicht erreichbar: {e}")

    try:
        conn = _connect_single(backup_host)
        LAST_DB_STATUS = "BACKUP"
        return conn
    except Exception as e:
        print(f"WARNUNG: Backup-Datenbank ({backup_host}) ebenfalls nicht erreichbar: {e}")

    LAST_DB_STATUS = "OFFLINE"
    return None

def get_write_connections():
    """Verbindet für Schreibvorgänge mit Aktiv-DB und (als Backup-Kopie) mit Passiv-DB."""
    global LAST_DB_STATUS
    primary_host = os.getenv("DB_HOST", "db")
    backup_host = os.getenv("DB_BACKUP_HOST", "db_backup")
    conns = []
    primary_ok = False
    backup_ok = False

    try:
        conns.append(_connect_single(primary_host))
        primary_ok = True
    except Exception as e:
        print(f"WARNUNG: Schreiben auf Hauptdatenbank ({primary_host}) fehlgeschlagen: {e}")

    try:
        conns.append(_connect_single(backup_host))
        backup_ok = True
    except Exception as e:
        print(f"WARNUNG: Schreiben auf Backup-Datenbank ({backup_host}) fehlgeschlagen: {e}")

    if primary_ok:
        LAST_DB_STATUS = "PRIMARY"
    elif backup_ok:
        LAST_DB_STATUS = "BACKUP"
    else:
        LAST_DB_STATUS = "OFFLINE"

    return conns

def get_db_status():
    """Prüft aktiv den aktuellen Datenbank-Status für die Anzeige in der Web-App."""
    conn = get_read_connection()
    if conn:
        conn.close()
    return LAST_DB_STATUS

def create_database():
    conns = get_write_connections()
    for conn in conns:
        conn.close()

def schueler_anlegen(vorname, nachname, geburtsdatum):
    conns = get_write_connections()
    if not conns:
        return None

    schueler_id = None
    for conn in conns:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM schueler WHERE vorname=%s AND nachname=%s AND geburtsdatum=%s",
                (vorname, nachname, geburtsdatum)
            )
            vorhanden = cursor.fetchone()
            if vorhanden:
                if schueler_id is None:
                    schueler_id = vorhanden[0]
            else:
                cursor.execute(
                    "INSERT INTO schueler (vorname, nachname, geburtsdatum) VALUES (%s, %s, %s) RETURNING id",
                    (vorname, nachname, geburtsdatum)
                )
                neue_id = cursor.fetchone()[0]
                if schueler_id is None:
                    schueler_id = neue_id
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Fehler in schueler_anlegen: {e}")
        finally:
            conn.close()

    return schueler_id

def berechnung_speichern(
    schueler_id,
    deutsch5, mathe5, englisch5, nawi5, gewi5, kunst5, musik5, sport5,
    deutsch6, mathe6, englisch6, nawi6, gewi6, kunst6, musik6, sport6,
    durchschnitt, hauptfachsumme, ergebnis
):
    if schueler_id is None:
        return False

    conns = get_write_connections()
    if not conns:
        return False

    for conn in conns:
        try:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO berechnungen (
                schueler_id,
                deutsch5, mathe5, englisch5, nawi5, gewi5, kunst5, musik5, sport5,
                deutsch6, mathe6, englisch6, nawi6, gewi6, kunst6, musik6, sport6,
                durchschnitt, hauptfachsumme, ergebnis
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s
            )
            """, (
                schueler_id,
                deutsch5, mathe5, englisch5, nawi5, gewi5, kunst5, musik5, sport5,
                deutsch6, mathe6, englisch6, nawi6, gewi6, kunst6, musik6, sport6,
                durchschnitt, hauptfachsumme, ergebnis
            ))
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Fehler in berechnung_speichern: {e}")
        finally:
            conn.close()
    return True

def alle_schueler():
    conn = get_read_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT s.id, s.vorname, s.nachname, s.geburtsdatum, COUNT(b.id)
        FROM schueler s
        LEFT JOIN berechnungen b ON s.id = b.schueler_id
        GROUP BY s.id
        ORDER BY s.id
        """)
        daten = cursor.fetchall()
        cursor.close()
        return daten
    except Exception:
        return []
    finally:
        conn.close()

def alle_berechnungen():
    conn = get_read_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM berechnungen")
        daten = cursor.fetchall()
        cursor.close()
        return daten
    except Exception:
        return []
    finally:
        conn.close()

def berechnungen_von_schueler(schueler_id):
    if schueler_id is None:
        return []
    conn = get_read_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT durchschnitt, hauptfachsumme, ergebnis
        FROM berechnungen
        WHERE schueler_id=%s
        ORDER BY id DESC
        """, (schueler_id,))
        daten = cursor.fetchall()
        cursor.close()
        return daten
    except Exception:
        return []
    finally:
        conn.close()

def aktualisiere_schueler(schueler_id, vorname, nachname, geburtsdatum):
    conns = get_write_connections()
    for conn in conns:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE schueler SET vorname=%s, nachname=%s, geburtsdatum=%s WHERE id=%s",
                (vorname, nachname, geburtsdatum, schueler_id)
            )
            conn.commit()
            cursor.close()
        except Exception:
            pass
        finally:
            conn.close()

def hole_schueler(schueler_id):
    conn = get_read_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schueler WHERE id=%s", (schueler_id,))
        daten = cursor.fetchone()
        cursor.close()
        return daten
    except Exception:
        return None
    finally:
        conn.close()

def hole_letzte_berechnung(schueler_id):
    conn = get_read_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM berechnungen WHERE schueler_id=%s ORDER BY id DESC LIMIT 1",
            (schueler_id,)
        )
        daten = cursor.fetchone()
        cursor.close()
        return daten
    except Exception:
        return None
    finally:
        conn.close()

def aktualisiere_noten(
    schueler_id,
    deutsch5, mathe5, englisch5, nawi5, gewi5, kunst5, musik5, sport5,
    deutsch6, mathe6, englisch6, nawi6, gewi6, kunst6, musik6, sport6,
    durchschnitt, hauptfachsumme, ergebnis
):
    conns = get_write_connections()
    for conn in conns:
        try:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE berechnungen SET
                deutsch5=%s, mathe5=%s, englisch5=%s, nawi5=%s,
                gewi5=%s, kunst5=%s, musik5=%s, sport5=%s,
                deutsch6=%s, mathe6=%s, englisch6=%s, nawi6=%s,
                gewi6=%s, kunst6=%s, musik6=%s, sport6=%s,
                durchschnitt=%s, hauptfachsumme=%s, ergebnis=%s
            WHERE schueler_id=%s
            """, (
                deutsch5, mathe5, englisch5, nawi5, gewi5, kunst5, musik5, sport5,
                deutsch6, mathe6, englisch6, nawi6, gewi6, kunst6, musik6, sport6,
                durchschnitt, hauptfachsumme, ergebnis, schueler_id
            ))
            conn.commit()
            cursor.close()
        except Exception:
            pass
        finally:
            conn.close()

def loesche_schueler(schueler_id):
    conns = get_write_connections()
    for conn in conns:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM berechnungen WHERE schueler_id=%s", (schueler_id,))
            cursor.execute("DELETE FROM schueler WHERE id=%s", (schueler_id,))
            conn.commit()
            cursor.close()
        except Exception:
            pass
        finally:
            conn.close()

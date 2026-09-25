import psycopg2

import os

import time




def wait_for_db():


    while True:

        try:

            conn = psycopg2.connect(

                host=os.getenv("DB_HOST", "db"),

                database=os.getenv("DB_NAME", "gymnasium"),

                user=os.getenv("DB_USER", "postgres"),

                password=os.getenv("DB_PASSWORD", "geheim")

            )


            conn.close()


            print("✅ PostgreSQL bereit")


            break


        except Exception as e:


            print("⏳ Warte auf PostgreSQL...")


            time.sleep(3




def get_connection():

    return psycopg2.connect(

        host=os.getenv("DB_HOST", "db"),

        database=os.getenv("DB_NAME", "gymnasium"),

        user=os.getenv("DB_USER", "postgres"),

        password=os.getenv("DB_PASSWORD", "geheim")

    )




def create_database():


    conn = get_connection()

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


        deutsch5 INTEGER,

        mathe5 INTEGER,

        englisch5 INTEGER,

        nawi5 INTEGER,

        gewi5 INTEGER,

        kunst5 INTEGER,

        musik5 INTEGER,

        sport5 INTEGER,


        deutsch6 INTEGER,

        mathe6 INTEGER,

        englisch6 INTEGER,

        nawi6 INTEGER,

        gewi6 INTEGER,

        kunst6 INTEGER,

        musik6 INTEGER,

        sport6 INTEGER,


        durchschnitt NUMERIC(4,2),

        hauptfachsumme INTEGER,

        ergebnis TEXT

    )

    """)


    conn.commit()

    cursor.close()

    conn.close()




def schueler_anlegen(vorname, nachname, geburtsdatum):


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""

    SELECT id

    FROM schueler

    WHERE vorname=%s

    AND nachname=%s

    AND geburtsdatum=%s

    """,

    (

        vorname,

        nachname,

        geburtsdatum

    ))


    vorhandener_schueler = cursor.fetchone()
    if vorhandener_schueler:

        conn.close()

        return vorhandener_schueler[0]

    cursor.execute("""

    INSERT INTO schueler

    (vorname,nachname,geburtsdatum)

    VALUES (%s,%s,%s)

    RETURNING id

    """,

    (

        vorname,

        nachname,

        geburtsdatum

    ))


    schueler_id = cursor.fetchone()[0]

    conn.commit()

    conn.close()

    return schueler_id

def berechnung_speichern(

    schueler_id,

    deutsch5,

    mathe5,

    englisch5,

    nawi5,

    gewi5,

    kunst5,

    musik5,

    sport5,

    deutsch6,

    mathe6,

    englisch6,

    nawi6,

    gewi6,

    kunst6,

    musik6,

    sport6,

    durchschnitt,

    hauptfachsumme,

    ergebnis

):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO berechnungen (

        schueler_id,

        deutsch5,

        mathe5,

        englisch5,

        nawi5,

        gewi5,

        kunst5,

        musik5,

        sport5,

        deutsch6,

        mathe6,

        englisch6,

        nawi6,

        gewi6,

        kunst6,

        musik6,

        sport6,

        durchschnitt,

        hauptfachsumme,

        ergebnis

    )

    VALUES (

        %s,%s,%s,%s,%s,%s,%s,%s,%s,

        %s,%s,%s,%s,%s,%s,%s,%s,

        %s,%s,%s

    )

    """,

    (

        schueler_id,

        deutsch5,

        mathe5,

        englisch5,

        nawi5,

        gewi5,

        kunst5,

        musik5,

        sport5,

        deutsch6,

        mathe6,

        englisch6,

        nawi6,

        gewi6,

        kunst6,

        musik6,

        sport6,

        durchschnitt,

        hauptfachsumme,

        ergebnis

    ))
    conn.commit()
    conn.close()

def alle_schueler():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

        s.id,

        s.vorname,

        s.nachname,

        s.geburtsdatum,

        COUNT(b.id)

    FROM schueler s

    LEFT JOIN berechnungen b

    ON s.id = b.schueler_id

    GROUP BY s.id

    ORDER BY s.id

    """)

    daten = cursor.fetchall()

    conn.close()

    return daten


def alle_berechnungen():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM berechnungen

    """)

    daten = cursor.fetchall()

    conn.close()

    return daten

def berechnungen_von_schueler(schueler_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

        durchschnitt,

        hauptfachsumme,

        ergebnis

    FROM berechnungen

    WHERE schueler_id=%s

    ORDER BY id DESC

    """, (schueler_id,))

    daten = cursor.fetchall()

    conn.close()

    return daten

def aktualisiere_schueler(

    schueler_id,

    vorname,

    nachname,

    geburtsdatum

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    UPDATE schueler

    SET vorname=%s,

        nachname=%s,

        geburtsdatum=%s

    WHERE id=%s

    """,

    (

        vorname,

        nachname,

        geburtsdatum,

        schueler_id

    ))

    conn.commit()

    conn.close()

def hole_schueler(schueler_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM schueler

    WHERE id=%s

    """, (schueler_id,))

    daten = cursor.fetchone()

    conn.close()

    return daten

def hole_letzte_berechnung(schueler_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM berechnungen

    WHERE schueler_id=%s

    ORDER BY id DESC

    LIMIT 1

    """, (schueler_id,))

    daten = cursor.fetchone()

    conn.close()

    return daten

def aktualisiere_noten(

    schueler_id,

    deutsch5,

    mathe5,

    englisch5,

    nawi5,

    gewi5,

    kunst5,

    musik5,

    sport5,

    deutsch6,

    mathe6,

    englisch6,

    nawi6,

    gewi6,

    kunst6,

    musik6,

    sport6,

    durchschnitt,

    hauptfachsumme,

    ergebnis

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    UPDATE berechnungen

    SET

        deutsch5=%s,

        mathe5=%s,

        englisch5=%s,

        nawi5=%s,

        gewi5=%s,

        kunst5=%s,

        musik5=%s,

        sport5=%s,

        deutsch6=%s,

        mathe6=%s,

        englisch6=%s,

        nawi6=%s,

        gewi6=%s,

        kunst6=%s,

        musik6=%s,

        sport6=%s,

        durchschnitt=%s,

        hauptfachsumme=%s,

        ergebnis=%s

    WHERE schueler_id=%s

    """,

    (

        deutsch5,

        mathe5,

        englisch5,

        nawi5,

        gewi5,

        kunst5,

        musik5,

        sport5,

        deutsch6,

        mathe6,

        englisch6,

        nawi6,

        gewi6,

        kunst6,

        musik6,

        sport6,

        durchschnitt,

        hauptfachsumme,

        ergebnis,

        schueler_id

    ))
    conn.commit()
    conn.close()

def loesche_schueler(schueler_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    DELETE FROM berechnungen

    WHERE schueler_id=%s

    """, (schueler_id,))

    cursor.execute("""

    DELETE FROM schueler

    WHERE id=%s

    """, (schueler_id,))

    conn.commit()
    conn.close()

wait_for_db()
create_database()
from flask import Flask, render_template, request, redirect
from database import (
    create_database,
    get_db_status,
    schueler_anlegen,
    berechnung_speichern,
    alle_schueler,
    berechnungen_von_schueler,
    hole_schueler,
    aktualisiere_schueler,
    loesche_schueler,
    aktualisiere_noten,
    hole_letzte_berechnung
)

app = Flask(__name__)

# Tabellen beim Start anlegen, falls mindestens eine DB erreichbar ist (ohne Absturz bei Ausfall)
create_database()

class GymnasiumRechner:
    def __init__(self, vorname, nachname,
                 deutsch5, mathe5, englisch5, nawi5, gewi5, kunst5, musik5, sport5,
                 deutsch6, mathe6, englisch6, nawi6, gewi6, kunst6, musik6, sport6):
        self.vorname = vorname
        self.nachname = nachname
        self.deutsch5 = deutsch5
        self.mathe5 = mathe5
        self.englisch5 = englisch5
        self.nawi5 = nawi5
        self.gewi5 = gewi5
        self.kunst5 = kunst5
        self.musik5 = musik5
        self.sport5 = sport5
        self.deutsch6 = deutsch6
        self.mathe6 = mathe6
        self.englisch6 = englisch6
        self.nawi6 = nawi6
        self.gewi6 = gewi6
        self.kunst6 = kunst6
        self.musik6 = musik6
        self.sport6 = sport6

    def berechne_durchschnitt(self):
        gewichtete_summe = (
            self.deutsch5 * 2 +
            self.mathe5 * 2 +
            self.englisch5 * 2 +
            self.nawi5 * 2 +
            self.gewi5 * 2 +
            self.kunst5 +
            self.musik5 +
            self.sport5 +
            self.deutsch6 * 2 +
            self.mathe6 * 2 +
            self.englisch6 * 2 +
            self.nawi6 * 2 +
            self.gewi6 * 2 +
            self.kunst6 +
            self.musik6 +
            self.sport6
        )
        return round(gewichtete_summe / 26, 2)

    def berechne_hauptfachsumme(self):
        return (
            self.deutsch5 +
            self.mathe5 +
            self.englisch5 +
            self.deutsch6 +
            self.mathe6 +
            self.englisch6
        )

    def pruefe_empfehlung(self):
        hauptfachsumme = self.berechne_hauptfachsumme()
        if hauptfachsumme <= 14:
            return "Gymnasialempfehlung erhalten"
        return "Probeunterricht erforderlich"

@app.route("/loeschen/<int:schueler_id>")
def loeschen(schueler_id):
    loesche_schueler(schueler_id)
    return redirect("/")

@app.route("/bearbeiten/<int:schueler_id>", methods=["GET", "POST"])
def bearbeiten(schueler_id):
    if request.method == "POST":
        aktualisiere_schueler(
            schueler_id,
            request.form["vorname"],
            request.form["nachname"],
            request.form["geburtsdatum"]
        )
        rechner = GymnasiumRechner(
            request.form["vorname"],
            request.form["nachname"],
            int(request.form["deutsch5"]),
            int(request.form["mathe5"]),
            int(request.form["englisch5"]),
            int(request.form["nawi5"]),
            int(request.form["gewi5"]),
            int(request.form["kunst5"]),
            int(request.form["musik5"]),
            int(request.form["sport5"]),
            int(request.form["deutsch6"]),
            int(request.form["mathe6"]),
            int(request.form["englisch6"]),
            int(request.form["nawi6"]),
            int(request.form["gewi6"]),
            int(request.form["kunst6"]),
            int(request.form["musik6"]),
            int(request.form["sport6"])
        )
        durchschnitt = rechner.berechne_durchschnitt()
        hauptfachsumme = rechner.berechne_hauptfachsumme()
        ergebnis = rechner.pruefe_empfehlung()
        aktualisiere_noten(
            schueler_id,
            int(request.form["deutsch5"]),
            int(request.form["mathe5"]),
            int(request.form["englisch5"]),
            int(request.form["nawi5"]),
            int(request.form["gewi5"]),
            int(request.form["kunst5"]),
            int(request.form["musik5"]),
            int(request.form["sport5"]),
            int(request.form["deutsch6"]),
            int(request.form["mathe6"]),
            int(request.form["englisch6"]),
            int(request.form["nawi6"]),
            int(request.form["gewi6"]),
            int(request.form["kunst6"]),
            int(request.form["musik6"]),
            int(request.form["sport6"]),
            durchschnitt,
            hauptfachsumme,
            ergebnis
        )
        return redirect(f"/bearbeiten/{schueler_id}")

    daten = hole_schueler(schueler_id)
    if not daten:
        return redirect("/")
    noten = hole_letzte_berechnung(schueler_id)
    return render_template(
        "bearbeiten.html",
        schueler=daten,
        noten=noten,
    )

@app.route("/", methods=["GET", "POST"])
def startseite():
    durchschnitt = None
    hauptfachsumme = None
    empfehlung = None
    alle_versuche = []
    schueler_id = None

    if request.method == "POST":
        schueler = GymnasiumRechner(
            request.form["vorname"],
            request.form["nachname"],
            int(request.form["deutsch5"]),
            int(request.form["mathe5"]),
            int(request.form["englisch5"]),
            int(request.form["nawi5"]),
            int(request.form["gewi5"]),
            int(request.form["kunst5"]),
            int(request.form["musik5"]),
            int(request.form["sport5"]),
            int(request.form["deutsch6"]),
            int(request.form["mathe6"]),
            int(request.form["englisch6"]),
            int(request.form["nawi6"]),
            int(request.form["gewi6"]),
            int(request.form["kunst6"]),
            int(request.form["musik6"]),
            int(request.form["sport6"])
        )

        durchschnitt = schueler.berechne_durchschnitt()
        hauptfachsumme = schueler.berechne_hauptfachsumme()
        empfehlung = schueler.pruefe_empfehlung()

        schueler_id = schueler_anlegen(
            request.form["vorname"],
            request.form["nachname"],
            request.form["geburtsdatum"]
        )

        berechnung_speichern(
            schueler_id,
            schueler.deutsch5,
            schueler.mathe5,
            schueler.englisch5,
            schueler.nawi5,
            schueler.gewi5,
            schueler.kunst5,
            schueler.musik5,
            schueler.sport5,
            schueler.deutsch6,
            schueler.mathe6,
            schueler.englisch6,
            schueler.nawi6,
            schueler.gewi6,
            schueler.kunst6,
            schueler.musik6,
            schueler.sport6,
            durchschnitt,
            hauptfachsumme,
            empfehlung
        )

        alle_versuche = berechnungen_von_schueler(schueler_id)
        db_status = get_db_status()
    else:
        db_status = get_db_status()

    return render_template(
        "index.html",
        durchschnitt=durchschnitt,
        hauptfachsumme=hauptfachsumme,
        empfehlung=empfehlung,
        versuche=alle_versuche,
        schueler_id=schueler_id,
        db_status=db_status
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )

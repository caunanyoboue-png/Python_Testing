import json
from flask import Flask, render_template, request, redirect, flash, url_for, render_template_string


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['GET', 'POST'])
def showSummary():
    if request.method == 'POST':
        email = request.form['email']
        club = [club for club in clubs if club['email'] == email][0]
    else:
        # Si l'utilisateur arrive via "Back to competitions" (GET), on peut garder le dernier club connecté
        club = clubs[0]  # ⚠️ Tu peux plus tard remplacer par la session de l'utilisateur connecté

    return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)



@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Quelque chose s'est mal passé - veuillez réessayer.")
        # passer la liste des clubs aussi
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form.get('competition')), None)
    club = next((c for c in clubs if c['name'] == request.form.get('club')), None)

    try:
        placesRequired = int(request.form.get('places', 0))
    except (ValueError, TypeError):
        flash("Nombre de places invalide.")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

    if club is None or competition is None:
        flash("Quelque chose s'est mal passé - veuillez réessayer.")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

    if placesRequired <= 0:
        flash("Le nombre de places doit être positif.")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

    if placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places par club.")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

    club_points = int(club.get('points', 0))
    available_places = int(competition.get('numberOfPlaces', 0))

    if placesRequired > club_points:
        flash("Impossible de réserver plus de places que vos points disponibles.")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

    if placesRequired > available_places:
        flash("Pas assez de places disponibles dans la compétition.")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

    # --- MISE À JOUR DES DONNÉES ---
    club['points'] = club_points - placesRequired
    competition['numberOfPlaces'] = available_places - placesRequired

    # --- SAUVEGARDE dans clubs.json ---
    try:
        with open('clubs.json', 'w') as f:
            json.dump({'clubs': clubs}, f, indent=4)
    except Exception as e:
        flash(f"Erreur de sauvegarde : {e}")

    flash('Réservation réussie !')
    return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

# route pour afficher la page récapitulative des points
@app.route('/points')
def points():
    # Génère un tableau HTML simple récapitulant les points de chaque club
    table_rows = "".join(
        f"<tr><td>{club.get('name')}</td><td style='text-align:right'>{club.get('points')}</td></tr>"
        for club in clubs
    )
    html = f"""
    <!doctype html>
    <html lang="fr">
      <head>
        <meta charset="utf-8">
        <title>Récapitulatif des points</title>
        <style>
          table {{ border-collapse: collapse; width: 50%; margin: 20px 0; }}
          th, td {{ border: 1px solid #ccc; padding: 8px; }}
          th {{ background: #f0f0f0; text-align: left; }}
        </style>
      </head>
      <body>
        <h1>Récapitulatif des points par club</h1>
        <table>
          <thead>
            <tr><th>Club</th><th>Points</th></tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
        <p><a href="{url_for('index')}">Retour à l'accueil</a></p>
      </body>
    </html>
    """
    return render_template_string(html)
@app.route('/clubs_data')
def clubs_data():
    with open('clubs.json') as f:
        data = json.load(f)
    return data


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/clubs_data')
def clubs_data():
    with open('clubs.json') as f:
        data = json.load(f)
    return data


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

    # validation et conversion
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

    # Limite maximale : pas plus de 12 places par club (par réservation)
    if placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places par club.")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

    # Vérifier que le club a assez de points
    try:
        club_points = int(club.get('points', 0))
    except (ValueError, TypeError):
        club_points = 0

    if placesRequired > club_points:
        flash("Impossible de réserver plus de places que vos points disponibles.")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

    # Vérifier qu'il y a assez de places dans la compétition
    try:
        available_places = int(competition.get('numberOfPlaces', 0))
    except (ValueError, TypeError):
        available_places = 0

    if placesRequired > available_places:
        flash("Pas assez de places disponibles dans la compétition.")
        return render_template('welcome.html', club=club, competitions=competitions, clubs=clubs)

    # effectuer la réservation : décrémenter points et places
    club['points'] = club_points - placesRequired
    competition['numberOfPlaces'] = available_places - placesRequired

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


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

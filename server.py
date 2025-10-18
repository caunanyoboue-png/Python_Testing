import json
from flask import Flask, render_template, request, redirect, flash, url_for


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


@app.route('/showSummary', methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Quelque chose s'est mal passé - veuillez réessayer.")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form.get('competition')), None)
    club = next((c for c in clubs if c['name'] == request.form.get('club')), None)

    # validation et conversion
    try:
        placesRequired = int(request.form.get('places', 0))
    except (ValueError, TypeError):
        flash("Nombre de places invalide.")
        return render_template('welcome.html', club=club, competitions=competitions)

    if club is None or competition is None:
        flash("Quelque chose s'est mal passé - veuillez réessayer.")
        return render_template('welcome.html', club=club, competitions=competitions)

    if placesRequired <= 0:
        flash("Le nombre de places doit être positif.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérifier que le club a assez de points
    try:
        club_points = int(club.get('points', 0))
    except (ValueError, TypeError):
        club_points = 0

    if placesRequired > club_points:
        flash("Impossible de réserver plus de places que vos points disponibles.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # Vérifier qu'il y a assez de places dans la compétition
    try:
        available_places = int(competition.get('numberOfPlaces', 0))
    except (ValueError, TypeError):
        available_places = 0

    if placesRequired > available_places:
        flash("Pas assez de places disponibles dans la compétition.")
        return render_template('welcome.html', club=club, competitions=competitions)

    # effectuer la réservation : décrémenter points et places
    club['points'] = club_points - placesRequired
    competition['numberOfPlaces'] = available_places - placesRequired

    flash('Réservation réussie !')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
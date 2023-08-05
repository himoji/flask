from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Note
import json
from sqlalchemy.sql import text

views = Blueprint('views', __name__)
 


"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    money = db.Column(db.Integer)
"""

"""class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))"""

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/question', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 
        answer = request.form.get('answer')#Gets the note from the HTML 
        bounty = int(request.form.get('bounty'))#Gets the note from the HTML 

        if len(note) < 1 and answer.lower() in "yes no":
            flash('Question is too short or answer is not corrent!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id, answer=answer, bounty=bounty)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash(f'Question added!, {note} : {answer} : {bounty}', category='success')

    return render_template("question.html", user=current_user)


@views.route('/info', methods=['GET', 'POST'])
@login_required
def info():
    return render_template("info.html", user=current_user)

@views.route('/bonus', methods=['GET', 'POST'])
@login_required
def bonus():
    return render_template("bonus.html", user=current_user)


@views.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST': 
        money = request.form.get('money')

        try:
            if int(money) < 1:
                flash("You can't deposit this amount of money!", category="error")
        except:
            flash("You need to enter a valid integer!", category='error')

        money = int(money)
        
        user_id = current_user.id
        try:
            current_user.money += money
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        flash(f'Success, your account is {current_user.money}', category='success')

    return render_template("deposit.html", user=current_user)

@views.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST': 
        money = request.form.get('money')

        try:
            if int(money) < 1:
                flash("You can't withdraw this amount of money!", category="error")
        except:
            flash("You need to enter a valid integer!", category='error')

        money = int(money)

        try:
            current_user.money -= money
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        flash(f'Success, your account is {current_user.money}', category='success')
            
    return render_template("withdraw.html", user=current_user)

"""@views.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    if request.method == 'POST': 
        money = request.form.get('money')
        taker_id = request.form.get('id')

        try:
            if int(money) < 1:
                flash("You can't send this amount of money!", category="error")
            elif int(taker_id) < 1:
                flash("Taker's ID is invalid!", category='error')
        except:
            flash("You need to enter a valid integer!", category='error')

        money = int(money)
        taker_id = int(taker_id)
        
        user_id = current_user.id
        try:                                    TODO: find out how to change money at taker
            current_user.money -= money

            db.session.commit()
        except Exception as e:
            db.session.rollback()

        flash(f'Success, your account is {current_user.money}', category='success')
            
    return render_template("send.html", user=current_user)"""


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/answer-question', methods=['GET', 'POST'])
@login_required
def answer_question():
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    answer = note['noteAnswer']
    
    print(noteId, answer)

    try:
        bounty = int(db.session.query(Note.bounty).filter_by(id=noteId).first()[0])
        if db.session.query(Note.answer).filter_by(id=noteId).first()[0] == answer: #get Note answer by its id and check if its right
            print("curr ", current_user.money, current_user.money + bounty)
            current_user.money += bounty
            print("curr ", current_user.money)
            db.session.commit()
            
    except Exception as e:
        print("rollback", e)

    return jsonify({})


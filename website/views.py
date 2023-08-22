from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Note, User, Transaction
import json

views = Blueprint('views', __name__)
 
FEE = 0.05

def get_first_name_by_id(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    if user:
        return user.first_name
    return None


def get_transactions_for_user(user_id):
    transactions = db.session.query(Transaction).filter_by(user_id=user_id).all()
    taker_transactions = db.session.query(Transaction).filter_by(taker_id=user_id).all()
    all_transactions = transactions + taker_transactions
    all_transactions.sort(key=lambda x: x.date)
    return all_transactions

def add_transaction(user_id, taker_id, money, ttype, user_name, taker_name):
    new_transaction = Transaction(user_id=user_id, taker_id=taker_id, money=money, ttype=ttype, user_name=user_name, taker_name=taker_name)
    db.session.add(new_transaction)
    db.session.commit()

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

            last_user = db.session.query(User).order_by(User.id.desc()).first()
            last_user_id = last_user.id if last_user else None
            print(last_user_id)

            for i in range(1, last_user_id+1): 
                new_note = Note(data=note, user_id=i, answer=answer, bounty=bounty)  #providing the schema for the note 
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
        money = request.form.get('total_amount')

        try:
            if int(money) < 1:
                flash(f"You can't deposit this amount of money!", category="error")
        except:
            flash(f"You need to enter a valid integer!", category='error')

        money = int(money)
        
        try:
            add_transaction(current_user.id, 0, round(money*FEE), "Deposit", current_user.first_name, '') #hardcode
            current_user.money += money - round(money*FEE)
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        flash(f'Success, your account is {current_user.money}, Fee is {FEE*100}%', category='success')

    return render_template("deposit.html", user=current_user)

@views.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST': 
        money = request.form.get('money')

        try:
            if int(money) < 1:
                flash(f"You can't withdraw this amount of money!", category="error")
        except:
            flash(f"You need to enter a valid integer!", category='error')

        money = int(money)

        try:
            if current_user.money - money - round(money*FEE) < 0:
                flash(f"You don't have enough money! Fee is {FEE*100}%", category="error")
                return render_template("withdraw.html", user=current_user)
            
            current_user.money -= money - round(money*FEE)
            add_transaction(current_user.id, 0, round(money*FEE), "Withdraw", current_user.first_name, '')
            db.session.commit()
        except Exception as e:
            db.session.rollback()

        flash(f'Success, your account is {current_user.money}', category='success')
            
    return render_template("withdraw.html", user=current_user)

@views.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    if request.method == 'POST': 
        money = request.form.get('money')
        taker_id = request.form.get('id')

        try:
            if int(money) < 1:
                flash(f"You can't send this amount of money!", category="error")
            elif int(taker_id) < 1:
                flash(f"Taker's ID is invalid!", category='error')
            elif int(taker_id) == current_user.id:
                flash(f"You can't transfer money to yourself!", category='error')
        except:
            flash(f"You need to enter a valid integer!", category='error')

        money = int(money)
        taker_id = int(taker_id)

        try:       
            if current_user.money - money - round(money*FEE) < 0:
                flash(f"You don't have enough money! Fee is {FEE*100}%", category="error")
                return render_template("send.html", user=current_user)
            
            current_user.money -= money - round(money*FEE)

            user = db.session.query(User).get(taker_id)

            if user:
                user.money += money - round(money*FEE)
                add_transaction(current_user.id, taker_id, round(money - money*FEE), "Transfer", current_user.first_name, get_first_name_by_id(taker_id))

                flash(f"Transfered with success! Fee is {FEE*100}%", category="success")
            else:
                flash(f"User was not found!", category="error")
            
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()

        flash(f'Success, your account is {current_user.money}', category='success')
            
    return render_template("send.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    all_users = db.session.query(User).all()
    for user in all_users:

        notes_to_delete = user.notes

        for noteIter in notes_to_delete:
            #print(noteIter==note, noteIter, note, user, note)
            if noteIter.data == note.data:
                db.session.delete(noteIter)
                
                db.session.commit()

    return jsonify({})


@views.route('/answer-question', methods=['GET', 'POST'])
@login_required
def answer_question():
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    answer = note['noteAnswer']
    note = Note.query.get(noteId)
    print(noteId, answer)

    try:
        bounty = int(db.session.query(Note.bounty).filter_by(id=noteId).first()[0])
        answered_questions = json.loads(current_user.answered) if current_user.answered else []

        if noteId not in answered_questions:

            if db.session.query(Note.answer).filter_by(id=noteId).first()[0] == answer: #get Note answer by its id and check if its right

                current_user.money += bounty - round(bounty*FEE)
                answered_questions.append(noteId)
                current_user.answered = json.dumps(answered_questions)


                db.session.delete(note)
                db.session.commit()
                add_transaction(current_user.id, 0, round(bounty - bounty*FEE), "Quiz", current_user.first_name, '')
                flash(f"Correct! You got {round(bounty-bounty*FEE)}$, fee is {FEE*100}%", category="success")
                
    except Exception as e:
        print("rollback", e)

    return jsonify({})

@views.route('/history', methods=['GET', 'POST'])
@login_required
def transaction_history(): #thistory
    user_transactions = get_transactions_for_user(current_user.id)
    return render_template('thistory.html', user_transactions=user_transactions, user=current_user)



import json

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '$€cR3LK3y__1234'
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 300000

jwt = JWTManager(app)

db = SQLAlchemy(app)

# DEFAULT VALUES
DEFAULT_BALANCE = 500
DEFAULT_CURRENCY = "XOF"

# USER MODEL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Integer)

# TRANSACTION MODEL
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    transaction_status = db.Column(db.String)
    sent_at = db.Column(db.Date, default=datetime.datetime.utcnow)


# Create tables in the database
with app.app_context():
    db.create_all()


def create_jwt_token(payload):
    return create_access_token(payload)

def getUserFullnameById(id):
    return User.query.get(id).fullname

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    fullname = data.get('fullname')
    phone = data.get('phone')
    password = data.get('password')

    # Check if phone number is unique
    if User.query.filter_by(phone=phone) is None:
        return jsonify({'message': 'Phone number already registered'}), 400

    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2', salt_length=16)

    new_user = User(fullname=fullname, phone=phone, password=hashed_password, balance=DEFAULT_BALANCE)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Phone number already registered'}), 400


@app.route('/login', methods=['POST'])
def login():

    data = request.json
    phone = data.get('phone')
    password = data.get('password')

    user = User.query.filter_by(phone=phone).first()

    if user and check_password_hash(user.password, password):
        # Code is correct, generate JWT token
        payload = {
            'id': user.id,
            'fullname': user.fullname,
            'phone': user.phone
        }
        access_token = create_jwt_token(payload)
        payload['access_token'] = access_token
        return jsonify(payload), 200
    else:
        return jsonify({'message': 'Invalid phone number or password'}), 401

@app.route('/transactions', methods=['GET'])
@jwt_required()
def getUserTransactions():
    current_user = get_jwt_identity()

    transactions = (Transaction.query.order_by(Transaction.id.desc()).filter(or_(Transaction.sender_id == current_user["id"], Transaction.receiver_id == current_user["id"]),).all())
    # Convert the query result to a serializable format
    serializable_transactions = [
        {
            'id': transaction.id,
            'amount': f"{'-' if transaction.sender_id == current_user['id'] else '+'}{transaction.amount} {DEFAULT_CURRENCY}",
            'message': f"A {getUserFullnameById(transaction.receiver_id)}" if transaction.sender_id == current_user["id"] else f"De {getUserFullnameById(transaction.sender_id)}",
            'sent_at': transaction.sent_at.isoformat(),  # Convert datetime to string
        }
        for transaction in transactions
    ]
    return jsonify(serializable_transactions), 200


@app.route('/transaction', methods=['POST'])
@jwt_required()
def createTransactions():
    data = request.json
    current_user = get_jwt_identity()

    sender_id = current_user["id"]
    receiver_id = data.get('receiver_id')
    amount = int(data.get('amount'))

    # Debit sender balance
    sender_balance = User.query.get(sender_id)

    # Credit receiver balance
    receiver_balance = User.query.get(receiver_id)

    if int(sender_balance.balance) >= amount:
        sender_balance.balance -= amount
        receiver_balance.balance += amount

        # Transactions tracking
        new_transaction = Transaction(sender_id=sender_id, receiver_id=receiver_id, amount=amount, transaction_status="SUCCED")
        try:

            db.session.add(new_transaction)
            db.session.commit()
            return jsonify({'message': 'Money sent successfully'}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'An error occured'}), 400
    else:
        return jsonify({'message': 'Insufficient balance'}), 400

@app.route('/balance', methods=['GET'])
@jwt_required()
def getBalance():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    return jsonify({'user_id': current_user['id'],'balance': f'{user.balance} {DEFAULT_CURRENCY}'}), 200

if __name__ == '__main__':
    app.run(debug=False)

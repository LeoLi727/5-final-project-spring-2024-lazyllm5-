from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.getenv('SECRET_KEY', 'a_very_secret_fallback_key')

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:123456@mongodb:27017/mydatabase")
client = MongoClient(mongo_uri, tls=True, tlsAllowInvalidCertificates=True)
db = client['BudgetTracker']
users = db.users
transactions = db.transactions

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Flask-Bcrypt setup
bcrypt = Bcrypt(app)

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = str(user_id)
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user['_id']), user['username'])
    return None

@app.route('/')
@login_required
def home():
    user_transactions = transactions.find({'user_id': current_user.id})
    return render_template('home.html', transactions=list(user_transactions))

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('_flashes', None)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({"username": username})
        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(str(user['_id']), username)
            login_user(user_obj)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Clear all flash messages
    session.pop('_flashes', None)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(db, users, users.find_one({"username": username}))
        user_exists = users.find_one({"username": username})
        if user_exists:
            flash('Username already exists', 'error')
            print("here")
            #return redirect(url_for('register'))
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            users.insert_one({"username": username, "password": hashed_password})
            flash('Registration successful', 'success')
            #return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add-transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        item_name = request.form['item_name']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        transactions.insert_one({
            'item_name': item_name,
            'amount': amount,
            'category': category,
            'date': date,
            'user_id': current_user.id
        })
        return redirect(url_for('home'))
    return render_template('add_transaction.html')


@app.route('/edit-transaction/<transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = transactions.find_one({'_id': ObjectId(transaction_id), 'user_id': current_user.id})
    if request.method == 'POST':
        item_name = request.form.get('item_name')  # Capture the item name from the form
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        date = request.form.get('date')

        # Update the transaction document with new values
        updated_transaction = {
            'item_name': item_name,
            'amount': amount,
            'category': category,
            'date': date
        }
        transactions.update_one({'_id': ObjectId(transaction_id)}, {'$set': updated_transaction})
        flash('Transaction updated successfully.')
        return redirect(url_for('home'))

    return render_template('edit_transaction.html', transaction=transaction)


@app.route('/delete-transaction/<transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transactions.delete_one({'_id': ObjectId(transaction_id), 'user_id': current_user.id})
    flash('Transaction deleted successfully.')
    # Redirect back to the page the user came from
    referrer = request.headers.get("Referer")
    return redirect(referrer or url_for('home'))
    

@app.route('/detailed-spending-summary')
@login_required
def detailed_spending_summary():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', type=int)  # Optional month selection

    # Define the start and end of the period based on user selection
    if year and month:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month+1, 1) if month < 12 else datetime(year+1, 1, 1)
    else:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year+1, 1, 1)

    # Adjust the aggregation to limit by the selected period
    summary = list(transactions.aggregate([
        {'$match': {
            'user_id': current_user.id,
            'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lt': end_date.strftime('%Y-%m-%d')}
        }},
        {'$group': {'_id': '$category', 'total': {'$sum': '$amount'}}},
        {'$sort': {'total': -1}}
    ]))

    total = sum(item['total'] for item in summary)  # Calculate the total spent in the selected period

    user_transactions = transactions.find({
        'user_id': current_user.id,
        'date': {'$gte': start_date.strftime('%Y-%m-%d'), '$lt': end_date.strftime('%Y-%m-%d')}
    })

    return render_template('detailed_spending_summary.html', summary=summary, total=total, now=datetime.now(), transactions=list(user_transactions))



@app.route('/spending-summary')
@login_required
def spending_summary():
        # Define the pipeline for weekly aggregation
    weekly_pipeline = [
        {'$match': {'user_id': current_user.id}},
        {'$group': {
            '_id': {
                'year': {'$year': {'$toDate': '$date'}},
                'week': {'$week': {'$toDate': '$date'}}
            },
            'total': {'$sum': '$amount'}
        }},
        {'$sort': {'_id.year': -1, '_id.week': -1}}
    ]

    # Define the pipeline for monthly aggregation
    monthly_pipeline = [
        {'$match': {'user_id': current_user.id}},
        {'$group': {
            '_id': {
                'year': {'$year': {'$toDate': '$date'}},
                'month': {'$month': {'$toDate': '$date'}}
            },
            'total': {'$sum': '$amount'}
        }},
        {'$sort': {'_id.year': -1, '_id.month': -1}}
    ]

    # Define the pipeline for yearly aggregation
    yearly_pipeline = [
        {'$match': {'user_id': current_user.id}},
        {'$group': {
            '_id': {
                'year': {'$year': {'$toDate': '$date'}}
            },
            'total': {'$sum': '$amount'}
        }},
        {'$sort': {'_id.year': -1}}
    ]

    # Execute the aggregation queries
    db = client['BudgetTracker']
    weekly_spending = list(db.transactions.aggregate(weekly_pipeline))
    monthly_spending = list(db.transactions.aggregate(monthly_pipeline))
    yearly_spending = list(db.transactions.aggregate(yearly_pipeline))

    return render_template('spending_summary.html',
                           weekly_spending=weekly_spending,
                           monthly_spending=monthly_spending,
                           yearly_spending=yearly_spending)

if __name__ == '__main__':
    app.run(debug=True)

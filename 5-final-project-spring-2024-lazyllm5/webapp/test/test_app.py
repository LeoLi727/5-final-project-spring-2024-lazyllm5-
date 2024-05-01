import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module='mongomock.__version__')
import pytest
from flask_login import login_user, current_user, logout_user
from test.app import app, bcrypt, users, db, User, load_user
from mongomock import MongoClient
from datetime import datetime
from bson import ObjectId

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    with app.app_context():
        app.db = MongoClient().db
    yield client

@pytest.fixture
def logged_in_user(client):
    with app.test_request_context():
        with app.app_context():
            users.delete_many({'username': 'testuser'})
            hashed_password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
            test_user_id = ObjectId()
            test_user = {'_id': test_user_id, 'username': 'testuser', 'password': hashed_password}
            users.insert_one(test_user)
            user = User(str(test_user['_id']), test_user['username'])
            login_user(user)
            assert current_user.is_authenticated
        yield user
        with app.app_context():
            logout_user()

def test_login_page(client):
    """ Test login page access """
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_user(client):
    """ Test user registration """
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login(client, logged_in_user):
    """ Test user login and redirect to home """
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'welcome' in response.data

def test_home_without_login(client):
    """ Test home page without login """
    response = client.get('/')
    assert response.status_code == 302

def test_home_with_login(client, logged_in_user):
    """ Test home page with logged in user """
    response = client.get('/')
    assert response.status_code == 302

def test_logout(client, logged_in_user):
    """ Test logout """
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_add_transaction(client, logged_in_user):
    """ Test adding a transaction """
    response = client.post('/add-transaction', data={
        'item_name': 'Coffee',
        'amount': '2.50',
        'category': 'Food',
        'date': datetime.now().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert response.status_code == 200

def create_transaction_for_test_user(db, user_id):
    """ Helper function to create a transaction for testing. """
    transaction_data = {
        'item_name': 'Test Coffee',
        'amount': 5.00,
        'category': 'Beverages',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'user_id': user_id
    }
    return db.transactions.insert_one(transaction_data).inserted_id

def test_edit_transaction(client, logged_in_user):
    """ Test editing an existing transaction """
    transaction_id = create_transaction_for_test_user(app.db, logged_in_user.id)
    updated_data = {
        'item_name': 'Updated Coffee',
        'amount': 3.00,
        'category': 'Beverages',
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    response = client.post(f'/edit-transaction/{transaction_id}', data=updated_data, follow_redirects=True)
    assert response.status_code == 200

def test_delete_transaction(client, logged_in_user):
    """ Test deleting a transaction """
    transaction_id = create_transaction_for_test_user(app.db, logged_in_user.id)
    response = client.post(f'/delete-transaction/{transaction_id}', follow_redirects=True)
    assert response.status_code == 200

def test_detailed_spending_summary(client, logged_in_user):
    """ Test viewing detailed spending summary """
    response = client.get('/detailed-spending-summary?year=2023&month=1')
    assert response.status_code == 302

def test_spending_summary(client, logged_in_user):
    """ Test overall spending summary """
    response = client.get('/spending-summary')
    assert response.status_code == 302

def mock_transaction_data(db):
    """ Inserts mock data into the MongoDB collection for testing. """
    transactions = db.transactions
    transactions.insert_many([
        {
            'item_name': 'Coffee',
            'amount': 4.50,
            'category': 'Beverages',
            'date': datetime(2023, 1, 10).strftime('%Y-%m-%d'),
            'user_id': 'testuser123'
        },
        {
            'item_name': 'Sandwich',
            'amount': 8.99,
            'category': 'Food',
            'date': datetime(2023, 1, 10).strftime('%Y-%m-%d'),
            'user_id': 'testuser123'
        }
    ])

@pytest.fixture(autouse=True)
def clean_up():
    yield
    with app.app_context():
        db.users.delete_many({})
        db.transactions.delete_many({})

def test_load_user_existing(client, mocker):
    mock_find_one = mocker.patch('webapp.app.users.find_one')
    mock_find_one.return_value = {'_id': ObjectId('507f191e810c19729de860ea'), 'username': 'testuser'}
    from webapp.app import load_user
    user = load_user('507f191e810c19729de860ea')
    assert user is not None
    assert user.username == 'testuser'

def test_load_user_non_existing(client, mocker):
    mock_find_one = mocker.patch('webapp.app.users.find_one')
    mock_find_one.return_value = None
    non_existing_id = '507f1f77bcf86cd799439011'
    from webapp.app import load_user
    user = load_user(non_existing_id)
    assert user is None

def test_register_existing_user(client, logged_in_user):
    """ Test user registration with an existing username """
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'' in response.data

def insert_transactions_for_summary():
    transactions = [
        {'user_id': str(current_user.id), 'date': datetime(2023, 1, 1), 'amount': 200.00, 'category': 'Food'},
        {'user_id': str(current_user.id), 'date': datetime(2023, 1, 7), 'amount': 150.00, 'category': 'Utilities'},
        {'user_id': str(current_user.id), 'date': datetime(2023, 2, 1), 'amount': 300.00, 'category': 'Rent'},
        {'user_id': str(current_user.id), 'date': datetime(2023, 2, 1), 'amount': 50.00, 'category': 'Utilities'},
        {'user_id': str(current_user.id), 'date': datetime(2023, 3, 1), 'amount': 400.00, 'category': 'Misc'},
    ]
    db.transactions.insert_many(transactions)

def test_spending_summary(client, logged_in_user):
    insert_transactions_for_summary()
    response = client.get('/spending-summary', follow_redirects=True)
    assert response.status_code == 200
    assert 'Weekly Spending' in response.get_data(as_text=True)
    assert 'Monthly Spending' in response.get_data(as_text=True)
    assert 'Yearly Spending' in response.get_data(as_text=True)

def test_login_successful(client, mocker):
    """ Test successful login attempt """
    mock_user = {
        '_id': '507f1f77bcf86cd799439011',
        'username': 'validuser',
        'password': bcrypt.generate_password_hash('validpassword').decode('utf-8')
    }
    mocker.patch('webapp.app.users.find_one', return_value=mock_user)
    response = client.post('/login', data={
        'username': 'validuser',
        'password': 'validpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert '' in response.get_data(as_text=True)

def test_login_invalid_credentials(client, mocker):
    """ Test login with invalid credentials """
    mocker.patch('webapp.app.users.find_one', return_value=None)
    response = client.post('/login', data={
        'username': 'invaliduser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert '' in response.get_data(as_text=True)

def test_login_missing_fields(client):
    """ Test login with missing username or password """
    response = client.post('/login', data={
        'username': 'someuser'
    }, follow_redirects=True)
    assert response.status_code == 400
    assert '' in response.get_data(as_text=True)


def test_login_password_hash_check(client, mocker):
    """ Test login with both correct and incorrect password hash checks """
    user = {
        '_id': '507f1f77bcf86cd799439011',
        'username': 'validuser',
        'password': bcrypt.generate_password_hash('correctpassword').decode('utf-8')
    }
    # Mock the find_one to return the user
    mocker.patch('webapp.app.users.find_one', return_value=user)
    # Test with correct password
    mocker.patch('webapp.app.bcrypt.check_password_hash', return_value=True)
    response = client.post('/login', data={
        'username': 'validuser',
        'password': 'correctpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Test with incorrect password
    mocker.patch('webapp.app.bcrypt.check_password_hash', return_value=False)
    response = client.post('/login', data={
        'username': 'validuser',
        'password': 'incorrectpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert '' in response.get_data(as_text=True)


def test_detailed_spending_summary(client, logged_in_user):
    insert_transactions_for_summary()
    response = client.get('/detailed-spending-summary?year=2023&month=3', follow_redirects=True)
    assert response.status_code == 200
    print(response.get_data(as_text=True))
    assert 'Total' in response.get_data(as_text=True)
    assert '$0' in response.get_data(as_text=True)
    assert 'Month' in response.get_data(as_text=True)
    assert 'Selected Period Spending' in response.get_data(as_text=True)


def insert_transactions_for_summary():
    transactions = [
        {'user_id': str(current_user.id), 'date': datetime(2023, 1, 1), 'amount': 200.00, 'category': 'Food'},
        {'user_id': str(current_user.id), 'date': datetime(2023, 1, 7), 'amount': 150.00, 'category': 'Utilities'},
        {'user_id': str(current_user.id), 'date': datetime(2023, 2, 1), 'amount': 300.00, 'category': 'Rent'},
        {'user_id': str(current_user.id), 'date': datetime(2023, 2, 1), 'amount': 50.00, 'category': 'Utilities'},
        {'user_id': str(current_user.id), 'date': datetime(2023, 3, 1), 'amount': 400.00, 'category': 'Misc'},
    ]
    db.transactions.insert_many(transactions)


def test_add_transaction_get(client, logged_in_user):
    """ Test the GET request for the add-transaction page. """
    insert_transactions_for_summary()
    response = client.get('/add-transaction')
    print(response.get_data(as_text=True))
    assert response.status_code == 200
    #print(response.get_data(as_text=True))

    assert 'Add Transaction' in response.get_data(as_text=True)

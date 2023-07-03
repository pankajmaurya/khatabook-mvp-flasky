from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask import flash
from datetime import datetime
from datetime import timedelta
from random import randint

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///khata.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# User model for SQLAlchemy
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(10), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# User loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the KhataEntry model
class KhataEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    farmer_name = db.Column(db.String(100), nullable=False)
    crop_kind = db.Column(db.String(100), nullable=False)
    locality = db.Column(db.String(100), nullable=False)
    farm_area = db.Column(db.Float, nullable=False)
    billed_amount = db.Column(db.Float, nullable=False)
    date_of_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"KhataEntry(id={self.id}, lender_id={self.lender_id},farmer_name='{self.farmer_name}', crop_kind='{self.crop_kind}', " \
               f"locality='{self.locality}', farm_area={self.farm_area}, billed_amount={self.billed_amount}, " \
               f"date_of_activity='{self.date_of_activity}')"


# Define the Payment model
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    khata_entry_id = db.Column(db.Integer, db.ForeignKey('khata_entry.id'), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"Payment(id={self.id}, lender_id={self.lender_id},khata_entry_id={self.khata_entry_id}, payment_date='{self.payment_date}', " \
               f"amount={self.amount}, notes='{self.notes}')"

# Home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')

        user = User.query.filter_by(phone_number=phone_number).first()
        if user and user.verify_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('error.html', error_message='Invalid phone number or password')
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Dashboard - Show khata entries in the last 7 days and summary
@login_required
@app.route('/dashboard')
def dashboard():
    print("current user id " + str(current_user.id))
    entries = KhataEntry.query.filter_by(lender_id=current_user.id).all()
    
    # Calculate grand total of billed amounts and payments received
    billed_total = sum(entry.billed_amount for entry in entries)
    payments_total = sum(entry.amount for entry in Payment.query.filter_by(lender_id=current_user.id).all())

    balance = billed_total - payments_total

    # Render only the khata entries in the last 7 days
    # seven_days_ago = datetime.utcnow() - timedelta(days=7)
    return render_template('dashboard.html', user_id=current_user.id, name=current_user.name, entries=entries, billed_total=billed_total, payments_total=payments_total, balance=balance)

# Add a khata entry
@login_required
@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        lender_id = current_user.id
        farmer_name = request.form.get('farmer_name')
        crop_kind = request.form.get('crop_kind')
        locality = request.form.get('locality')
        farm_area = float(request.form.get('farm_area'))
        billed_amount = float(request.form.get('billed_amount'))
        date_of_activity = datetime.strptime(request.form.get('date_of_activity'), '%Y-%m-%d')

        entry = KhataEntry(lender_id=lender_id, farmer_name=farmer_name, crop_kind=crop_kind, locality=locality, farm_area=farm_area,
                           billed_amount=billed_amount, date_of_activity=date_of_activity)
        db.session.add(entry)
        db.session.commit()
        flash('Khata entry added successfully.')

        return redirect('/dashboard')

    return render_template('add_entry.html')


# Edit a khata entry
@login_required
@app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = KhataEntry.query.get_or_404(entry_id)

    if request.method == 'POST':
        entry.farmer_name = request.form.get('farmer_name')
        entry.crop_kind = request.form.get('crop_kind')
        entry.locality = request.form.get('locality')
        entry.farm_area = float(request.form.get('farm_area'))
        entry.billed_amount = float(request.form.get('billed_amount'))

        db.session.commit()
        flash('Khata entry updated successfully.')

        return redirect('/dashboard')

    return render_template('edit_entry.html', entry=entry)


# Delete a khata entry
@login_required
@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = KhataEntry.query.get_or_404(entry_id)

    db.session.delete(entry)
    db.session.commit()
    flash('Khata entry deleted successfully.')

    return redirect('/dashboard')


# Mark a payment received against a borrower farmer
@login_required
@app.route('/mark_payment/<int:entry_id>', methods=['GET', 'POST'])
def mark_payment(entry_id):
    entry = KhataEntry.query.get_or_404(entry_id)

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        notes = request.form.get('notes')

        payment = Payment(khata_entry_id=entry.id, lender_id=current_user.id, amount=amount, notes=notes)
        db.session.add(payment)
        db.session.commit()
        flash('Payment marked successfully.')

        return redirect('/dashboard')

    return render_template('mark_payment.html', entry=entry)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        name = request.form.get('name')
        password = request.form.get('password')

        existing_user = User.query.filter_by(phone_number=phone_number).first()
        if existing_user:
            return 'Phone number already exists'

        new_user = User(phone_number=phone_number, name=name)
        new_user.password = password  # Set the password (hashing is done automatically)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('dashboard'))
    else:
        return render_template('register.html')
    
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

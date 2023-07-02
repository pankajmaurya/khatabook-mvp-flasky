from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from datetime import timedelta
from random import randint

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to your own secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///khata.db'  # SQLite database file
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Define the KhataEntry model
class KhataEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farmer_name = db.Column(db.String(100), nullable=False)
    crop_kind = db.Column(db.String(100), nullable=False)
    locality = db.Column(db.String(100), nullable=False)
    farm_area = db.Column(db.Float, nullable=False)
    billed_amount = db.Column(db.Float, nullable=False)
    date_of_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"KhataEntry(id={self.id}, farmer_name='{self.farmer_name}', crop_kind='{self.crop_kind}', " \
               f"locality='{self.locality}', farm_area={self.farm_area}, billed_amount={self.billed_amount}, " \
               f"date_of_activity='{self.date_of_activity}')"


# Define the Payment model
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    khata_entry_id = db.Column(db.Integer, db.ForeignKey('khata_entry.id'), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"Payment(id={self.id}, khata_entry_id={self.khata_entry_id}, payment_date='{self.payment_date}', " \
               f"amount={self.amount}, notes='{self.notes}')"


# Home page
@app.route('/')
def home():
    return render_template('index.html')


# OTP-based login or username/password-based authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        otp = request.form.get('otp')

        # Check login credentials
        # if username == 'admin' and password == 'admin' and otp == str(randint(1000, 9999)):
        if username == 'admin' and password == 'admin' and otp == "8888":
            # Successful login
            return redirect('/dashboard')
        else:
            flash('Invalid login credentials.')
    
    return render_template('login.html')


# Dashboard - Show khata entries in the last 7 days and summary
@app.route('/dashboard')
def dashboard():
    # Get khata entries in the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    entries = KhataEntry.query.filter(KhataEntry.date_of_activity >= seven_days_ago).all()
    
    # Calculate grand total of billed amounts and payments received
    # This is not what we want, we want a billed total and payments total not based on the 7 days filter but 
    # for all entries.
    billed_total = sum(entry.billed_amount for entry in entries)
    payments_total = sum(entry.amount for entry in Payment.query.all())
    
    return render_template('dashboard.html', entries=entries, billed_total=billed_total, payments_total=payments_total)


# Add a khata entry
@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        farmer_name = request.form.get('farmer_name')
        crop_kind = request.form.get('crop_kind')
        locality = request.form.get('locality')
        farm_area = float(request.form.get('farm_area'))
        billed_amount = float(request.form.get('billed_amount'))

        entry = KhataEntry(farmer_name=farmer_name, crop_kind=crop_kind, locality=locality, farm_area=farm_area,
                           billed_amount=billed_amount)
        db.session.add(entry)
        db.session.commit()
        flash('Khata entry added successfully.')

        return redirect('/dashboard')

    return render_template('add_entry.html')


# Edit a khata entry
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
@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = KhataEntry.query.get_or_404(entry_id)

    db.session.delete(entry)
    db.session.commit()
    flash('Khata entry deleted successfully.')

    return redirect('/dashboard')


# Mark a payment received against a lender farmer
@app.route('/mark_payment/<int:entry_id>', methods=['GET', 'POST'])
def mark_payment(entry_id):
    entry = KhataEntry.query.get_or_404(entry_id)

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        notes = request.form.get('notes')

        payment = Payment(khata_entry_id=entry.id, amount=amount, notes=notes)
        db.session.add(payment)
        db.session.commit()
        flash('Payment marked successfully.')

        return redirect('/dashboard')

    return render_template('mark_payment.html', entry=entry)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

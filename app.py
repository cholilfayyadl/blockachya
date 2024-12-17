from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta

from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MongoDB setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client.blockachya

# Flask-Bcrypt setup
bcrypt = Bcrypt(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(id=str(user["_id"]), email=user["email"])
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        fullname = request.form['fullname']  # Ambil nama lengkap dari form
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        # Cek apakah email sudah terdaftar
        if db.users.find_one({"email": email}):
            flash("Email already registered.", "danger")
            return redirect(url_for('register'))
        
        # Simpan data pengguna ke database
        db.users.insert_one({
            "email": email,
            "full_name": fullname,  # Simpan nama lengkap ke database
            "password": password,
            "coins": 100  # Set default coin balance
        })
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.users.find_one({"email": email})

        if user and bcrypt.check_password_hash(user["password"], password):
            login_user(User(id=str(user["_id"]), email=user["email"]))
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))

        flash("Invalid email or password.", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_data = db.users.find_one({"email": current_user.email})
    return render_template('dashboard.html', user=user_data)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_email = request.form['email']
        new_fullname = request.form['fullname']

        # Update data pengguna di database
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"email": new_email, "full_name": new_fullname}}
        )
        
        flash("Profile updated successfully!", "success")
        return redirect(url_for('dashboard'))

    # Ambil data pengguna untuk ditampilkan di form
    user_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    return render_template('edit_profile.html', user=user_data)


@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        # Ambil data dari form
        recipient_email = request.form['recipient_email']
        amount = request.form.get('amount', type=int)
        password = request.form['password']
        note = request.form.get('note', '')  # Catatan opsional

        # Validasi jumlah transfer
        if amount <= 0:
            flash("Invalid amount. Please enter a positive value.", "danger")
            return redirect(url_for('transfer'))

        # Ambil data pengguna pengirim dan penerima dari database
        sender = db.users.find_one({"_id": ObjectId(current_user.id)})
        recipient = db.users.find_one({"email": recipient_email})

        # Validasi kata sandi pengguna
        if not bcrypt.check_password_hash(sender['password'], password):
            flash("Invalid password. Please try again.", "danger")
            return redirect(url_for('transfer'))

        # Validasi penerima
        if not recipient:
            flash("Recipient not found.", "danger")
            return redirect(url_for('transfer'))

        # Validasi saldo
        if sender["coins"] < amount:
            flash("Insufficient balance.", "danger")
            return redirect(url_for('transfer'))

        # Proses transfer
        db.users.update_one({"_id": ObjectId(sender["_id"])}, {"$inc": {"coins": -amount}})
        db.users.update_one({"_id": recipient["_id"]}, {"$inc": {"coins": amount}})

        # Log transaksi dengan catatan
        db.transactions.insert_one({
            "sender_id": sender["_id"],
            "recipient_id": recipient["_id"],
            "amount": amount,
            "note": note,  # Simpan catatan dalam log transaksi
            "type": "transfer",
            "date": datetime.utcnow(),
        })

        flash(f"Successfully transferred {amount} coins to {recipient_email}.", "success")
        return redirect(url_for('dashboard'))

    return render_template('transfer.html')


@app.route('/mutasi', methods=['GET'])
@login_required
def mutasi():
    # Get filter values
    filter_type = request.args.get('filter', 'daily')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Default filter
    query = {}
    now = datetime.utcnow()

    if filter_type == 'daily':
        query = {"date": {"$gte": now.replace(hour=0, minute=0, second=0, microsecond=0)}}
    elif filter_type == 'monthly':
        query = {"date": {"$gte": now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)}}
    elif filter_type == 'yearly':
        query = {"date": {"$gte": now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)}}
    elif filter_type == 'custom' and start_date and end_date:
        try:
            start_date_parsed = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_parsed = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            query = {"date": {"$gte": start_date_parsed, "$lte": end_date_parsed}}
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for('mutasi'))

    # Fetch transactions
    transactions = list(db.transactions.find({
        "$or": [
            {"sender_id": ObjectId(current_user.id)},
            {"recipient_id": ObjectId(current_user.id)}
        ],
        **query
    }))

    # Calculate coin in and coin out
    total_coin_keluar = sum(t['amount'] for t in transactions if t.get("sender_id") == ObjectId(current_user.id))
    total_coin_masuk = sum(t['amount'] for t in transactions if t.get("recipient_id") == ObjectId(current_user.id))

    # Fetch user's total coins
    user_data = db.users.find_one({"_id": ObjectId(current_user.id)})
    total_koin_dimiliki = user_data.get("coins", 0) if user_data else 0

    # Prepare data for template
    mutasi_list = []
    for t in transactions:
        if t.get("sender_id") == ObjectId(current_user.id):
            transaction_type = "Coin Keluar"
            detail = f"To: {db.users.find_one({'_id': t['recipient_id']})['email']}"
        else:
            transaction_type = "Coin Masuk"
            detail = f"From: {db.users.find_one({'_id': t['sender_id']})['email']}"
        
        mutasi_list.append({
            "date": t["date"].strftime('%Y-%m-%d %H:%M:%S'),
            "type": transaction_type,
            "amount": t["amount"],
            "note": t.get("note", "-"),  # Tampilkan catatan jika ada
            "detail": detail
        })

    return render_template('mutasi.html', 
                           mutasi_list=mutasi_list,
                           total_coin_keluar=total_coin_keluar,
                           total_coin_masuk=total_coin_masuk,
                           total_koin_dimiliki=total_koin_dimiliki,  # Pass user's total coins
                           selected_filter=filter_type,
                           start_date=start_date, 
                           end_date=end_date)

@app.route('/topup', methods=['GET', 'POST'])
@login_required
def topup():
    if request.method == 'POST':
        # Ambil jumlah yang diminta
        amount = request.form.get('amount', type=int)
        
        if amount <= 0:
            flash("Invalid amount. Please enter a positive value.", "danger")
            return redirect(url_for('topup'))
        
        # Simpan permintaan ke database
        db.topups.insert_one({
            "user_id": ObjectId(current_user.id),
            "amount": amount,
            "status": "pending",
            "created_at": datetime.utcnow()
        })

        flash(f"Top-up request for {amount} coins created successfully!", "success")
        return redirect(url_for('topup'))

    # Tampilkan halaman form
    return render_template('topup.html')

@app.route('/topup_requests', methods=['GET'])
@login_required
def topup_requests():
    # Ambil semua permintaan top-up yang belum selesai
    pending_topups = list(db.topups.find({"status": "pending"}))

    # Tambahkan detail pengguna ke dalam data
    for topup in pending_topups:
        user = db.users.find_one({"_id": topup["user_id"]})
        topup["user_email"] = user["email"] if user else "Unknown"
    
    return render_template('topup_requests.html', topups=pending_topups)

@app.route('/fulfill_topup/<topup_id>', methods=['POST'])
@login_required
def fulfill_topup(topup_id):
    # Cari permintaan top-up
    topup = db.topups.find_one({"_id": ObjectId(topup_id), "status": "pending"})
    if not topup:
        flash("Top-up request not found or already fulfilled.", "danger")
        return redirect(url_for('topup_requests'))

    # Validasi apakah pengguna memiliki cukup koin
    fulfiller = db.users.find_one({"_id": ObjectId(current_user.id)})
    if fulfiller["coins"] < topup["amount"]:
        flash("Insufficient coins to fulfill this request.", "danger")
        return redirect(url_for('topup_requests'))

    # Ambil data pengguna yang meminta top-up
    requester = db.users.find_one({"_id": topup["user_id"]})
    if not requester:
        flash("Requester not found.", "danger")
        return redirect(url_for('topup_requests'))

    # Update koin kedua pengguna
    db.users.update_one({"_id": ObjectId(fulfiller["_id"])}, {"$inc": {"coins": -topup["amount"]}})
    db.users.update_one({"_id": ObjectId(requester["_id"])}, {"$inc": {"coins": topup["amount"]}})
    
    # Tandai top-up sebagai selesai
    db.topups.update_one({"_id": ObjectId(topup["_id"])}, {"$set": {"status": "completed"}})

    flash(f"You have successfully fulfilled a top-up of {topup['amount']} coins for {requester['email']}.", "success")
    return redirect(url_for('topup_requests'))




if __name__ == '__main__':
    app.run(debug=True)

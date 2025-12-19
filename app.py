from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "kunci_rahasia_stqa_2025"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_pos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user') 

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(10)) 
    category = db.Column(db.String(20))
    stock = db.Column(db.Integer, default=0)

class Promo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    subtotal = db.Column(db.Integer)
    promo_info = db.Column(db.String(100))
    total = db.Column(db.Integer) 
    amount_paid = db.Column(db.Integer) 
    change = db.Column(db.Integer)
    cashier_name = db.Column(db.String(50))

temp_carts = {} 

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()

# --- ROUTES ---
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'kasir':
        return render_template('index.html', products=Product.query.all(), user=session['username'])
    elif role == 'user':
        return '''
        <script>
            alert("Anda login sebagai user biasa. Mohon hubungi admin untuk akses kasir!");
            window.location.href = "/login";
        </script>
        '''
    else:
        return '''
        <script>
            alert("Role Anda belum ditentukan oleh admin!");
            window.location.href = "/login";
        </script>
        '''

@app.route('/login')
def login_page(): 
    return render_template('auth.html')

@app.route('/signup')
def signup_page(): 
    return render_template('signup.html')

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin': 
        return redirect(url_for('index'))
    prods = Product.query.all()
    promos = Promo.query.all()
    today = date.today()
    histories = Transaction.query.filter(db.func.date(Transaction.timestamp) == today).all()
    total_revenue = sum(h.total for h in histories)
    return render_template('admin.html', products=prods, promos=promos, histories=histories, revenue=total_revenue)

@app.route('/roles')
def role_management():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('role.html', users=users)

# --- API AUTH ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    u = data.get('username', '').strip()
    p = data.get('password', '').strip()
    cp = data.get('confirm_password', '').strip()

    if not u or not p or not cp:
        return jsonify({"message": "Input kosong!"}), 400
    if len(p) < 6:
        return jsonify({"message": "Password minimal 6 karakter"}), 400
    if p != cp:
        return jsonify({"message": "Password dan konfirmasi tidak sama"}), 400
    if User.query.filter_by(username=u).first():
        return jsonify({"message": "Username sudah ada!"}), 400
    
    db.session.add(User(username=u, password=generate_password_hash(p), role='user'))
    db.session.commit()
    return jsonify({"message": "Signup Berhasil"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and check_password_hash(user.password, data.get('password')):
        session['username'], session['role'] = user.username, user.role
        return jsonify({"message": "Login Sukses", "role": user.role}), 200
    return jsonify({"message": "Username/Password salah!"}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# --- API KASIR & PROMO ---
@app.route('/api/cart', methods=['GET'])
def get_cart():
    user = session.get('username')
    cart = temp_carts.get(user, {})
    items, total = [], 0
    for p_id, qty in cart.items():
        p = Product.query.get(int(p_id))
        if p:
            sub = p.price * qty
            items.append({"id": p.id, "name": p.name, "price": p.price, "quantity": qty, "subtotal": sub})
            total += sub
    return jsonify({"items": items, "total": total})

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    p_id, user = str(request.json.get('product_id')), session['username']
    product = Product.query.get(int(p_id))
    if user not in temp_carts: temp_carts[user] = {}
    curr = temp_carts[user].get(p_id, 0)
    if product and product.stock > curr:
        temp_carts[user][p_id] = curr + 1
        return jsonify({"success": True})
    return jsonify({"error": "Stok tidak cukup"}), 400

@app.route('/api/cart/reduce', methods=['POST'])
def reduce_from_cart():
    p_id, user = str(request.json.get('product_id')), session.get('username')
    if user in temp_carts and p_id in temp_carts[user]:
        if temp_carts[user][p_id] > 1: temp_carts[user][p_id] -= 1
        else: del temp_carts[user][p_id]
        return jsonify({"success": True})
    return jsonify({"error": "Item tidak ditemukan"}), 404

@app.route('/api/promos')
def get_promos():
    return jsonify([{"code": p.code, "discount": p.discount_percent} for p in Promo.query.all()])

@app.route('/api/checkout', methods=['POST'])
def checkout():
    user = session.get('username')
    cart = temp_carts.get(user, {})
    data = request.json
    paid, promo_code = data.get('amount_paid'), data.get('promo_code')
    if not cart: return jsonify({"message": "Keranjang kosong"}), 400

    subtotal = sum(Product.query.get(int(pid)).price * qty for pid, qty in cart.items())
    disc_val, promo_text = 0, "-"

    if promo_code:
        p_obj = Promo.query.filter_by(code=promo_code).first()
        if p_obj:
            disc_val = int(subtotal * (p_obj.discount_percent / 100))
            promo_text = f"{p_obj.code} ({p_obj.discount_percent}%)"

    final = subtotal - disc_val
    if not paid or int(paid) < final: return jsonify({"message": "Uang tunai kurang"}), 400

    change = int(paid) - final
    for pid, qty in cart.items(): Product.query.get(int(pid)).stock -= qty

    new_tx = Transaction(
        subtotal=subtotal,
        promo_info=promo_text,
        total=final,
        amount_paid=int(paid),
        change=change,
        cashier_name=user
    )
    db.session.add(new_tx)
    db.session.commit()
    temp_carts[user] = {}
    return jsonify({"status": "SUCCESS", "change": change, "discount": disc_val})

@app.route('/api/history')
def get_user_history():
    user = session.get('username')
    hists = Transaction.query.filter_by(cashier_name=user).order_by(Transaction.timestamp.desc()).all()
    return jsonify([{
        "time": h.timestamp.strftime('%Y-%m-%d %H:%M'),
        "subtotal": h.subtotal,
        "promo": h.promo_info,
        "total": h.total,
        "paid": h.amount_paid,
        "change": h.change
    } for h in hists])

# --- API ADMIN ---
@app.route('/api/admin/add_product', methods=['POST'])
def add_product():
    if session.get('role') != 'admin': return jsonify({"error":"Unauthorized"}), 403
    d = request.json
    db.session.add(Product(name=d['name'], price=d['price'], img=d['img'], category=d['category'], stock=d['stock']))
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/admin/delete_product', methods=['POST'])
def delete_product():
    if session.get('role') != 'admin': return jsonify({"error":"Unauthorized"}), 403
    p = Product.query.get(request.json['id'])
    if p:
        db.session.delete(p)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Gagal"}), 404

@app.route('/api/admin/update_stock', methods=['POST'])
def update_stock():
    if session.get('role') != 'admin': return jsonify({"error":"Unauthorized"}), 403
    p = Product.query.get(request.json['id'])
    new_stk = request.json.get('new_stock', 0)
    if new_stk < 0:
        return jsonify({"error": "Stok tidak boleh kurang dari 0"}), 400
    p.stock = new_stk
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/admin/add_promo', methods=['POST'])
def add_promo():
    if session.get('role') != 'admin': return jsonify({"error":"Unauthorized"}), 403
    d = request.json
    db.session.add(Promo(code=d['code'].upper(), discount_percent=d['discount']))
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/admin/delete_promo', methods=['POST'])
def delete_promo():
    if session.get('role') != 'admin': return jsonify({"error":"Unauthorized"}), 403
    p = Promo.query.get(request.json['id'])
    if p:
        db.session.delete(p)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Gagal"}), 404

# --- API ROLE MANAGEMENT ---
@app.route('/api/admin/set_role', methods=['POST'])
def set_role():
    if session.get('role') != 'admin': return jsonify({"error":"Unauthorized"}), 403
    data = request.json
    user = User.query.get(data.get('user_id'))
    new_role = data.get('role')
    if user:
        user.role = new_role
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "User tidak ditemukan"}), 404

if __name__ == '__main__':
    app.run(debug=True)

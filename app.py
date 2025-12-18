from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = "kunci_rahasia_stqa_2025" 

# --- 1. DATA PRODUK (Ditambahkan Kategori) ---
products = {
    "1": {"id": "1", "name": "Kopi Espresso", "price": 15000, "img": "☕", "category": "minuman"},
    "2": {"id": "2", "name": "Roti Bakar", "price": 12000, "img": "🍞", "category": "makanan"},
    "3": {"id": "3", "name": "Teh Manis", "price": 5000, "img": "🍵", "category": "minuman"},
    "4": {"id": "4", "name": "Sandwich", "price": 25000, "img": "🥪", "category": "makanan"},
    "5": {"id": "5", "name": "Nasi Goreng", "price": 20000, "img": "🍳", "category": "makanan"},
    "6": {"id": "6", "name": "Mie Ayam", "price": 15000, "img": "🍜", "category": "makanan"},
    "7": {"id": "7", "name": "Bakso Sapi", "price": 18000, "img": "🥣", "category": "makanan"},
    "8": {"id": "8", "name": "Sate Ayam", "price": 25000, "img": "🍢", "category": "makanan"},
    "9": {"id": "9", "name": "Ayam Geprek", "price": 17000, "img": "🍗", "category": "makanan"},
    "10": {"id": "10", "name": "Jus Jeruk", "price": 10000, "img": "🍊", "category": "minuman"},
    "11": {"id": "11", "name": "Es Teh", "price": 5000, "img": "🧊", "category": "minuman"},
    "12": {"id": "12", "name": "Soda Gembira", "price": 12000, "img": "🥤", "category": "minuman"},
    "13": {"id": "13", "name": "Pisang Goreng", "price": 10000, "img": "🍌", "category": "makanan"},
    "14": {"id": "14", "name": "Kentang Goreng", "price": 15000, "img": "🍟", "category": "makanan"}
}

# --- 2. DATA PROMO ---
PROMO_CODES = {"HEMAT10": 0.10, "MERDEKA20": 0.20}

# --- 3. DATABASE MOCK (In-Memory) ---
users = {"admin": "admin123"} 
user_carts = {}    
user_histories = {} 

# --- 4. ROUTE HALAMAN ---
@app.route('/')
def index():
    if 'username' not in session:
        return render_template('auth.html')
    return render_template('index.html', products=products, user=session['username'])

# --- 5. API AUTHENTICATION ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"message": "Username dan Password tidak boleh kosong!"}), 400
    if username in users:
        return jsonify({"message": "Username sudah terdaftar!"}), 400
        
    users[username] = password
    user_carts[username] = {}
    user_histories[username] = []
    return jsonify({"message": "Signup Berhasil, silakan Login"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"message": "Username dan Password wajib diisi!"}), 400
    
    if users.get(username) == password:
        session['username'] = username
        if username not in user_carts: user_carts[username] = {}
        if username not in user_histories: user_histories[username] = []
        return jsonify({"message": "Login Sukses"}), 200
        
    return jsonify({"message": "Username atau Password salah!"}), 401

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# --- 6. API KERANJANG ---
@app.route('/api/cart', methods=['GET'])
def get_cart():
    user = session.get('username')
    if not user: return jsonify({"error": "Unauthorized"}), 401
    
    cart = user_carts.get(user, {})
    details = []
    total = 0
    for p_id, qty in cart.items():
        p = products[p_id]
        subtotal = p['price'] * qty
        details.append({"id": p_id, "name": p['name'], "price": p['price'], "quantity": qty, "subtotal": subtotal})
        total += subtotal
    return jsonify({"items": details, "total": total})

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    user = session.get('username')
    if not user: return jsonify({"error": "Unauthorized"}), 401
    
    p_id = request.json.get('product_id')
    if p_id in products:
        user_carts[user][p_id] = user_carts[user].get(p_id, 0) + 1
        return jsonify({"success": True}), 200
    return jsonify({"error": "Produk tidak ditemukan"}), 404

@app.route('/api/cart/reduce', methods=['POST'])
def reduce_from_cart():
    user = session.get('username')
    if not user: return jsonify({"error": "Unauthorized"}), 401
    
    p_id = request.json.get('product_id')
    cart = user_carts[user]
    if p_id in cart:
        if cart[p_id] > 1: cart[p_id] -= 1
        else: cart.pop(p_id)
        return jsonify({"success": True}), 200
    return jsonify({"error": "Item tidak ada"}), 404

# --- 7. API CHECKOUT & HISTORY ---
@app.route('/api/checkout', methods=['POST'])
def checkout():
    user = session.get('username')
    if not user: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    paid = data.get('amount_paid', 0)
    promo = data.get('promo_code', "").upper()
    
    cart = user_carts[user]
    if not cart:
        return jsonify({"status": "FAILED", "message": "Keranjang masih kosong!"}), 400

    total = sum(products[p_id]['price'] * qty for p_id, qty in cart.items())
    
    discount = 0
    if promo in PROMO_CODES:
        discount = total * PROMO_CODES[promo]
        total -= discount

    if paid >= total:
        change = paid - total
        user_histories[user].insert(0, {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total,
            "discount": discount,
            "change": change
        })
        user_carts[user] = {} 
        return jsonify({"status": "SUCCESS", "change": change, "discount": discount}), 200
    else:
        return jsonify({"status": "FAILED", "message": f"Uang kurang Rp {(total - paid):,}"}), 400

@app.route('/api/history')
def get_history():
    user = session.get('username')
    if not user: return jsonify({"error": "Unauthorized"}), 401
    return jsonify(user_histories.get(user, []))

if __name__ == '__main__':
    app.run(debug=True)
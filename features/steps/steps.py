# features/steps/steps.py
from behave import given, when, then
from app import db, User, Product, Transaction, Promo
from werkzeug.security import generate_password_hash
import json

# ==========================================
# 1. SETUP & AUTHENTICATION
# ==========================================

@given('sistem dalam keadaan bersih')
def step_impl(context):
    pass

@when('saya mendaftar dengan username "{username}" dan password "{password}"')
def step_register(context, username, password):
    context.response = context.client.post('/api/signup', json={
        'username': username, 
        'password': password,
        'confirm_password': password
    })

@when('saya mendaftar dengan username "" dan password ""')
def step_register_empty(context):
    context.response = context.client.post('/api/signup', json={
        'username': '', 
        'password': '',
        'confirm_password': ''
    })

@when('saya login dengan username "{username}" dan password "{password}"')
def step_login(context, username, password):
    context.response = context.client.post('/api/login', json={
        'username': username, 'password': password
    })

@then('saya mendapatkan pesan "{message}"')
def step_check_msg(context, message):
    data = context.response.get_json()
    msg_content = data.get('message') or data.get('error')
    assert message in msg_content, f"Harapan: {message}, Dapat: {msg_content}"

@then('status respon harus {status_code:d}')
def step_status(context, status_code):
    assert context.response.status_code == status_code, \
        f"Status salah. Harapan {status_code}, Dapat {context.response.status_code}"

@given('user "{username}" sudah mendaftar dengan password "{password}"')
def step_user_registered_only(context, username, password):
    u = User(username=username, password=generate_password_hash(password), role='user')
    db.session.add(u)
    db.session.commit()

@when('saya melakukan logout')
def step_logout(context):
    context.response = context.client.get('/logout')

# ==========================================
# 2. SETUP DATA & LOGIN HELPER (CRITICAL FOR NEW APP.PY)
# ==========================================

@given('user "{username}" sudah login')
def step_user_login_setup(context, username):
    """
    Helper untuk mendaftarkan user DAN memaksa login ke session.
    PENTING: Kita manipulasi session agar 'role' terbaca.
    """
    # 1. Pastikan User ada di DB
    if not User.query.filter_by(username=username).first():
        u = User(username=username, password=generate_password_hash('pw'), role='user')
        db.session.add(u)
        db.session.commit()

    # 2. Login via API (Untuk test flow normal)
    context.client.post('/api/login', json={'username': username, 'password': 'pw'})
    
    # 3. [Force] Session Injection
    # app.py sekarang butuh session['username'] dan session['role']
    with context.client.session_transaction() as sess:
        sess['username'] = username
        sess['role'] = 'user'

@given('admin sudah login')
def step_admin_login(context):
    """
    Helper khusus Admin.
    PENTING: Harus set role='admin' di session agar tidak kena Error 403.
    """
    # 1. Pastikan Admin ada di DB
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()

    # 2. Login via API
    context.client.post('/api/login', json={'username': 'admin', 'password': 'admin123'})

    # 3. [Force] Session Injection (KUNCI AGAR TIDAK ERROR 403)
    with context.client.session_transaction() as sess:
        sess['username'] = 'admin'
        sess['role'] = 'admin'

# ==========================================
# 3. SETUP PRODUK & PROMO (ADMIN ACTIONS)
# ==========================================

@given('admin telah menambahkan produk "{name}" harga {price:d} stok {stock:d}')
def step_admin_add_prod(context, name, price, stock):
    # Inject langsung ke DB untuk mempercepat setup
    p = Product(name=name, price=price, stock=stock, category='minuman', img='☕')
    db.session.add(p)
    db.session.commit()
    
    if not hasattr(context, 'product_ids'):
        context.product_ids = {}
    context.product_ids[name] = p.id
    context.product_id = p.id # Backward compatibility

@given('admin menambah promo "{code}" diskon {percent:d} persen')
def step_admin_add_promo(context, code, percent):
    p = Promo(code=code, discount_percent=percent)
    db.session.add(p)
    db.session.commit()

# ==========================================
# 4. KERANJANG & TRANSAKSI
# ==========================================

@when('user menambahkan produk "{name}" ke keranjang sebanyak {count:d} kali')
def step_add_cart(context, name, count):
    p_id = context.product_ids[name]
    for _ in range(count):
        context.response = context.client.post('/api/cart/add', json={'product_id': p_id})

@then('total keranjang harus menjadi {total:d}')
def step_check_cart(context, total):
    resp = context.client.get('/api/cart')
    data = resp.get_json()
    assert data['total'] == total, f"Total salah. Harapan: {total}, Actual: {data['total']}"

@when('user mengurangi produk "{name}" dari keranjang sebanyak {count:d} kali')
def step_reduce_cart(context, name, count):
    p_id = context.product_ids[name]
    for _ in range(count):
        context.response = context.client.post('/api/cart/reduce', json={'product_id': p_id})

# Versi Checkout Tanpa Promo
@when('user melakukan checkout dengan uang {money:d}')
def step_checkout(context, money):
    context.response = context.client.post('/api/checkout', json={
        'amount_paid': money,
        'promo_code': ''
    })

# Versi Checkout DENGAN Promo
@when('user checkout dengan uang {money:d} dan kode "{code}"')
def step_checkout_promo(context, money, code):
    context.response = context.client.post('/api/checkout', json={
        'amount_paid': money,
        'promo_code': code
    })

@then('transaksi berhasil dengan kembalian {change:d}')
def step_check_change(context, change):
    assert context.response.status_code == 200, "Transaksi Gagal (Bukan 200 OK)"
    data = context.response.get_json()
    assert data['change'] == change, f"Kembalian salah. Harapan: {change}, Actual: {data['change']}"

@then('total belanja tercatat {total:d}')
def step_check_total_trx(context, total):
    trx = Transaction.query.order_by(Transaction.id.desc()).first()
    assert trx.total == total, f"Total DB salah. Harapan: {total}, DB: {trx.total}"

@when('user mencoba mengurangi produk "{name}" dari keranjang')
def step_try_reduce_empty(context, name):
    p_id = context.product_ids[name]
    context.response = context.client.post('/api/cart/reduce', json={'product_id': p_id})

@when('user mencoba menambahkan produk dengan ID "{id_val}" yang tidak valid')
def step_add_invalid_id(context, id_val):
    context.response = context.client.post('/api/cart/add', json={'product_id': id_val})

# ==========================================
# 5. VALIDASI STOK, ADMIN API & ERROR HANDLING
# ==========================================

@then('stok produk "{name}" di database harus menjadi {final_stock:d}')
def step_check_db_stock(context, name, final_stock):
    p_id = context.product_ids[name]
    db.session.expire_all()
    p = Product.query.get(p_id)
    assert p.stock == final_stock, f"Stok salah. Harapan: {final_stock}, Aktual: {p.stock}"

@then('stok produk "{name}" di database harus tetap {stock:d}')
def step_check_stock_remain(context, name, stock):
    step_check_db_stock(context, name, stock)

@when('admin mengubah stok produk "{name}" menjadi {qty:d}')
def step_update_stock(context, name, qty):
    p_id = context.product_ids[name]
    context.response = context.client.post('/api/admin/update_stock', json={
        'id': p_id,
        'new_stock': qty
    })

@then('sistem menolak dengan pesan error "{msg}"')
def step_check_error_msg(context, msg):
    data = context.response.get_json()
    response_msg = data.get('message') or data.get('error')
    assert msg in response_msg, f"Harapan error: '{msg}', Dapat: '{response_msg}'"
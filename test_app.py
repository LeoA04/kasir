# INTEGRATION TESTING
import unittest
import json
from app import app, users, user_carts, user_histories, products

class TestIntegrationPOS(unittest.TestCase):

    def setUp(self):
        """Persiapan sebelum setiap test dijalankan"""
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret'
        
        # Reset data agar setiap test dimulai dari kondisi bersih
        users.clear()
        users["admin"] = "admin123"
        user_carts.clear()
        user_histories.clear()

    def test_auth_and_session_integration(self):
        """Menguji integrasi pendaftaran, login, dan pembatasan akses"""
        # 1. Signup user baru
        res_signup = self.client.post('/api/signup', json={"username": "tester", "password": "password123"})
        self.assertEqual(res_signup.status_code, 201)

        # 2. Login dengan user tersebut
        res_login = self.client.post('/api/login', json={"username": "tester", "password": "password123"})
        self.assertEqual(res_login.status_code, 200)

        # 3. Akses data keranjang
        res_cart = self.client.get('/api/cart')
        self.assertEqual(res_cart.status_code, 200)

    # --- Menguji Logout ---
    def test_logout_and_session_clearing(self):
        """Menguji apakah sesi benar-benar hilang setelah logout"""
        self.client.post('/api/login', json={"username": "admin", "password": "admin123"})
        self.client.get('/logout')
        
        # Mencoba akses keranjang setelah logout harus gagal
        res = self.client.get('/api/cart')
        self.assertEqual(res.status_code, 401)

    def test_unauthorized_access(self):
        """Menguji apakah sistem menolak akses jika belum login"""
        res = self.client.get('/api/cart')
        self.assertEqual(res.status_code, 401)

    # --- Menguji Produk Tidak Valid ---
    def test_add_invalid_product(self):
        """Menguji respons jika ID produk tidak ada di sistem"""
        self.client.post('/api/login', json={"username": "admin", "password": "admin123"})
        res = self.client.post('/api/cart/add', json={"product_id": "999"})
        self.assertEqual(res.status_code, 404)
        self.assertIn("Produk tidak ditemukan", res.get_json()['error'])

    # --- Menguji Logika Pengurangan Item ---
    def test_cart_reduce_logic(self):
        """Menguji fungsi pengurangan kuantitas dan penghapusan item"""
        self.client.post('/api/login', json={"username": "admin", "password": "admin123"})
        
        # Tambah 2 item yang sama
        self.client.post('/api/cart/add', json={"product_id": "1"})
        self.client.post('/api/cart/add', json={"product_id": "1"})
        
        # Kurangi 1 (sisa 1)
        self.client.post('/api/cart/reduce', json={"product_id": "1"})
        res = self.client.get('/api/cart')
        self.assertEqual(res.get_json()['items'][0]['quantity'], 1)
        
        # Kurangi lagi (item harus terhapus/pop dari cart)
        self.client.post('/api/cart/reduce', json={"product_id": "1"})
        res_final = self.client.get('/api/cart')
        self.assertEqual(len(res_final.get_json()['items']), 0)

    # --- Menguji Checkout Gagal (Uang Kurang & Keranjang Kosong) ---
    def test_checkout_failures(self):
        """Menguji validasi uang kurang dan keranjang kosong"""
        self.client.post('/api/login', json={"username": "admin", "password": "admin123"})

        # Kasus 1: Checkout saat keranjang kosong
        res_empty = self.client.post('/api/checkout', json={"amount_paid": 50000})
        self.assertEqual(res_empty.status_code, 400)
        self.assertIn("Keranjang masih kosong", res_empty.get_json()['message'])

        # Kasus 2: Uang kurang
        self.client.post('/api/cart/add', json={"product_id": "4"}) # Sandwich 25.000
        res_less = self.client.post('/api/checkout', json={"amount_paid": 10000})
        self.assertEqual(res_less.status_code, 400)
        self.assertIn("Uang kurang", res_less.get_json()['message'])

    def test_full_transaction_flow_with_promo(self):
        """Integrasi utama: Login -> Belanja -> Promo -> Bayar"""
        self.client.post('/api/login', json={"username": "admin", "password": "admin123"})
        self.client.post('/api/cart/add', json={"product_id": "5"}) # 20.000
        self.client.post('/api/cart/add', json={"product_id": "11"}) # 5.000
        
        # Promo HEMAT10 (10% dari 25rb = 2.500). Total 22.500
        res_pay = self.client.post('/api/checkout', json={
            "amount_paid": 30000,
            "promo_code": "HEMAT10"
        })
        
        data = res_pay.get_json()
        self.assertEqual(data['discount'], 2500)
        self.assertEqual(data['change'], 7500)

    def test_cart_isolation_between_users(self):
        """Memastikan keranjang user tidak tertukar"""
        with self.client as c:
            c.post('/api/signup', json={"username": "userA", "password": "123"})
            c.post('/api/login', json={"username": "userA", "password": "123"})
            c.post('/api/cart/add', json={"product_id": "1"})
            c.get('/logout')

        with self.client as c:
            c.post('/api/signup', json={"username": "userB", "password": "123"})
            c.post('/api/login', json={"username": "userB", "password": "123"})
            res = c.get('/api/cart')
            self.assertEqual(len(res.get_json()['items']), 0)

if __name__ == '__main__':
    unittest.main()
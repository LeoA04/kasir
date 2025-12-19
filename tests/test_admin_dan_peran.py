import unittest
from app import app, db
from models import User, Product, Promo
from werkzeug.security import generate_password_hash

class TestAdminDanPeran(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # use in memory db
        self.client = app.test_client()

        # push an application context
        self.konteks_app = app.app_context()
        self.konteks_app.push()

        # create all tables
        db.create_all()

        # create dummy users with different roles
        admin = User(username='admin_test', password=generate_password_hash('password'), role='admin')
        kasir = User(username='kasir_test', password=generate_password_hash('password'), role='kasir')
        user_biasa = User(username='user_test', password=generate_password_hash('password'), role='user')
        
        db.session.add_all([admin, kasir, user_biasa])
        db.session.commit()

    def tearDown(self):
        """membersihkan lingkungan setelah setiap tes"""
        db.session.remove()
        db.drop_all()
        self.konteks_app.pop()

    def masuk(self, username, password):
        """fungsi bantuan untuk login pengguna"""
        return self.client.post('/api/login', json={'username': username, 'password': password})

    # --- uji akses peran---

    def test_admin_bisa_akses_dashboard_admin(self):
        """admin seharusnya bisa mengakses /admin"""
        self.masuk('admin_test', 'password')
        respons = self.client.get('/admin')
        self.assertEqual(respons.status_code, 200)
        self.assertIn(b'ADMIN DASHBOARD', respons.data)

    def test_kasir_dialihkan_dari_dashboard_admin(self):
        """non-admin (kasir) seharusnya dialihkan dari /admin"""
        self.masuk('kasir_test', 'password')
        respons = self.client.get('/admin', follow_redirects=False)
        self.assertEqual(respons.status_code, 302) # redirect

    def test_kasir_bisa_akses_halaman_kasir(self):
        """kasir seharusnya bisa mengakses halaman kasir utama"""
        self.masuk('kasir_test', 'password')
        respons = self.client.get('/')
        self.assertEqual(respons.status_code, 200)
        self.assertIn(b'MENU KASIR', respons.data) # cek kata kunci yang lebih stabil

    def test_user_ditolak_dari_halaman_kasir(self):
        """pengguna dengan peran 'user' seharusnya ditolak akses ke halaman kasir"""
        self.masuk('user_test', 'password')
        respons = self.client.get('/')
        self.assertEqual(respons.status_code, 200)
        # check for the specific alert message shown to 'user' roles
        self.assertIn(b'alert("Anda login sebagai user biasa. Mohon hubungi admin untuk akses kasir!");', respons.data)

    # --- pengujian api admin ---

    def test_admin_bisa_tambah_produk(self):
        """admin seharusnya bisa menambah produk baru via api"""
        self.masuk('admin_test', 'password')
        respons = self.client.post('/api/admin/add_product', json={
            'name': 'New Drink', 'price': 15000, 'img': 'drink.jpg', 'category': 'Minuman', 'stock': 100
        })
        self.assertEqual(respons.status_code, 200)
        produk = Product.query.filter_by(name='New Drink').first()
        self.assertIsNotNone(produk)
        self.assertEqual(produk.price, 15000)

    def test_admin_bisa_hapus_produk(self):
        """admin seharusnya bisa menghapus produk"""
        self.masuk('admin_test', 'password')
        produk_baru = Product(name='To Be Deleted', price=100)
        db.session.add(produk_baru)
        db.session.commit()
        produk_id = produk_baru.id # simpan id sebelum objek dihapus

        respons = self.client.post('/api/admin/delete_product', json={'id': produk_id})
        self.assertEqual(respons.status_code, 200)
        produk = db.session.get(Product, produk_id) # pakai id yang disimpan untuk verifikasi
        self.assertIsNone(produk)

    def test_admin_bisa_update_stok(self):
        """admin seharusnya bisa memperbarui stok produk"""
        self.masuk('admin_test', 'password')
        produk = Product(name='Test Stock', price=100, stock=10)
        db.session.add(produk)
        db.session.commit()

        respons = self.client.post('/api/admin/update_stock', json={'id': produk.id, 'new_stock': 55})
        self.assertEqual(respons.status_code, 200)
        db.session.refresh(produk) # refresh objek dari db
        self.assertEqual(produk.stock, 55)

    def test_admin_bisa_tambah_promo(self):
        """admin seharusnya bisa membuat promo baru"""
        self.masuk('admin_test', 'password')
        respons = self.client.post('/api/admin/add_promo', json={'code': 'BARU20', 'discount': 20})
        self.assertEqual(respons.status_code, 200)
        promo = Promo.query.filter_by(code='BARU20').first()
        self.assertIsNotNone(promo)

    def test_admin_bisa_hapus_promo(self):
        """admin seharusnya bisa menghapus promo"""
        self.masuk('admin_test', 'password')
        promo = Promo(code='HAPUS', discount_percent=10)
        db.session.add(promo)
        db.session.commit()
        promo_id = promo.id # simpan id sebelum objek dihapus

        respons = self.client.post('/api/admin/delete_promo', json={'id': promo_id})
        self.assertEqual(respons.status_code, 200)
        self.assertIsNone(db.session.get(Promo, promo_id)) # pakai id yang disimpan untuk verifikasi

    def test_admin_bisa_atur_peran_user(self):
        """admin seharusnya bisa mengubah peran pengguna lain"""
        self.masuk('admin_test', 'password')
        user_yang_diubah = User.query.filter_by(username='user_test').first()
        self.assertEqual(user_yang_diubah.role, 'user') # verifikasi peran awal

        user_id = user_yang_diubah.id
        respons = self.client.post('/api/admin/set_role', json={'user_id': user_id, 'role': 'kasir'})
        self.assertEqual(respons.status_code, 200)

        user_updated = db.session.get(User, user_id) # ambil ulang objek dari db
        self.assertEqual(user_updated.role, 'kasir') # verifikasi peran baru

if __name__ == '__main__':
    unittest.main()
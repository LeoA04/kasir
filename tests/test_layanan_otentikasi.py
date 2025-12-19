import unittest
from unittest.mock import patch, MagicMock

from app import app, db
from models import User
from auth_service import validasi_daftar, buat_user, validasi_login, atur_peran_user
from werkzeug.security import generate_password_hash

class TestLayananOtentikasi(unittest.TestCase):

    def setUp(self):
        """sediakan application context dan setup database test"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.konteks_app = app.app_context()
        self.konteks_app.push()
        db.create_all()

    def tearDown(self):
        """hapus session dan drop semua tabel"""
        db.session.remove()
        db.drop_all()
        self.konteks_app.pop()

    @patch('auth_service.User')
    def test_validasi_daftar_sukses(self, mock_kelas_user):
        """tes validasi pendaftaran yang sukses"""
        mock_kelas_user.query.filter_by.return_value.first.return_value = None
        hasil = validasi_daftar("userbaru", "password123", "password123")
        self.assertTrue(hasil)

    def test_validasi_daftar_password_terlalu_pendek(self):
        """tes pendaftaran dengan password yang terlalu pendek"""
        with self.assertRaisesRegex(ValueError, "Password minimal 6 karakter"):
            validasi_daftar("userbaru", "123", "123")

    def test_validasi_daftar_password_tidak_cocok(self):
        """tes pendaftaran dengan password yang tidak cocok"""
        with self.assertRaisesRegex(ValueError, "Password dan konfirmasi tidak sama"):
            validasi_daftar("userbaru", "password123", "password456")

    @patch('auth_service.User')
    def test_validasi_daftar_username_sudah_ada(self, mock_kelas_user):
        """tes pendaftaran dengan username yang sudah ada"""
        mock_kelas_user.query.filter_by.return_value.first.return_value = MagicMock() # simulasi menemukan objek user
        with self.assertRaisesRegex(ValueError, "Username sudah ada!"):
            validasi_daftar("admin", "password123", "password123")

    @patch('auth_service.db.session')
    @patch('auth_service.User')
    def test_buat_user(self, mock_user, mock_sesi):
        """tes pembuatan user dan hashing password"""
        buat_user("testuser", "securepass")
        
        # dicek user dipanggil dengan username dan role yang benar apa nggak
        # password dihash jadi kita ga bisa membandingkan stringnya secara langsung
        self.assertTrue(mock_user.call_args[1]['username'] == 'testuser')
        self.assertTrue('password' in mock_user.call_args[1])

        # cek apakah user ditambahkan ke session dan di commit
        mock_sesi.add.assert_called_once()
        mock_sesi.commit.assert_called_once()

    @patch("auth_service.check_password_hash")
    @patch("auth_service.User")
    def test_validasi_login_sukses(self, mock_kelas_user, mock_periksa_hash):
        """tes login yang sukses"""
        mock_user = MagicMock()
        mock_user.password = "hashed"
        mock_user.role = "admin"

        mock_kelas_user.query.filter_by.return_value.first.return_value = mock_user
        mock_periksa_hash.return_value = True

        hasil = validasi_login("admin", "admin123")

        self.assertIsNotNone(hasil)
        self.assertEqual(hasil.role, "admin")

    @patch("auth_service.check_password_hash")
    @patch("auth_service.User")
    def test_validasi_login_password_salah(self, mock_kelas_user, mock_periksa_hash):
        """tes login dengan password yang salah"""
        mock_user = MagicMock()
        mock_user.password = "hashed"

        mock_kelas_user.query.filter_by.return_value.first.return_value = mock_user
        mock_periksa_hash.return_value = False

        hasil = validasi_login("admin", "salah")

        self.assertIsNone(hasil)

    @patch("auth_service.check_password_hash")
    @patch("auth_service.User")
    def test_validasi_login_user_tidak_ditemukan(self, mock_kelas_user, mock_periksa_hash):
        """tes login dengan user yang tidak ada"""
        mock_kelas_user.query.filter_by.return_value.first.return_value = None

        hasil = validasi_login("tidakada", "123")

        self.assertIsNone(hasil)

    def test_atur_peran_user_sukses(self):
        """tes keberhasilan mengatur peran baru untuk pengguna dengan database"""
        # patch db object di dalam service agar menggunakan db instance dari test
        with patch('auth_service.db', db):
            # buat user di database test
            user = User(username='testuser', password=generate_password_hash('password'), role='user')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

            # panggil fungsi yang diuji
            atur_peran_user(user_id, 'admin')
            user_yang_diubah = db.session.get(User, user_id)
            
            # verifikasi bahwa role pada user sudah diubah
            self.assertIsNotNone(user_yang_diubah)
            self.assertEqual(user_yang_diubah.role, 'admin')

    def test_atur_peran_user_tidak_ditemukan(self):
        """tes kegagalan pengaturan peran saat pengguna tidak ditemukan dengan database"""
        # patch db object di dalam service agar menggunakan db instance dari test
        with patch('auth_service.db', db):
            with self.assertRaisesRegex(ValueError, "User tidak ditemukan"):
                atur_peran_user(999, 'kasir')
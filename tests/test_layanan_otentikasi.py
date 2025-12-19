import unittest
from unittest.mock import patch, MagicMock

from app import app
from auth_service import validasi_daftar, buat_user, validasi_login, atur_peran_user

class TestLayananOtentikasi(unittest.TestCase):

    def setUp(self):
        """sediakan application context sebelum setiap test"""
        self.konteks_app = app.app_context()
        self.konteks_app.push()

    def tearDown(self):
        """hapus application context setelah setiap test"""
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

    @patch('auth_service.db.session')
    def test_atur_peran_user_sukses(self, mock_sesi):
        """tes keberhasilan mengatur peran baru untuk pengguna"""
        # buat mock user yang akan "ditemukan" oleh query
        instance_mock_user = MagicMock()
        instance_mock_user.role = 'user' # Role awal
        mock_sesi.get.return_value = instance_mock_user

        # panggil fungsi yang diuji
        atur_peran_user(1, 'admin')

        # verifikasi bahwa role pada instance user sdh diubah
        self.assertEqual(instance_mock_user.role, 'admin')
        # verifikasi perubahan di commit ke database
        mock_sesi.commit.assert_called_once()

    @patch('auth_service.db.session')
    def test_atur_peran_user_tidak_ditemukan(self, mock_sesi):
        """tes kegagalan pengaturan peran saat pengguna tidak ditemukan"""
        mock_sesi.get.return_value = None
        with self.assertRaisesRegex(ValueError, "User tidak ditemukan"):
            atur_peran_user(999, 'kasir')
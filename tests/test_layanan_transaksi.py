import unittest
from unittest.mock import patch, MagicMock

from app import app
from transaction_service import hitung_total_keranjang, terapkan_promo, proses_checkout

class TestLayananTransaksi(unittest.TestCase):

    def setUp(self):
        """mempersiapkan fixture tes"""
        self.konteks_app = app.app_context()
        self.konteks_app.push()

        # produk
        self.produk1 = MagicMock(id=1, name="Kopi", price=10000, stock=10)
        self.produk2 = MagicMock(id=2, name="Teh", price=8000, stock=5)

        # promo
        self.promo10persen = MagicMock(code="HEMAT10", discount_percent=10)

        # keranjang belanja
        self.keranjang = {'1': 2, '2': 1} # 2 kopi, 1 teh

    def tearDown(self):
        self.konteks_app.pop()

    def mock_kueri_produk(self, model, id_produk):
        if id_produk == 1:
            return self.produk1
        if id_produk == 2:
            return self.produk2
        return None

    @patch('transaction_service.db.session')
    def test_hitung_subtotal_keranjang(self, mock_sesi):
        """tes perhitungan subtotal sudah benar"""
        mock_sesi.get.side_effect = self.mock_kueri_produk
        
        subtotal = hitung_total_keranjang(self.keranjang)
        # (2 * 10000) + (1 * 8000) = 28000
        self.assertEqual(subtotal, 28000)

    @patch("transaction_service.db.session")
    def test_hitung_keranjang_stok_tidak_cukup(self, mock_sesi):
        """tes bahwa checkout gagal jika stok tidak cukup"""
        mock_produk = MagicMock(spec=["name", "stock", "price"])
        mock_produk.name = "Kopi"
        mock_produk.stock = 1
        mock_produk.price = 10000

        mock_sesi.get.return_value = mock_produk

        keranjang = {"1": 5} # coba beli 5, padahal stok cuma 1

        with self.assertRaisesRegex(ValueError, "Stok tidak cukup untuk produk: Kopi"):
            hitung_total_keranjang(keranjang)

    @patch('transaction_service.Promo')
    def test_terapkan_promo_valid(self, mock_kelas_promo):
        """tes bahwa kode promo yang valid menerapkan diskon yang benar"""
        mock_kelas_promo.query.filter_by.return_value.first.return_value = self.promo10persen
        
        subtotal = 28000
        diskon, info_promo = terapkan_promo(subtotal, "HEMAT10")
        
        self.assertEqual(diskon, 2800) # 10% dari 28000
        self.assertEqual(info_promo, "HEMAT10 (10%)")

    @patch('transaction_service.Promo')
    def test_terapkan_promo_tidak_valid(self, mock_kelas_promo):
        """tes bahwa kode promo yang tidak valid menghasilkan diskon nol"""
        mock_kelas_promo.query.filter_by.return_value.first.return_value = None
        
        subtotal = 28000
        diskon, info_promo = terapkan_promo(subtotal, "INVALIDCODE")
        
        self.assertEqual(diskon, 0)
        self.assertEqual(info_promo, "-")

    @patch('transaction_service.db.session')
    @patch('transaction_service.Transaction')
    @patch('transaction_service.Promo')
    @patch('transaction_service.Product')
    def test_proses_checkout_sukses(self, mock_product_class, mock_promo_class, mock_transaction_model, mock_sesi):
        """tes proses checkout yang lengkap dan sukses"""
        mock_sesi.get.side_effect = self.mock_kueri_produk
        mock_promo_class.query.filter_by.return_value.first.return_value = self.promo10persen

        # total akhir = 28000 - 2800 = 25200
        # bayar = 30000
        # kembalian = 4800
        hasil = proses_checkout(self.keranjang, 30000, "HEMAT10", "kasir_test")

        # assert results
        self.assertEqual(hasil['status'], "SUCCESS")
        self.assertEqual(hasil['change'], 4800)
        self.assertEqual(hasil['discount'], 2800)

        # assert that the database session was used to save the transaction
        mock_sesi.add.assert_called_once()
        # commit dipanggil 2x: 1x di reduce_stock_after_checkout, 1x di process_checkout
        self.assertEqual(mock_sesi.commit.call_count, 2)

    @patch('transaction_service.db.session')
    def test_proses_checkout_pembayaran_kurang(self, mock_sesi):
        """tes kegagalan checkout karena pembayaran kurang"""
        mock_sesi.get.side_effect = self.mock_kueri_produk

        # total 28000 bayar hanya 20000
        with self.assertRaisesRegex(ValueError, "Uang tunai kurang"):
            proses_checkout(self.keranjang, 20000, None, "kasir_test")

    def test_proses_checkout_keranjang_kosong(self):
        """tes kegagalan checkout dengan keranjang kosong"""
        with self.assertRaisesRegex(ValueError, "Keranjang kosong"):
            proses_checkout({}, 50000, None, "kasir_test")
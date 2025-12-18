from models import Product, Promo, Transaction
from database import db
from product_service import kurangi_stok_setelah_checkout

def hitung_total_keranjang(keranjang):
    """Menghitung subtotal dari item di dalam keranjang."""
    subtotal = 0
    for id_p, jumlah in keranjang.items():
        produk = db.session.get(Product, int(id_p))
        if produk:
            # Memastikan stok cukup untuk item di keranjang
            if produk.stock < jumlah:
                raise ValueError(f"Stok tidak cukup untuk produk: {produk.name}")
            subtotal += produk.price * jumlah
    return subtotal

def terapkan_promo(subtotal, kode_promo):
    """Menerapkan diskon berdasarkan kode promo."""
    if not kode_promo:
        return 0, "-"

    promo = Promo.query.filter_by(code=kode_promo).first()
    if not promo:
        # Promo tidak valid, tidak ada diskon
        return 0, "-"
    
    nilai_diskon = int(subtotal * (promo.discount_percent / 100))
    info_promo = f"{promo.code} ({promo.discount_percent}%)"
    return nilai_diskon, info_promo

def proses_checkout(keranjang, jumlah_bayar, kode_promo, nama_kasir):
    """Memproses seluruh logika checkout."""
    if not keranjang:
        raise ValueError("Keranjang kosong")

    subtotal = hitung_total_keranjang(keranjang)
    nilai_diskon, info_promo = terapkan_promo(subtotal, kode_promo)
    
    total_akhir = subtotal - nilai_diskon
    
    if jumlah_bayar < total_akhir:
        raise ValueError("Uang tunai kurang")
        
    kembalian = jumlah_bayar - total_akhir
    
    # Kurangi stok
    kurangi_stok_setelah_checkout(keranjang)
    
    # Simpan transaksi
    tx_baru = Transaction(subtotal=subtotal, promo_info=info_promo, total=total_akhir, 
                         amount_paid=jumlah_bayar, change=kembalian, cashier_name=nama_kasir)
    db.session.add(tx_baru)
    db.session.commit()
    
    return {"status": "SUCCESS", "change": kembalian, "discount": nilai_diskon}
from models import Product
from database import db

def perbarui_stok_produk(id_produk, stok_baru):
    """Memperbarui stok dari produk tertentu."""
    if stok_baru < 0:
        raise ValueError("Stok tidak boleh kurang dari 0")
    
    produk = db.session.get(Product, id_produk)
    if not produk:
        raise ValueError("Produk tidak ditemukan")
        
    produk.stock = stok_baru
    db.session.commit()
    return produk

def kurangi_stok_setelah_checkout(keranjang):
    """Mengurangi stok untuk setiap item di keranjang setelah transaksi berhasil."""
    for id_p, jumlah in keranjang.items():
        produk = db.session.get(Product, int(id_p))
        if produk:
            produk.stock -= jumlah
    db.session.commit()
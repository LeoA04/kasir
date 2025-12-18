# Smart POS System 🚀

Smart POS adalah sistem kasir berbasis web sederhana yang dibuat menggunakan **Flask**, **SQLite**, dan **Bootstrap**. Sistem ini mendukung manajemen produk, promo, transaksi, serta manajemen role pengguna (admin, kasir, user).

---

## **Fitur Utama**

### 1. **Autentikasi**
- Signup / pendaftaran akun baru.
- Login untuk **admin**, **kasir**, dan **user**.
- Logout dan proteksi role.

### 2. **Role Management**
- Admin dapat mengatur role pengguna (`user`, `kasir`, `admin`).
- Proteksi akses: 
  - Admin → dashboard admin.
  - Kasir → halaman kasir untuk transaksi.
  - User → halaman khusus user atau peringatan jika mencoba masuk halaman kasir.

### 3. **Sistem POS / Kasir**
- Tambah produk ke keranjang.
- Kurangi jumlah produk di keranjang.
- Pilih promo untuk diskon (%).
- Checkout transaksi dengan kalkulasi kembalian otomatis.
- Melihat histori transaksi.

### 4. **Manajemen Produk**
- Admin dapat menambah, menghapus, dan update stok produk.
- Menggunakan emoji sebagai icon produk (opsional).

### 5. **Manajemen Promo**
- Admin dapat menambahkan dan menghapus kode promo beserta diskonnya (%).

### 6. **Laporan Transaksi**
- Admin dapat melihat laporan transaksi harian beserta omzet hari ini.

---

## **Database**

Database default menggunakan **SQLite**:

- File: `smart_pos.db`  
- Tabel:
  - `User` → username, password (hash), role
  - `Product` → name, price, stock, category, img
  - `Promo` → code, discount_percent
  - `Transaction` → timestamp, subtotal, promo_info, total, amount_paid, change, cashier_name

> Catatan: Bisa dikonfigurasi ke **MySQL** dengan mengganti `SQLALCHEMY_DATABASE_URI`.

---

## **Setup & Instalasi**

- git clone <url-repo>
- cd <nama-folder>
- python -m venv venv
- venv\Scripts\activate
- pip install -r requirements.txt
- python app.py

Akses aplikasi melalui browser:
http://127.0.0.1:5000

Default akun admin sudah dibuat:
* Username: admin
* Password: admin123
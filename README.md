🚀 Smart POS System - Kasir Enterprise
Sistem Kasir (Point of Sale) berbasis web yang dibangun menggunakan Flask untuk backend dan Bootstrap 5 untuk antarmuka pengguna. Aplikasi ini dirancang untuk menangani transaksi penjualan makanan dan minuman secara efisien dengan fitur manajemen keranjang dan perhitungan promo otomatis.

✨ Fitur Utama
Sistem Autentikasi: Pengguna dapat mendaftar akun baru dan masuk ke sistem untuk mulai bertransaksi.

Manajemen Produk & Kategori: Mendukung 14 item produk default yang terbagi dalam kategori Makanan dan Minuman.

Filter Cerdas: Memungkinkan kasir mencari produk berdasarkan nama atau menyaringnya berdasarkan kategori tertentu secara real-time di sisi klien.

Keranjang Interaktif: Fitur untuk menambah, mengurangi, atau menghapus item dari keranjang belanja dengan pembaruan total tagihan instan.

Sistem Promo: Mendukung kode promo seperti HEMAT10 (Diskon 10%) dan MERDEKA20 (Diskon 20%).

Riwayat Transaksi: Mencatat setiap transaksi yang berhasil, lengkap dengan detail waktu, total bayar, diskon, dan kembalian.

Isolasi Data: Data keranjang dan riwayat transaksi bersifat privat dan tidak akan tertukar antar pengguna yang berbeda.

🛠️ Teknologi yang Digunakan
Backend: Python 3.x dengan Flask Framework.

Frontend: HTML5, CSS (Bootstrap 5), dan Vanilla JavaScript (Fetch API).

Testing: Python unittest untuk Integration Testing.

Database: In-memory database (Mocking menggunakan Python Dictionary).

📂 Struktur Proyek
Plaintext

├── app.py              # Logika utama backend, API, dan rute aplikasi
├── test_app.py         # Skrip pengujian integrasi otomatis
├── templates/
│   ├── auth.html       # Halaman Login dan Signup
│   └── index.html      # Halaman utama Kasir & Histori
└── README.md           # Dokumentasi proyek

🚀 Cara Menjalankan Aplikasi
Instalasi Dependensi: Pastikan Anda memiliki Python dan Flask terinstal di perangkat Anda.

Bash

pip install flask
Menjalankan Server: Jalankan file app.py menggunakan terminal.

Bash

python app.py
Buka browser dan akses http://127.0.0.1:5000.

Akun Default: Anda bisa mendaftar akun baru atau menggunakan akun admin bawaan:

Username: admin

Password: admin123

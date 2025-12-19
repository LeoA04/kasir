Feature: Transaksi Toko Lengkap
  Sebagai pemilik toko
  Saya ingin sistem menangani berbagai kondisi belanja
  Baik itu sukses, uang kurang, atau edit keranjang

  Background:
    Given admin telah menambahkan produk "Kopi Susu" harga 15000 stok 10
    And admin telah menambahkan produk "Roti Bakar" harga 20000 stok 5
    And user "pembeli" sudah login

  Scenario: Transaksi pembelian normal sukses memotong stok
    When user menambahkan produk "Kopi Susu" ke keranjang sebanyak 2 kali
    Then total keranjang harus menjadi 30000
    When user melakukan checkout dengan uang 50000
    Then transaksi berhasil dengan kembalian 20000
    And stok produk "Kopi Susu" di database harus menjadi 8

  Scenario: Transaksi gagal karena uang tunai kurang (Negative Case)
    When user menambahkan produk "Roti Bakar" ke keranjang sebanyak 1 kali
    When user melakukan checkout dengan uang 5000
    Then status respon harus 400
    And sistem menolak dengan pesan error "Uang tunai kurang"
    And stok produk "Roti Bakar" di database harus tetap 5

  Scenario: Transaksi gagal jika keranjang kosong (Edge Case)
    Given sistem dalam keadaan bersih
    And user "orang_iseng" sudah login
    When user melakukan checkout dengan uang 100000
    Then status respon harus 400
    And sistem menolak dengan pesan error "Keranjang kosong"

  Scenario: Mengurangi barang dari keranjang (Edit Cart)
    When user menambahkan produk "Kopi Susu" ke keranjang sebanyak 3 kali
    Then total keranjang harus menjadi 45000
    When user mengurangi produk "Kopi Susu" dari keranjang sebanyak 1 kali
    Then total keranjang harus menjadi 30000
    When user melakukan checkout dengan uang 30000
    Then transaksi berhasil dengan kembalian 0
    And stok produk "Kopi Susu" di database harus menjadi 8

  Scenario: Membeli bermacam-macam produk sekaligus (Complex Flow)
    When user menambahkan produk "Kopi Susu" ke keranjang sebanyak 1 kali
    And user menambahkan produk "Roti Bakar" ke keranjang sebanyak 1 kali
    Then total keranjang harus menjadi 35000
    When user melakukan checkout dengan uang 40000
    Then transaksi berhasil dengan kembalian 5000
    And stok produk "Kopi Susu" di database harus menjadi 9
    And stok produk "Roti Bakar" di database harus menjadi 4
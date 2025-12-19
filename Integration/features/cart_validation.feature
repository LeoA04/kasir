Feature: Validasi dan Batasan Keranjang
  Untuk mencegah inkonsistensi data
  Sistem harus memvalidasi setiap aksi penambahan dan pengurangan item

  Background:
    Given sistem dalam keadaan bersih
    And admin telah menambahkan produk "Barang Limited" harga 50000 stok 1
    And admin telah menambahkan produk "Barang Melimpah" harga 1000 stok 100
    And user "tester_keranjang" sudah login

  Scenario: Mencegah penambahan barang melebihi stok yang tersedia
    When user menambahkan produk "Barang Limited" ke keranjang sebanyak 1 kali
    Then status respon harus 200
    # Stok cuma 1, mencoba nambah lagi harus gagal
    When user menambahkan produk "Barang Limited" ke keranjang sebanyak 1 kali
    Then status respon harus 400
    And sistem menolak dengan pesan error "Stok tidak cukup"

  Scenario: Mengurangi barang yang tidak ada di keranjang (Error 404)
    # Keranjang masih kosong
    When user mencoba mengurangi produk "Barang Melimpah" dari keranjang
    Then status respon harus 404
    And sistem menolak dengan pesan error "Item tidak ditemukan"

  Scenario: Validasi ID Produk tidak valid (Security Test)
    # Mencoba inject ID produk ngawur (misal ID 99999) via API
    When user mencoba menambahkan produk dengan ID "99999" yang tidak valid
    Then status respon harus 400
    # App.py mengembalikan "Stok tidak cukup" jika produk tidak ditemukan/None (karena if product... gagal)
    And sistem menolak dengan pesan error "Stok tidak cukup"

  Scenario: Transaksi gagal total jika keranjang kosong saat checkout
    # Langsung checkout tanpa belanja
    When user melakukan checkout dengan uang 100000
    Then status respon harus 400
    And sistem menolak dengan pesan error "Keranjang kosong"
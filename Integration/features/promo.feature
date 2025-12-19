Feature: Kode Promo dan Diskon
  Sebagai pemburu diskon
  Saya ingin harga lebih murah saat checkout

  Scenario: Menggunakan voucher diskon yang valid
    Given admin telah menambahkan produk "Pizza" harga 100000 stok 10
    And admin menambah promo "HEMAT50" diskon 50 persen
    And user "hemat_man" sudah login
    When user menambahkan produk "Pizza" ke keranjang sebanyak 1 kali
    And user checkout dengan uang 100000 dan kode "HEMAT50"
    Then transaksi berhasil dengan kembalian 50000
    And total belanja tercatat 50000
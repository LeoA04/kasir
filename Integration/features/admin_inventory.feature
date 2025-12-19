Feature: Manajemen Inventaris Admin
  Sebagai admin
  Saya ingin mengelola stok barang dengan benar

  Scenario: Admin berhasil update stok barang
    Given admin telah menambahkan produk "Teh Botol" harga 5000 stok 10
    And admin sudah login
    When admin mengubah stok produk "Teh Botol" menjadi 100
    Then stok produk "Teh Botol" di database harus menjadi 100

  Scenario: Admin gagal update stok jadi negatif (Negative Test)
    Given admin telah menambahkan produk "Teh Botol" harga 5000 stok 10
    And admin sudah login
    When admin mengubah stok produk "Teh Botol" menjadi -5
    Then sistem menolak dengan pesan error "Stok tidak boleh kurang dari 0"
    And stok produk "Teh Botol" di database harus tetap 10
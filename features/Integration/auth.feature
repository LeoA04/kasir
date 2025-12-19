Feature: Keamanan dan Otentikasi
  Agar sistem aman dari akses ilegal
  Sistem harus memvalidasi pendaftaran dan login dengan ketat

  Background:
    Given sistem dalam keadaan bersih

  Scenario: Pendaftaran dan Login Sukses (Happy Path)
    When saya mendaftar dengan username "kasir_teladan" dan password "rahasia123"
    Then status respon harus 201
    And saya mendapatkan pesan "Signup Berhasil"
    When saya login dengan username "kasir_teladan" dan password "rahasia123"
    Then status respon harus 200
    And saya mendapatkan pesan "Login Sukses"

  Scenario: Gagal Daftar - Username Sudah Terpakai (Duplicate Account)
    Given user "kasir_lama" sudah mendaftar dengan password "123"
    When saya mendaftar dengan username "kasir_lama" dan password "password_baru"
    Then status respon harus 400
    And saya mendapatkan pesan "Username sudah ada!"

  Scenario: Gagal Daftar - Input Kosong (Validation)
    When saya mendaftar dengan username "" dan password ""
    Then status respon harus 400
    And saya mendapatkan pesan "Input kosong!"

  Scenario: Gagal Login - Password Salah (Security)
    Given user "admin" sudah mendaftar dengan password "admin123"
    When saya login dengan username "admin" dan password "password_ngawur"
    Then status respon harus 401
    And saya mendapatkan pesan "Username/Password salah!"

  Scenario: Gagal Login - Username Tidak Dikenal (Security)
    When saya login dengan username "hantu" dan password "apapun"
    Then status respon harus 401
    And saya mendapatkan pesan "Username/Password salah!"

  Scenario: Logout Berhasil
    Given user "kasir_siap" sudah login
    When saya melakukan logout
    Then status respon harus 302
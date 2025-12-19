from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from database import db

def validasi_daftar(nama_user, kata_sandi, konfirmasi_sandi):
    """Memvalidasi input pengguna untuk pendaftaran."""
    if not nama_user or not kata_sandi or not konfirmasi_sandi:
        raise ValueError("Input kosong!")
    if len(kata_sandi) < 6:
        raise ValueError("Password minimal 6 karakter")
    if kata_sandi != konfirmasi_sandi:
        raise ValueError("Password dan konfirmasi tidak sama")
    if User.query.filter_by(username=nama_user).first():
        raise ValueError("Username sudah ada!")
    return True

def buat_user(nama_user, kata_sandi, peran='user'):
    """Membuat dan menyimpan pengguna baru ke database."""
    kata_sandi_hash = generate_password_hash(kata_sandi)
    user_baru = User(username=nama_user, password=kata_sandi_hash, role=peran)
    db.session.add(user_baru)
    db.session.commit()
    return user_baru

def validasi_login(nama_user, kata_sandi):
    """Memvalidasi kredensial pengguna untuk login."""
    if not nama_user or not kata_sandi:
        return None
    user = User.query.filter_by(username=nama_user).first()
    if user and check_password_hash(user.password, kata_sandi):
        return user
    return None

def atur_peran_user(id_user, peran_baru):
    """Mengatur peran baru untuk seorang pengguna."""
    user = db.session.get(User, id_user)
    if not user:
        raise ValueError("User tidak ditemukan")
    user.role = peran_baru
    db.session.commit()
    return user
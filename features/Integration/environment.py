# features/environment.py
import sys
import os

# Tambahkan folder project ke path agar app.py bisa diimport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, temp_carts

def before_scenario(context, scenario):
    """
    Dijalankan SEBELUM setiap skenario dimulai.
    Kita reset database bersih setiap kali test baru jalan.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # DB di RAM
    
    # Setup context client (browser simulator)
    context.app = app
    context.client = app.test_client()
    context.ctx = app.app_context()
    context.ctx.push()
    
    db.create_all()
    temp_carts.clear()

def after_scenario(context, scenario):
    """
    Dijalankan SETELAH skenario selesai.
    Hapus database.
    """
    db.session.remove()
    db.drop_all()
    context.ctx.pop()
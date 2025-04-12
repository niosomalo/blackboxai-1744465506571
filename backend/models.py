from database import db
from datetime import datetime

class BahanBaku(db.Model):
    """Model for raw materials (bahan baku)"""
    __tablename__ = 'bahan_baku'
    
    id_bahan = db.Column(db.Integer, primary_key=True)
    nama_bahan = db.Column(db.String(100), nullable=False)
    satuan = db.Column(db.String(20), nullable=False)
    stok_awal = db.Column(db.Float, nullable=False)
    harga_per_gram = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id_bahan': self.id_bahan,
            'nama_bahan': self.nama_bahan,
            'satuan': self.satuan,
            'stok_awal': self.stok_awal,
            'harga_per_gram': self.harga_per_gram,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Menu(db.Model):
    """Model for menu items"""
    __tablename__ = 'menu'
    
    id_menu = db.Column(db.Integer, primary_key=True)
    nama_menu = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with Resep
    resep = db.relationship('Resep', backref='menu', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id_menu': self.id_menu,
            'nama_menu': self.nama_menu,
            'resep': [r.to_dict() for r in self.resep],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Resep(db.Model):
    """Model for recipes"""
    __tablename__ = 'resep'
    
    id = db.Column(db.Integer, primary_key=True)
    id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), nullable=False)
    id_bahan = db.Column(db.Integer, db.ForeignKey('bahan_baku.id_bahan'), nullable=False)
    jumlah = db.Column(db.Float, nullable=False)
    waste_percent = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with BahanBaku
    bahan = db.relationship('BahanBaku')

    def to_dict(self):
        return {
            'id': self.id,
            'id_menu': self.id_menu,
            'id_bahan': self.id_bahan,
            'jumlah': self.jumlah,
            'waste_percent': self.waste_percent,
            'bahan': self.bahan.to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Penjualan(db.Model):
    """Model for sales records"""
    __tablename__ = 'penjualan'
    
    id_penjualan = db.Column(db.Integer, primary_key=True)
    id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    jumlah_terjual = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Menu
    menu = db.relationship('Menu')
    
    def to_dict(self):
        return {
            'id_penjualan': self.id_penjualan,
            'id_menu': self.id_menu,
            'tanggal': self.tanggal.isoformat(),
            'jumlah_terjual': self.jumlah_terjual,
            'created_at': self.created_at.isoformat()
        }

class LogPemakaian(db.Model):
    """Model for usage logs"""
    __tablename__ = 'log_pemakaian'
    
    id_log = db.Column(db.Integer, primary_key=True)
    id_penjualan = db.Column(db.Integer, db.ForeignKey('penjualan.id_penjualan'), nullable=False)
    id_bahan = db.Column(db.Integer, db.ForeignKey('bahan_baku.id_bahan'), nullable=False)
    jumlah_terpakai = db.Column(db.Float, nullable=False)
    jumlah_waste = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    penjualan = db.relationship('Penjualan')
    bahan = db.relationship('BahanBaku')
    
    def to_dict(self):
        return {
            'id_log': self.id_log,
            'id_penjualan': self.id_penjualan,
            'id_bahan': self.id_bahan,
            'jumlah_terpakai': self.jumlah_terpakai,
            'jumlah_waste': self.jumlah_waste,
            'total_cost': self.total_cost,
            'created_at': self.created_at.isoformat()
        }

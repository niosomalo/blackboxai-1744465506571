from flask import Blueprint, request, jsonify
from database import db
from models import BahanBaku
from errors import ValidationError, ResourceNotFoundError

bahan_bp = Blueprint('bahan', __name__)

@bahan_bp.route('/bahan', methods=['GET'])
def get_all_bahan():
    """Get all raw materials"""
    bahan_list = BahanBaku.query.all()
    return jsonify({
        'status': 'success',
        'data': [bahan.to_dict() for bahan in bahan_list]
    })

@bahan_bp.route('/bahan/<int:id_bahan>', methods=['GET'])
def get_bahan(id_bahan):
    """Get a specific raw material by ID"""
    bahan = BahanBaku.query.get(id_bahan)
    if not bahan:
        raise ResourceNotFoundError(f'Bahan with ID {id_bahan} not found')
    
    return jsonify({
        'status': 'success',
        'data': bahan.to_dict()
    })

@bahan_bp.route('/bahan', methods=['POST'])
def create_bahan():
    """Create a new raw material"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['nama_bahan', 'satuan', 'stok_awal', 'harga_per_gram']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f'Missing required field: {field}')
    
    # Validate numeric fields
    try:
        stok_awal = float(data['stok_awal'])
        harga_per_gram = float(data['harga_per_gram'])
        if stok_awal < 0 or harga_per_gram < 0:
            raise ValueError
    except ValueError:
        raise ValidationError('stok_awal and harga_per_gram must be positive numbers')
    
    # Create new bahan
    bahan = BahanBaku(
        nama_bahan=data['nama_bahan'],
        satuan=data['satuan'],
        stok_awal=stok_awal,
        harga_per_gram=harga_per_gram
    )
    
    db.session.add(bahan)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Bahan created successfully',
        'data': bahan.to_dict()
    }), 201

@bahan_bp.route('/bahan/<int:id_bahan>', methods=['PUT'])
def update_bahan(id_bahan):
    """Update a specific raw material"""
    bahan = BahanBaku.query.get(id_bahan)
    if not bahan:
        raise ResourceNotFoundError(f'Bahan with ID {id_bahan} not found')
    
    data = request.get_json()
    
    # Update fields if provided
    if 'nama_bahan' in data:
        bahan.nama_bahan = data['nama_bahan']
    if 'satuan' in data:
        bahan.satuan = data['satuan']
    if 'stok_awal' in data:
        try:
            stok_awal = float(data['stok_awal'])
            if stok_awal < 0:
                raise ValueError
            bahan.stok_awal = stok_awal
        except ValueError:
            raise ValidationError('stok_awal must be a positive number')
    if 'harga_per_gram' in data:
        try:
            harga_per_gram = float(data['harga_per_gram'])
            if harga_per_gram < 0:
                raise ValueError
            bahan.harga_per_gram = harga_per_gram
        except ValueError:
            raise ValidationError('harga_per_gram must be a positive number')
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Bahan updated successfully',
        'data': bahan.to_dict()
    })

@bahan_bp.route('/bahan/<int:id_bahan>', methods=['DELETE'])
def delete_bahan(id_bahan):
    """Delete a specific raw material"""
    bahan = BahanBaku.query.get(id_bahan)
    if not bahan:
        raise ResourceNotFoundError(f'Bahan with ID {id_bahan} not found')
    
    db.session.delete(bahan)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Bahan deleted successfully'
    })

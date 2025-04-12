from flask import Blueprint, request, jsonify
from database import db
from models import Penjualan, Menu, LogPemakaian, BahanBaku
from errors import ValidationError, ResourceNotFoundError, StockError
from datetime import datetime

penjualan_bp = Blueprint('penjualan', __name__)

def calculate_usage_and_cost(menu, quantity):
    """
    Calculate ingredient usage, waste, and costs for a menu item
    Returns: list of dictionaries containing usage details per ingredient
    """
    usage_details = []
    
    for resep_item in menu.resep:
        bahan = resep_item.bahan
        
        # Calculate quantities
        base_usage = resep_item.jumlah * quantity
        waste_amount = base_usage * (resep_item.waste_percent / 100)
        total_usage = base_usage + waste_amount
        
        # Calculate cost
        cost = total_usage * bahan.harga_per_gram
        
        # Check stock availability
        if total_usage > bahan.stok_awal:
            raise StockError(
                f'Insufficient stock for {bahan.nama_bahan}. ' +
                f'Required: {total_usage:.2f} {bahan.satuan}, ' +
                f'Available: {bahan.stok_awal:.2f} {bahan.satuan}'
            )
        
        usage_details.append({
            'id_bahan': bahan.id_bahan,
            'jumlah_terpakai': base_usage,
            'jumlah_waste': waste_amount,
            'total_usage': total_usage,
            'cost': cost
        })
    
    return usage_details

@penjualan_bp.route('/penjualan', methods=['GET'])
def get_all_penjualan():
    """Get all sales records"""
    penjualan_list = Penjualan.query.all()
    return jsonify({
        'status': 'success',
        'data': [penjualan.to_dict() for penjualan in penjualan_list]
    })

@penjualan_bp.route('/penjualan/<int:id_penjualan>', methods=['GET'])
def get_penjualan(id_penjualan):
    """Get a specific sales record"""
    penjualan = Penjualan.query.get(id_penjualan)
    if not penjualan:
        raise ResourceNotFoundError(f'Penjualan with ID {id_penjualan} not found')
    
    # Get associated usage logs
    logs = LogPemakaian.query.filter_by(id_penjualan=id_penjualan).all()
    
    return jsonify({
        'status': 'success',
        'data': {
            'penjualan': penjualan.to_dict(),
            'usage_logs': [log.to_dict() for log in logs]
        }
    })

@penjualan_bp.route('/penjualan', methods=['POST'])
def create_penjualan():
    """Create a new sales record"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['id_menu', 'tanggal', 'jumlah_terjual']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f'Missing required field: {field}')
    
    # Validate menu exists
    menu = Menu.query.get(data['id_menu'])
    if not menu:
        raise ResourceNotFoundError(f'Menu with ID {data["id_menu"]} not found')
    
    # Validate quantity
    try:
        quantity = int(data['jumlah_terjual'])
        if quantity <= 0:
            raise ValueError
    except ValueError:
        raise ValidationError('jumlah_terjual must be a positive integer')
    
    # Validate and parse date
    try:
        sale_date = datetime.strptime(data['tanggal'], '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError('Invalid date format. Use YYYY-MM-DD')
    
    # Calculate usage and costs
    usage_details = calculate_usage_and_cost(menu, quantity)
    
    # Create sales record
    penjualan = Penjualan(
        id_menu=menu.id_menu,
        tanggal=sale_date,
        jumlah_terjual=quantity
    )
    db.session.add(penjualan)
    
    # Create usage logs and update stock
    total_cost = 0
    for usage in usage_details:
        # Create usage log
        log = LogPemakaian(
            id_penjualan=penjualan.id_penjualan,
            id_bahan=usage['id_bahan'],
            jumlah_terpakai=usage['jumlah_terpakai'],
            jumlah_waste=usage['jumlah_waste'],
            total_cost=usage['cost']
        )
        db.session.add(log)
        
        # Update stock
        bahan = BahanBaku.query.get(usage['id_bahan'])
        bahan.stok_awal -= usage['total_usage']
        
        total_cost += usage['cost']
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Penjualan recorded successfully',
        'data': {
            'penjualan': penjualan.to_dict(),
            'usage_details': usage_details,
            'total_cost': total_cost
        }
    }), 201

@penjualan_bp.route('/penjualan/daily/<string:date>', methods=['GET'])
def get_daily_sales(date):
    """Get sales summary for a specific date"""
    try:
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError('Invalid date format. Use YYYY-MM-DD')
    
    # Get all sales for the date
    sales = Penjualan.query.filter_by(tanggal=target_date).all()
    
    # Calculate totals
    total_sales = len(sales)
    total_items = sum(sale.jumlah_terjual for sale in sales)
    
    # Get usage logs for these sales
    usage_logs = LogPemakaian.query.filter(
        LogPemakaian.id_penjualan.in_([sale.id_penjualan for sale in sales])
    ).all()
    
    # Calculate totals from logs
    total_usage = sum(log.jumlah_terpakai for log in usage_logs)
    total_waste = sum(log.jumlah_waste for log in usage_logs)
    total_cost = sum(log.total_cost for log in usage_logs)
    
    return jsonify({
        'status': 'success',
        'data': {
            'date': date,
            'total_sales': total_sales,
            'total_items_sold': total_items,
            'total_ingredient_usage': total_usage,
            'total_waste': total_waste,
            'total_cost': total_cost,
            'sales': [sale.to_dict() for sale in sales]
        }
    })

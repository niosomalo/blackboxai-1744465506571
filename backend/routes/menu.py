from flask import Blueprint, request, jsonify
from database import db
from models import Menu, Resep, BahanBaku
from errors import ValidationError, ResourceNotFoundError

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/menu', methods=['GET'])
def get_all_menu():
    """Get all menu items with their recipes"""
    menu_list = Menu.query.all()
    return jsonify({
        'status': 'success',
        'data': [menu.to_dict() for menu in menu_list]
    })

@menu_bp.route('/menu/<int:id_menu>', methods=['GET'])
def get_menu(id_menu):
    """Get a specific menu item by ID"""
    menu = Menu.query.get(id_menu)
    if not menu:
        raise ResourceNotFoundError(f'Menu with ID {id_menu} not found')
    
    return jsonify({
        'status': 'success',
        'data': menu.to_dict()
    })

@menu_bp.route('/menu', methods=['POST'])
def create_menu():
    """Create a new menu item with its recipe"""
    data = request.get_json()
    
    # Validate required fields
    if 'nama_menu' not in data:
        raise ValidationError('Missing required field: nama_menu')
    if 'resep' not in data or not isinstance(data['resep'], list):
        raise ValidationError('Menu must include a recipe (list of ingredients)')
    
    # Create new menu
    menu = Menu(nama_menu=data['nama_menu'])
    db.session.add(menu)
    
    # Add recipe items
    for item in data['resep']:
        # Validate recipe item
        required_fields = ['id_bahan', 'jumlah', 'waste_percent']
        for field in required_fields:
            if field not in item:
                raise ValidationError(f'Recipe item missing required field: {field}')
        
        # Validate bahan exists
        bahan = BahanBaku.query.get(item['id_bahan'])
        if not bahan:
            raise ResourceNotFoundError(f'Bahan with ID {item["id_bahan"]} not found')
        
        # Validate numeric fields
        try:
            jumlah = float(item['jumlah'])
            waste_percent = float(item['waste_percent'])
            if jumlah <= 0 or waste_percent < 0:
                raise ValueError
        except ValueError:
            raise ValidationError('jumlah must be positive and waste_percent must be non-negative')
        
        # Create recipe item
        resep = Resep(
            id_bahan=item['id_bahan'],
            jumlah=jumlah,
            waste_percent=waste_percent
        )
        menu.resep.append(resep)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Menu created successfully',
        'data': menu.to_dict()
    }), 201

@menu_bp.route('/menu/<int:id_menu>', methods=['PUT'])
def update_menu(id_menu):
    """Update a menu item and its recipe"""
    menu = Menu.query.get(id_menu)
    if not menu:
        raise ResourceNotFoundError(f'Menu with ID {id_menu} not found')
    
    data = request.get_json()
    
    # Update menu name if provided
    if 'nama_menu' in data:
        menu.nama_menu = data['nama_menu']
    
    # Update recipe if provided
    if 'resep' in data:
        if not isinstance(data['resep'], list):
            raise ValidationError('Recipe must be a list of ingredients')
        
        # Remove existing recipe items
        menu.resep.clear()
        
        # Add new recipe items
        for item in data['resep']:
            # Validate recipe item
            required_fields = ['id_bahan', 'jumlah', 'waste_percent']
            for field in required_fields:
                if field not in item:
                    raise ValidationError(f'Recipe item missing required field: {field}')
            
            # Validate bahan exists
            bahan = BahanBaku.query.get(item['id_bahan'])
            if not bahan:
                raise ResourceNotFoundError(f'Bahan with ID {item["id_bahan"]} not found')
            
            # Validate numeric fields
            try:
                jumlah = float(item['jumlah'])
                waste_percent = float(item['waste_percent'])
                if jumlah <= 0 or waste_percent < 0:
                    raise ValueError
            except ValueError:
                raise ValidationError('jumlah must be positive and waste_percent must be non-negative')
            
            # Create recipe item
            resep = Resep(
                id_bahan=item['id_bahan'],
                jumlah=jumlah,
                waste_percent=waste_percent
            )
            menu.resep.append(resep)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Menu updated successfully',
        'data': menu.to_dict()
    })

@menu_bp.route('/menu/<int:id_menu>', methods=['DELETE'])
def delete_menu(id_menu):
    """Delete a menu item and its recipe"""
    menu = Menu.query.get(id_menu)
    if not menu:
        raise ResourceNotFoundError(f'Menu with ID {id_menu} not found')
    
    db.session.delete(menu)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Menu deleted successfully'
    })

@menu_bp.route('/menu/<int:id_menu>/recipe', methods=['GET'])
def get_menu_recipe(id_menu):
    """Get the recipe for a specific menu item"""
    menu = Menu.query.get(id_menu)
    if not menu:
        raise ResourceNotFoundError(f'Menu with ID {id_menu} not found')
    
    return jsonify({
        'status': 'success',
        'data': {
            'menu': menu.nama_menu,
            'resep': [r.to_dict() for r in menu.resep]
        }
    })

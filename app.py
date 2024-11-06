import os
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.utils import secure_filename
import urllib.parse

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

with app.app_context():
    from models import Listing, Category
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    
    # Create default categories if they don't exist
    default_categories = [
        {"name": "Lights", "description": "Lighting equipment for video and film production"},
        {"name": "Cameras", "description": "Camera bodies, lenses, and accessories"},
        {"name": "Audio", "description": "Microphones, recorders, and audio equipment"},
        {"name": "Accessories", "description": "Various production accessories and tools"}
    ]
    
    for cat_data in default_categories:
        if not Category.query.filter_by(name=cat_data["name"]).first():
            category = Category(**cat_data)
            db.session.add(category)
    db.session.commit()

# Routes
@app.route('/')
def index():
    listings = Listing.query.order_by(Listing.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('index.html', listings=listings, categories=categories)

@app.route('/listing/<int:id>')
def listing_detail(id):
    listing = Listing.query.get_or_404(id)
    return render_template('listing_detail.html', listing=listing)

@app.route('/create', methods=['GET', 'POST'])
def create_listing():
    if request.method == 'POST':
        try:
            category = Category.query.get(request.form['category_id'])
            if not category:
                flash('Invalid category selected.', 'error')
                return redirect(url_for('create_listing'))
                
            listing = Listing(
                title=request.form['title'],
                description=request.form['description'],
                equipment_type=request.form['equipment_type'],
                price=float(request.form['price']),
                contact_name=request.form['contact_name'],
                contact_email=request.form['contact_email'],
                contact_phone=request.form['contact_phone'],
                image_url=request.form.get('image_url', ''),
                category_id=category.id
            )
            db.session.add(listing)
            db.session.commit()
            flash('Listing created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash('Error creating listing.', 'error')
            return redirect(url_for('create_listing'))
    
    categories = Category.query.all()
    return render_template('create_listing.html', categories=categories)

@app.route('/search')
def search():
    category_id = request.args.get('category_id', type=int)
    equipment_type = request.args.get('equipment_type', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    query = Listing.query
    
    if category_id:
        query = query.filter(Listing.category_id == category_id)
    if equipment_type:
        query = query.filter(Listing.equipment_type == equipment_type)
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
        
    listings = query.all()
    return jsonify([{
        'id': l.id,
        'title': l.title,
        'price': l.price,
        'equipment_type': l.equipment_type,
        'image_url': l.image_url,
        'category': l.category.name
    } for l in listings])

# Category Management Routes
@app.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Category name is required.', 'error')
            return redirect(url_for('manage_categories'))
            
        try:
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
        except Exception as e:
            flash('Error creating category.', 'error')
            
    categories = Category.query.all()
    return render_template('manage_categories.html', categories=categories)

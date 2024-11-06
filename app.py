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
    from models import Listing
    db.create_all()

# Routes
@app.route('/')
def index():
    listings = Listing.query.order_by(Listing.created_at.desc()).all()
    return render_template('index.html', listings=listings)

@app.route('/listing/<int:id>')
def listing_detail(id):
    listing = Listing.query.get_or_404(id)
    return render_template('listing_detail.html', listing=listing)

@app.route('/create', methods=['GET', 'POST'])
def create_listing():
    if request.method == 'POST':
        try:
            listing = Listing(
                title=request.form['title'],
                description=request.form['description'],
                equipment_type=request.form['equipment_type'],
                price=float(request.form['price']),
                contact_name=request.form['contact_name'],
                contact_email=request.form['contact_email'],
                contact_phone=request.form['contact_phone'],
                image_url=request.form.get('image_url', '')
            )
            db.session.add(listing)
            db.session.commit()
            flash('Listing created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash('Error creating listing.', 'error')
            return redirect(url_for('create_listing'))
    return render_template('create_listing.html')

@app.route('/search')
def search():
    equipment_type = request.args.get('equipment_type', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    query = Listing.query
    
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
        'image_url': l.image_url
    } for l in listings])

from flask import Blueprint, render_template, current_app
from models import LaptopModel

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main index page - redirect to guest shop"""
    laptop_model = LaptopModel(current_app.db)
    available_laptops = laptop_model.find_all(status='available')
    return render_template('index.html', laptops=available_laptops[:6])  # Show first 6

@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')
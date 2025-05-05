from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from models import db, Build, PreBuiltConfig
from utils import load_component_data, check_compatibility, calculate_total_price
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

# Create a blueprint for builds routes
builds_bp = Blueprint('builds', __name__)

# Define save build form
class SaveBuildForm(FlaskForm):
    name = StringField('Build Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    is_public = BooleanField('Make this build public')
    submit = SubmitField('Save Build')

@builds_bp.route('/save_build', methods=['GET', 'POST'])
def save_build():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to save your build.', 'warning')
        return redirect(url_for('auth.login'))
    
    # Check if there's a PC configuration in the session
    if 'pc_config' not in session or not session['pc_config']:
        flash('Please build a PC configuration first.', 'warning')
        return redirect(url_for('builder'))
    
    form = SaveBuildForm()
    
    if form.validate_on_submit():
        # Calculate total price
        total_price = calculate_total_price(session['pc_config'])
        
        # Create a new build
        new_build = Build(
            name=form.name.data,
            description=form.description.data,
            user_id=session['user_id'],
            is_public=form.is_public.data,
            total_price=total_price
        )
        
        # Add component IDs
        for category, component_id in session['pc_config'].items():
            setattr(new_build, f'{category}_id', component_id)
        
        # Save to database
        db.session.add(new_build)
        db.session.commit()
        
        flash('Your build has been saved!', 'success')
        return redirect(url_for('builds.view_build', build_id=new_build.id))
    
    return render_template('builds/save_build.html', form=form)

@builds_bp.route('/builds')
def list_builds():
    # Get public builds and user's builds if logged in
    public_builds = Build.query.filter_by(is_public=True).order_by(Build.created_at.desc()).all()
    
    user_builds = []
    if 'user_id' in session:
        user_builds = Build.query.filter_by(user_id=session['user_id']).order_by(Build.created_at.desc()).all()
    
    return render_template('builds/list_builds.html', public_builds=public_builds, user_builds=user_builds)

@builds_bp.route('/build/<int:build_id>')
def view_build(build_id):
    # Get the build
    build = Build.query.get_or_404(build_id)
    
    # Check if the build is public or belongs to the logged-in user
    if not build.is_public and ('user_id' not in session or build.user_id != session['user_id']):
        flash('You do not have permission to view this build.', 'danger')
        return redirect(url_for('builds.list_builds'))
    
    # Load component details
    components = load_component_data()
    config_details = {}
    config = {}
    
    # Get component details for each category
    for category in ['cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'case', 'cooling']:
        component_id = getattr(build, f'{category}_id')
        if component_id:
            config[category] = component_id
            category_components = components.get(category, [])
            component = next((c for c in category_components if c['id'] == component_id), None)
            if component:
                config_details[category] = component
    
    # Check compatibility
    compatibility_issues = check_compatibility(config)
    
    return render_template(
        'builds/view_build.html',
        build=build,
        config=config_details,
        compatibility_issues=compatibility_issues
    )

@builds_bp.route('/build/<int:build_id>/load')
def load_build(build_id):
    # Get the build
    build = Build.query.get_or_404(build_id)
    
    # Check if the build belongs to the logged-in user
    if 'user_id' not in session or build.user_id != session['user_id']:
        flash('You do not have permission to load this build.', 'danger')
        return redirect(url_for('builds.list_builds'))
    
    # Load the build into the session
    session['pc_config'] = {}
    for category in ['cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'case', 'cooling']:
        component_id = getattr(build, f'{category}_id')
        if component_id:
            session['pc_config'][category] = component_id
    
    session.modified = True
    
    flash(f'Build "{build.name}" has been loaded.', 'success')
    return redirect(url_for('builder'))

@builds_bp.route('/build/<int:build_id>/delete', methods=['POST'])
def delete_build(build_id):
    # Get the build
    build = Build.query.get_or_404(build_id)
    
    # Check if the build belongs to the logged-in user
    if 'user_id' not in session or build.user_id != session['user_id']:
        flash('You do not have permission to delete this build.', 'danger')
        return redirect(url_for('builds.list_builds'))
    
    # Delete the build
    db.session.delete(build)
    db.session.commit()
    
    flash('Build has been deleted.', 'success')
    return redirect(url_for('auth.profile'))

@builds_bp.route('/prebuilt')
def prebuilt_configs():
    # Get prebuilt configurations
    configs = PreBuiltConfig.query.order_by(PreBuiltConfig.price).all()
    
    # Group by category
    categories = {}
    for config in configs:
        if config.category not in categories:
            categories[config.category] = []
        categories[config.category].append(config)
    
    return render_template('builds/prebuilt.html', categories=categories)

@builds_bp.route('/prebuilt/<int:config_id>/load')
def load_prebuilt(config_id):
    # Get the prebuilt configuration
    config = PreBuiltConfig.query.get_or_404(config_id)
    
    # Load the configuration into the session
    session['pc_config'] = {}
    for category in ['cpu', 'motherboard', 'ram', 'gpu', 'storage', 'power_supply', 'case', 'cooling']:
        component_id = getattr(config, f'{category}_id')
        if component_id:
            session['pc_config'][category] = component_id
    
    session.modified = True
    
    flash(f'Prebuilt configuration "{config.name}" has been loaded.', 'success')
    return redirect(url_for('builder'))
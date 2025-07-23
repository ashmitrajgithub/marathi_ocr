from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, date
from typing import Dict, List, Any
import sqlite3

# Import our custom modules
from blockchain import land_blockchain
from models import db, LandRecord, Property, Ownership, Project, AcquisitionDeclaration, CompensationPayment, CitizenQuery, LitigationCase, User
from ai_analytics import land_ai

# Import OCR functionality from existing app
from PIL import Image
import pytesseract
import pdf2image
import cv2

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'land-acquisition-blockchain-system-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///land_acquisition.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
MAP_FOLDER = 'static/maps'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(MAP_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
CORS(app)
db.init_app(app)
migrate = Migrate(app, db)

# Utility functions
def preprocess_image(image_path, save_as):
    """Grayscale → Denoise → Threshold → Save and return path"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.fastNlMeansDenoising(img, h=30)
    _, img_bw = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite(save_as, img_bw)
    return save_as

def allowed_file(filename):
    """Check if file extension is allowed."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'tiff', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator to require login for certain routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and authentication."""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Login successful',
                'user': user.to_dict()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Invalid username or password'
            }), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    return redirect(url_for('login'))

# Dashboard Routes
@app.route('/')
@login_required
def dashboard():
    """Main dashboard with overview statistics."""
    # Get dashboard data from AI analytics
    dashboard_data = land_ai.generate_acquisition_dashboard_data()
    
    # Get blockchain statistics
    blockchain_stats = land_blockchain.get_blockchain_stats()
    
    # Get recent activities
    recent_activities = get_recent_activities()
    
    return render_template('dashboard.html', 
                         dashboard_data=dashboard_data,
                         blockchain_stats=blockchain_stats,
                         recent_activities=recent_activities)

def get_recent_activities(limit=10):
    """Get recent system activities."""
    activities = []
    
    # Recent acquisitions
    recent_acquisitions = AcquisitionDeclaration.query.order_by(AcquisitionDeclaration.created_at.desc()).limit(5).all()
    for acq in recent_acquisitions:
        activities.append({
            'type': 'ACQUISITION_DECLARED',
            'description': f'Land acquisition declared for survey number {acq.land_record.survey_number}',
            'timestamp': acq.created_at,
            'officer': acq.declaring_officer
        })
    
    # Recent payments
    recent_payments = CompensationPayment.query.order_by(CompensationPayment.created_at.desc()).limit(5).all()
    for payment in recent_payments:
        activities.append({
            'type': 'PAYMENT_MADE',
            'description': f'Compensation paid: ₹{payment.payment_amount} to {payment.owner.owner_name}',
            'timestamp': payment.created_at,
            'officer': payment.authorizing_officer
        })
    
    # Sort by timestamp and return limited results
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    return activities[:limit]

# Land Records Management
@app.route('/api/land-records', methods=['GET', 'POST'])
@login_required
def manage_land_records():
    """Manage land records - list and create."""
    if request.method == 'POST':
        data = request.get_json()
        
        # Create new land record
        land_record = LandRecord(
            survey_number=data['survey_number'],
            sub_division=data.get('sub_division'),
            village=data['village'],
            tehsil=data['tehsil'],
            district=data['district'],
            total_area=float(data['total_area']),
            area_unit=data.get('area_unit', 'acres'),
            land_type=data['land_type'],
            land_classification=data.get('land_classification'),
            old_map_reference=data.get('old_map_reference'),
            map_image_path=data.get('map_image_path')
        )
        
        db.session.add(land_record)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Land record created successfully',
            'land_record': land_record.to_dict()
        })
    
    else:
        # Get land records with filtering
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        village = request.args.get('village')
        tehsil = request.args.get('tehsil')
        district = request.args.get('district')
        
        query = LandRecord.query
        
        if village:
            query = query.filter(LandRecord.village.ilike(f'%{village}%'))
        if tehsil:
            query = query.filter(LandRecord.tehsil.ilike(f'%{tehsil}%'))
        if district:
            query = query.filter(LandRecord.district.ilike(f'%{district}%'))
        
        land_records = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'status': 'success',
            'land_records': [record.to_dict() for record in land_records.items],
            'pagination': {
                'page': page,
                'pages': land_records.pages,
                'per_page': per_page,
                'total': land_records.total
            }
        })

@app.route('/api/land-records/<int:record_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def land_record_detail(record_id):
    """Get, update, or delete a specific land record."""
    land_record = LandRecord.query.get_or_404(record_id)
    
    if request.method == 'GET':
        # Get detailed information including related data
        record_data = land_record.to_dict()
        record_data['properties'] = [prop.to_dict() for prop in land_record.properties]
        record_data['ownerships'] = [owner.to_dict() for owner in land_record.ownerships]
        record_data['acquisitions'] = [acq.to_dict() for acq in land_record.acquisitions]
        
        # Get blockchain transactions for this survey number
        blockchain_transactions = land_blockchain.get_transactions_by_survey_number(land_record.survey_number)
        record_data['blockchain_transactions'] = blockchain_transactions
        
        return jsonify({
            'status': 'success',
            'land_record': record_data
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        # Update land record
        for key, value in data.items():
            if hasattr(land_record, key) and key != 'id':
                setattr(land_record, key, value)
        
        land_record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Land record updated successfully',
            'land_record': land_record.to_dict()
        })
    
    elif request.method == 'DELETE':
        db.session.delete(land_record)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Land record deleted successfully'
        })

# Project Management
@app.route('/api/projects', methods=['GET', 'POST'])
@login_required
def manage_projects():
    """Manage projects - list and create."""
    if request.method == 'POST':
        data = request.get_json()
        
        # Create new project
        project = Project(
            project_name=data['project_name'],
            project_code=data['project_code'],
            project_type=data['project_type'],
            description=data.get('description'),
            implementing_agency=data['implementing_agency'],
            project_officer=data.get('project_officer'),
            districts_covered=json.dumps(data.get('districts_covered', [])),
            total_land_required=data.get('total_land_required'),
            project_start_date=datetime.strptime(data['project_start_date'], '%Y-%m-%d').date() if data.get('project_start_date') else None,
            expected_completion_date=datetime.strptime(data['expected_completion_date'], '%Y-%m-%d').date() if data.get('expected_completion_date') else None,
            land_acquisition_deadline=datetime.strptime(data['land_acquisition_deadline'], '%Y-%m-%d').date() if data.get('land_acquisition_deadline') else None,
            total_project_cost=data.get('total_project_cost'),
            land_acquisition_budget=data.get('land_acquisition_budget'),
            project_status=data.get('project_status', 'PLANNING')
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Project created successfully',
            'project': project.to_dict()
        })
    
    else:
        projects = Project.query.all()
        return jsonify({
            'status': 'success',
            'projects': [project.to_dict() for project in projects]
        })

# Acquisition Declaration (Award)
@app.route('/api/acquisitions', methods=['GET', 'POST'])
@login_required
def manage_acquisitions():
    """Manage acquisition declarations."""
    if request.method == 'POST':
        data = request.get_json()
        
        # Create acquisition declaration
        acquisition = AcquisitionDeclaration(
            project_id=data['project_id'],
            land_record_id=data['land_record_id'],
            declaration_number=data['declaration_number'],
            declaration_date=datetime.strptime(data['declaration_date'], '%Y-%m-%d').date(),
            notification_number=data.get('notification_number'),
            land_compensation_rate=float(data['land_compensation_rate']),
            solatium_percentage=float(data.get('solatium_percentage', 100.0)),
            area_to_acquire=float(data.get('area_to_acquire', 0)),
            declaring_officer=session.get('username', 'Unknown'),
            officer_designation=data.get('officer_designation')
        )
        
        # Calculate total compensation
        land_record = LandRecord.query.get(data['land_record_id'])
        area_to_acquire = acquisition.area_to_acquire or land_record.total_area
        
        land_compensation = area_to_acquire * acquisition.land_compensation_rate
        solatium = land_compensation * (acquisition.solatium_percentage / 100)
        acquisition.total_land_compensation = land_compensation
        acquisition.total_compensation = land_compensation + solatium
        
        db.session.add(acquisition)
        db.session.commit()
        
        # Update land record status
        land_record.acquisition_status = 'DECLARED'
        db.session.commit()
        
        # Create blockchain entry
        project = Project.query.get(data['project_id'])
        tx_id = land_blockchain.create_award_declaration(
            project_name=project.project_name,
            survey_numbers=[land_record.survey_number],
            village=land_record.village,
            tehsil=land_record.tehsil,
            district=land_record.district,
            compensation_rate=acquisition.land_compensation_rate,
            officer_id=session.get('username', 'Unknown')
        )
        
        # Mine the blockchain transaction
        land_blockchain.mine_pending_transactions()
        
        return jsonify({
            'status': 'success',
            'message': 'Acquisition declared successfully',
            'acquisition': acquisition.to_dict(),
            'blockchain_tx_id': tx_id
        })
    
    else:
        acquisitions = AcquisitionDeclaration.query.all()
        return jsonify({
            'status': 'success',
            'acquisitions': [acq.to_dict() for acq in acquisitions]
        })

# Compensation Payment
@app.route('/api/payments', methods=['GET', 'POST'])
@login_required
def manage_payments():
    """Manage compensation payments."""
    if request.method == 'POST':
        data = request.get_json()
        
        # Create compensation payment
        payment = CompensationPayment(
            acquisition_id=data['acquisition_id'],
            ownership_id=data['ownership_id'],
            payment_reference=data['payment_reference'],
            payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date(),
            payment_amount=float(data['payment_amount']),
            land_compensation=float(data.get('land_compensation', 0)),
            property_compensation=float(data.get('property_compensation', 0)),
            solatium_amount=float(data.get('solatium_amount', 0)),
            payment_method=data.get('payment_method', 'DBT'),
            transaction_id=data.get('transaction_id'),
            authorizing_officer=session.get('username', 'Unknown'),
            disbursing_officer=data.get('disbursing_officer')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Update acquisition status
        acquisition = AcquisitionDeclaration.query.get(data['acquisition_id'])
        ownership = Ownership.query.get(data['ownership_id'])
        
        # Create blockchain entry
        tx_id = land_blockchain.create_compensation_payment(
            survey_number=acquisition.land_record.survey_number,
            property_number=f"PROP_{acquisition.land_record.id}",
            beneficiary_name=ownership.owner_name,
            beneficiary_account=ownership.bank_account_number or 'N/A',
            amount=payment.payment_amount,
            payment_method=payment.payment_method,
            officer_id=session.get('username', 'Unknown')
        )
        
        # Mine the blockchain transaction
        land_blockchain.mine_pending_transactions()
        
        return jsonify({
            'status': 'success',
            'message': 'Payment recorded successfully',
            'payment': payment.to_dict(),
            'blockchain_tx_id': tx_id
        })
    
    else:
        payments = CompensationPayment.query.all()
        return jsonify({
            'status': 'success',
            'payments': [payment.to_dict() for payment in payments]
        })

# Citizen Query Management
@app.route('/api/queries', methods=['GET', 'POST'])
@login_required
def manage_queries():
    """Manage citizen queries and complaints."""
    if request.method == 'POST':
        data = request.get_json()
        
        # Create citizen query
        query = CitizenQuery(
            acquisition_id=data.get('acquisition_id'),
            query_number=data['query_number'],
            query_date=datetime.strptime(data['query_date'], '%Y-%m-%d').date(),
            query_type=data['query_type'],
            complainant_name=data['complainant_name'],
            complainant_contact=data.get('complainant_contact'),
            complainant_address=data.get('complainant_address'),
            subject=data['subject'],
            description=data['description'],
            priority=data.get('priority', 'NORMAL')
        )
        
        db.session.add(query)
        db.session.commit()
        
        # Create blockchain entry
        survey_number = 'GENERAL'
        if query.acquisition_id:
            acquisition = AcquisitionDeclaration.query.get(query.acquisition_id)
            survey_number = acquisition.land_record.survey_number
        
        tx_id = land_blockchain.create_query_record(
            survey_number=survey_number,
            query_type=query.query_type,
            complainant_name=query.complainant_name,
            query_details=query.description,
            officer_id=session.get('username', 'Unknown')
        )
        
        # Mine the blockchain transaction
        land_blockchain.mine_pending_transactions()
        
        return jsonify({
            'status': 'success',
            'message': 'Query recorded successfully',
            'query': query.to_dict(),
            'blockchain_tx_id': tx_id
        })
    
    else:
        queries = CitizenQuery.query.all()
        return jsonify({
            'status': 'success',
            'queries': [query.to_dict() for query in queries]
        })

# OCR Document Processing
@app.route('/api/ocr/upload', methods=['POST'])
@login_required
def upload_document():
    """Upload and process documents using OCR."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    text_output = ""

    try:
        if filename.lower().endswith('.pdf'):
            images = pdf2image.convert_from_path(file_path)
            for i, image in enumerate(images):
                page_path = os.path.join(PROCESSED_FOLDER, f'page_{i}.png')
                image.save(page_path)

                bw_path = os.path.join(PROCESSED_FOLDER, f'page_{i}_bw.png')
                preprocessed_path = preprocess_image(page_path, bw_path)

                pil_img = Image.open(preprocessed_path)
                text = pytesseract.image_to_string(pil_img, lang='mar+eng')
                text_output += text + "\n"
        else:
            img = Image.open(file_path)
            img_path = os.path.join(PROCESSED_FOLDER, 'image_input.png')
            img.save(img_path)

            bw_path = os.path.join(PROCESSED_FOLDER, 'image_input_bw.png')
            preprocessed_path = preprocess_image(img_path, bw_path)

            pil_img = Image.open(preprocessed_path)
            text_output = pytesseract.image_to_string(pil_img, lang='mar+eng')

        return jsonify({
            'status': 'success',
            'extracted_text': text_output.strip(),
            'filename': filename
        })

    except Exception as e:
        return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500

# AI Analytics and Predictions
@app.route('/api/ai/dashboard-data')
@login_required
def get_ai_dashboard_data():
    """Get AI-powered dashboard data."""
    dashboard_data = land_ai.generate_acquisition_dashboard_data()
    return jsonify(dashboard_data)

@app.route('/api/ai/predict-compensation', methods=['POST'])
@login_required
def predict_compensation():
    """Predict compensation amount using AI."""
    data = request.get_json()
    
    prediction = land_ai.predict_compensation(
        land_area=float(data['land_area']),
        owner_count=int(data['owner_count']),
        property_count=int(data['property_count']),
        land_type=data['land_type'],
        district=data['district'],
        project_type=data['project_type'],
        compensation_rate=float(data['compensation_rate'])
    )
    
    return jsonify(prediction)

@app.route('/api/ai/predict-litigation', methods=['POST'])
@login_required
def predict_litigation():
    """Predict litigation risk using AI."""
    data = request.get_json()
    
    prediction = land_ai.predict_litigation_risk(
        land_area=float(data['land_area']),
        owner_count=int(data['owner_count']),
        property_count=int(data['property_count']),
        compensation_amount=float(data['compensation_amount']),
        query_count=int(data['query_count']),
        land_type=data['land_type'],
        district=data['district'],
        project_type=data['project_type']
    )
    
    return jsonify(prediction)

@app.route('/api/ai/project-report/<project_name>')
@login_required
def get_project_ai_report(project_name):
    """Get AI-powered predictive report for a project."""
    report = land_ai.generate_predictive_report(project_name)
    return jsonify(report)

# Blockchain API
@app.route('/api/blockchain/stats')
@login_required
def get_blockchain_stats():
    """Get blockchain statistics."""
    stats = land_blockchain.get_blockchain_stats()
    return jsonify(stats)

@app.route('/api/blockchain/transactions/<survey_number>')
@login_required
def get_blockchain_transactions(survey_number):
    """Get blockchain transactions for a survey number."""
    transactions = land_blockchain.get_transactions_by_survey_number(survey_number)
    return jsonify({
        'status': 'success',
        'survey_number': survey_number,
        'transactions': transactions
    })

@app.route('/api/blockchain/mine')
@login_required
def mine_blockchain():
    """Mine pending blockchain transactions."""
    if session.get('role') not in ['ADMIN', 'SENIOR_OFFICER']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    success = land_blockchain.mine_pending_transactions()
    return jsonify({
        'status': 'success' if success else 'no_pending_transactions',
        'message': 'Transactions mined successfully' if success else 'No pending transactions to mine'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
def create_tables():
    """Create database tables and initialize system."""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@landacquisition.gov.in',
                password_hash=generate_password_hash('admin123'),
                full_name='System Administrator',
                employee_id='ADMIN001',
                designation='System Administrator',
                department='Land Acquisition Department',
                role='ADMIN'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username=admin, password=admin123")

if __name__ == '__main__':
    print("🏗️  Land Acquisition Blockchain System Starting...")
    print("🔗 Blockchain initialized with immutable ledger")
    print("🤖 AI analytics ready for predictive insights")
    print("📊 Dashboard available at http://127.0.0.1:5000")
    print("👤 Default login: admin / admin123")
    
    # Initialize database and create tables
    create_tables()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
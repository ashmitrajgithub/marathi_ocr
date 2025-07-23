from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import List, Dict, Optional
import json

db = SQLAlchemy()

class LandRecord(db.Model):
    """
    Core land record model representing individual survey numbers/plots.
    This is the foundation of the land acquisition system.
    """
    __tablename__ = 'land_records'
    
    id = db.Column(db.Integer, primary_key=True)
    survey_number = db.Column(db.String(50), nullable=False, index=True)
    sub_division = db.Column(db.String(20), nullable=True)  # For subdivided plots
    village = db.Column(db.String(100), nullable=False, index=True)
    tehsil = db.Column(db.String(100), nullable=False, index=True)
    district = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False, default='Maharashtra')
    
    # Land characteristics
    total_area = db.Column(db.Float, nullable=False)  # In acres or hectares
    area_unit = db.Column(db.String(20), default='acres')
    land_type = db.Column(db.String(50), nullable=False)  # Agricultural, Non-agricultural, etc.
    land_classification = db.Column(db.String(100))  # Irrigated, Dry, etc.
    
    # Current status
    acquisition_status = db.Column(db.String(50), default='NOT_ACQUIRED')  # NOT_ACQUIRED, DECLARED, ACQUIRED, PAID
    is_under_litigation = db.Column(db.Boolean, default=False)
    
    # Map references
    old_map_reference = db.Column(db.String(200))  # Reference to scanned old map
    map_image_path = db.Column(db.String(500))  # Path to scanned map image
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    properties = db.relationship('Property', backref='land_record', lazy=True, cascade='all, delete-orphan')
    ownerships = db.relationship('Ownership', backref='land_record', lazy=True, cascade='all, delete-orphan')
    acquisitions = db.relationship('AcquisitionDeclaration', backref='land_record', lazy=True)
    
    def __repr__(self):
        return f'<LandRecord {self.survey_number} - {self.village}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'survey_number': self.survey_number,
            'sub_division': self.sub_division,
            'village': self.village,
            'tehsil': self.tehsil,
            'district': self.district,
            'total_area': self.total_area,
            'area_unit': self.area_unit,
            'land_type': self.land_type,
            'acquisition_status': self.acquisition_status,
            'is_under_litigation': self.is_under_litigation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Property(db.Model):
    """
    Represents structures/properties on land (houses, industries, trees, crops).
    Multiple properties can exist on a single land record.
    """
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    land_record_id = db.Column(db.Integer, db.ForeignKey('land_records.id'), nullable=False)
    property_number = db.Column(db.String(50), nullable=False, index=True)
    
    # Property details
    property_type = db.Column(db.String(50), nullable=False)  # HOUSE, INDUSTRY, TREE, CROP, SHOP, etc.
    property_subtype = db.Column(db.String(100))  # Pucca house, Kutcha house, Mango tree, etc.
    description = db.Column(db.Text)
    
    # Valuation
    assessed_value = db.Column(db.Float, default=0.0)
    valuation_date = db.Column(db.Date)
    valuation_method = db.Column(db.String(100))  # Government rate, Market rate, etc.
    
    # Physical characteristics
    area_occupied = db.Column(db.Float)  # Area occupied by this property
    construction_year = db.Column(db.Integer)
    condition = db.Column(db.String(50))  # Good, Fair, Poor
    
    # Status
    compensation_status = db.Column(db.String(50), default='PENDING')  # PENDING, CALCULATED, PAID
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Property {self.property_number} - {self.property_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'property_number': self.property_number,
            'property_type': self.property_type,
            'property_subtype': self.property_subtype,
            'description': self.description,
            'assessed_value': self.assessed_value,
            'area_occupied': self.area_occupied,
            'compensation_status': self.compensation_status
        }

class Ownership(db.Model):
    """
    Represents ownership details for land records.
    Handles multiple owners with undivided shares.
    """
    __tablename__ = 'ownerships'
    
    id = db.Column(db.Integer, primary_key=True)
    land_record_id = db.Column(db.Integer, db.ForeignKey('land_records.id'), nullable=False)
    
    # Owner details
    owner_name = db.Column(db.String(200), nullable=False, index=True)
    father_name = db.Column(db.String(200))
    owner_type = db.Column(db.String(50), default='INDIVIDUAL')  # INDIVIDUAL, JOINT, COMPANY, TRUST
    
    # Contact information
    address = db.Column(db.Text)
    phone_number = db.Column(db.String(20))
    aadhar_number = db.Column(db.String(20), index=True)
    pan_number = db.Column(db.String(20))
    
    # Banking details for compensation
    bank_account_number = db.Column(db.String(50))
    bank_ifsc = db.Column(db.String(20))
    bank_name = db.Column(db.String(200))
    
    # Ownership details
    ownership_share = db.Column(db.Float, default=1.0)  # Share in decimal (0.5 for 50%)
    ownership_type = db.Column(db.String(50), default='ABSOLUTE')  # ABSOLUTE, JOINT, LIFE_INTEREST
    
    # Legal status
    is_legal_heir = db.Column(db.Boolean, default=False)
    succession_certificate = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    compensations = db.relationship('CompensationPayment', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<Ownership {self.owner_name} - {self.ownership_share}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'owner_name': self.owner_name,
            'father_name': self.father_name,
            'owner_type': self.owner_type,
            'address': self.address,
            'phone_number': self.phone_number,
            'ownership_share': self.ownership_share,
            'ownership_type': self.ownership_type,
            'bank_account_number': self.bank_account_number,
            'bank_name': self.bank_name
        }

class Project(db.Model):
    """
    Represents government projects requiring land acquisition.
    """
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    project_code = db.Column(db.String(50), unique=True, index=True)
    project_type = db.Column(db.String(100), nullable=False)  # HIGHWAY, RAILWAY, AIRPORT, PORT, etc.
    
    # Project details
    description = db.Column(db.Text)
    implementing_agency = db.Column(db.String(200), nullable=False)
    project_officer = db.Column(db.String(200))
    
    # Location
    districts_covered = db.Column(db.Text)  # JSON array of districts
    total_land_required = db.Column(db.Float)  # In acres/hectares
    
    # Timeline
    project_start_date = db.Column(db.Date)
    expected_completion_date = db.Column(db.Date)
    land_acquisition_deadline = db.Column(db.Date)
    
    # Budget
    total_project_cost = db.Column(db.Float)
    land_acquisition_budget = db.Column(db.Float)
    
    # Status
    project_status = db.Column(db.String(50), default='PLANNING')  # PLANNING, APPROVED, ONGOING, COMPLETED
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    acquisitions = db.relationship('AcquisitionDeclaration', backref='project', lazy=True)
    
    def __repr__(self):
        return f'<Project {self.project_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_name': self.project_name,
            'project_code': self.project_code,
            'project_type': self.project_type,
            'description': self.description,
            'implementing_agency': self.implementing_agency,
            'project_status': self.project_status,
            'total_land_required': self.total_land_required,
            'land_acquisition_budget': self.land_acquisition_budget
        }

class AcquisitionDeclaration(db.Model):
    """
    Represents official acquisition declarations (awards) for specific land parcels.
    """
    __tablename__ = 'acquisition_declarations'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    land_record_id = db.Column(db.Integer, db.ForeignKey('land_records.id'), nullable=False)
    
    # Declaration details
    declaration_number = db.Column(db.String(100), nullable=False, unique=True, index=True)
    declaration_date = db.Column(db.Date, nullable=False)
    notification_number = db.Column(db.String(100))
    
    # Compensation details
    land_compensation_rate = db.Column(db.Float, nullable=False)  # Per unit area
    solatium_percentage = db.Column(db.Float, default=100.0)  # Additional compensation %
    total_land_compensation = db.Column(db.Float)
    total_property_compensation = db.Column(db.Float, default=0.0)
    total_compensation = db.Column(db.Float)
    
    # Legal details
    acquisition_type = db.Column(db.String(50), default='FULL')  # FULL, PARTIAL
    area_to_acquire = db.Column(db.Float)  # Area being acquired
    
    # Status
    declaration_status = db.Column(db.String(50), default='DECLARED')  # DECLARED, POSSESSION_TAKEN, COMPLETED
    objection_period_end = db.Column(db.Date)
    
    # Officer details
    declaring_officer = db.Column(db.String(200), nullable=False)
    officer_designation = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    compensations = db.relationship('CompensationPayment', backref='acquisition', lazy=True)
    queries = db.relationship('CitizenQuery', backref='acquisition', lazy=True)
    
    def __repr__(self):
        return f'<AcquisitionDeclaration {self.declaration_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'declaration_number': self.declaration_number,
            'declaration_date': self.declaration_date.isoformat() if self.declaration_date else None,
            'land_compensation_rate': self.land_compensation_rate,
            'total_compensation': self.total_compensation,
            'declaration_status': self.declaration_status,
            'declaring_officer': self.declaring_officer,
            'area_to_acquire': self.area_to_acquire
        }

class CompensationPayment(db.Model):
    """
    Records actual compensation payments made to beneficiaries.
    """
    __tablename__ = 'compensation_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    acquisition_id = db.Column(db.Integer, db.ForeignKey('acquisition_declarations.id'), nullable=False)
    ownership_id = db.Column(db.Integer, db.ForeignKey('ownerships.id'), nullable=False)
    
    # Payment details
    payment_reference = db.Column(db.String(100), unique=True, nullable=False, index=True)
    payment_date = db.Column(db.Date, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    
    # Payment breakdown
    land_compensation = db.Column(db.Float, default=0.0)
    property_compensation = db.Column(db.Float, default=0.0)
    solatium_amount = db.Column(db.Float, default=0.0)
    interest_amount = db.Column(db.Float, default=0.0)
    other_compensation = db.Column(db.Float, default=0.0)
    
    # Payment method
    payment_method = db.Column(db.String(50), default='DBT')  # DBT, CHEQUE, CASH, RTGS
    transaction_id = db.Column(db.String(100))
    bank_reference = db.Column(db.String(100))
    
    # Status
    payment_status = db.Column(db.String(50), default='COMPLETED')  # PENDING, COMPLETED, FAILED, REVERSED
    
    # Officer details
    authorizing_officer = db.Column(db.String(200), nullable=False)
    disbursing_officer = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompensationPayment {self.payment_reference} - ₹{self.payment_amount}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'payment_reference': self.payment_reference,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_amount': self.payment_amount,
            'land_compensation': self.land_compensation,
            'property_compensation': self.property_compensation,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'authorizing_officer': self.authorizing_officer
        }

class CitizenQuery(db.Model):
    """
    Records citizen queries, complaints, and objections.
    """
    __tablename__ = 'citizen_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    acquisition_id = db.Column(db.Integer, db.ForeignKey('acquisition_declarations.id'), nullable=True)
    
    # Query details
    query_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    query_date = db.Column(db.Date, nullable=False)
    query_type = db.Column(db.String(50), nullable=False)  # OBJECTION, COMPLAINT, INQUIRY, CORRECTION
    
    # Complainant details
    complainant_name = db.Column(db.String(200), nullable=False)
    complainant_contact = db.Column(db.String(20))
    complainant_address = db.Column(db.Text)
    
    # Query content
    subject = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    supporting_documents = db.Column(db.Text)  # JSON array of document paths
    
    # Response
    response_date = db.Column(db.Date)
    response_details = db.Column(db.Text)
    responding_officer = db.Column(db.String(200))
    
    # Status
    query_status = db.Column(db.String(50), default='RECEIVED')  # RECEIVED, UNDER_REVIEW, RESOLVED, CLOSED
    priority = db.Column(db.String(20), default='NORMAL')  # LOW, NORMAL, HIGH, URGENT
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CitizenQuery {self.query_number} - {self.query_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'query_number': self.query_number,
            'query_date': self.query_date.isoformat() if self.query_date else None,
            'query_type': self.query_type,
            'complainant_name': self.complainant_name,
            'subject': self.subject,
            'description': self.description,
            'query_status': self.query_status,
            'priority': self.priority,
            'response_date': self.response_date.isoformat() if self.response_date else None
        }

class LitigationCase(db.Model):
    """
    Records litigation cases related to land acquisition.
    """
    __tablename__ = 'litigation_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    land_record_id = db.Column(db.Integer, db.ForeignKey('land_records.id'), nullable=False)
    
    # Case details
    case_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    case_type = db.Column(db.String(50), nullable=False)  # COMPENSATION_DISPUTE, OWNERSHIP_DISPUTE, etc.
    court_name = db.Column(db.String(200), nullable=False)
    court_level = db.Column(db.String(50))  # DISTRICT, HIGH, SUPREME
    
    # Parties
    petitioner_name = db.Column(db.String(200), nullable=False)
    respondent_name = db.Column(db.String(200), nullable=False)
    
    # Case timeline
    filing_date = db.Column(db.Date, nullable=False)
    first_hearing_date = db.Column(db.Date)
    last_hearing_date = db.Column(db.Date)
    next_hearing_date = db.Column(db.Date)
    
    # Case details
    case_subject = db.Column(db.String(500))
    case_description = db.Column(db.Text)
    compensation_claimed = db.Column(db.Float)
    
    # Status
    case_status = db.Column(db.String(50), default='PENDING')  # PENDING, DISPOSED, WITHDRAWN, SETTLED
    judgment_date = db.Column(db.Date)
    judgment_summary = db.Column(db.Text)
    
    # Legal representation
    government_counsel = db.Column(db.String(200))
    petitioner_counsel = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LitigationCase {self.case_number} - {self.case_status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_number': self.case_number,
            'case_type': self.case_type,
            'court_name': self.court_name,
            'petitioner_name': self.petitioner_name,
            'filing_date': self.filing_date.isoformat() if self.filing_date else None,
            'case_status': self.case_status,
            'next_hearing_date': self.next_hearing_date.isoformat() if self.next_hearing_date else None,
            'compensation_claimed': self.compensation_claimed
        }

class User(db.Model):
    """
    System users (government officers) with different access levels.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Personal details
    full_name = db.Column(db.String(200), nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    
    # Contact
    phone_number = db.Column(db.String(20))
    office_address = db.Column(db.Text)
    
    # System access
    role = db.Column(db.String(50), default='OFFICER')  # ADMIN, SENIOR_OFFICER, OFFICER, VIEWER
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username} - {self.designation}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'employee_id': self.employee_id,
            'designation': self.designation,
            'department': self.department,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
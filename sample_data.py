#!/usr/bin/env python3
"""
Sample Data Initialization Script for Land Acquisition Blockchain System

This script populates the system with realistic sample data for demonstration purposes.
It includes land records, projects, acquisitions, payments, and blockchain transactions.

Usage:
    python sample_data.py
"""

import sys
import os
from datetime import datetime, date, timedelta
import random
from faker import Faker

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from land_acquisition_app import app, db
from models import (
    LandRecord, Property, Ownership, Project, AcquisitionDeclaration, 
    CompensationPayment, CitizenQuery, LitigationCase, User
)
from blockchain import land_blockchain
from werkzeug.security import generate_password_hash

# Initialize Faker for generating realistic data
fake = Faker('en_IN')  # Indian locale for realistic names and addresses

def create_sample_users():
    """Create sample users with different roles."""
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@landacquisition.gov.in',
            'password': 'admin123',
            'full_name': 'System Administrator',
            'employee_id': 'ADMIN001',
            'designation': 'System Administrator',
            'department': 'Land Acquisition Department',
            'role': 'ADMIN'
        },
        {
            'username': 'collector_pune',
            'email': 'collector.pune@maharashtra.gov.in',
            'password': 'collector123',
            'full_name': 'Dr. Rajesh Kumar',
            'employee_id': 'COL001',
            'designation': 'District Collector',
            'department': 'Revenue Department',
            'role': 'SENIOR_OFFICER'
        },
        {
            'username': 'officer_mumbai',
            'email': 'officer.mumbai@maharashtra.gov.in',
            'password': 'officer123',
            'full_name': 'Mrs. Priya Sharma',
            'employee_id': 'OFF001',
            'designation': 'Land Acquisition Officer',
            'department': 'Land Acquisition Department',
            'role': 'OFFICER'
        },
        {
            'username': 'clerk_nashik',
            'email': 'clerk.nashik@maharashtra.gov.in',
            'password': 'clerk123',
            'full_name': 'Mr. Suresh Patil',
            'employee_id': 'CLK001',
            'designation': 'Senior Clerk',
            'department': 'Revenue Department',
            'role': 'VIEWER'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                full_name=user_data['full_name'],
                employee_id=user_data['employee_id'],
                designation=user_data['designation'],
                department=user_data['department'],
                role=user_data['role']
            )
            db.session.add(user)
            created_users.append(user)
            print(f"✓ Created user: {user_data['username']} ({user_data['role']})")
        else:
            created_users.append(existing_user)
            print(f"- User already exists: {user_data['username']}")
    
    db.session.commit()
    return created_users

def create_sample_projects():
    """Create sample government projects."""
    projects_data = [
        {
            'project_name': 'Mumbai-Nagpur Expressway Phase 2',
            'project_code': 'MNE-P2-2024',
            'project_type': 'HIGHWAY',
            'description': 'Extension of Mumbai-Nagpur Expressway covering 150km through Pune and Nashik districts',
            'implementing_agency': 'Maharashtra State Road Development Corporation',
            'project_officer': 'Dr. Rajesh Kumar',
            'districts_covered': ['Pune', 'Nashik', 'Ahmednagar'],
            'total_land_required': 2500.0,  # acres
            'project_start_date': date(2024, 1, 15),
            'expected_completion_date': date(2026, 12, 31),
            'land_acquisition_deadline': date(2025, 6, 30),
            'total_project_cost': 15000000000.0,  # 150 Crores
            'land_acquisition_budget': 3000000000.0,  # 30 Crores
            'project_status': 'ONGOING'
        },
        {
            'project_name': 'Pune Metro Rail Phase 3',
            'project_code': 'PMR-P3-2024',
            'project_type': 'RAILWAY',
            'description': 'Pune Metro Rail extension from Hinjewadi to Wakad covering 25km',
            'implementing_agency': 'Maharashtra Metro Rail Corporation Limited',
            'project_officer': 'Mrs. Priya Sharma',
            'districts_covered': ['Pune'],
            'total_land_required': 800.0,
            'project_start_date': date(2024, 3, 1),
            'expected_completion_date': date(2027, 3, 31),
            'land_acquisition_deadline': date(2025, 9, 30),
            'total_project_cost': 8000000000.0,  # 80 Crores
            'land_acquisition_budget': 1600000000.0,  # 16 Crores
            'project_status': 'ONGOING'
        },
        {
            'project_name': 'New Pune International Airport',
            'project_code': 'NPIA-2024',
            'project_type': 'AIRPORT',
            'description': 'Construction of new international airport at Purandar, Pune',
            'implementing_agency': 'Airport Authority of India',
            'project_officer': 'Dr. Rajesh Kumar',
            'districts_covered': ['Pune'],
            'total_land_required': 5000.0,
            'project_start_date': date(2024, 6, 1),
            'expected_completion_date': date(2029, 12, 31),
            'land_acquisition_deadline': date(2026, 3, 31),
            'total_project_cost': 25000000000.0,  # 250 Crores
            'land_acquisition_budget': 7500000000.0,  # 75 Crores
            'project_status': 'PLANNING'
        }
    ]
    
    created_projects = []
    for proj_data in projects_data:
        # Check if project already exists
        existing_project = Project.query.filter_by(project_name=proj_data['project_name']).first()
        if not existing_project:
            project = Project(
                project_name=proj_data['project_name'],
                project_code=proj_data['project_code'],
                project_type=proj_data['project_type'],
                description=proj_data['description'],
                implementing_agency=proj_data['implementing_agency'],
                project_officer=proj_data['project_officer'],
                districts_covered=str(proj_data['districts_covered']),
                total_land_required=proj_data['total_land_required'],
                project_start_date=proj_data['project_start_date'],
                expected_completion_date=proj_data['expected_completion_date'],
                land_acquisition_deadline=proj_data['land_acquisition_deadline'],
                total_project_cost=proj_data['total_project_cost'],
                land_acquisition_budget=proj_data['land_acquisition_budget'],
                project_status=proj_data['project_status']
            )
            db.session.add(project)
            created_projects.append(project)
            print(f"✓ Created project: {proj_data['project_name']}")
        else:
            created_projects.append(existing_project)
            print(f"- Project already exists: {proj_data['project_name']}")
    
    db.session.commit()
    return created_projects

def create_sample_land_records(num_records=50):
    """Create sample land records with realistic data."""
    villages = [
        'Katraj', 'Warje', 'Kothrud', 'Baner', 'Wakad', 'Hinjewadi',
        'Hadapsar', 'Kharadi', 'Wagholi', 'Manjri', 'Undri', 'Kondhwa'
    ]
    
    tehsils = ['Pune City', 'Haveli', 'Mulshi', 'Maval']
    districts = ['Pune', 'Nashik', 'Ahmednagar']
    land_types = ['Agricultural', 'Non-Agricultural', 'Industrial', 'Residential']
    
    created_records = []
    
    for i in range(num_records):
        # Generate realistic survey number
        survey_number = f"{random.randint(100, 999)}/{random.randint(1, 20)}"
        
        # Check if survey number already exists
        existing_record = LandRecord.query.filter_by(survey_number=survey_number).first()
        if existing_record:
            continue
        
        village = random.choice(villages)
        tehsil = random.choice(tehsils)
        district = random.choice(districts)
        
        land_record = LandRecord(
            survey_number=survey_number,
            sub_division=f"{random.randint(1, 5)}" if random.choice([True, False]) else None,
            village=village,
            tehsil=tehsil,
            district=district,
            state='Maharashtra',
            total_area=round(random.uniform(0.5, 10.0), 2),
            area_unit='acres',
            land_type=random.choice(land_types),
            land_classification=random.choice(['Irrigated', 'Dry', 'Garden', 'Orchard']),
            old_map_reference=f"MAP-{village}-{random.randint(1900, 1980)}",
            map_image_path=f"static/maps/{village}_{survey_number.replace('/', '_')}.jpg",
            acquisition_status=random.choice(['NOT_ACQUIRED', 'DECLARED', 'ACQUIRED', 'PAID'])
        )
        
        db.session.add(land_record)
        created_records.append(land_record)
    
    db.session.commit()
    print(f"✓ Created {len(created_records)} land records")
    return created_records

def create_sample_properties(land_records):
    """Create sample properties on land records."""
    property_types = [
        ('HOUSE', ['Pucca House', 'Kutcha House', 'Semi-Pucca House']),
        ('INDUSTRY', ['Small Scale Industry', 'Workshop', 'Warehouse']),
        ('TREE', ['Mango Tree', 'Coconut Tree', 'Neem Tree', 'Banyan Tree']),
        ('CROP', ['Sugarcane', 'Cotton', 'Wheat', 'Rice', 'Vegetables']),
        ('SHOP', ['General Store', 'Tea Stall', 'Medical Store'])
    ]
    
    created_properties = []
    
    for land_record in land_records[:30]:  # Add properties to first 30 land records
        num_properties = random.randint(0, 3)  # 0-3 properties per land record
        
        for j in range(num_properties):
            prop_type, subtypes = random.choice(property_types)
            subtype = random.choice(subtypes)
            
            # Generate realistic valuation based on property type
            if prop_type == 'HOUSE':
                base_value = random.randint(500000, 2000000)  # 5L to 20L
            elif prop_type == 'INDUSTRY':
                base_value = random.randint(1000000, 5000000)  # 10L to 50L
            elif prop_type == 'TREE':
                base_value = random.randint(5000, 50000)  # 5K to 50K per tree
            elif prop_type == 'CROP':
                base_value = random.randint(10000, 100000)  # 10K to 1L
            else:  # SHOP
                base_value = random.randint(200000, 800000)  # 2L to 8L
            
            property_obj = Property(
                land_record_id=land_record.id,
                property_number=f"PROP-{land_record.survey_number.replace('/', '-')}-{j+1}",
                property_type=prop_type,
                property_subtype=subtype,
                description=f"{subtype} located in {land_record.village}",
                assessed_value=base_value,
                valuation_date=fake.date_between(start_date='-2y', end_date='today'),
                valuation_method='Government Rate',
                area_occupied=round(random.uniform(0.1, 2.0), 2),
                construction_year=random.randint(1980, 2020) if prop_type in ['HOUSE', 'INDUSTRY', 'SHOP'] else None,
                condition=random.choice(['Good', 'Fair', 'Poor']),
                compensation_status=random.choice(['PENDING', 'CALCULATED', 'PAID'])
            )
            
            db.session.add(property_obj)
            created_properties.append(property_obj)
    
    db.session.commit()
    print(f"✓ Created {len(created_properties)} properties")
    return created_properties

def create_sample_ownerships(land_records):
    """Create sample ownership records."""
    created_ownerships = []
    
    for land_record in land_records:
        # Determine number of owners (1-4)
        num_owners = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        
        # Calculate ownership shares
        if num_owners == 1:
            shares = [1.0]
        else:
            # Generate random shares that sum to 1.0
            shares = [random.uniform(0.1, 0.8) for _ in range(num_owners - 1)]
            shares.append(1.0 - sum(shares))
            shares = [max(0.05, min(0.8, share)) for share in shares]  # Ensure reasonable bounds
            # Normalize to sum to 1.0
            total = sum(shares)
            shares = [share / total for share in shares]
        
        for i, share in enumerate(shares):
            # Generate realistic Indian names
            owner_name = fake.name()
            father_name = fake.name_male()
            
            ownership = Ownership(
                land_record_id=land_record.id,
                owner_name=owner_name,
                father_name=father_name,
                owner_type=random.choice(['INDIVIDUAL', 'JOINT', 'COMPANY', 'TRUST']),
                address=fake.address(),
                phone_number=fake.phone_number()[:15],  # Limit length
                aadhar_number=f"{random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}",
                pan_number=f"{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}{random.randint(1000, 9999)}{fake.random_letter().upper()}",
                bank_account_number=f"{random.randint(10000000, 99999999)}",
                bank_ifsc=f"{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}0{random.randint(100000, 999999)}",
                bank_name=random.choice(['State Bank of India', 'HDFC Bank', 'ICICI Bank', 'Punjab National Bank', 'Bank of Maharashtra']),
                ownership_share=round(share, 3),
                ownership_type=random.choice(['ABSOLUTE', 'JOINT', 'LIFE_INTEREST']),
                is_legal_heir=random.choice([True, False])
            )
            
            db.session.add(ownership)
            created_ownerships.append(ownership)
    
    db.session.commit()
    print(f"✓ Created {len(created_ownerships)} ownership records")
    return created_ownerships

def create_sample_acquisitions(projects, land_records):
    """Create sample acquisition declarations."""
    created_acquisitions = []
    
    # Create acquisitions for first 20 land records
    for i, land_record in enumerate(land_records[:20]):
        project = random.choice(projects)
        
        # Generate declaration number
        year = datetime.now().year
        decl_number = f"DECL-{project.project_code}-{year}-{i+1:03d}"
        
        # Calculate compensation
        base_rate = random.randint(500000, 2000000)  # 5L to 20L per acre
        area_to_acquire = land_record.total_area
        land_compensation = area_to_acquire * base_rate
        solatium_percentage = 100.0  # Standard 100% solatium
        total_compensation = land_compensation * (1 + solatium_percentage / 100)
        
        acquisition = AcquisitionDeclaration(
            project_id=project.id,
            land_record_id=land_record.id,
            declaration_number=decl_number,
            declaration_date=fake.date_between(start_date='-1y', end_date='today'),
            notification_number=f"NOTIF-{random.randint(1000, 9999)}-{year}",
            land_compensation_rate=base_rate,
            solatium_percentage=solatium_percentage,
            total_land_compensation=land_compensation,
            total_property_compensation=random.randint(100000, 500000),
            total_compensation=total_compensation,
            acquisition_type='FULL',
            area_to_acquire=area_to_acquire,
            declaration_status=random.choice(['DECLARED', 'POSSESSION_TAKEN', 'COMPLETED']),
            objection_period_end=fake.date_between(start_date='today', end_date='+30d'),
            declaring_officer='Dr. Rajesh Kumar',
            officer_designation='District Collector'
        )
        
        db.session.add(acquisition)
        created_acquisitions.append(acquisition)
        
        # Update land record status
        land_record.acquisition_status = 'DECLARED'
    
    db.session.commit()
    print(f"✓ Created {len(created_acquisitions)} acquisition declarations")
    return created_acquisitions

def create_sample_payments(acquisitions, ownerships):
    """Create sample compensation payments."""
    created_payments = []
    
    for acquisition in acquisitions[:10]:  # Create payments for first 10 acquisitions
        # Get ownerships for this land record
        land_ownerships = [o for o in ownerships if o.land_record_id == acquisition.land_record_id]
        
        for ownership in land_ownerships:
            # Calculate payment amount based on ownership share
            total_compensation = acquisition.total_compensation
            payment_amount = total_compensation * ownership.ownership_share
            
            # Generate payment reference
            payment_ref = f"PAY-{acquisition.declaration_number}-{ownership.id}"
            
            payment = CompensationPayment(
                acquisition_id=acquisition.id,
                ownership_id=ownership.id,
                payment_reference=payment_ref,
                payment_date=fake.date_between(start_date=acquisition.declaration_date, end_date='today'),
                payment_amount=payment_amount,
                land_compensation=payment_amount * 0.6,
                property_compensation=payment_amount * 0.1,
                solatium_amount=payment_amount * 0.3,
                interest_amount=0,
                other_compensation=0,
                payment_method='DBT',
                transaction_id=f"TXN{random.randint(100000000, 999999999)}",
                bank_reference=f"REF{random.randint(10000000, 99999999)}",
                payment_status='COMPLETED',
                authorizing_officer='Dr. Rajesh Kumar',
                disbursing_officer='Mrs. Priya Sharma'
            )
            
            db.session.add(payment)
            created_payments.append(payment)
    
    db.session.commit()
    print(f"✓ Created {len(created_payments)} compensation payments")
    return created_payments

def create_sample_queries(acquisitions):
    """Create sample citizen queries."""
    query_types = ['OBJECTION', 'COMPLAINT', 'INQUIRY', 'CORRECTION']
    query_subjects = [
        'Incorrect compensation calculation',
        'Survey number not matching records',
        'Missing property in valuation',
        'Objection to land acquisition',
        'Request for higher compensation',
        'Ownership dispute clarification',
        'Timeline inquiry for payment',
        'Documentation correction needed'
    ]
    
    created_queries = []
    
    for i, acquisition in enumerate(acquisitions[:8]):  # Create queries for 8 acquisitions
        query_number = f"QRY-{acquisition.declaration_number}-{i+1:02d}"
        
        query = CitizenQuery(
            acquisition_id=acquisition.id,
            query_number=query_number,
            query_date=fake.date_between(start_date=acquisition.declaration_date, end_date='today'),
            query_type=random.choice(query_types),
            complainant_name=fake.name(),
            complainant_contact=fake.phone_number()[:15],
            complainant_address=fake.address(),
            subject=random.choice(query_subjects),
            description=fake.text(max_nb_chars=500),
            response_date=fake.date_between(start_date='today', end_date='+15d') if random.choice([True, False]) else None,
            response_details=fake.text(max_nb_chars=300) if random.choice([True, False]) else None,
            responding_officer='Mrs. Priya Sharma' if random.choice([True, False]) else None,
            query_status=random.choice(['RECEIVED', 'UNDER_REVIEW', 'RESOLVED', 'CLOSED']),
            priority=random.choice(['LOW', 'NORMAL', 'HIGH', 'URGENT'])
        )
        
        db.session.add(query)
        created_queries.append(query)
    
    db.session.commit()
    print(f"✓ Created {len(created_queries)} citizen queries")
    return created_queries

def create_blockchain_transactions(acquisitions, payments, queries):
    """Create blockchain transactions for all activities."""
    print("Creating blockchain transactions...")
    
    # Create award declaration transactions
    for acquisition in acquisitions:
        tx_id = land_blockchain.create_award_declaration(
            project_name=acquisition.project.project_name,
            survey_numbers=[acquisition.land_record.survey_number],
            village=acquisition.land_record.village,
            tehsil=acquisition.land_record.tehsil,
            district=acquisition.land_record.district,
            compensation_rate=acquisition.land_compensation_rate,
            officer_id=acquisition.declaring_officer
        )
        print(f"  ✓ Award declaration: {tx_id[:16]}...")
    
    # Create payment transactions
    for payment in payments:
        tx_id = land_blockchain.create_compensation_payment(
            survey_number=payment.acquisition.land_record.survey_number,
            property_number=f"PROP_{payment.acquisition.land_record.id}",
            beneficiary_name=payment.owner.owner_name,
            beneficiary_account=payment.owner.bank_account_number or 'N/A',
            amount=payment.payment_amount,
            payment_method=payment.payment_method,
            officer_id=payment.authorizing_officer
        )
        print(f"  ✓ Payment: {tx_id[:16]}...")
    
    # Create query transactions
    for query in queries:
        survey_number = query.acquisition.land_record.survey_number if query.acquisition else 'GENERAL'
        tx_id = land_blockchain.create_query_record(
            survey_number=survey_number,
            query_type=query.query_type,
            complainant_name=query.complainant_name,
            query_details=query.description,
            officer_id='System'
        )
        print(f"  ✓ Query: {tx_id[:16]}...")
    
    # Mine all pending transactions
    print("Mining blockchain transactions...")
    success = land_blockchain.mine_pending_transactions()
    if success:
        print("✓ All transactions mined successfully")
    else:
        print("- No pending transactions to mine")

def main():
    """Main function to create all sample data."""
    print("🏗️  Land Acquisition Blockchain System - Sample Data Creation")
    print("=" * 70)
    
    # Create application context
    with app.app_context():
        # Create database tables
        db.create_all()
        print("✓ Database tables created/verified")
        
        # Create sample data
        print("\n📊 Creating sample data...")
        
        # 1. Create users
        print("\n1. Creating users...")
        users = create_sample_users()
        
        # 2. Create projects
        print("\n2. Creating projects...")
        projects = create_sample_projects()
        
        # 3. Create land records
        print("\n3. Creating land records...")
        land_records = create_sample_land_records(50)
        
        # 4. Create properties
        print("\n4. Creating properties...")
        properties = create_sample_properties(land_records)
        
        # 5. Create ownerships
        print("\n5. Creating ownerships...")
        ownerships = create_sample_ownerships(land_records)
        
        # 6. Create acquisitions
        print("\n6. Creating acquisitions...")
        acquisitions = create_sample_acquisitions(projects, land_records)
        
        # 7. Create payments
        print("\n7. Creating payments...")
        payments = create_sample_payments(acquisitions, ownerships)
        
        # 8. Create queries
        print("\n8. Creating queries...")
        queries = create_sample_queries(acquisitions)
        
        # 9. Create blockchain transactions
        print("\n9. Creating blockchain transactions...")
        create_blockchain_transactions(acquisitions, payments, queries)
        
        print("\n" + "=" * 70)
        print("🎉 Sample data creation completed successfully!")
        print("\n📈 Summary:")
        print(f"   • {len(users)} users created")
        print(f"   • {len(projects)} projects created")
        print(f"   • {len(land_records)} land records created")
        print(f"   • {len(properties)} properties created")
        print(f"   • {len(ownerships)} ownership records created")
        print(f"   • {len(acquisitions)} acquisition declarations created")
        print(f"   • {len(payments)} compensation payments created")
        print(f"   • {len(queries)} citizen queries created")
        
        # Get blockchain stats
        blockchain_stats = land_blockchain.get_blockchain_stats()
        print(f"   • {blockchain_stats['total_blocks']} blockchain blocks")
        print(f"   • {blockchain_stats['total_transactions']} blockchain transactions")
        
        print("\n🚀 System is ready for demonstration!")
        print("   Login credentials:")
        print("   • Admin: admin / admin123")
        print("   • Collector: collector_pune / collector123")
        print("   • Officer: officer_mumbai / officer123")
        print("   • Clerk: clerk_nashik / clerk123")
        
        print("\n🌐 Start the application with:")
        print("   python land_acquisition_app.py")

if __name__ == '__main__':
    main()
# Land Acquisition Blockchain System 🏗️

A comprehensive blockchain-based system for digitizing and streamlining government land acquisition processes, integrated with AI analytics and OCR capabilities.

## 🌟 Overview

This system transforms the traditional manual land acquisition process into a digital, transparent, and immutable platform. By leveraging blockchain technology, AI analytics, and OCR processing, it addresses critical issues in government land acquisition projects like national highways, railways, airports, and ports.

## 🎯 Problem Statement

The current manual land acquisition process suffers from:

- **Complex Valuation & Ownership**: Multiple owners with undivided shares, various property types (houses, trees, crops)
- **Manual Record Keeping**: 100-year-old physical maps and documents that are damaged and outdated
- **Lack of Transparency**: Vulnerability to fraud, unauthorized modifications, and fund misappropriation
- **Inefficient Reporting**: Slow manual processes for generating status reports
- **Missing Digital Data**: Absence of GIS maps, KML files, and precise coordinates

## 🚀 Solution Features

### 🔗 Blockchain Technology
- **Immutable Ledger**: Permanent, unchangeable record of all transactions
- **Transparency**: All activities are recorded and verifiable
- **Accountability**: Complete audit trail of every action
- **Fraud Prevention**: Eliminates possibility of unauthorized modifications

### 🤖 AI-Powered Analytics
- **Compensation Prediction**: ML models to estimate fair compensation amounts
- **Litigation Risk Assessment**: Predict probability of legal disputes
- **Anomaly Detection**: Identify unusual patterns in data
- **Trend Analysis**: Insights into acquisition patterns and progress
- **Intelligent Reporting**: Automated report generation with insights

### 📄 OCR Document Processing
- **Digital Conversion**: Convert old physical documents to digital format
- **Multi-language Support**: Process documents in Marathi and English
- **Batch Processing**: Handle multiple documents simultaneously
- **Text Extraction**: Extract structured data from scanned documents

### 📊 Comprehensive Dashboard
- **Real-time Statistics**: Live updates on acquisition progress
- **Interactive Charts**: Visual representation of data
- **Quick Actions**: Streamlined workflows for common tasks
- **Activity Tracking**: Monitor all system activities

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Blockchain    │
│   (Bootstrap)   │◄──►│   (Flask)       │◄──►│   (Custom)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OCR Engine    │    │   Database      │    │   AI Analytics  │
│   (Tesseract)   │    │   (SQLite)      │    │   (Scikit-learn)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Core Components

### 1. **Blockchain Module** (`blockchain.py`)
- Custom blockchain implementation
- Proof-of-work consensus
- Transaction validation
- Block mining and verification

### 2. **Database Models** (`models.py`)
- Land records and properties
- Ownership details with shares
- Project and acquisition declarations
- Compensation payments
- Citizen queries and litigation cases

### 3. **AI Analytics** (`ai_analytics.py`)
- Machine learning models
- Predictive analytics
- Data visualization
- Intelligent insights

### 4. **Main Application** (`land_acquisition_app.py`)
- Flask web application
- RESTful API endpoints
- Authentication and authorization
- Integration of all components

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Tesseract OCR engine
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd land-acquisition-blockchain-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr tesseract-ocr-mar`
- **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract tesseract-lang`

### 5. Initialize Database
```bash
python -c "from land_acquisition_app import app, db; app.app_context().push(); db.create_all()"
```

### 6. Run the Application
```bash
python land_acquisition_app.py
```

The system will be available at `http://localhost:5000`

## 🔐 Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

## 📱 Usage Guide

### 1. **Dashboard Overview**
- View key statistics and metrics
- Monitor blockchain status
- Access AI insights and recommendations
- Track recent activities

### 2. **Land Records Management**
- Add new land records with survey numbers
- Upload and link scanned maps
- Manage property details and ownership
- Track acquisition status

### 3. **Project Management**
- Create new acquisition projects
- Set budgets and timelines
- Track progress across districts
- Generate project reports

### 4. **Acquisition Declaration (Awards)**
- Declare land parcels for acquisition
- Calculate compensation amounts
- Record official notifications
- Update blockchain ledger

### 5. **Compensation Payments**
- Process DBT payments to beneficiaries
- Track payment status
- Generate payment reports
- Maintain audit trails

### 6. **Citizen Query Management**
- Record citizen complaints and queries
- Track resolution status
- Maintain communication history
- Generate response reports

### 7. **OCR Document Processing**
- Upload scanned documents
- Extract text automatically
- Process multi-page PDFs
- Support for regional languages

### 8. **AI Analytics & Predictions**
- Predict compensation amounts
- Assess litigation risks
- Identify data anomalies
- Generate intelligent insights

### 9. **Blockchain Explorer**
- View transaction history
- Verify data integrity
- Track immutable records
- Monitor system security

## 🔧 API Endpoints

### Authentication
- `POST /login` - User authentication
- `GET /logout` - User logout

### Land Records
- `GET /api/land-records` - List land records
- `POST /api/land-records` - Create new record
- `GET /api/land-records/<id>` - Get specific record
- `PUT /api/land-records/<id>` - Update record
- `DELETE /api/land-records/<id>` - Delete record

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create new project

### Acquisitions
- `GET /api/acquisitions` - List acquisitions
- `POST /api/acquisitions` - Create acquisition declaration

### Payments
- `GET /api/payments` - List payments
- `POST /api/payments` - Record payment

### Queries
- `GET /api/queries` - List citizen queries
- `POST /api/queries` - Create new query

### OCR
- `POST /api/ocr/upload` - Upload and process document

### AI Analytics
- `GET /api/ai/dashboard-data` - Get dashboard analytics
- `POST /api/ai/predict-compensation` - Predict compensation
- `POST /api/ai/predict-litigation` - Assess litigation risk
- `GET /api/ai/project-report/<name>` - Get project report

### Blockchain
- `GET /api/blockchain/stats` - Get blockchain statistics
- `GET /api/blockchain/transactions/<survey>` - Get transactions
- `POST /api/blockchain/mine` - Mine pending transactions

## 🎨 Frontend Structure

### Templates
- `base.html` - Common layout and navigation
- `dashboard.html` - Main dashboard with statistics
- `login.html` - Authentication page

### Styling
- Bootstrap 5 for responsive design
- Custom CSS with modern gradients
- Interactive charts with Chart.js
- Icons from Bootstrap Icons

## 🔒 Security Features

### Authentication & Authorization
- Session-based authentication
- Role-based access control
- Password hashing with Werkzeug
- CSRF protection

### Data Security
- Blockchain immutability
- Transaction verification
- Audit trail maintenance
- Secure file uploads

### System Security
- Input validation
- SQL injection prevention
- XSS protection
- Secure session management

## 📊 Database Schema

### Core Tables
- `land_records` - Survey numbers and land details
- `properties` - Structures on land (houses, trees, etc.)
- `ownerships` - Owner details with shares
- `projects` - Government projects
- `acquisition_declarations` - Official awards
- `compensation_payments` - Payment records
- `citizen_queries` - Public complaints/queries
- `litigation_cases` - Legal disputes
- `users` - System users

### Blockchain Tables
- `blocks` - Blockchain blocks
- `transaction_index` - Transaction search index

## 🤖 AI Models

### Compensation Predictor
- **Algorithm**: Random Forest Regressor
- **Features**: Land area, owner count, property count, location
- **Purpose**: Estimate fair compensation amounts

### Litigation Risk Predictor
- **Algorithm**: Random Forest Classifier
- **Features**: Compensation amount, queries, ownership complexity
- **Purpose**: Assess probability of legal disputes

### Anomaly Detection
- **Method**: Statistical analysis with IQR
- **Purpose**: Identify unusual patterns in data

## 📈 Performance Optimization

### Database
- Indexed columns for fast queries
- Pagination for large datasets
- Optimized SQL queries

### Blockchain
- Low difficulty for faster mining
- Efficient Merkle tree implementation
- SQLite persistence for reliability

### Frontend
- Lazy loading of charts
- AJAX for dynamic content
- Responsive design for mobile

## 🔄 Workflow Examples

### 1. **Complete Land Acquisition Process**
```
1. Add Land Record → 2. Create Project → 3. Declare Award → 
4. Process Payment → 5. Update Blockchain → 6. Generate Report
```

### 2. **Citizen Query Resolution**
```
1. Receive Query → 2. Record in System → 3. Investigate → 
4. Provide Response → 5. Update Status → 6. Close Query
```

### 3. **OCR Document Processing**
```
1. Upload Document → 2. OCR Processing → 3. Text Extraction → 
4. Data Validation → 5. System Integration → 6. Archive Document
```

## 📋 Future Enhancements

### Phase 2 Features
- **GIS Integration**: Interactive maps with zoom capabilities
- **Mobile Application**: Native mobile app for field officers
- **Advanced AI**: Deep learning models for better predictions
- **Multi-language Support**: Additional regional languages
- **Blockchain Network**: Distributed blockchain across departments

### Phase 3 Features
- **IoT Integration**: Drone surveys and GPS coordinates
- **Smart Contracts**: Automated compensation payments
- **Public Portal**: Citizen-facing transparency portal
- **Advanced Analytics**: Predictive project timelines
- **Integration APIs**: Connect with other government systems

## 🐛 Troubleshooting

### Common Issues

1. **Tesseract Not Found**
   - Ensure Tesseract is installed and in PATH
   - Install language packs for Marathi support

2. **Database Errors**
   - Check SQLite permissions
   - Ensure database directory exists

3. **Blockchain Issues**
   - Verify chain integrity with validation
   - Check mining permissions for users

4. **OCR Processing Fails**
   - Verify image quality and format
   - Check file size limits

## 📞 Support & Contact

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check documentation for troubleshooting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Government Land Acquisition Department for requirements
- Open source community for tools and libraries
- Contributors and testers for feedback and improvements

---

**Built with ❤️ for transparent and efficient land acquisition processes**

## 🔧 Development Setup

### For Developers

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes and test thoroughly**
4. **Commit changes**: `git commit -m "Add new feature"`
5. **Push to branch**: `git push origin feature/new-feature`
6. **Create Pull Request**

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include type hints where appropriate

### Testing
- Write unit tests for new features
- Test blockchain functionality thoroughly
- Verify AI model accuracy
- Test OCR with various document types

---

*Last updated: December 2024*
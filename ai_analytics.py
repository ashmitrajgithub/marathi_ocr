import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, classification_report
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class LandAcquisitionAI:
    """
    AI-powered analytics and insights for land acquisition processes.
    Provides predictive modeling, anomaly detection, and intelligent reporting.
    """
    
    def __init__(self, db_path: str = "land_acquisition.db"):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self._init_models()
    
    def _init_models(self):
        """Initialize ML models for various predictions."""
        self.models = {
            'compensation_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
            'litigation_predictor': RandomForestClassifier(n_estimators=100, random_state=42),
            'timeline_predictor': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        self.scalers = {
            'compensation': StandardScaler(),
            'litigation': StandardScaler(),
            'timeline': StandardScaler()
        }
        
        self.encoders = {
            'land_type': LabelEncoder(),
            'district': LabelEncoder(),
            'project_type': LabelEncoder()
        }
    
    def load_data_from_db(self) -> pd.DataFrame:
        """Load comprehensive data from the database for analysis."""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT 
            lr.survey_number,
            lr.village,
            lr.tehsil,
            lr.district,
            lr.total_area,
            lr.land_type,
            lr.acquisition_status,
            lr.is_under_litigation,
            p.project_name,
            p.project_type,
            ad.declaration_date,
            ad.land_compensation_rate,
            ad.total_compensation,
            ad.declaration_status,
            cp.payment_date,
            cp.payment_amount,
            COUNT(DISTINCT o.id) as owner_count,
            COUNT(DISTINCT prop.id) as property_count,
            COUNT(DISTINCT cq.id) as query_count,
            COUNT(DISTINCT lc.id) as litigation_count
        FROM land_records lr
        LEFT JOIN acquisition_declarations ad ON lr.id = ad.land_record_id
        LEFT JOIN projects p ON ad.project_id = p.id
        LEFT JOIN compensation_payments cp ON ad.id = cp.acquisition_id
        LEFT JOIN ownerships o ON lr.id = o.land_record_id
        LEFT JOIN properties prop ON lr.id = prop.land_record_id
        LEFT JOIN citizen_queries cq ON ad.id = cq.acquisition_id
        LEFT JOIN litigation_cases lc ON lr.id = lc.land_record_id
        GROUP BY lr.id, ad.id, cp.id
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Data preprocessing
        df['declaration_date'] = pd.to_datetime(df['declaration_date'])
        df['payment_date'] = pd.to_datetime(df['payment_date'])
        df['days_to_payment'] = (df['payment_date'] - df['declaration_date']).dt.days
        
        # Fill missing values
        df = df.fillna({
            'owner_count': 1,
            'property_count': 0,
            'query_count': 0,
            'litigation_count': 0,
            'days_to_payment': 0,
            'total_compensation': 0,
            'payment_amount': 0
        })
        
        return df
    
    def train_compensation_predictor(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train ML model to predict compensation amounts."""
        # Prepare features for compensation prediction
        feature_cols = ['total_area', 'owner_count', 'property_count', 'land_compensation_rate']
        categorical_cols = ['land_type', 'district', 'project_type']
        
        # Filter data with valid compensation values
        train_df = df[(df['total_compensation'] > 0) & (df['total_compensation'].notna())].copy()
        
        if len(train_df) < 10:
            return {'status': 'insufficient_data', 'message': 'Need at least 10 records with compensation data'}
        
        # Encode categorical variables
        for col in categorical_cols:
            if col in train_df.columns:
                train_df[col + '_encoded'] = self.encoders[col.split('_')[0]].fit_transform(train_df[col].fillna('Unknown'))
                feature_cols.append(col + '_encoded')
        
        X = train_df[feature_cols].fillna(0)
        y = train_df['total_compensation']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scalers['compensation'].fit_transform(X_train)
        X_test_scaled = self.scalers['compensation'].transform(X_test)
        
        # Train model
        self.models['compensation_predictor'].fit(X_train_scaled, y_train)
        
        # Predictions and evaluation
        y_pred = self.models['compensation_predictor'].predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        
        return {
            'status': 'success',
            'mae': mae,
            'feature_importance': dict(zip(feature_cols, self.models['compensation_predictor'].feature_importances_)),
            'training_samples': len(X_train)
        }
    
    def predict_compensation(self, land_area: float, owner_count: int, property_count: int, 
                           land_type: str, district: str, project_type: str, 
                           compensation_rate: float) -> Dict[str, Any]:
        """Predict compensation amount for new land acquisition."""
        try:
            # Prepare features
            features = [land_area, owner_count, property_count, compensation_rate]
            
            # Encode categorical variables
            categorical_features = []
            for encoder_name, encoder in self.encoders.items():
                if encoder_name == 'land_type':
                    try:
                        encoded_val = encoder.transform([land_type])[0]
                    except:
                        encoded_val = 0  # Unknown category
                    categorical_features.append(encoded_val)
                elif encoder_name == 'district':
                    try:
                        encoded_val = encoder.transform([district])[0]
                    except:
                        encoded_val = 0
                    categorical_features.append(encoded_val)
                elif encoder_name == 'project_type':
                    try:
                        encoded_val = encoder.transform([project_type])[0]
                    except:
                        encoded_val = 0
                    categorical_features.append(encoded_val)
            
            all_features = features + categorical_features
            features_scaled = self.scalers['compensation'].transform([all_features])
            
            predicted_compensation = self.models['compensation_predictor'].predict(features_scaled)[0]
            
            return {
                'status': 'success',
                'predicted_compensation': round(predicted_compensation, 2),
                'confidence_interval': self._calculate_confidence_interval(predicted_compensation)
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _calculate_confidence_interval(self, prediction: float, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for predictions."""
        # Simplified confidence interval calculation
        margin = prediction * 0.15  # 15% margin
        return (round(prediction - margin, 2), round(prediction + margin, 2))
    
    def train_litigation_predictor(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train ML model to predict litigation probability."""
        feature_cols = ['total_area', 'owner_count', 'property_count', 'total_compensation', 'query_count']
        categorical_cols = ['land_type', 'district', 'project_type']
        
        # Prepare target variable
        train_df = df.copy()
        train_df['will_litigate'] = (train_df['litigation_count'] > 0).astype(int)
        
        if len(train_df) < 20:
            return {'status': 'insufficient_data', 'message': 'Need at least 20 records for litigation prediction'}
        
        # Encode categorical variables
        for col in categorical_cols:
            if col in train_df.columns:
                train_df[col + '_encoded'] = self.encoders[col.split('_')[0]].transform(train_df[col].fillna('Unknown'))
                feature_cols.append(col + '_encoded')
        
        X = train_df[feature_cols].fillna(0)
        y = train_df['will_litigate']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scalers['litigation'].fit_transform(X_train)
        X_test_scaled = self.scalers['litigation'].transform(X_test)
        
        # Train model
        self.models['litigation_predictor'].fit(X_train_scaled, y_train)
        
        # Predictions and evaluation
        y_pred = self.models['litigation_predictor'].predict(X_test_scaled)
        accuracy = (y_pred == y_test).mean()
        
        return {
            'status': 'success',
            'accuracy': accuracy,
            'feature_importance': dict(zip(feature_cols, self.models['litigation_predictor'].feature_importances_)),
            'training_samples': len(X_train)
        }
    
    def predict_litigation_risk(self, land_area: float, owner_count: int, property_count: int,
                              compensation_amount: float, query_count: int, land_type: str,
                              district: str, project_type: str) -> Dict[str, Any]:
        """Predict litigation risk for a land parcel."""
        try:
            features = [land_area, owner_count, property_count, compensation_amount, query_count]
            
            # Encode categorical variables
            categorical_features = []
            for encoder_name, encoder in self.encoders.items():
                if encoder_name == 'land_type':
                    try:
                        encoded_val = encoder.transform([land_type])[0]
                    except:
                        encoded_val = 0
                    categorical_features.append(encoded_val)
                elif encoder_name == 'district':
                    try:
                        encoded_val = encoder.transform([district])[0]
                    except:
                        encoded_val = 0
                    categorical_features.append(encoded_val)
                elif encoder_name == 'project_type':
                    try:
                        encoded_val = encoder.transform([project_type])[0]
                    except:
                        encoded_val = 0
                    categorical_features.append(encoded_val)
            
            all_features = features + categorical_features
            features_scaled = self.scalers['litigation'].transform([all_features])
            
            litigation_probability = self.models['litigation_predictor'].predict_proba(features_scaled)[0][1]
            risk_level = 'LOW' if litigation_probability < 0.3 else 'MEDIUM' if litigation_probability < 0.7 else 'HIGH'
            
            return {
                'status': 'success',
                'litigation_probability': round(litigation_probability, 3),
                'risk_level': risk_level,
                'recommendations': self._get_litigation_recommendations(risk_level)
            }
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _get_litigation_recommendations(self, risk_level: str) -> List[str]:
        """Get recommendations based on litigation risk level."""
        recommendations = {
            'LOW': [
                "Proceed with standard acquisition process",
                "Maintain regular communication with landowners",
                "Document all interactions properly"
            ],
            'MEDIUM': [
                "Conduct additional stakeholder meetings",
                "Consider mediation for any disputes",
                "Ensure transparent compensation calculation",
                "Provide detailed documentation to owners"
            ],
            'HIGH': [
                "Engage legal counsel early",
                "Consider alternative dispute resolution",
                "Review compensation calculation thoroughly",
                "Conduct detailed ownership verification",
                "Prepare for potential court proceedings"
            ]
        }
        return recommendations.get(risk_level, [])
    
    def generate_acquisition_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data with AI insights."""
        df = self.load_data_from_db()
        
        if df.empty:
            return {'status': 'no_data', 'message': 'No data available for analysis'}
        
        # Basic statistics
        total_parcels = len(df)
        total_area = df['total_area'].sum()
        total_compensation = df['total_compensation'].sum()
        avg_compensation_per_acre = total_compensation / total_area if total_area > 0 else 0
        
        # Status distribution
        status_counts = df['acquisition_status'].value_counts().to_dict()
        
        # District-wise analysis
        district_stats = df.groupby('district').agg({
            'total_area': 'sum',
            'total_compensation': 'sum',
            'litigation_count': 'sum',
            'query_count': 'sum'
        }).to_dict('index')
        
        # Project-wise analysis
        project_stats = df.groupby('project_name').agg({
            'total_area': 'sum',
            'total_compensation': 'sum',
            'survey_number': 'count'
        }).to_dict('index')
        
        # Timeline analysis
        monthly_acquisitions = df.groupby(df['declaration_date'].dt.to_period('M')).size().to_dict()
        monthly_acquisitions = {str(k): v for k, v in monthly_acquisitions.items() if pd.notna(k)}
        
        # AI Insights
        ai_insights = self._generate_ai_insights(df)
        
        return {
            'status': 'success',
            'summary': {
                'total_parcels': total_parcels,
                'total_area': round(total_area, 2),
                'total_compensation': round(total_compensation, 2),
                'avg_compensation_per_acre': round(avg_compensation_per_acre, 2)
            },
            'status_distribution': status_counts,
            'district_stats': district_stats,
            'project_stats': project_stats,
            'monthly_acquisitions': monthly_acquisitions,
            'ai_insights': ai_insights
        }
    
    def _generate_ai_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate AI-powered insights from the data."""
        insights = {
            'trends': [],
            'anomalies': [],
            'predictions': [],
            'recommendations': []
        }
        
        # Trend analysis
        if len(df) > 10:
            # Compensation trend
            avg_compensation = df['total_compensation'].mean()
            recent_avg = df.tail(5)['total_compensation'].mean()
            if recent_avg > avg_compensation * 1.1:
                insights['trends'].append("Compensation amounts are trending upward in recent acquisitions")
            elif recent_avg < avg_compensation * 0.9:
                insights['trends'].append("Compensation amounts are trending downward in recent acquisitions")
            
            # Litigation trend
            litigation_rate = (df['litigation_count'] > 0).mean()
            if litigation_rate > 0.2:
                insights['trends'].append(f"High litigation rate detected: {litigation_rate:.1%} of cases")
            
            # Query trend
            avg_queries = df['query_count'].mean()
            if avg_queries > 2:
                insights['trends'].append(f"High query volume: average {avg_queries:.1f} queries per parcel")
        
        # Anomaly detection
        if len(df) > 5:
            # Compensation anomalies
            compensation_q75, compensation_q25 = np.percentile(df['total_compensation'], [75, 25])
            iqr = compensation_q75 - compensation_q25
            upper_bound = compensation_q75 + 1.5 * iqr
            
            high_compensation_count = (df['total_compensation'] > upper_bound).sum()
            if high_compensation_count > 0:
                insights['anomalies'].append(f"{high_compensation_count} parcels with unusually high compensation")
            
            # Area anomalies
            area_q75, area_q25 = np.percentile(df['total_area'], [75, 25])
            area_iqr = area_q75 - area_q25
            area_upper_bound = area_q75 + 1.5 * area_iqr
            
            large_parcel_count = (df['total_area'] > area_upper_bound).sum()
            if large_parcel_count > 0:
                insights['anomalies'].append(f"{large_parcel_count} unusually large parcels detected")
        
        # Predictions
        pending_parcels = len(df[df['acquisition_status'] == 'DECLARED'])
        if pending_parcels > 0:
            estimated_time = self._estimate_completion_time(df)
            insights['predictions'].append(f"Estimated {estimated_time} days to complete pending acquisitions")
        
        # Recommendations
        if litigation_rate > 0.15:
            insights['recommendations'].append("Consider implementing better stakeholder engagement strategies")
        
        if avg_queries > 1.5:
            insights['recommendations'].append("Improve information dissemination to reduce citizen queries")
        
        return insights
    
    def _estimate_completion_time(self, df: pd.DataFrame) -> int:
        """Estimate time to complete pending acquisitions."""
        completed_df = df[df['days_to_payment'] > 0]
        if len(completed_df) > 5:
            avg_days = completed_df['days_to_payment'].mean()
            return int(avg_days)
        return 90  # Default estimate
    
    def generate_predictive_report(self, project_name: str) -> Dict[str, Any]:
        """Generate AI-powered predictive report for a specific project."""
        df = self.load_data_from_db()
        project_df = df[df['project_name'] == project_name]
        
        if project_df.empty:
            return {'status': 'no_data', 'message': f'No data found for project: {project_name}'}
        
        # Train models if sufficient data
        compensation_model_result = self.train_compensation_predictor(df)
        litigation_model_result = self.train_litigation_predictor(df)
        
        # Project statistics
        total_parcels = len(project_df)
        completed_parcels = len(project_df[project_df['acquisition_status'] == 'PAID'])
        pending_parcels = total_parcels - completed_parcels
        
        # Predictions for pending parcels
        pending_df = project_df[project_df['acquisition_status'] != 'PAID']
        predictions = []
        
        for _, row in pending_df.iterrows():
            if compensation_model_result['status'] == 'success':
                comp_pred = self.predict_compensation(
                    row['total_area'], row['owner_count'], row['property_count'],
                    row['land_type'], row['district'], row['project_type'],
                    row['land_compensation_rate']
                )
            else:
                comp_pred = {'status': 'error', 'predicted_compensation': 0}
            
            if litigation_model_result['status'] == 'success':
                lit_pred = self.predict_litigation_risk(
                    row['total_area'], row['owner_count'], row['property_count'],
                    row['total_compensation'], row['query_count'], row['land_type'],
                    row['district'], row['project_type']
                )
            else:
                lit_pred = {'status': 'error', 'litigation_probability': 0, 'risk_level': 'UNKNOWN'}
            
            predictions.append({
                'survey_number': row['survey_number'],
                'predicted_compensation': comp_pred.get('predicted_compensation', 0),
                'litigation_risk': lit_pred.get('risk_level', 'UNKNOWN'),
                'litigation_probability': lit_pred.get('litigation_probability', 0)
            })
        
        return {
            'status': 'success',
            'project_name': project_name,
            'summary': {
                'total_parcels': total_parcels,
                'completed_parcels': completed_parcels,
                'pending_parcels': pending_parcels,
                'completion_rate': round(completed_parcels / total_parcels * 100, 1) if total_parcels > 0 else 0
            },
            'model_performance': {
                'compensation_model': compensation_model_result,
                'litigation_model': litigation_model_result
            },
            'predictions': predictions,
            'risk_summary': self._summarize_project_risks(predictions)
        }
    
    def _summarize_project_risks(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Summarize risks for a project based on predictions."""
        if not predictions:
            return {'high_risk_parcels': 0, 'medium_risk_parcels': 0, 'low_risk_parcels': 0}
        
        risk_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0}
        total_predicted_compensation = 0
        
        for pred in predictions:
            risk_level = pred.get('litigation_risk', 'UNKNOWN')
            risk_counts[risk_level] += 1
            total_predicted_compensation += pred.get('predicted_compensation', 0)
        
        return {
            'high_risk_parcels': risk_counts['HIGH'],
            'medium_risk_parcels': risk_counts['MEDIUM'],
            'low_risk_parcels': risk_counts['LOW'],
            'total_predicted_compensation': round(total_predicted_compensation, 2),
            'average_predicted_compensation': round(total_predicted_compensation / len(predictions), 2) if predictions else 0
        }
    
    def create_visualization_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create interactive visualization charts using Plotly."""
        charts = {}
        
        # Status distribution pie chart
        if 'status_distribution' in data:
            fig = px.pie(
                values=list(data['status_distribution'].values()),
                names=list(data['status_distribution'].keys()),
                title="Land Acquisition Status Distribution"
            )
            charts['status_pie'] = fig.to_html(include_plotlyjs='cdn')
        
        # District-wise compensation bar chart
        if 'district_stats' in data:
            districts = list(data['district_stats'].keys())
            compensations = [data['district_stats'][d]['total_compensation'] for d in districts]
            
            fig = px.bar(
                x=districts,
                y=compensations,
                title="District-wise Total Compensation",
                labels={'x': 'District', 'y': 'Total Compensation (₹)'}
            )
            charts['district_compensation'] = fig.to_html(include_plotlyjs='cdn')
        
        # Monthly acquisitions timeline
        if 'monthly_acquisitions' in data:
            months = list(data['monthly_acquisitions'].keys())
            counts = list(data['monthly_acquisitions'].values())
            
            fig = px.line(
                x=months,
                y=counts,
                title="Monthly Land Acquisition Trend",
                labels={'x': 'Month', 'y': 'Number of Acquisitions'}
            )
            charts['monthly_trend'] = fig.to_html(include_plotlyjs='cdn')
        
        return charts

# Initialize global AI analytics instance
land_ai = LandAcquisitionAI()
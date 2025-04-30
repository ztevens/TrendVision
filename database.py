"""
Database module for the TrendVision AI application.
Manages database connections and models for storing user preferences, saved reports, and data history.
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create SQLAlchemy engine and base
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    """User model for storing user preferences and settings."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    preferences = Column(Text, default='{}')
    
    # Relationships
    reports = relationship("Report", back_populates="user")
    data_sources = relationship("SavedDataSource", back_populates="user")
    
    def get_preferences(self):
        """Return preferences as a dictionary."""
        return json.loads(self.preferences)
    
    def set_preferences(self, preferences_dict):
        """Set preferences from a dictionary."""
        self.preferences = json.dumps(preferences_dict)

class Report(Base):
    """Model for storing saved reports and visualizations."""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    configuration = Column(Text, nullable=False)  # JSON string with report configuration
    visualization_type = Column(String(50), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="reports")
    
    def get_configuration(self):
        """Return configuration as a dictionary."""
        return json.loads(self.configuration)
    
    def set_configuration(self, config_dict):
        """Set configuration from a dictionary."""
        self.configuration = json.dumps(config_dict)

class SavedDataSource(Base):
    """Model for storing configured data sources."""
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # yfinance, simulated, upload, etc.
    configuration = Column(Text, nullable=False)  # JSON string with source configuration
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="data_sources")
    
    def get_configuration(self):
        """Return configuration as a dictionary."""
        return json.loads(self.configuration)
    
    def set_configuration(self, config_dict):
        """Set configuration from a dictionary."""
        self.configuration = json.dumps(config_dict)

class DataHistory(Base):
    """Model for storing historical data for later retrieval."""
    __tablename__ = 'data_history'
    
    id = Column(Integer, primary_key=True)
    source_type = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False)
    metadata = Column(Text, nullable=False)  # JSON string with data metadata
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    def get_metadata(self):
        """Return metadata as a dictionary."""
        return json.loads(self.metadata)
    
    def set_metadata(self, metadata_dict):
        """Set metadata from a dictionary."""
        self.metadata = json.dumps(metadata_dict)

# Initialize database tables
def init_db():
    """Create all database tables if they don't exist."""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session."""
    return Session()

# Database helper functions
def save_user_preferences(username, preferences):
    """Save user preferences to database."""
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username)
            session.add(user)
        
        user.set_preferences(preferences)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error saving user preferences: {e}")
        return False
    finally:
        session.close()

def get_user_preferences(username):
    """Get user preferences from database."""
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user:
            return user.get_preferences()
        return {}
    except Exception as e:
        print(f"Error getting user preferences: {e}")
        return {}
    finally:
        session.close()

def save_report(username, title, description, configuration, visualization_type):
    """Save a report to database."""
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username)
            session.add(user)
            session.flush()
        
        report = Report(
            user_id=user.id,
            title=title,
            description=description,
            visualization_type=visualization_type
        )
        report.set_configuration(configuration)
        
        session.add(report)
        session.commit()
        return report.id
    except Exception as e:
        session.rollback()
        print(f"Error saving report: {e}")
        return None
    finally:
        session.close()

def get_reports(username):
    """Get all reports for a user."""
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return []
        
        reports = session.query(Report).filter_by(user_id=user.id).all()
        return [{
            'id': report.id,
            'title': report.title,
            'description': report.description,
            'created_at': report.created_at,
            'updated_at': report.updated_at,
            'configuration': report.get_configuration(),
            'visualization_type': report.visualization_type
        } for report in reports]
    except Exception as e:
        print(f"Error getting reports: {e}")
        return []
    finally:
        session.close()

def save_data_source(username, name, source_type, configuration):
    """Save a data source configuration to database."""
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username)
            session.add(user)
            session.flush()
        
        source = SavedDataSource(
            user_id=user.id,
            name=name,
            source_type=source_type
        )
        source.set_configuration(configuration)
        
        session.add(source)
        session.commit()
        return source.id
    except Exception as e:
        session.rollback()
        print(f"Error saving data source: {e}")
        return None
    finally:
        session.close()

def get_data_sources(username):
    """Get all data sources for a user."""
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return []
        
        sources = session.query(SavedDataSource).filter_by(user_id=user.id).all()
        return [{
            'id': source.id,
            'name': source.name,
            'source_type': source.source_type,
            'configuration': source.get_configuration(),
            'created_at': source.created_at
        } for source in sources]
    except Exception as e:
        print(f"Error getting data sources: {e}")
        return []
    finally:
        session.close()

def store_data_point(source_type, date, value, metadata):
    """Store a data point for historical reference."""
    session = get_session()
    try:
        data_point = DataHistory(
            source_type=source_type,
            date=date,
            value=value
        )
        data_point.set_metadata(metadata)
        
        session.add(data_point)
        session.commit()
        return data_point.id
    except Exception as e:
        session.rollback()
        print(f"Error storing data point: {e}")
        return None
    finally:
        session.close()

def get_data_history(source_type, start_date, end_date, metadata_filter=None):
    """Get historical data points within a date range and optional metadata filter."""
    session = get_session()
    try:
        query = session.query(DataHistory).filter(
            DataHistory.source_type == source_type,
            DataHistory.date >= start_date,
            DataHistory.date <= end_date
        )
        
        results = query.all()
        
        # Apply metadata filter if provided
        if metadata_filter:
            filtered_results = []
            for result in results:
                metadata = result.get_metadata()
                match = True
                for key, value in metadata_filter.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                if match:
                    filtered_results.append(result)
            results = filtered_results
        
        return [{
            'id': point.id,
            'date': point.date,
            'value': point.value,
            'metadata': point.get_metadata(),
            'created_at': point.created_at
        } for point in results]
    except Exception as e:
        print(f"Error getting data history: {e}")
        return []
    finally:
        session.close()

# Initialize the database
init_db()
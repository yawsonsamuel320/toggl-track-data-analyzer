import requests
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

# Retrieve sensitive information from environment variables
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
TOGGL_API_TOKEN = os.getenv('TOGGL_API_TOKEN')

# Check if the API token is loaded properly
if not TOGGL_API_TOKEN:
    print("Please check your API token!")
    exit()

# Initialize SQLAlchemy
Base = declarative_base()

# Define database connection string
DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Create the SQLAlchemy engine and session
engine = create_engine(DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# ORM Models

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    workspaces = relationship('Workspace', back_populates='organization')

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))

class Workspace(Base):
    __tablename__ = 'workspaces'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    organization = relationship('Organization', back_populates='workspaces')
    clients = relationship('Client', back_populates='workspace')
    time_entries = relationship('TimeEntry', back_populates='workspace')

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))
    workspace = relationship('Workspace', back_populates='clients')
    tasks = relationship('Task', back_populates='client')

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    client_id = Column(Integer, ForeignKey('clients.id'))
    client = relationship('Client', back_populates='tasks')

class TimeEntry(Base):
    __tablename__ = 'time_entries'
    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Float)
    user_id = Column(Integer)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))
    workspace = relationship('Workspace', back_populates='time_entries')
    project = relationship('Project', back_populates='time_entries')

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    time_entries = relationship('TimeEntry', back_populates='project')

class Approval(Base):
    __tablename__ = 'approvals'
    id = Column(Integer, primary_key=True)
    approved_by = Column(String(255))
    time_entry_id = Column(Integer, ForeignKey('time_entries.id'))
    time_entry = relationship('TimeEntry')

# Create all the tables in the database
Base.metadata.create_all(engine)

# Function to fetch data from the Toggl API
def fetch_toggl_data(api_token):
    url = "https://api.track.toggl.com/api/v9/me/time_entries"
    auth = (api_token, "api_token")
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, auth=auth, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

# Function to populate the database with data
def insert_toggl_data_into_db(time_entries):
    for entry in time_entries:
        # Get or create the related records
        workspace = session.query(Workspace).filter_by(id=entry['workspace_id']).first()
        if not workspace:
            workspace = Workspace(id=entry['workspace_id'], name="Unknown")
            session.add(workspace)

        project = session.query(Project).filter_by(id=entry['project_id']).first()
        if not project:
            project = Project(id=entry['project_id'], name="Unknown")
            session.add(project)

        # Create Time Entry object
        time_entry = TimeEntry(
            id=entry['id'],
            description=entry.get('description', ''),
            start_time=datetime.strptime(entry['start'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            end_time=datetime.strptime(entry['end'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            duration=entry['duration'],
            user_id=entry['user_id'],
            project_id=entry['project_id'],
            workspace_id=entry['workspace_id']
        )
        session.add(time_entry)

    # Commit the transaction
    session.commit()

# Main script
if __name__ == '__main__':
    # Fetch Toggl time entries using the API token from .env
    time_entries = fetch_toggl_data(TOGGL_API_TOKEN)
    
    if time_entries:
        # Insert the data into the database
        insert_toggl_data_into_db(time_entries)
        
        print("Data insertion complete.")
    else:
        print("No data retrieved from Toggl API.")

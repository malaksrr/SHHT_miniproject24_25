import sqlite3
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # directory where the script lives
DB_PATH = os.path.join(BASE_DIR, "study_habits.db")

def init_db():
    """Initialize database with proper table structure"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Remove this line so table is NOT dropped every time
    # cursor.execute("DROP TABLE IF EXISTS study_sessions")
    
    # Create table only if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            study_hours REAL NOT NULL,
            sleep_hours REAL NOT NULL,
            break_frequency INTEGER NOT NULL,
            concentration_level INTEGER NOT NULL,
            risk_score REAL
        )
    ''')
    
    # Create index if not exists
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_username 
        ON study_sessions (username)
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")


def save_study_session(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO study_sessions (
            username, study_hours, sleep_hours, 
            break_frequency, concentration_level, risk_score
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['username'],
        data['study_hours'],
        data['sleep_hours'],
        data['break_frequency'],
        data['concentration_level'],
        data.get('risk_score')
    ))
    conn.commit()
    conn.close()
    
def get_user_sessions(username, time_range='all'):
    """Retrieve user's study sessions with optional time filtering"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Calculate cutoff time in UTC
    cutoff = None
    if time_range == 'hour':
        cutoff = datetime.utcnow() - timedelta(hours=1)
    elif time_range == 'day':
        cutoff = datetime.utcnow() - timedelta(days=1)
    elif time_range == 'week':
        cutoff = datetime.utcnow() - timedelta(weeks=1)
    elif time_range == 'month':
        cutoff = datetime.utcnow() - timedelta(days=30)
    
    query = """
        SELECT 
            id,
            datetime(timestamp, 'localtime') as timestamp,
            study_hours,
            sleep_hours,
            break_frequency,
            concentration_level,
            risk_score,
            CASE
                WHEN risk_score > 70 THEN 'high'
                WHEN risk_score > 40 THEN 'medium'
                ELSE 'low'
            END as risk_level
        FROM study_sessions 
        WHERE username = ?
    """
    params = [username]
    
    if cutoff:
        query += " AND timestamp >= ?"
        params.append(cutoff.strftime('%Y-%m-%d %H:%M:%S'))
    
    query += " ORDER BY timestamp DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_user_history(username, time_range='all'):
    """Clear user's history based on time range"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Use UTC for all time calculations
    current_time = datetime.utcnow()
    cutoff = None
    
    if time_range == 'hour':
        cutoff = current_time - timedelta(hours=1)
    elif time_range == 'day':
        cutoff = current_time - timedelta(days=1)
    elif time_range == 'week':
        cutoff = current_time - timedelta(weeks=1)
    elif time_range == 'month':
        cutoff = current_time - timedelta(days=30)
    
    if cutoff:
        # Convert cutoff to UTC string without timezone conversion
        cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
        # Use timestamp column directly without conversion
        count_query = "SELECT COUNT(*) FROM study_sessions WHERE username = ? AND timestamp >= ?"
        delete_query = "DELETE FROM study_sessions WHERE username = ? AND timestamp >= ?"
        params = (username, cutoff_str)
    else:
        count_query = "SELECT COUNT(*) FROM study_sessions WHERE username = ?"
        delete_query = "DELETE FROM study_sessions WHERE username = ?"
        params = (username,)
    
    cursor.execute(count_query, params)
    count = cursor.fetchone()[0]
    
    cursor.execute(delete_query, params)
    conn.commit()
    conn.close()
    return count
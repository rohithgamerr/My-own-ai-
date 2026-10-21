
import sqlite3
from datetime import datetime, timedelta

db_path = '/root/Lumina_OS/nexus/nexus_calendar.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    title TEXT,
    start_time TEXT,
    end_time TEXT,
    priority TEXT,
    category TEXT
)
''')

# Sample Data for a "Power Day"
events = [
    ('Wake Up Call', '05:00', '05:15', 'Critical', 'Routine'),
    ('Deep Work: Project Dev', '06:00', '08:00', 'Critical', 'Work'),
    ('Morning Review & Email Batching', '09:00', '10:00', 'Medium', 'Work'),
    ('Scheduled Reminder', '10:50', '11:00', 'High', 'Reminder'),
    ('Recovery & Lunch', '13:00', '14:00', 'Low', 'Rest'),
]

for title, start, end, prio, cat in events:
    cursor.execute('INSERT INTO events (title, start_time, end_time, priority, category) VALUES (?, ?, ?, ?, ?)', 
                   (title, start, end, prio, cat))

conn.commit()
conn.close()
print("Power Day data injected successfully.")

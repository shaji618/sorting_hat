import sqlite3

def create_connection():
    conn = sqlite3.connect('hogwarts.db')
    return conn

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        name TEXT PRIMARY KEY,
        favorite_color TEXT,
        pet_type TEXT,
        adjective_descriptors TEXT,
        chosen_house TEXT
    )
    ''')
    conn.commit()

def insert_or_update_student(conn, name, favorite_color, pet_type, adjective_descriptors, chosen_house):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO students (name, favorite_color, pet_type, adjective_descriptors, chosen_house)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, favorite_color, pet_type, ','.join(adjective_descriptors), chosen_house))
    conn.commit()

def get_student_house(conn, name):
    cursor = conn.cursor()
    cursor.execute('SELECT chosen_house FROM students WHERE name = ?', (name,))
    result = cursor.fetchone()
    return result[0] if result else None

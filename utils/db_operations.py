import sqlite3
import os

DATABASE_PATH = 'database/educational_resources.db'

def insert_resource(name, category, path):
    """Insert a new resource into the database."""
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO resources (name, category, path) VALUES (?, ?, ?)", (name, category, path))
    connection.commit()
    connection.close()

def get_categories():
    """Retrieve all unique categories from the database."""
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    categories = cursor.execute("SELECT DISTINCT category FROM resources").fetchall()
    connection.close()
    return [category[0] for category in categories]

def get_resources_by_category(category):
    """Retrieve all resources under a specific category."""
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    resources = cursor.execute("SELECT name, path FROM resources WHERE category = ?", (category,)).fetchall()
    connection.close()
    return resources

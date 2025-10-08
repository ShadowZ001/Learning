#!/usr/bin/env python3
"""
Database update script to add embeds table
"""

import sqlite3

def update_database():
    conn = sqlite3.connect("dravon.db")
    cursor = conn.cursor()
    
    # Add embeds table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeds (
            guild_id INTEGER,
            embed_name TEXT,
            config TEXT,
            PRIMARY KEY (guild_id, embed_name)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database updated successfully!")

if __name__ == "__main__":
    update_database()
import sqlite3
import json
import os

DB_PATH = "agent_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 存储普通对话历史
    cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                      (session_id TEXT PRIMARY KEY, messages TEXT)''')
    # 存储用户指定的长期记忆（事实库）
    cursor.execute('''CREATE TABLE IF NOT EXISTS long_term_memory 
                      (user_id TEXT, key TEXT, value TEXT, PRIMARY KEY(user_id, key))''')
    conn.commit()
    conn.close()

def save_history(session_id, messages):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO history VALUES (?, ?)", 
                   (session_id, json.dumps(messages)))
    conn.commit()
    conn.close()

def get_history(session_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT messages FROM history WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else []
import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin','123','gerente')")

conn.commit()
conn.close()
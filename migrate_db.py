# Script de migração do banco de dados
# Execute este script se atualizar de uma versão anterior
# python migrate_db.py

import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

print("Verificando e aplicando migrações...")

# Adicionar colunas faltantes em clients
try:
    cur.execute("ALTER TABLE clients ADD COLUMN phone TEXT;")
    print("✓ Adicionada coluna phone em clients")
except sqlite3.OperationalError:
    print("⚠ Coluna phone já existe em clients")

try:
    cur.execute("ALTER TABLE clients ADD COLUMN address TEXT;")
    print("✓ Adicionada coluna address em clients")
except sqlite3.OperationalError:
    print("⚠ Coluna address já existe em clients")

try:
    cur.execute("ALTER TABLE clients ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;")
    print("✓ Adicionada coluna created_at em clients")
except sqlite3.OperationalError:
    print("⚠ Coluna created_at já existe em clients")

# Adicionar colunas faltantes em products
try:
    cur.execute("ALTER TABLE products ADD COLUMN barcode TEXT;")
    print("✓ Adicionada coluna barcode em products")
except sqlite3.OperationalError:
    print("⚠ Coluna barcode já existe em products")

try:
    cur.execute("ALTER TABLE products ADD COLUMN description TEXT;")
    print("✓ Adicionada coluna description em products")
except sqlite3.OperationalError:
    print("⚠ Coluna description já existe em products")

try:
    cur.execute("ALTER TABLE products ADD COLUMN category TEXT;")
    print("✓ Adicionada coluna category em products")
except sqlite3.OperationalError:
    print("⚠ Coluna category já existe em products")

try:
    cur.execute("ALTER TABLE products ADD COLUMN brand TEXT;")
    print("✓ Adicionada coluna brand em products")
except sqlite3.OperationalError:
    print("⚠ Coluna brand já existe em products")

try:
    cur.execute("ALTER TABLE products ADD COLUMN margin REAL;")
    print("✓ Adicionada coluna margin em products")
except sqlite3.OperationalError:
    print("⚠ Coluna margin já existe em products")

try:
    cur.execute("ALTER TABLE products ADD COLUMN unit TEXT DEFAULT 'UN';")
    print("✓ Adicionada coluna unit em products")
except sqlite3.OperationalError:
    print("⚠ Coluna unit já existe em products")

# Adicionar colunas faltantes em sales
try:
    cur.execute("ALTER TABLE sales ADD COLUMN discount REAL DEFAULT 0;")
    print("✓ Adicionada coluna discount em sales")
except sqlite3.OperationalError:
    print("⚠ Coluna discount já existe em sales")

try:
    cur.execute("ALTER TABLE sales ADD COLUMN status TEXT DEFAULT 'Finalizada';")
    print("✓ Adicionada coluna status em sales")
except sqlite3.OperationalError:
    print("⚠ Coluna status já existe em sales")

# Adicionar coluna status em payment_methods se não existir
try:
    cur.execute("ALTER TABLE payment_methods ADD COLUMN status TEXT DEFAULT 'Ativo';")
    print("✓ Adicionada coluna status em payment_methods")
except sqlite3.OperationalError:
    print("⚠ Coluna status já existe em payment_methods")

# Verificar se payment_methods tem dados padrão
cur.execute("SELECT COUNT(*) FROM payment_methods;")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO payment_methods (name, status) VALUES ('Dinheiro', 'Ativo');")
    cur.execute("INSERT INTO payment_methods (name, status) VALUES ('Cartão', 'Ativo');")
    cur.execute("INSERT INTO payment_methods (name, status) VALUES ('PIX', 'Ativo');")
    print("✓ Inseridos métodos de pagamento padrão")

conn.commit()
conn.close()

print("\nMigrações concluídas!")
import sqlite3
from datetime import datetime

DB = 'database.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(row['name'] == column for row in cur.fetchall())


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )''')

    # Clients
    cur.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cpf TEXT UNIQUE,
        email TEXT,
        phone TEXT,
        gender TEXT DEFAULT 'Masculino',
        cep TEXT,
        street TEXT,
        number TEXT,
        neighborhood TEXT,
        city TEXT,
        state TEXT,
        address TEXT,
        status TEXT DEFAULT 'Ativo',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    if not column_exists(cur, 'clients', 'gender'):
        cur.execute("ALTER TABLE clients ADD COLUMN gender TEXT DEFAULT 'Masculino'")
    if not column_exists(cur, 'clients', 'cep'):
        cur.execute("ALTER TABLE clients ADD COLUMN cep TEXT")
    if not column_exists(cur, 'clients', 'street'):
        cur.execute("ALTER TABLE clients ADD COLUMN street TEXT")
    if not column_exists(cur, 'clients', 'number'):
        cur.execute("ALTER TABLE clients ADD COLUMN number TEXT")
    if not column_exists(cur, 'clients', 'neighborhood'):
        cur.execute("ALTER TABLE clients ADD COLUMN neighborhood TEXT")
    if not column_exists(cur, 'clients', 'city'):
        cur.execute("ALTER TABLE clients ADD COLUMN city TEXT")
    if not column_exists(cur, 'clients', 'state'):
        cur.execute("ALTER TABLE clients ADD COLUMN state TEXT")
    if not column_exists(cur, 'clients', 'address'):
        cur.execute("ALTER TABLE clients ADD COLUMN address TEXT")
    if not column_exists(cur, 'clients', 'status'):
        cur.execute("ALTER TABLE clients ADD COLUMN status TEXT DEFAULT 'Ativo'")
    cur.execute("UPDATE clients SET status='Ativo' WHERE status IS NULL")

    # Products
    cur.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT UNIQUE,
        name TEXT,
        description TEXT,
        category TEXT,
        brand TEXT,
        cost REAL,
        margin REAL,
        price REAL,
        stock INTEGER DEFAULT 0,
        min_stock INTEGER,
        unit TEXT DEFAULT 'UN',
        status TEXT DEFAULT 'Ativo'
    )''')
    if not column_exists(cur, 'products', 'status'):
        cur.execute("ALTER TABLE products ADD COLUMN status TEXT DEFAULT 'Ativo'")
    else:
        cur.execute("UPDATE products SET status='Ativo' WHERE status IS NULL")

    cur.execute("UPDATE products SET status='Ativo' WHERE status IS NULL")

    # Stock Movements
    cur.execute('''CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        type TEXT,  -- 'Entrada' or 'Saída'
        quantity INTEGER,
        reason TEXT,
        user TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')

    # Payment Methods
    cur.execute('''CREATE TABLE IF NOT EXISTS payment_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        status TEXT DEFAULT 'Ativo'
    )''')

    # Sales
    cur.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        total REAL,
        discount REAL DEFAULT 0,
        status TEXT DEFAULT 'Finalizada',  -- 'Finalizada', 'Cancelada'
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )''')

    # Sale Items
    cur.execute('''CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY (sale_id) REFERENCES sales(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')

    # Sale Payments
    cur.execute('''CREATE TABLE IF NOT EXISTS sale_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        payment_method_id INTEGER,
        amount REAL,
        FOREIGN KEY (sale_id) REFERENCES sales(id),
        FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
    )''')

    # Insert default payment methods
    cur.execute("INSERT OR IGNORE INTO payment_methods (name) VALUES ('Dinheiro')")
    cur.execute("INSERT OR IGNORE INTO payment_methods (name) VALUES ('Cartão')")
    cur.execute("INSERT OR IGNORE INTO payment_methods (name) VALUES ('PIX')")

    # Seed initial clients when database is empty or low
    cur.execute("SELECT COUNT(*) as total FROM clients")
    if cur.fetchone()['total'] < 20:
        sample_clients = [
            ('Maria Silva', '123.456.789-00', 'maria.silva@email.com', '(11) 91234-5678', 'Feminino', '01001-000', 'Rua das Flores', '10', 'Jardim', 'São Paulo', 'SP', 'Rua das Flores, 10, Jardim, São Paulo, SP', 'Ativo'),
            ('João Ferreira', '987.654.321-00', 'joao.ferreira@email.com', '(21) 99876-5432', 'Masculino', '20040-000', 'Av. Brasil', '250', 'Centro', 'Rio de Janeiro', 'RJ', 'Av. Brasil, 250, Centro, Rio de Janeiro, RJ', 'Ativo'),
            ('Tech Serviços Ltda', '12.345.678/0001-90', 'contato@techserv.com.br', '(11) 4002-8922', 'Masculino', '01310-100', 'Av. Paulista', '1000', 'Bela Vista', 'São Paulo', 'SP', 'Av. Paulista, 1000, Bela Vista, São Paulo, SP', 'Ativo'),
            ('Eletro Comércio ME', '98.765.432/0001-09', 'financeiro@eletrocom.com.br', '(31) 3333-4444', 'Masculino', '30190-000', 'R. dos Navegantes', '45', 'Funcionários', 'Belo Horizonte', 'MG', 'R. dos Navegantes, 45, Funcionários, Belo Horizonte, MG', 'Ativo'),
            ('Carla Santos', '111.222.333-44', 'carla.santos@email.com', '(11) 93333-2222', 'Feminino', '01042-000', 'Rua das Acácias', '55', 'Vila Madalena', 'São Paulo', 'SP', 'Rua das Acácias, 55, Vila Madalena, São Paulo, SP', 'Ativo'),
            ('Loja Central Ltda', '23.456.789/0001-12', 'vendas@lojacentral.com.br', '(41) 3411-2211', 'Masculino', '80010-210', 'Rua Central', '123', 'Centro', 'Curitiba', 'PR', 'Rua Central, 123, Centro, Curitiba, PR', 'Ativo'),
            ('Grupo Soluções', '34.567.890/0001-23', 'suporte@gruposolucoes.com.br', '(51) 3020-3030', 'Masculino', '90010-000', 'Av. Independência', '77', 'Centro Histórico', 'Porto Alegre', 'RS', 'Av. Independência, 77, Centro Histórico, Porto Alegre, RS', 'Ativo'),
            ('Felipe Costa', '222.333.444-55', 'felipe.costa@email.com', '(11) 94444-5555', 'Masculino', '02240-050', 'Rua do Comércio', '82', 'Santana', 'São Paulo', 'SP', 'Rua do Comércio, 82, Santana, São Paulo, SP', 'Ativo'),
            ('Juliana Almeida', '333.444.555-66', 'juliana.almeida@email.com', '(21) 95555-6666', 'Feminino', '22021-020', 'Av. das Palmeiras', '91', 'Laranjeiras', 'Rio de Janeiro', 'RJ', 'Av. das Palmeiras, 91, Laranjeiras, Rio de Janeiro, RJ', 'Ativo'),
            ('Prime Engenharia Ltda', '45.678.901/0001-34', 'contato@primeengenharia.com.br', '(61) 3444-5566', 'Masculino', '70634-901', 'R. do Progresso', '200', 'Setor Norte', 'Brasília', 'DF', 'R. do Progresso, 200, Setor Norte, Brasília, DF', 'Ativo'),
            ('Lucas Pereira', '444.555.666-77', 'lucas.pereira@email.com', '(11) 96666-7777', 'Masculino', '03063-020', 'Rua da Liberdade', '12', 'Liberdade', 'São Paulo', 'SP', 'Rua da Liberdade, 12, Liberdade, São Paulo, SP', 'Ativo'),
            ('Store Online ME', '56.789.012/0001-45', 'comercial@storeonline.com.br', '(71) 3333-8888', 'Masculino', '40015-280', 'Av. do Comércio', '310', 'Centro', 'Salvador', 'BA', 'Av. do Comércio, 310, Centro, Salvador, BA', 'Ativo'),
            ('Inove Soluções', '67.890.123/0001-56', 'contabilidade@inovesolucoes.com.br', '(81) 3200-9900', 'Masculino', '50030-000', 'Av. Bela Vista', '420', 'Boa Viagem', 'Recife', 'PE', 'Av. Bela Vista, 420, Boa Viagem, Recife, PE', 'Ativo'),
            ('Fernando Rocha', '555.666.777-88', 'fernando.rocha@email.com', '(21) 97777-8888', 'Masculino', '22640-460', 'Rua dos Cravos', '98', 'Barra', 'Rio de Janeiro', 'RJ', 'Rua dos Cravos, 98, Barra, Rio de Janeiro, RJ', 'Ativo'),
            ('Mamae Cuida Ltda', '78.901.234/0001-67', 'financeiro@mamãecuida.com.br', '(11) 3222-4455', 'Feminino', '08225-130', 'Rua das Orquídeas', '10', 'Tatuapé', 'São Paulo', 'SP', 'Rua das Orquídeas, 10, Tatuapé, São Paulo, SP', 'Ativo'),
            ('Ana Beatriz', '666.777.888-99', 'ana.beatriz@email.com', '(31) 98888-9999', 'Feminino', '30190-151', 'Rua Nova', '14', 'Savassi', 'Belo Horizonte', 'MG', 'Rua Nova, 14, Savassi, Belo Horizonte, MG', 'Ativo'),
            ('Gold Equipamentos', '89.012.345/0001-78', 'vendas@goldequip.com.br', '(41) 3511-8899', 'Masculino', '80720-020', 'Av. das Nações', '550', 'Água Verde', 'Curitiba', 'PR', 'Av. das Nações, 550, Água Verde, Curitiba, PR', 'Ativo'),
            ('Pedro Gomes', '777.888.999-00', 'pedro.gomes@email.com', '(21) 96666-0000', 'Masculino', '23010-120', 'Rua da Paz', '32', 'Tijuca', 'Rio de Janeiro', 'RJ', 'Rua da Paz, 32, Tijuca, Rio de Janeiro, RJ', 'Ativo'),
            ('Max Importação', '90.123.456/0001-89', 'import@maximport.com.br', '(61) 3344-2233', 'Masculino', '70040-010', 'Rua do Trabalho', '100', 'Asa Norte', 'Brasília', 'DF', 'Rua do Trabalho, 100, Asa Norte, Brasília, DF', 'Ativo'),
            ('Vendas Rápidas', '01.234.567/0001-90', 'comercial@vendarapidas.com.br', '(71) 3455-6677', 'Masculino', '44013-250', 'Rua do Comércio', '77', 'Centro', 'Feira de Santana', 'BA', 'Rua do Comércio, 77, Centro, Feira de Santana, BA', 'Ativo')
        ]
        for client in sample_clients:
            cur.execute("INSERT OR IGNORE INTO clients (name, cpf, email, phone, gender, cep, street, number, neighborhood, city, state, address, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", client)

    # Seed sample products when database is empty or low
    cur.execute("SELECT COUNT(*) as total FROM products")
    if cur.fetchone()['total'] < 100:
        sample_product_types = [
            'Cabo USB', 'Teclado Mecânico', 'Mouse Gamer', 'Monitor 24"', 'SSD SATA', 'HD Externo',
            'Fonte ATX', 'Ventoinha RGB', 'Placa Mãe', 'Processador', 'Memória RAM', 'Adaptador HDMI',
            'Fone de Ouvido', 'Roteador Wireless', 'Carregador USB-C', 'Bateria Recarregável',
            'Microfone USB', 'Webcam Full HD', 'Leitor de Cartão', 'Estabilizador', 'Sensor de Presença',
            'Caixa de Som', 'Suporte de Monitor', 'Notebook 14"', 'Tablet 10"', 'SSD NVMe',
            'Câmera IP', 'Teclado Sem Fio', 'Mouse Sem Fio', 'Headset Gamer'
        ]
        sample_brands = ['Corsair', 'Logitech', 'Intel', 'Xiaomi', 'Sony', 'Philips', 'Samsung', 'Kingston', 'TP-Link', 'Acer']
        sample_categories = ['Acessórios', 'Hardware', 'Periféricos', 'Redes', 'Áudio', 'Energia', 'Computadores']

        for i in range(1, 101):
            name = f"{sample_brands[i % len(sample_brands)]} {sample_product_types[i % len(sample_product_types)]} {100 + i}"
            barcode = f"PROD{i:04d}"
            description = f"{name} de alta performance para uso profissional e cotidiano."
            category = sample_categories[i % len(sample_categories)]
            brand = sample_brands[i % len(sample_brands)]
            cost = round(15.0 + i * 1.8, 2)
            margin = 25.0
            price = round(cost * (1 + margin / 100), 2)
            min_stock = 5 + (i % 6)
            unit = 'un'
            cur.execute("INSERT OR IGNORE INTO products (barcode, name, description, category, brand, cost, margin, price, stock, min_stock, unit, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (barcode, name, description, category, brand, cost, margin, price, 12 + (i % 18), min_stock, unit, 'Ativo'))

    conn.commit()
    conn.close()
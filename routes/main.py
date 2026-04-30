from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.database import get_db
from datetime import datetime
import qrcode
import io
import base64
import urllib.request
import json
import math

main = Blueprint('main', __name__)

@main.before_app_request
def require_login():
    if request.endpoint and request.endpoint.startswith('main.'):
        if request.endpoint not in ('main.login', 'main.logout') and 'user' not in session:
            return redirect(url_for('main.login'))

# ------------------ LOGIN ------------------
@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        result = cur.fetchone()

        if result:
            session['user'] = user
            session['role'] = result['role']
            return redirect('/dashboard')
        else:
            flash('Login inválido')

    return render_template('login.html')

# ------------------ DASHBOARD ------------------
@main.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()
    # Total vendas
    cur.execute("SELECT SUM(total) as total_sales FROM sales WHERE status='Finalizada'")
    total_sales = cur.fetchone()['total_sales'] or 0
    # Produtos baixo estoque
    cur.execute("SELECT COUNT(*) as low_stock FROM products WHERE stock <= min_stock")
    low_stock = cur.fetchone()['low_stock']
    # Total clientes
    cur.execute("SELECT COUNT(*) as total_clients FROM clients WHERE status='Ativo'")
    total_clients = cur.fetchone()['total_clients']
    return render_template('dashboard.html', total_sales=total_sales, low_stock=low_stock, total_clients=total_clients)

# ------------------ CLIENTS ------------------
@main.route('/clients', methods=['GET', 'POST'])
def clients():
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        cpf = request.form['cpf']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form.get('gender', 'Masculino')
        cep = request.form.get('cep', '')
        street = request.form.get('street', '')
        number = request.form.get('number', '')
        neighborhood = request.form.get('neighborhood', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        status = request.form.get('status', 'Ativo')
        address = f"{street}, {number} - {neighborhood}, {city}/{state} - CEP {cep}"

        try:
            cur.execute("INSERT INTO clients (name, cpf, email, phone, gender, cep, street, number, neighborhood, city, state, address, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (name, cpf, email, phone, gender, cep, street, number, neighborhood, city, state, address, status))
            conn.commit()
            flash('Cliente cadastrado!')
            return redirect(url_for('main.clients'))
        except:
            flash('CPF já cadastrado!')

    search = request.args.get('search', '')
    per_page = int(request.args.get('per_page', 10))
    if per_page not in [10, 20, 40, 60, 80, 100]:
        per_page = 10
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1

    if search:
        cur.execute("SELECT COUNT(*) as total FROM clients WHERE name LIKE ? OR cpf LIKE ? OR email LIKE ?", ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
        total_clients = cur.fetchone()['total']
        total_pages = max(1, math.ceil(total_clients / per_page))
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page
        cur.execute("SELECT * FROM clients WHERE name LIKE ? OR cpf LIKE ? OR email LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?", ('%' + search + '%', '%' + search + '%', '%' + search + '%', per_page, offset))
    else:
        cur.execute("SELECT COUNT(*) as total FROM clients")
        total_clients = cur.fetchone()['total']
        total_pages = max(1, math.ceil(total_clients / per_page))
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page
        cur.execute("SELECT * FROM clients ORDER BY created_at DESC LIMIT ? OFFSET ?", (per_page, offset))
    data = cur.fetchall()

    return render_template('clients.html', clients=data, page=page, per_page=per_page, total_pages=total_pages, total_clients=total_clients, search=search)

# API para busca de clientes
@main.route('/api/clients/search')
def search_clients():
    query = request.args.get('q', '')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, cpf FROM clients WHERE name LIKE ? AND status='Ativo' LIMIT 10", ('%' + query + '%',))
    clients = cur.fetchall()
    return jsonify([dict(client) for client in clients])

@main.route('/api/cep/<cep>')
def lookup_cep(cep):
    cep_clean = ''.join(filter(str.isdigit, cep))[:8]
    if len(cep_clean) != 8:
        return jsonify({'error': 'CEP inválido'}), 400
    try:
        with urllib.request.urlopen(f'https://viacep.com.br/ws/{cep_clean}/json/') as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('erro'):
                return jsonify({'error': 'CEP não encontrado'}), 404
            return jsonify(data)
    except Exception:
        return jsonify({'error': 'Erro ao consultar CEP'}), 500

# ------------------ PRODUCTS ------------------
@main.route('/products', methods=['GET', 'POST'])
def products():
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        barcode = request.form['barcode']
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        brand = request.form['brand']
        cost = float(request.form['cost'])
        margin = float(request.form['margin'])
        price = cost + (cost * margin / 100)
        min_stock = int(request.form['min_stock'])
        unit = request.form['unit']
        status = request.form.get('status', 'Ativo')

        try:
            cur.execute("INSERT INTO products (barcode, name, description, category, brand, cost, margin, price, min_stock, unit, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (barcode, name, description, category, brand, cost, margin, price, min_stock, unit, status))
            conn.commit()
            flash('Produto cadastrado!')
            return redirect(url_for('main.products'))
        except:
            flash('Código de barras já existe!')

    search = request.args.get('search', '')
    per_page = int(request.args.get('per_page', 10))
    if per_page not in [10, 20, 40, 60, 80, 100]:
        per_page = 10
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1

    if search:
        cur.execute("SELECT COUNT(*) as total FROM products WHERE name LIKE ? OR barcode LIKE ? OR category LIKE ?", ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
        total_products = cur.fetchone()['total']
        total_pages = max(1, math.ceil(total_products / per_page))
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page
        cur.execute("SELECT * FROM products WHERE name LIKE ? OR barcode LIKE ? OR category LIKE ? ORDER BY name LIMIT ? OFFSET ?", ('%' + search + '%', '%' + search + '%', '%' + search + '%', per_page, offset))
    else:
        cur.execute("SELECT COUNT(*) as total FROM products")
        total_products = cur.fetchone()['total']
        total_pages = max(1, math.ceil(total_products / per_page))
        if page > total_pages:
            page = total_pages
        offset = (page - 1) * per_page
        cur.execute("SELECT * FROM products ORDER BY name LIMIT ? OFFSET ?", (per_page, offset))
    data = cur.fetchall()

    return render_template('products.html', products=data, page=page, per_page=per_page, total_pages=total_pages, total_products=total_products, search=search)

# API para busca de produtos
@main.route('/api/products/search')
def search_products():
    query = request.args.get('q', '')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products WHERE name LIKE ? AND status='Ativo' LIMIT 10", ('%' + query + '%',))
    products = cur.fetchall()
    return jsonify([dict(product) for product in products])

# ------------------ STOCK ------------------
@main.route('/stock', methods=['GET', 'POST'])
def stock():
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        product_id = request.form['product_id']
        qty = int(request.form['qty'])
        type_op = request.form['type']
        reason = request.form['reason']
        user = session['user']

        if type_op == 'Entrada':
            cur.execute("UPDATE products SET stock = stock + ? WHERE id=?", (qty, product_id))
        else:
            cur.execute("UPDATE products SET stock = stock - ? WHERE id=?", (qty, product_id))

        cur.execute("INSERT INTO stock_movements (product_id, type, quantity, reason, user) VALUES (?, ?, ?, ?, ?)",
                    (product_id, type_op, qty, reason, user))
        conn.commit()
        flash('Movimentação registrada!')

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    cur.execute("SELECT sm.*, p.name FROM stock_movements sm JOIN products p ON sm.product_id = p.id ORDER BY sm.created_at DESC LIMIT 20")
    movements = cur.fetchall()

    return render_template('stock.html', products=products, movements=movements)

# ------------------ PAYMENT METHODS ------------------
@main.route('/payment_methods', methods=['GET', 'POST'])
def payment_methods():
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        status = request.form.get('status', 'Ativo')
        try:
            cur.execute("INSERT INTO payment_methods (name, status) VALUES (?, ?)", (name, status))
            conn.commit()
            flash('Forma de pagamento cadastrada!')
        except:
            flash('Nome já existe!')

    cur.execute("SELECT * FROM payment_methods")
    data = cur.fetchall()

    return render_template('payment_methods.html', methods=data)

@main.route('/payment_methods/toggle/<int:id>')
def toggle_payment_method(id):
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT status FROM payment_methods WHERE id=?", (id,))
    current = cur.fetchone()['status']
    new_status = 'Inativo' if current == 'Ativo' else 'Ativo'
    cur.execute("UPDATE payment_methods SET status=? WHERE id=?", (new_status, id))
    conn.commit()
    return redirect('/payment_methods')

# ------------------ PDV ------------------
@main.route('/pdv', methods=['GET', 'POST'])
def pdv():
    if 'user' not in session:
        return redirect('/')
    if request.method == 'POST':
        # Processar venda
        client_id = request.form.get('client_id')
        items = request.form.getlist('product_id[]')
        qtys = request.form.getlist('qty[]')
        payments = request.form.getlist('payment_method[]')
        amounts = request.form.getlist('amount[]')
        discount = float(request.form.get('discount', 0))

        conn = get_db()
        cur = conn.cursor()

        # Verificar cliente ativo
        if client_id:
            cur.execute("SELECT status FROM clients WHERE id=?", (client_id,))
            if cur.fetchone()['status'] != 'Ativo':
                flash('Cliente inativo!')
                return redirect('/pdv')

        total = 0
        sale_items = []
        for i, product_id in enumerate(items):
            qty = int(qtys[i])
            cur.execute("SELECT * FROM products WHERE id=?", (product_id,))
            product = cur.fetchone()
            if product['stock'] < qty:
                flash(f'Sem estoque para {product["name"]}!')
                return redirect('/pdv')
            total += product['price'] * qty
            sale_items.append((product_id, qty, product['price']))

        # Desconto
        if discount > 5 and session['role'] != 'gerente':
            flash('Desconto acima de 5% requer gerente!')
            return redirect('/pdv')
        total -= total * discount / 100

        # Verificar pagamentos
        paid = sum(float(a) for a in amounts)
        if paid < total:
            flash('Valor pago insuficiente!')
            return redirect('/pdv')

        # Inserir venda
        cur.execute("INSERT INTO sales (client_id, total, discount) VALUES (?, ?, ?)", (client_id, total, discount))
        sale_id = cur.lastrowid

        # Itens
        for product_id, qty, price in sale_items:
            cur.execute("INSERT INTO sale_items (sale_id, product_id, quantity, price) VALUES (?, ?, ?, ?)", (sale_id, product_id, qty, price))
            cur.execute("UPDATE products SET stock = stock - ? WHERE id=?", (qty, product_id))

        # Pagamentos
        for i, pm_name in enumerate(payments):
            cur.execute("SELECT id FROM payment_methods WHERE name=? AND status='Ativo'", (pm_name,))
            pm_row = cur.fetchone()
            if pm_row:
                cur.execute("INSERT INTO sale_payments (sale_id, payment_method_id, amount) VALUES (?, ?, ?)", (sale_id, pm_row['id'], amounts[i]))

        conn.commit()
        flash('Venda realizada!')

        # Comprovante
        return redirect(url_for('main.receipt', sale_id=sale_id))

    # GET
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM payment_methods WHERE status='Ativo'")
    payment_methods = [dict(method) for method in cur.fetchall()]
    return render_template('pdv.html', payment_methods=payment_methods)

# ------------------ RECEIPT ------------------
@main.route('/receipt/<int:sale_id>')
def receipt(sale_id):
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT s.*, c.name as client_name FROM sales s LEFT JOIN clients c ON s.client_id = c.id WHERE s.id=?", (sale_id,))
    sale = cur.fetchone()
    cur.execute("SELECT si.*, p.name FROM sale_items si JOIN products p ON si.product_id = p.id WHERE si.sale_id=?", (sale_id,))
    items = cur.fetchall()
    cur.execute("SELECT sp.amount, pm.name FROM sale_payments sp JOIN payment_methods pm ON sp.payment_method_id = pm.id WHERE sp.sale_id=?", (sale_id,))
    payments = cur.fetchall()
    paid = sum([payment['amount'] for payment in payments]) if payments else 0
    change = paid - sale['total'] if sale else 0
    return render_template('receipt.html', sale=sale, items=items, payments=payments, paid=paid, change=change)

# ------------------ SALES LIST ------------------
@main.route('/sales_list')
def sales_list():
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()
    search = request.args.get('search', '')
    if search:
        cur.execute("SELECT s.*, c.name as client_name FROM sales s LEFT JOIN clients c ON s.client_id = c.id WHERE s.id LIKE ? OR c.name LIKE ? ORDER BY s.created_at DESC", ('%' + search + '%', '%' + search + '%'))
    else:
        cur.execute("SELECT s.*, c.name as client_name FROM sales s LEFT JOIN clients c ON s.client_id = c.id ORDER BY s.created_at DESC")
    sales = cur.fetchall()
    return render_template('sales_list.html', sales=sales, search=search)

# ------------------ REPORTS ------------------
@main.route('/reports')
def reports():
    if 'user' not in session:
        return redirect('/')
    conn = get_db()
    cur = conn.cursor()
    
    # Existing stats
    cur.execute("SELECT COUNT(*) as total_finalized FROM sales WHERE status='Finalizada'")
    total_finalized = cur.fetchone()['total_finalized']
    cur.execute("SELECT COUNT(*) as total_cancelled FROM sales WHERE status='Cancelada'")
    total_cancelled = cur.fetchone()['total_cancelled']
    cur.execute("SELECT SUM(total) as revenue FROM sales WHERE status='Finalizada'")
    revenue = cur.fetchone()['revenue'] or 0
    cur.execute("SELECT COUNT(*) as active_clients FROM clients WHERE status='Ativo'")
    active_clients = cur.fetchone()['active_clients']
    cur.execute("SELECT p.name as client_name, COUNT(s.id) as sale_count FROM sales s JOIN clients p ON s.client_id = p.id WHERE s.client_id IS NOT NULL GROUP BY p.id ORDER BY sale_count DESC LIMIT 5")
    top_clients = cur.fetchall()
    cur.execute("SELECT pr.name as product_name, SUM(si.quantity) as sold_quantity FROM sale_items si JOIN products pr ON si.product_id = pr.id JOIN sales s ON si.sale_id = s.id WHERE s.status='Finalizada' GROUP BY pr.id ORDER BY sold_quantity DESC LIMIT 5")
    top_products = cur.fetchall()
    
    # Filters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    client_search = request.args.get('client_search', '')
    product_search = request.args.get('product_search', '')
    category_search = request.args.get('category_search', '')
    
    # Filtered sales
    per_page = int(request.args.get('per_page', 10))
    if per_page not in [10, 20, 40, 60, 80, 100]:
        per_page = 10
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1
    
    query = """
    SELECT s.id, s.created_at, s.total, s.status, c.name as client_name, 
           GROUP_CONCAT(p.name || ' (Qtd: ' || si.quantity || ')', '; ') as products
    FROM sales s 
    LEFT JOIN clients c ON s.client_id = c.id 
    LEFT JOIN sale_items si ON s.id = si.sale_id 
    LEFT JOIN products p ON si.product_id = p.id 
    WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND DATE(s.created_at) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND DATE(s.created_at) <= ?"
        params.append(end_date)
    
    if client_search:
        client_terms = [term.strip().lower() for term in client_search.replace(';', ',').split(',') if term.strip()]
        if client_terms:
            query += " AND (" + " OR ".join(["LOWER(c.name) LIKE ?" for _ in client_terms]) + ")"
            params.extend([f"%{term}%" for term in client_terms])
    
    if product_search:
        product_terms = [term.strip().lower() for term in product_search.replace(';', ',').split(',') if term.strip()]
        if product_terms:
            query += " AND (" + " OR ".join(["LOWER(p.name) LIKE ?" for _ in product_terms]) + ")"
            params.extend([f"%{term}%" for term in product_terms])
    
    if category_search:
        category_terms = [term.strip().lower() for term in category_search.replace(';', ',').split(',') if term.strip()]
        if category_terms:
            query += " AND (" + " OR ".join(["LOWER(p.category) LIKE ?" for _ in category_terms]) + ")"
            params.extend([f"%{term}%" for term in category_terms])
    
    query += " GROUP BY s.id ORDER BY s.created_at DESC"
    
    count_query = f"SELECT COUNT(*) as total FROM ({query}) as sub"
    cur.execute(count_query, params)
    total_sales = cur.fetchone()['total']
    total_pages = max(1, math.ceil(total_sales / per_page))
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * per_page
    
    paginated_query = query + " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    cur.execute(paginated_query, params)
    filtered_sales = cur.fetchall()
    
    return render_template('reports.html', 
                           total_finalized=total_finalized, 
                           total_cancelled=total_cancelled, 
                           revenue=revenue, 
                           active_clients=active_clients, 
                           top_clients=top_clients, 
                           top_products=top_products,
                           filtered_sales=filtered_sales,
                           page=page,
                           per_page=per_page,
                           total_pages=total_pages,
                           total_sales=total_sales,
                           start_date=start_date,
                           end_date=end_date,
                           client_search=client_search,
                           product_search=product_search,
                           category_search=category_search)

# ------------------ CANCEL SALE ------------------
@main.route('/cancel_sale/<int:sale_id>', methods=['POST'])
def cancel_sale(sale_id):
    if 'user' not in session:
        return redirect('/')
    reason = request.form['reason']
    conn = get_db()
    cur = conn.cursor()
    # Devolver estoque
    cur.execute("SELECT product_id, quantity FROM sale_items WHERE sale_id=?", (sale_id,))
    items = cur.fetchall()
    for item in items:
        cur.execute("UPDATE products SET stock = stock + ? WHERE id=?", (item['quantity'], item['product_id']))
        cur.execute("INSERT INTO stock_movements (product_id, type, quantity, reason, user) VALUES (?, 'Entrada', ?, ?, ?)",
                    (item['product_id'], item['quantity'], f'Estorno venda {sale_id}: {reason}', session['user']))
    cur.execute("UPDATE sales SET status='Cancelada' WHERE id=?", (sale_id,))
    conn.commit()
    flash('Venda cancelada!')
    return redirect('/sales_list')

# ------------------ GENERATE QR ------------------
@main.route('/generate_qr/<float:amount>')
def generate_qr(amount):
    qr_data = f"00020101021126860014BR.GOV.BCB.PIX0136639922542555204000053039865404{amount:.2f}5802BR5918EletroTech Distribuidora6009SAO PAULO62070503***6304"  # PIX com chave 63992254255
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return jsonify({'qr': f"data:image/png;base64,{img_base64}"})

# ------------------ LOGOUT ------------------
@main.route('/logout')
def logout():
    session.clear()
    return redirect('/')
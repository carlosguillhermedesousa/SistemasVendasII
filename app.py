from flask import Flask
from models.database import init_db
from routes.main import main

app = Flask(__name__)
app.secret_key = 'secret'
app.register_blueprint(main)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

# ------------------ TEMPLATES ------------------
# Crie uma pasta chamada templates e adicione os arquivos abaixo:

# login.html
"""
<!DOCTYPE html>
<html>
<head>
<title>EletroTech Login</title>
<style>
body { font-family: Arial; background:#0f172a; color:white; text-align:center; }
form { margin-top:100px; }
input { padding:10px; margin:5px; }
button { padding:10px; background:#22c55e; border:none; }
</style>
</head>
<body>
<h1>EletroTech</h1>
<form method="POST">
<input name="username" placeholder="Usuário"><br>
<input name="password" type="password" placeholder="Senha"><br>
<button>Entrar</button>
</form>
</body>
</html>
"""

# dashboard.html
"""
<h2>Dashboard</h2>
<a href="/clients">Clientes</a>
<a href="/products">Produtos</a>
<a href="/stock">Estoque</a>
<a href="/sales">Vendas</a>
"""

# clients.html
"""
<h2>Clientes</h2>
<form method="POST">
<input name="name" placeholder="Nome">
<input name="cpf" placeholder="CPF">
<input name="email" placeholder="Email">
<button>Cadastrar</button>
</form>
<ul>
{% for c in clients %}
<li>{{c.name}} - {{c.cpf}}</li>
{% endfor %}
</ul>
"""

# products.html
"""
<h2>Produtos</h2>
<form method="POST">
<input name="name" placeholder="Nome">
<input name="code" placeholder="Código">
<input name="cost" placeholder="Custo">
<input name="margin" placeholder="Margem %">
<input name="min_stock" placeholder="Estoque mínimo">
<button>Cadastrar</button>
</form>
<ul>
{% for p in products %}
<li>{{p.name}} - Estoque: {{p.stock}}</li>
{% endfor %}
</ul>
"""

# stock.html
"""
<h2>Entrada de Estoque</h2>
<form method="POST">
<select name="product_id">
{% for p in products %}
<option value="{{p.id}}">{{p.name}}</option>
{% endfor %}
</select>
<input name="qty" placeholder="Quantidade">
<button>Adicionar</button>
</form>
"""

# sales.html
"""
<h2>Vendas</h2>
<form method="POST">
<select name="product_id">
{% for p in products %}
<option value="{{p.id}}">{{p.name}} ({{p.stock}})</option>
{% endfor %}
</select>
<input name="qty" placeholder="Quantidade">
<button>Vender</button>
</form>
"""

# EletroTech Distribuidora - Sistema de Gestão de Vendas e Estoque

Sistema completo de PDV (Ponto de Venda) com controle de estoque profissional, desenvolvido em Flask, SQLite e Bootstrap.

## 🚀 Funcionalidades

### ✅ Implementadas
- **Login seguro** com roles (gerente/operador)
- **Dashboard** com métricas em tempo real
- **Cadastro de Clientes** avançado (CPF, telefone, endereço)
- **Cadastro de Produtos** completo (código barras, categoria, margem automática)
- **Controle de Estoque** com entradas/saídas manuais e log completo
- **Formas de Pagamento** customizáveis
- **PDV Completo** com busca dinâmica de clientes e produtos
- **Múltiplas formas de pagamento** por venda
- **Pagamento PIX** com QR Code gerado automaticamente
- **Comprovante de Venda** estilo cupom fiscal
- **Lista de Vendas** com opção de cancelamento/estorno
- **Regras de Negócio** rigorosas (estoque, desconto, cliente ativo)
- **Interface Profissional** com tema escuro e Bootstrap 5

### 🎨 Design
- Tema escuro elegante
- Layout responsivo
- Ícones Font Awesome
- Feedback visual (alertas, badges)
- Buscas AJAX em tempo real

## 🛠️ Tecnologias
- **Backend**: Flask (Python)
- **Banco**: SQLite
- **Frontend**: Bootstrap 5, JavaScript
- **QR Code**: Biblioteca qrcode (Python)

## 📦 Instalação

1. **Instalar dependências**:
   ```bash
   pip install flask qrcode[pil]
   ```

2. **Executar setup inicial**:
   ```bash
   python db.py
   ```

3. **Se atualizando de versão anterior, executar migração**:
   ```bash
   python migrate_db.py  # Se existir
   ```

4. **Rodar aplicação**:
   ```bash
   python app.py
   ```

5. **Acessar**: http://localhost:5000

## 👤 Usuário Padrão
- **Usuário**: admin
- **Senha**: 123
- **Role**: gerente

## 📋 Estrutura do Projeto
```
projeto vendas/
├── app.py                 # Arquivo principal
├── db.py                  # Setup inicial do banco
├── models/
│   └── database.py        # Funções de banco de dados
├── routes/
│   ├── __init__.py
│   └── main.py            # Todas as rotas Flask
├── static/
│   ├── css/
│   │   └── style.css      # Tema escuro
│   └── js/                # Scripts JS (futuro)
└── templates/
    ├── base.html          # Layout base
    ├── login.html
    ├── dashboard.html
    ├── clients.html
    ├── products.html
    ├── stock.html
    ├── payment_methods.html
    ├── pdv.html           # Ponto de Venda
    ├── receipt.html       # Comprovante
    └── sales_list.html
```

## 🔧 Regras de Negócio Implementadas

### RN01 - Baixa Automática de Estoque
- Estoque reduzido automaticamente na finalização da venda

### RN02 - Bloqueio de Venda sem Estoque
- Venda bloqueada se quantidade solicitada > estoque disponível
- Mensagem clara ao usuário

### RN03 - Estorno de Venda
- Cancelamento devolve produtos ao estoque
- Registro de motivo obrigatório
- Log de movimentação

### RN04 - Desconto Restrito
- Desconto até 5% liberado
- Acima de 5% requer senha de gerente

### RN05 - Cliente Ativo
- Bloqueio de venda para clientes inativos

## 🎯 Como Usar

1. **Login** com admin/123
2. **Cadastrar produtos** na seção Produtos
3. **Adicionar estoque** na seção Estoque
4. **Cadastrar clientes** (opcional)
5. **Ir para PDV** para realizar vendas
6. **Buscar produtos** digitando no campo
7. **Adicionar ao carrinho**
8. **Selecionar pagamentos**
9. **Finalizar venda** e imprimir comprovante

## 🔍 APIs Internas
- `/api/clients/search?q=termo` - Busca clientes
- `/api/products/search?q=termo` - Busca produtos

## 📱 Responsivo
Sistema totalmente responsivo, funciona em desktop e mobile.

## 🚀 Próximas Melhorias Sugeridas
- Relatórios avançados
- Backup automático
- Integração com balança
- Impressora térmica
- Multi-usuário simultâneo
- API REST completa

---
**Desenvolvido para uso profissional em PDVs e distribuidoras.**
# Projeto Gestão_Salas - Resumo do Trabalho

## 📋 Visão Geral
Sistema de gestão de reservas de salas desenvolvido para estágio na **Geocad** (ISEP).

---

## 🛠️ Tecnologias Usadas
- **Frontend:** HTML + CSS + JavaScript (básico)
- **Backend:** Python + FastAPI
- **Base de Dados:** SQLite + SQLAlchemy
- **Templates:** Jinja2

---

## 📁 Estrutura do Projeto
```
projeto/
├── app/
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── models.py            # Modelos da base de dados
│   ├── database.py          # Configuração da BD
│   ├── utils.py             # Funções auxiliares
│   ├── routers/
│   │   ├── auth.py          # Autenticação (login/logout)
│   │   ├── admin.py         # Rotas de administração
│   │   ├── dashboard.py     # Dashboard do utilizador
│   │   └── public.py        # Página pública
│   └── templates/
│       ├── base.html        # Template base
│       ├── login.html       # Página de login
│       ├── dashboard.html   # Dashboard
│       ├── public.html      # Página pública
│       ├── admin (1).html   # Admin home
│       ├── admin_salas.html # Gestão de salas
│       ├── admin_utilizadores.html # Gestão de users
│       └── admin_reservas.html # Gestão de reservas
├── notes.db                 # Base de dados SQLite
└── requirements.txt         # Dependências
```

---

## 🔐 Credenciais de Login
| Campo | Valor |
|-------|-------|
| Email | `admin@salas.pt` |
| Password | `admin123` |

---

## 📚 Funcionalidades Implementadas

### 1. Autenticação
- Login com cookies (httponly)
- Passwords com hash SHA256
- Logout com remoção de cookie

### 2. CRUD de Utilizadores (Admin)
- Criar, Ler, Editar, Eliminar users
- Validação de emails duplicados

### 3. CRUD de Salas (Admin)
- Criar salas com nome, capacidade, localização, cor
- Definir horário de funcionamento e dias úteis

### 4. Reservas
- Utilizadores podem reservar salas
- Validação de conflitos (times_overlap)
- Verificação de horário da sala

### 5. Interface Pública
- Visualização de ocupação em tempo real
- Barra de ocupação visual

---

## 🧠 Conceitos Chave (Para Explicar)

### Cookies de Autenticação
O login fica guardado num cookie `user_id` no browser. Cada pedido envia o cookie automaticamente e o servidor verifica quem é o utilizador.

### Validação de Conflitos
A função `times_overlap()` verifica se dois intervalos de tempo se sobrepõem:
```python
def times_overlap(s1, e1, s2, e2):
    return s1 < e2 and e1 > s2
```

### Diferença Admin/User
- **Admin:** Acesso total (cria users, salas, vê todas as reservas)
- **User:** Apenas reserva salas e vê as suas reservas

---

## 🎯 Personalizações Feitas
- Cores: Azul corporativo (#0066cc) + Preto
- Nome: Gestão_Salas (em vez de RoomBook)
- Logo: 📋 (prancheta)
- Fonte: Segoe UI
- JavaScript em português: `abrirModal()`, `fecharModal()`

---

## 📝 Como Executar
```bash
# Ativar ambiente virtual
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Correr o servidor
python -m uvicorn app.main:app --reload
```

Aceder a: `http://127.0.0.1:8000`

---

## 🚀 Funcionalidades Futuras (Sugestões)
- [ ] Exportar reservas para Excel
- [ ] Enviar email de confirmação
- [ ] Calendário visual tipo Google Calendar
- [ ] Login com Microsoft/Google
- [ ] Notificações de reservas

---

## 📅 Notas de Desenvolvimento
- Desenvolvido em 2 dias
- Usado IA como辅助 (50/50)
- Código entendido e modificado pessoalmente
- Projeto para estágio Geocad/ISEP

---

**Autor:** Tiago
**Data:** Fevereiro 2026
**Estágio:** Geocad @ ISEP

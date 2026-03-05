# 🏢 Gestão de Salas

Sistema de gestão de reservas de salas com autenticação LDAP.

---

## 🚀 Funcionalidades

### Utilizadores Normais
- ✅ **Login LDAP** - Autenticação com servidor LDAP
- ✅ **Ver salas** - Consulta de salas disponíveis
- ✅ **Criar reservas** - Reserva de salas por horário
- ✅ **Gerir reservas** - Eliminar as suas reservas
- ✅ **Dashboard** - Visão geral das reservas

### Administradores
- ✅ **Gerir salas** - Criar, editar, eliminar salas
- ✅ **Gerir horários** - Definir horário de funcionamento
- ✅ **Ver todas as reservas** - Listagem completa
- ✅ **Editar reservas** - Modificar qualquer reserva
- ✅ **Estatísticas** - Dashboard administrativo

---

## 🔐 Separação de Áreas

| Área | Utilizador | Admin |
|------|------------|-------|
| `/dashboard` | ✅ | ✅ |
| `/user` | ✅ | ❌ Bloqueado |
| `/admin` | ❌ Bloqueado | ✅ |
| `/` (público) | ✅ | ✅ |

---

## 🛠️ Instalação

### 1. Clonar o projeto
```bash
cd C:\Users\tiago\Documents\EduTHINK
```

### 2. Criar ambiente virtual
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Iniciar servidor LDAP de teste (opcional)
```bash
cd ldap-test
docker-compose up -d
```

**Credenciais de teste:**
| Username | Password |
|----------|----------|
| tiago    | password |
| user1    | password |
| admin    | admin    |

### 5. Executar o servidor
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 6. Aceder à aplicação
- **Público:** http://127.0.0.1:8000
- **Login:** http://127.0.0.1:8000/login
- **Dashboard:** http://127.0.0.1:8000/dashboard

---

## 👤 Utilizador Padrão (Admin)

Na primeira execução, é criado automaticamente:

| Campo | Valor |
|-------|-------|
| **Email** | `admin@salas.pt` |
| **Password** | `admin123` |

⚠️ **Importante:** Altera a password após o primeiro login!

---

## 🔧 Configuração LDAP

Edita o ficheiro `ldap-test\.env`:

```env
LDAP_SERVER_URI=ldap://localhost:389
LDAP_USER_DN_TEMPLATE=cn={username},dc=test,dc=local
LDAP_USER_DOMAIN=test.local
LDAP_DEBUG=true
```

### Para usar um servidor LDAP real:

```env
LDAP_SERVER_URI=ldap://teu-servidor:389
LDAP_USER_DN_TEMPLATE=cn={username},ou=users,dc=empresa,dc=pt
LDAP_USER_DOMAIN=empresa.pt
```

---

## 📁 Estrutura do Projeto

```
projeto/
├── app/
│   ├── routers/
│   │   ├── auth.py        # Login, Registo, Logout
│   │   ├── dashboard.py   # Área do utilizador
│   │   ├── admin.py       # Área administrativa
│   │   ├── public.py      # Página pública
│   │   └── equipment.py   # Equipamentos (opcional)
│   ├── templates/
│   │   ├── base.html      # Template base
│   │   ├── login.html     # Login
│   │   ├── register.html  # Registo
│   │   ├── dashboard.html # Dashboard utilizador
│   │   ├── user.html      # Área do utilizador
│   │   ├── admin.html     # Admin dashboard
│   │   ├── admin_rooms.html
│   │   ├── admin_reservations.html
│   │   └── error.html     # Página de erro
│   ├── main.py            # Ponto de entrada
│   ├── models.py          # Modelos da BD
│   ├── database.py        # Configuração da BD
│   └── utils.py           # Funções utilitárias
├── backups/               # Backups automáticos
├── backup.py              # Script de backup
├── run_backup.bat         # Atalho backup
└── requirements.txt       # Dependências
```

---

## 🔄 Backup

### Criar backup manual
```bash
python backup.py
```

Ou usa o atalho:
```bash
run_backup.bat
```

Os backups são guardados em `backups/` e fazes upload para o Google Drive manualmente.

---

## 🎨 Visual

- **Tema escuro** moderno
- **Gradientes** e animações suaves
- **Responsivo** (funciona em telemóvel)
- **Modais** para formulários
- **Notificações** de erro

---

## 🐛 Bugs Conhecidos

Nenhum bug conhecido de momento. ✅

---

## 📝 Notas

- As passwords são guardadas com hash SHA256
- As sessões usam cookies HTTP-only
- Utilizadores só podem eliminar as suas próprias reservas
- Admin tem acesso total exceto à área `/user`
- Dias da semana: 0=Dom, 1=Seg, ..., 6=Sáb

---

## 🔧 Desenvolvimento

### Adicionar novas funcionalidades
1. Cria o router em `app/routers/`
2. Adiciona o template em `app/templates/`
3. Regista o router em `app/main.py`

### Alterar estilos
Edita `app/templates/base.html` na secção `<style>`.

---

## 📄 Licença

Projeto pessoal de gestão de salas.

---

**Criado em 2026** 🚀

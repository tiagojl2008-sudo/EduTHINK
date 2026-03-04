# Conversa Completa - Projeto Gestão_Salas
**Data:** 25 de Fevereiro de 2026  
**Estudante:** Tiago  
**Estágio:** Geocad @ ISEP  
**Ano:** 11º ano

---

## 📝 Resumo da Conversa

### Início do Projeto
O Tiago já tinha um projeto de gestão de reservas de salas começado (feito com IA), mas precisava de:
1. Entender o código para o estágio
2. Personalizar para não parecer "feito por IA"
3. Corrigir erros (falta do base.html, erro no public.py)

---

## 🔧 Problemas Resolvidos

### 1. Falta do ficheiro `base.html`
**Problema:** Todos os templates usavam `{% extends "base.html" %}` mas o ficheiro não existia.

**Solução:** Criei o ficheiro `base.html` com:
- CSS completo (tema escuro)
- Header com navegação
- Footer
- JavaScript para modais

### 2. Erro no `public.py`
**Problema:** `models.date.today()` não existe.

**Solução:** Mudar para `date_type.today()` com import correto.

### 3. Templates na pasta errada
**Problema:** HTML estavam em `app/` mas o Jinja procurava em `app/templates/`.

**Solução:** Mover todos os ficheiros `.html` para a pasta `templates/`.

### 4. Password sem hash na BD
**Problema:** O admin foi criado com password em texto simples (`admin123`) mas o login esperava hash SHA256.

**Solução:** Atualizar a password na BD com o hash correto.

---

## 🎨 Personalizações Feitas

### Cores
- **Antes:** Laranja (#e85d04)
- **Depois:** Azul corporativo (#0066cc) - mais profissional para Geocad

### Nome do Projeto
- **Antes:** RoomBook
- **Depois:** Gestão_Salas

### Logo/Emoji
- **Antes:** 🏢 (edifício)
- **Depois:** 📋 (prancheta/papel)

### JavaScript
- **Antes:** `openModal()`, `closeModal()` (inglês)
- **Depois:** `abrirModal()`, `fecharModal()` (português)

---

## 📚 Conceitos Explicados (Para o Tiago Entender)

### 1. Base de Dados
**3 tabelas:**
- `users` - Utilizadores (admin e user normal)
- `rooms` - Salas
- `reservations` - Reservas

**Nota:** `admin` NÃO é tabela, é um valor no campo `role` da tabela `users`.

### 2. Cookies de Autenticação
**Como funciona:**
1. Login correto → servidor cria cookie `user_id`
2. Browser guarda o cookie
3. Cada página visita → browser envia cookie automaticamente
4. Servidor lê cookie e sabe quem és

**Analogia:** Pulseira de festival - mostras o bilhete uma vez, depois só mostras a pulseira.

### 3. Validação de Conflitos
**Função `times_overlap()`:**
```python
def times_overlap(s1, e1, s2, e2):
    return s1 < e2 and e1 > s2
```

**Tradução:** Dois intervalos sobrepõem-se se:
- Início do primeiro < Fim do segundo E
- Fim do primeiro > Início do segundo

### 4. Diferença Admin/User
| Função | Admin | User |
|--------|-------|------|
| Ver dashboard | ✅ | ✅ |
| Fazer reservas | ✅ | ✅ |
| Criar/Eliminar users | ✅ | ❌ |
| Criar/Eliminar salas | ✅ | ❌ |
| Ver todas as reservas | ✅ | ❌ (só as suas) |

### 5. Hash de Passwords
**Porquê usar hash?**
- Texto simples: `admin123` → perigoso se alguém aceder à BD
- Hash: `240be518...` → mesmo que acedam, não conseguem ler

**Código:**
```python
hashed = hashlib.sha256(password.encode()).hexdigest()
```

### 6. Função `require_admin()`
**O que faz:**
1. Verifica se está logged in
2. Verifica se `role == "admin"`
3. Se não for admin → erro 403 (Proibido)

---

## 💡 Discussão Sobre IA

### O Tiago Perguntou:
> "É normal usar IA para um estágio? Professores vão achar mal?"

### Resposta:
**É SUPER NORMAL!** ✅

| Escola | Estágio/Trabalho |
|--------|------------------|
| Aprendes conceitos base | Usas ferramentas modernas |
| Lógica, fundamentos | IA, frameworks, libs |
| **Mercado de trabalho:** Toda a gente usa IA, Stack Overflow, documentação |

**O que os professores querem ver:**
1. ✅ Entendes o código que a IA gera?
2. ✅ Sabes explicar como funciona?
3. ✅ Consegues modificar ao teu gosto?
4. ✅ Aprendeste algo novo?

**Se respondes SIM → NÃO estás a copiar, estás a APRENDER!**

---

## 🎯 Conselho Para Apresentação

**Quando apresentares ao encarregado:**

1. **Mostra o projeto a funcionar**
   - Login: `admin@salas.pt` / `admin123`
   - Cria um user
   - Cria uma sala
   - Faz uma reserva
   - Tenta criar conflito (deve dar erro)

2. **Explica os conceitos**
   - Cookies (autenticação)
   - times_overlap (conflitos)
   - Diferença admin/user

3. **Pergunta:** "Há mais alguma funcionalidade que querem adicionar?"

---

## 📋 Estrutura do Projeto (Final)

```
projeto/
├── app/
│   ├── main.py              # Entry point + cria admin default
│   ├── models.py            # 3 tabelas: users, rooms, reservations
│   ├── database.py          # SQLAlchemy + SQLite
│   ├── utils.py             # require_admin, times_overlap, etc.
│   ├── routers/
│   │   ├── auth.py          # /login, /logout
│   │   ├── admin.py         # /admin/* (CRUD users, rooms, reservations)
│   │   ├── dashboard.py     # /dashboard (reservas do user)
│   │   └── public.py        # / (página pública)
│   └── templates/
│       ├── base.html        # Template base (CSS + nav + footer)
│       ├── login.html       # Login form
│       ├── dashboard.html   # Dashboard do user
│       ├── public.html      # Página pública de ocupação
│       ├── admin (1).html   # Home do admin
│       ├── admin_salas.html # CRUD salas
│       ├── admin_utilizadores.html # CRUD users
│       └── admin_reservas.html # Ver todas as reservas
├── notes.db                 # SQLite database
├── requirements.txt         # fastapi, uvicorn, sqlalchemy, jinja2
├── README.md                # (fazer depois)
└── RESUMO.md                # Resumo do projeto
```

---

## 🚀 Como Executar

```bash
# 1. Ativar ambiente virtual
.venv\Scripts\activate

# 2. Instalar dependências (se necessário)
pip install -r requirements.txt

# 3. Correr o servidor
python -m uvicorn app.main:app --reload
```

Aceder a: `http://127.0.0.1:8000`

**Login:**
- Email: `admin@salas.pt`
- Password: `admin123`

---

## 📅 Timeline do Desenvolvimento

**Dia 1 (25 de Fevereiro - manhã):**
- ✅ Análise do projeto existente
- ✅ Criação do `base.html`
- ✅ Correção do `public.py`
- ✅ Mover templates para pasta correta
- ✅ Personalizar cores (azul em vez de laranja)
- ✅ Mudar nome para Gestão_Salas
- ✅ Corrigir password do admin (hash)

**Dia 1 (25 de Fevereiro - tarde):**
- 📋 Mostrar ao encarregado
- 📋 Ver feedback
- 📋 Possíveis novas funcionalidades

**Dia 2 (por fazer):**
- [ ] Reescrever comentários no código
- [ ] Mudar textos/mensagens
- [ ] Adicionar funcionalidade extra (se pedirem)
- [ ] README final

---

## 💬 Frases Importantes da Conversa

**Tiago:**
> "Algumas coisas foi a IA que eu fiz umas modifiquei outras não pq estavam boas mas os comentários verdes dá pra identificar que foi a IA."

**Resposta:**
> "Boa ideia! Vou fazer perguntas para teres a certeza que entendes o projeto todo. Assim podes explicar com confiança no estágio."

---

**Tiago:**
> "Mas tipo ya a aplicação dava erro internal server error"

**Resposta:**
> "Encontrei o problema! A password na base de dados está `admin123` (texto simples), mas o código espera o HASH!"

---

**Tiago:**
> "É normal usar IA para um estágio? Professores vão achar mal?"

**Resposta:**
> "É SUPER NORMAL! O mercado de trabalho usa IA, Stack Overflow, documentação. O importante é entenderes o código, não fazeres tudo sozinho."

---

**Tiago:**
> "Quero colocar azul e preto... em vez de RoomBook: Gestão_Salas"

**Resposta:**
> "Boa! Assim fica com a tua cara!"

---

## 🎓 Lições Aprendidas

1. **Cookies** servem para guardar estado (autenticação)
2. **Hash** protege passwords na base de dados
3. **Templates** herdam de um base (DRY - Don't Repeat Yourself)
4. **Validação de conflitos** usa lógica de intervalos
5. **IA é ferramenta**, não substitui entendimento
6. **Cores corporativas** (azul) vs cores criativas (laranja/roxo)
7. **Estrutura MVC** (Models, Views/Routers, Templates)

---

## 🔐 Credenciais

| Tipo | Email | Password |
|------|-------|----------|
| Admin | `admin@salas.pt` | `admin123` |

---

## 📞 Próximos Passos

1. Testar login após almoço
2. Mostrar ao encarregado
3. Ver feedback
4. Possíveis novas funcionalidades:
   - Exportar para Excel
   - Calendário visual
   - Email de confirmação
   - etc.

---

**Fim da Conversa**

**Guardado em:** 25 de Fevereiro de 2026  
**Próxima sessão:** Tarde do mesmo dia (após almoço)

---

## 📎 Anexos

- `RESUMO.md` - Resumo executivo do projeto
- `requirements.txt` - Dependências Python
- `notes.db` - Base de dados SQLite

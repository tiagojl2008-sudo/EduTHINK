# 🧪 Guia de Testes Manuais - Sistema de Reservas

Este documento guia-te através de todos os testes manuais que deves realizar.

---

## 📋 Pré-requisitos

1. **Docker a correr:**
   ```bash
   cd ldap-test\local_ldap
   docker-compose up -d
   ```

2. **Servidor da aplicação a correr:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Browser aberto em:** http://127.0.0.1:8000

---

## 🔐 1. LOGIN LDAP COM CREDENCIAIS

### Teste 1.1: Login LDAP bem sucedido
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Ir para `/login` | Página de login abre |
| 2 | Username: `fry` | - |
| 3 | Password: `fry` | - |
| 4 | Clicar "Entrar" | Redireciona para `/dashboard` |
| 5 | Verificar nome no topo | "Olá, Philip 👋" |

✅ **Resultado:** Utilizador autenticado via LDAP

---

### Teste 1.2: Login LDAP com password errada
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Ir para `/login` | Página de login abre |
| 2 | Username: `fry` | - |
| 3 | Password: `wrongpassword` | - |
| 4 | Clicar "Entrar" | Erro: "Credenciais inválidas..." |
| 5 | Verificar erro visível | Mensagem de erro em vermelho |

✅ **Resultado:** Login falha com erro apropriado

---

### Teste 1.3: Login local (Admin)
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Ir para `/login` | Página de login abre |
| 2 | Email: `admin@salas.pt` | - |
| 3 | Password: `admin123` | - |
| 4 | Clicar "Entrar" | Redireciona para `/dashboard` |
| 5 | Verificar menu | Opção "Administração" visível |

✅ **Resultado:** Admin local autenticado

---

## 🏢 2. CRIAÇÃO DE RESERVA VÁLIDA

### Teste 2.1: Criar reserva dentro do horário útil
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Clicar "+ Nova Reserva" | Modal abre |
| 3 | Sala: "Sala A - Reuniões" | - |
| 4 | Título: "Reunião de Projeto" | - |
| 5 | Data: amanhã (dia útil) | - |
| 6 | Início: `09:00` | - |
| 7 | Fim: `11:00` | - |
| 8 | Clicar "Criar Reserva" | Reserva criada, modal fecha |
| 9 | Verificar "As minhas reservas" | Reserva listada |

✅ **Resultado:** Reserva criada com sucesso

---

## ⚠️ 3. VALIDADOR DE CONFLITOS DE HORÁRIOS

### Teste 3.1: Tentar reserva com conflito
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Criar reserva: 09:00-11:00 | Reserva criada |
| 3 | Clicar "+ Nova Reserva" | Modal abre |
| 4 | Mesma sala, mesma data | - |
| 5 | Início: `10:00` (sobreposição) | - |
| 6 | Fim: `12:00` | - |
| 7 | Clicar "Criar Reserva" | **ERRO:** "Conflito com reserva existente" |

✅ **Resultado:** Sistema deteta e bloqueia conflito

---

### Teste 3.2: Reserva noutra sala (sem conflito)
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Criar reserva na Sala A: 09:00-11:00 | Reserva criada |
| 3 | Criar reserva na Sala B: 09:00-11:00 | **SUCESSO** |
| 4 | Mesma data, horas iguais | Reserva criada |

✅ **Resultado:** Salas diferentes permitem mesmo horário

---

## 📅 4. VALIDADOR DE CONFLITOS SEMANAL

### Teste 4.1: Múltiplas reservas na mesma semana
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Criar reserva Segunda: 09:00-10:00 | ✅ |
| 3 | Criar reserva Terça: 09:00-10:00 | ✅ |
| 4 | Criar reserva Quarta: 09:00-10:00 | ✅ |
| 5 | Criar reserva Quinta: 09:00-10:00 | ✅ |
| 6 | Criar reserva Sexta: 09:00-10:00 | ✅ |
| 7 | Verificar "As minhas reservas" | 5 reservas listadas |

✅ **Resultado:** Múltiplas reservas na semana permitidas

---

## 🚫 5. VALIDADOR DE BLOQUEIOS POR DATA

### Teste 5.1: Tentar reserva no fim de semana
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Clicar "+ Nova Reserva" | Modal abre |
| 3 | Data: escolher Sábado/Domingo | - |
| 4 | Preencher resto do formulário | - |
| 5 | Clicar "Criar Reserva" | **ERRO:** "A sala está encerrada nesse dia" |

✅ **Resultado:** Fim de semana bloqueado

---

## ⏰ 6. VALIDAÇÃO DE REGRAS DE DURAÇÃO

### Teste 6.1: Reserva fora do horário útil
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Clicar "+ Nova Reserva" | Modal abre |
| 3 | Início: `07:00` (antes das 08:00) | - |
| 4 | Fim: `08:00` | - |
| 5 | Clicar "Criar Reserva" | **ERRO:** "Fora do horário útil" |

✅ **Resultado:** Horário fora do permitido é bloqueado

---

### Teste 6.2: Reserva após horário útil
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Clicar "+ Nova Reserva" | Modal abre |
| 3 | Início: `18:00` (depois das 18:00) | - |
| 4 | Fim: `20:00` | - |
| 5 | Clicar "Criar Reserva" | **ERRO:** "Fora do horário útil" |

✅ **Resultado:** Horário após fecho é bloqueado

---

### Teste 6.3: Hora fim antes da hora início
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Clicar "+ Nova Reserva" | Modal abre |
| 3 | Início: `14:00` | - |
| 4 | Fim: `13:00` (antes do início) | - |
| 5 | Clicar "Criar Reserva" | **ERRO:** "Hora de início deve ser anterior" |

✅ **Resultado:** Duração inválida é detetada

---

## 👥 7. VALIDAÇÃO DE PERMISSÕES (ADMIN VS USER)

### Teste 7.1: User normal acede a /admin
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` (user normal) | Dashboard abre |
| 2 | Navegar para `/admin` | **ERRO 403** ou redireciona |

✅ **Resultado:** User normal não acede admin

---

### Teste 7.2: Admin acede a /admin
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `admin@salas.pt` | Dashboard abre |
| 2 | Navegar para `/admin` | Página de administração abre |
| 3 | Verificar menu | "Salas", "Reservas", "Utilizadores" |

✅ **Resultado:** Admin acede área administrativa

---

## ❌ 8. CANCELAMENTO DE RESERVA

### Teste 8.1: Cancelamento por proprietário
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Ir para "As minhas reservas" | Lista de reservas |
| 3 | Escolher reserva criada por fry | - |
| 4 | Clicar "Eliminar" | Confirmação aparece |
| 5 | Confirmar eliminação | Reserva desaparece da lista |

✅ **Resultado:** Proprietário cancela própria reserva

---

### Teste 8.2: Cancelamento por não proprietário
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Criar reserva como fry | Reserva criada |
| 3 | Logout | - |
| 4 | Login como `leela` | Dashboard abre |
| 5 | Ir para "As minhas reservas" | **NÃO vê reserva do fry** |

✅ **Resultado:** User não vê reservas de outros

---

### Teste 8.3: Cancelamento por administrador
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como `fry` | Dashboard abre |
| 2 | Criar reserva | Reserva criada |
| 3 | Logout | - |
| 4 | Login como `admin@salas.pt` | Dashboard abre |
| 5 | Ir para `/admin/reservations` | Todas as reservas visíveis |
| 6 | Encontrar reserva do fry | - |
| 7 | Clicar "Eliminar" | Reserva eliminada |
| 8 | Logout e login como fry | Reserva já não existe |

✅ **Resultado:** Admin elimina reserva de qualquer user

---

## 🔄 9. RESERVA DENTRO DE BLOQUEIO

### Teste 9.1: Reserva em sala com horário restrito
| Passo | Ação | Resultado Esperado |
|-------|------|-------------------|
| 1 | Login como admin | Dashboard abre |
| 2 | Ir para `/admin/rooms` | Lista de salas |
| 3 | Editar sala: Horário 09:00-17:00 | - |
| 4 | Logout | - |
| 5 | Login como `fry` | Dashboard abre |
| 6 | Criar reserva: 08:00-09:00 | **ERRO:** "Fora do horário útil" |

✅ **Resultado:** Horário da sala é respeitado

---

## 📊 RESUMO DOS TESTES

| # | Categoria | Testes | ✅ Esperado |
|---|-----------|--------|-------------|
| 1 | Login LDAP | 3 | Autenticação funciona |
| 2 | Criação Reserva | 1 | Cria com sucesso |
| 3 | Conflitos Horário | 2 | Deteta conflitos |
| 4 | Conflitos Semanal | 1 | Múltiplas na semana OK |
| 5 | Bloqueios Data | 1 | Fim de semana bloqueado |
| 6 | Regras Duração | 3 | Horário útil respeitado |
| 7 | Permissões | 2 | Admin/User separados |
| 8 | Cancelamento | 3 | Permissões funcionam |
| 9 | Bloqueio Sala | 1 | Horário da sala respeitado |
| | **TOTAL** | **17** | **Todos devem passar** |

---

## 🐛 Como Reportar Bugs

Se algum teste falhar:

1. **Tira screenshot** do erro
2. **Anota os passos** exatos que levaram ao erro
3. **Verifica o console** do servidor (logs)
4. **Verifica o console** do browser (F12)

---

## 📝 Folha de Testes

Imprime esta tabela e marca ✅ ou ❌:

```
Teste 1.1: Login LDAP (fry)           [ ]
Teste 1.2: Login password errada      [ ]
Teste 1.3: Login Admin local          [ ]
Teste 2.1: Criar reserva válida       [ ]
Teste 3.1: Conflito de horário        [ ]
Teste 3.2: Sem conflito (outra sala)  [ ]
Teste 4.1: Múltiplas na semana        [ ]
Teste 5.1: Fim de semana bloqueado    [ ]
Teste 6.1: Fora do horário (antes)    [ ]
Teste 6.2: Fora do horário (depois)   [ ]
Teste 6.3: Fim antes do início        [ ]
Teste 7.1: User não acede admin       [ ]
Teste 7.2: Admin acede admin          [ ]
Teste 8.1: Owner cancela reserva      [ ]
Teste 8.2: Não owner não cancela      [ ]
Teste 8.3: Admin cancela qualquer     [ ]
Teste 9.1: Horário da sala respeitado [ ]
```

---

**Boa sorte com os testes! 🎯**

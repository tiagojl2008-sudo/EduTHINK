# Guia de Testes Manuais - EduTHINK

## Como usar este guia

Este documento contém os passos para testar manualmente todas as funcionalidades da aplicação EduTHINK.
Para cada teste:
1. Seguir os passos indicados
2. Inserir os valores exatos indicados na coluna "Dados a inserir"
3. Tirar **print screen** do resultado
4. Verificar se o resultado corresponde ao esperado

> **Antes de começar:** Iniciar a aplicação com `python -m uvicorn app.main:uvicorn_app --reload` e aceder a `http://localhost:8000`

---

## 1. Autenticação (Login)

### Pré-condição
Aceder à página de login: `http://localhost:8000/login`

### T1.1 - Login válido com email

| Campo | Dados a inserir |
|-------|-----------------|
| Username / Email | `admin@salas.pt` |
| Palavra-passe | `admin123` |

**Ação:** Clicar em "Entrar"
**Resultado esperado:** Redirecionamento para o Dashboard. Aparece a página principal com as salas disponíveis.
**Print screen:** Página do Dashboard após login bem-sucedido.

---

### T1.2 - Login válido com nome de utilizador

| Campo | Dados a inserir |
|-------|-----------------|
| Username / Email | `Admin` |
| Palavra-passe | `admin123` |

**Ação:** Clicar em "Entrar"
**Resultado esperado:** Redirecionamento para o Dashboard (mesmo resultado que T1.1).
**Print screen:** Página do Dashboard.

---

### T1.3 - Login com password errada

| Campo | Dados a inserir |
|-------|-----------------|
| Username / Email | `admin@salas.pt` |
| Palavra-passe | `password_errada` |

**Ação:** Clicar em "Entrar"
**Resultado esperado:** Mensagem de erro: "Credenciais inválidas ou servidor LDAP indisponível."
**Print screen:** Página de login com a mensagem de erro visível.

---

### T1.4 - Login com utilizador inexistente

| Campo | Dados a inserir |
|-------|-----------------|
| Username / Email | `utilizador_falso@email.pt` |
| Palavra-passe | `qualquer123` |

**Ação:** Clicar em "Entrar"
**Resultado esperado:** Mensagem de erro: "Credenciais inválidas ou servidor LDAP indisponível."
**Print screen:** Página de login com a mensagem de erro.

---

### T1.5 - Login com campos vazios

| Campo | Dados a inserir |
|-------|-----------------|
| Username / Email | *(deixar vazio)* |
| Palavra-passe | *(deixar vazio)* |

**Ação:** Clicar em "Entrar"
**Resultado esperado:** O browser impede o envio do formulário (validação HTML `required`). Aparece aviso "Preencha este campo".
**Print screen:** Mensagem de validação do browser no campo Username.

---

## 2. Gestão de Salas (Admin)

### Pré-condição
Fazer login como administrador (T1.1) e aceder a: **Painel Admin > Salas** (`/admin/rooms`)

### T2.1 - Criar sala válida

Clicar no botão **"+ Nova Sala"** e preencher:

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Sala de Reuniões B2` |
| Capacidade | `15` |
| Cor | *(selecionar vermelho: #ff0000)* |
| Localização | `Edifício B, Piso 2` |
| Início Horário | `09:00` |
| Fim Horário | `18:00` |
| Dias Úteis | *(marcar Seg, Ter, Qua, Qui, Sex)* |

**Ação:** Clicar em "Criar"
**Resultado esperado:** A sala "Sala de Reuniões B2" aparece na lista de salas com um ponto vermelho, capacidade 15, localização "Edifício B, Piso 2" e horário 09:00–18:00.
**Print screen:** Lista de salas com a nova sala visível.

---

### T2.2 - Criar sala com cor inválida (via inspetor do browser)

> **Nota:** Como o campo cor é `type="color"`, o browser não permite escrever texto diretamente. Para testar a validação do servidor, usar o Inspetor do browser (F12) para alterar o valor do campo color para `nao-e-cor` antes de submeter.

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Sala Teste Cor` |
| Capacidade | `10` |
| Localização | `Piso 1` |
| Cor | `nao-e-cor` *(via inspetor F12)* |
| Início Horário | `08:00` |
| Fim Horário | `18:00` |
| Dias Úteis | *(marcar Seg a Sex)* |

**Ação:** Alterar o valor do input color via F12 e submeter o formulário
**Resultado esperado:** Mensagem de erro: "Cor inválida. Use o formato hexadecimal (ex: #e85d04)."
**Print screen:** Página de salas com a mensagem de erro.

---

### T2.3 - Criar sala com hora de início depois da hora de fim

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Sala Teste Horário` |
| Capacidade | `10` |
| Localização | `Piso 1` |
| Cor | *(qualquer cor)* |
| Início Horário | `18:00` |
| Fim Horário | `08:00` |
| Dias Úteis | *(marcar Seg a Sex)* |

**Ação:** Clicar em "Criar"
**Resultado esperado:** Mensagem de erro: "Hora de início deve ser anterior à hora de fim."
**Print screen:** Página de salas com a mensagem de erro.

---

### T2.4 - Criar sala sem dias úteis selecionados

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Sala Teste Dias` |
| Capacidade | `10` |
| Localização | `Piso 1` |
| Cor | *(qualquer cor)* |
| Início Horário | `08:00` |
| Fim Horário | `18:00` |
| Dias Úteis | *(não marcar nenhum dia)* |

**Ação:** Clicar em "Criar"
**Resultado esperado:** Mensagem de erro: "Selecione pelo menos um dia útil."
**Print screen:** Página de salas com a mensagem de erro.

---

### T2.5 - Criar sala só para fins de semana

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Sala Fim de Semana` |
| Capacidade | `20` |
| Localização | `Pavilhão Desportivo` |
| Cor | *(selecionar azul)* |
| Início Horário | `10:00` |
| Fim Horário | `16:00` |
| Dias Úteis | *(marcar apenas Dom e Sáb)* |

**Ação:** Clicar em "Criar"
**Resultado esperado:** Sala criada com sucesso. Na lista aparece com os dias Dom e Sáb destacados.
**Print screen:** Detalhe da sala mostrando apenas Dom e Sáb ativos.

---

### T2.6 - Editar sala existente

**Ação:** Na lista de salas, clicar em "Editar" na sala criada em T2.1 e alterar:

| Campo | Dados a alterar |
|-------|-----------------|
| Nome | `Sala de Reuniões B2 - Premium` |
| Capacidade | `20` |

**Ação:** Clicar em "Guardar"
**Resultado esperado:** O nome e a capacidade da sala são atualizados na lista.
**Print screen:** Lista de salas com os dados atualizados.

---

### T2.7 - Eliminar sala

**Ação:** Na lista de salas, clicar no botão "✕" (vermelho) da sala "Sala Teste Dias" (ou outra sala de teste). Confirmar a eliminação no diálogo.
**Resultado esperado:** A sala desaparece da lista.
**Print screen:** Lista de salas sem a sala eliminada.

---

## 3. Criação de Reservas

### Pré-condição
Fazer login como administrador (T1.1). Ter pelo menos uma sala criada (T2.1). Estar no Dashboard (`/dashboard`).

### T3.1 - Reserva válida

Clicar num slot livre de uma sala para abrir o formulário de reserva, ou usar o botão de nova reserva:

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | `Sala de Reuniões B2` *(ou a sala existente)* |
| Título | `Reunião de Projeto EduTHINK` |
| Data | *(selecionar a próxima segunda-feira)* |
| Hora de Início | `10:00` |
| Hora de Fim | `11:30` |

**Ação:** Submeter o formulário
**Resultado esperado:** Redirecionamento para o Dashboard. A reserva aparece na barra de ocupação da sala e na lista "As minhas reservas de hoje" (se a data for hoje).
**Print screen:** Dashboard com a reserva visível na barra de ocupação da sala.

---

### T3.2 - Reserva com título vazio

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(qualquer sala)* |
| Título | *(deixar vazio)* |
| Data | *(próxima segunda-feira)* |
| Hora de Início | `09:00` |
| Hora de Fim | `10:00` |

**Ação:** Submeter o formulário
**Resultado esperado:** O browser impede o envio (campo required) ou mensagem de erro "Título é obrigatório".
**Print screen:** Mensagem de validação visível.

---

### T3.3 - Reserva com título muito longo (mais de 100 caracteres)

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(qualquer sala)* |
| Título | `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` *(101 letras A)* |
| Data | *(próxima segunda-feira)* |
| Hora de Início | `09:00` |
| Hora de Fim | `10:00` |

**Ação:** Submeter o formulário
**Resultado esperado:** Mensagem de erro: "Título muito longo (máx. 100 caracteres)."
**Print screen:** Dashboard com a mensagem de erro.

---

### T3.4 - Reserva com hora de início depois da hora de fim

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(qualquer sala)* |
| Título | `Teste Horário Invertido` |
| Data | *(próxima segunda-feira)* |
| Hora de Início | `14:00` |
| Hora de Fim | `10:00` |

**Ação:** Submeter o formulário
**Resultado esperado:** Mensagem de erro: "Hora de início deve ser anterior à hora de fim."
**Print screen:** Dashboard com a mensagem de erro.

---

### T3.5 - Reserva fora do horário da sala (antes de abrir)

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(sala com horário 09:00-18:00)* |
| Título | `Teste Fora de Horário` |
| Data | *(próxima segunda-feira)* |
| Hora de Início | `07:00` |
| Hora de Fim | `08:00` |

**Ação:** Submeter o formulário
**Resultado esperado:** Mensagem de erro: "Fora do horário útil (09:00 – 18:00)."
**Print screen:** Dashboard com a mensagem de erro.

---

### T3.6 - Reserva fora do horário da sala (depois de fechar)

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(sala com horário 09:00-18:00)* |
| Título | `Teste Depois de Fechar` |
| Data | *(próxima segunda-feira)* |
| Hora de Início | `18:30` |
| Hora de Fim | `19:30` |

**Ação:** Submeter o formulário
**Resultado esperado:** Mensagem de erro: "Fora do horário útil (09:00 – 18:00)."
**Print screen:** Dashboard com a mensagem de erro.

---

### T3.7 - Reserva nos limites exatos do horário da sala

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(sala com horário 09:00-18:00)* |
| Título | `Reserva Dia Inteiro` |
| Data | *(próxima terça-feira)* |
| Hora de Início | `09:00` |
| Hora de Fim | `18:00` |

**Ação:** Submeter o formulário
**Resultado esperado:** Reserva criada com sucesso. A barra de ocupação da sala mostra o dia inteiro ocupado.
**Print screen:** Dashboard com a barra de ocupação totalmente preenchida.

---

### T3.8 - Reserva com conflito de horário

**Pré-condição:** Ter a reserva T3.1 criada (10:00-11:30).

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(mesma sala da T3.1)* |
| Título | `Reunião Conflituosa` |
| Data | *(mesma data da T3.1)* |
| Hora de Início | `10:30` |
| Hora de Fim | `12:00` |

**Ação:** Submeter o formulário
**Resultado esperado:** Mensagem de erro: "Conflito com reserva existente: Reunião de Projeto EduTHINK (10:00–11:30)"
**Print screen:** Dashboard com a mensagem de erro de conflito.

---

### T3.9 - Reservas adjacentes (sem conflito)

**Pré-condição:** Ter a reserva T3.1 criada (10:00-11:30).

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(mesma sala da T3.1)* |
| Título | `Reunião Seguinte` |
| Data | *(mesma data da T3.1)* |
| Hora de Início | `11:30` |
| Hora de Fim | `12:30` |

**Ação:** Submeter o formulário
**Resultado esperado:** Reserva criada com sucesso. Duas reservas aparecem lado a lado na barra de ocupação.
**Print screen:** Dashboard com as duas reservas adjacentes visíveis.

---

### T3.10 - Reserva com data passada

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(qualquer sala)* |
| Título | `Teste Data Passada` |
| Data | `2020-01-15` *(inserir via inspetor F12 se o browser bloquear)* |
| Hora de Início | `09:00` |
| Hora de Fim | `10:00` |

**Ação:** Submeter o formulário
**Resultado esperado:** Mensagem de erro: "Não é possível reservar datas passadas."
**Print screen:** Dashboard com a mensagem de erro.

---

### T3.11 - Reserva num dia em que a sala está encerrada

**Pré-condição:** A sala só funciona de segunda a sexta (dias úteis 1-5).

| Campo | Dados a inserir |
|-------|-----------------|
| Sala | *(sala com dias úteis Seg-Sex)* |
| Título | `Teste Fim de Semana` |
| Data | *(selecionar o próximo sábado)* |
| Hora de Início | `10:00` |
| Hora de Fim | `11:00` |

**Ação:** Submeter o formulário
**Resultado esperado:** Mensagem de erro: "A sala está encerrada nesse dia da semana."
**Print screen:** Dashboard com a mensagem de erro.

---

### T3.12 - Eliminar reserva própria

**Pré-condição:** Ter uma reserva criada (ex: T3.9).

**Ação:** Na página "A Minha Conta" (`/user`) ou no Dashboard, clicar no botão de eliminar (✕) da reserva "Reunião Seguinte". Confirmar a eliminação.
**Resultado esperado:** A reserva desaparece da lista.
**Print screen:** Lista de reservas sem a reserva eliminada.

---

## 4. Gestão de Utilizadores (Admin)

### Pré-condição
Fazer login como administrador e aceder a: **Painel Admin > Utilizadores** (`/admin/users`)

### T4.1 - Criar utilizador válido

Clicar em **"+ Novo Utilizador"** e preencher:

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Maria Silva` |
| Email | `maria.silva@empresa.pt` |
| Função | `Utilizador` |

**Ação:** Clicar em "Criar"
**Resultado esperado:** O utilizador "Maria Silva" aparece na tabela de utilizadores com a função "user".
**Print screen:** Tabela de utilizadores com o novo utilizador.

---

### T4.2 - Criar utilizador com email duplicado

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Maria Duplicada` |
| Email | `maria.silva@empresa.pt` *(mesmo email da T4.1)* |
| Função | `Utilizador` |

**Ação:** Clicar em "Criar"
**Resultado esperado:** Mensagem de erro: "Este email já está registado."
**Print screen:** Página de utilizadores com a mensagem de erro.

---

### T4.3 - Criar utilizador com função admin

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `João Administrador` |
| Email | `joao.admin@empresa.pt` |
| Função | `Administrador` |

**Ação:** Clicar em "Criar"
**Resultado esperado:** O utilizador "João Administrador" aparece na tabela com a tag "admin".
**Print screen:** Tabela de utilizadores com o novo admin.

---

### T4.4 - Editar utilizador (alterar email para duplicado)

**Ação:** Clicar em "Editar" no utilizador "Maria Silva" e alterar:

| Campo | Dados a alterar |
|-------|-----------------|
| Email | `admin@salas.pt` *(email do administrador principal)* |

**Ação:** Clicar em "Guardar"
**Resultado esperado:** Mensagem de erro: "Este email já está em uso."
**Print screen:** Página de utilizadores com a mensagem de erro.

---

### T4.5 - Eliminar utilizador

**Ação:** Na tabela de utilizadores, clicar no botão "✕" do utilizador "João Administrador". Confirmar.
**Resultado esperado:** O utilizador desaparece da tabela.
**Print screen:** Tabela de utilizadores sem o utilizador eliminado.

---

## 5. Perfil do Utilizador

### Pré-condição
Fazer login e aceder a: **A Minha Conta** (`/user`). Clicar em "Editar Perfil".

### T5.1 - Atualizar nome

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Administrador Principal` |
| Email | *(manter o mesmo)* |
| Palavra-passe | *(deixar vazio)* |

**Ação:** Clicar em "Guardar"
**Resultado esperado:** Mensagem de sucesso: "Perfil atualizado com sucesso!" O nome no topo da página muda para "Olá, Administrador Principal".
**Print screen:** Página de perfil com a mensagem de sucesso e o nome atualizado.

---

### T5.2 - Alterar email para um já existente

**Pré-condição:** Ter pelo menos outro utilizador criado (ex: T4.1).

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | *(manter)* |
| Email | `maria.silva@empresa.pt` *(email de outro utilizador)* |
| Palavra-passe | *(deixar vazio)* |

**Ação:** Clicar em "Guardar"
**Resultado esperado:** Mensagem de erro: "Este email já está em uso."
**Print screen:** Página de perfil com a mensagem de erro.

---

### T5.3 - Upload de avatar com formato válido (PNG)

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | *(manter)* |
| Email | *(manter)* |
| Foto de Perfil | *(selecionar um ficheiro .png com menos de 2MB)* |

**Ação:** Clicar em "Guardar"
**Resultado esperado:** Mensagem de sucesso. A foto de perfil é atualizada.
**Print screen:** Página de perfil com a nova foto visível.

---

### T5.4 - Upload de avatar com formato inválido

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | *(manter)* |
| Email | *(manter)* |
| Foto de Perfil | *(selecionar um ficheiro .pdf ou .exe)* |

**Ação:** Clicar em "Guardar"
**Resultado esperado:** Mensagem de erro: "Formato não permitido. Usa JPG, PNG ou GIF."
**Print screen:** Página de perfil com a mensagem de erro.

---

### T5.5 - Upload de avatar demasiado grande (> 2MB)

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | *(manter)* |
| Email | *(manter)* |
| Foto de Perfil | *(selecionar uma imagem com mais de 2MB)* |

**Ação:** Clicar em "Guardar"
**Resultado esperado:** Mensagem de erro: "Ficheiro muito grande. Máximo 2MB."
**Print screen:** Página de perfil com a mensagem de erro.

---

## 6. Equipamento / Inventário (Admin)

### Pré-condição
Fazer login como administrador e aceder a: **Painel Admin > Inventário** (`/admin/inventory`)

### T6.1 - Criar equipamento válido

Clicar em **"+ Novo Equipamento"** e preencher:

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Projetor Epson EB-X51` |
| Descrição | `Projetor Full HD, 3800 lumens, com HDMI` |
| Sala | *(selecionar "Sala de Reuniões B2")* |

**Ação:** Clicar em "Criar"
**Resultado esperado:** O equipamento "Projetor Epson EB-X51" aparece na lista de inventário associado à sala escolhida.
**Print screen:** Lista de inventário com o novo equipamento.

---

### T6.2 - Criar equipamento sem descrição

| Campo | Dados a inserir |
|-------|-----------------|
| Nome | `Quadro Branco 120x90` |
| Descrição | *(deixar vazio)* |
| Sala | *(selecionar qualquer sala)* |

**Ação:** Clicar em "Criar"
**Resultado esperado:** Equipamento criado com sucesso (descrição é opcional).
**Print screen:** Lista de inventário com o equipamento sem descrição.

---

### T6.3 - Atribuir equipamento a utilizador

**Pré-condição:** Ter equipamento (T6.1) e utilizador (T4.1) criados.

**Ação:** No equipamento "Projetor Epson EB-X51", clicar em "Atribuir a utilizador":

| Campo | Dados a inserir |
|-------|-----------------|
| Utilizador | `Maria Silva` |
| Notas | `Empréstimo para apresentação do dia 25` |

**Ação:** Submeter
**Resultado esperado:** A atribuição aparece na vista "Equipamento por Utilizador".
**Print screen:** Página de equipamento por utilizador mostrando a atribuição.

---

### T6.4 - Atribuição duplicada (mesmo equipamento ao mesmo utilizador)

**Pré-condição:** Ter a atribuição T6.3 feita.

**Ação:** Tentar atribuir novamente o "Projetor Epson EB-X51" a "Maria Silva".
**Resultado esperado:** Mensagem de erro indicando que o equipamento já está atribuído a este utilizador.
**Print screen:** Mensagem de erro visível.

---

## 7. Permissões e Controlo de Acesso

### T7.1 - Utilizador normal não acede ao painel admin

**Pré-condição:** Fazer logout. Criar um utilizador normal com password (via admin) ou usar LDAP.

**Ação:** Fazer login como utilizador normal e tentar aceder diretamente a `http://localhost:8000/admin`
**Resultado esperado:** Erro 403 (Forbidden) - acesso negado.
**Print screen:** Página de erro 403.

---

### T7.2 - Utilizador normal não elimina reserva de outro

**Pré-condição:** Fazer login como utilizador normal. Existir uma reserva feita por outro utilizador.

**Ação:** Tentar aceder diretamente via URL: `http://localhost:8000/reservations/delete/{id_da_reserva_de_outro}` (submeter via POST ou via inspetor F12)
**Resultado esperado:** Erro 403 - "Não tens permissão".
**Print screen:** Página de erro 403.

---

### T7.3 - Admin pode eliminar qualquer reserva

**Pré-condição:** Fazer login como admin. Ir a **Admin > Reservas** (`/admin/reservations`).

**Ação:** Eliminar uma reserva de outro utilizador.
**Resultado esperado:** A reserva é eliminada com sucesso.
**Print screen:** Lista de reservas admin após eliminação.

---

### T7.4 - Acesso ao Dashboard sem login

**Ação:** Sem fazer login (ou após logout), aceder diretamente a: `http://localhost:8000/dashboard`
**Resultado esperado:** Erro 401 (Unauthorized) - não autenticado.
**Print screen:** Página de erro 401.

---

## 8. Página Pública

### T8.1 - Visualizar disponibilidade das salas

**Ação:** Aceder a `http://localhost:8000/public` (sem necessidade de login).
**Resultado esperado:** Página mostra todas as salas com as reservas de hoje visíveis nas barras de ocupação. Slots livres aparecem a verde e slots ocupados a vermelho/laranja.
**Print screen:** Página pública com a visualização de disponibilidade.

---

## Resumo dos Testes

| ID | Teste | Tipo | Resultado |
|----|-------|------|-----------|
| T1.1 | Login válido (email) | Válido | |
| T1.2 | Login válido (nome) | Válido | |
| T1.3 | Login password errada | Inválido | |
| T1.4 | Login utilizador inexistente | Inválido | |
| T1.5 | Login campos vazios | Inválido | |
| T2.1 | Criar sala válida | Válido | |
| T2.2 | Sala com cor inválida | Inválido | |
| T2.3 | Sala hora início > fim | Inválido | |
| T2.4 | Sala sem dias úteis | Inválido | |
| T2.5 | Sala só fim de semana | Válido | |
| T2.6 | Editar sala | Válido | |
| T2.7 | Eliminar sala | Válido | |
| T3.1 | Reserva válida | Válido | |
| T3.2 | Reserva título vazio | Inválido | |
| T3.3 | Reserva título > 100 chars | Inválido | |
| T3.4 | Reserva hora início > fim | Inválido | |
| T3.5 | Reserva fora horário (antes) | Inválido | |
| T3.6 | Reserva fora horário (depois) | Inválido | |
| T3.7 | Reserva limites exatos | Válido | |
| T3.8 | Reserva conflito horário | Inválido | |
| T3.9 | Reservas adjacentes | Válido | |
| T3.10 | Reserva data passada | Inválido | |
| T3.11 | Reserva dia encerrado | Inválido | |
| T3.12 | Eliminar reserva própria | Válido | |
| T4.1 | Criar utilizador válido | Válido | |
| T4.2 | Criar utilizador email duplicado | Inválido | |
| T4.3 | Criar utilizador admin | Válido | |
| T4.4 | Editar email para duplicado | Inválido | |
| T4.5 | Eliminar utilizador | Válido | |
| T5.1 | Atualizar nome perfil | Válido | |
| T5.2 | Email duplicado no perfil | Inválido | |
| T5.3 | Avatar PNG válido | Válido | |
| T5.4 | Avatar formato inválido | Inválido | |
| T5.5 | Avatar > 2MB | Inválido | |
| T6.1 | Criar equipamento válido | Válido | |
| T6.2 | Equipamento sem descrição | Válido | |
| T6.3 | Atribuir equipamento | Válido | |
| T6.4 | Atribuição duplicada | Inválido | |
| T7.1 | User normal acede admin | Permissão | |
| T7.2 | User elimina reserva alheia | Permissão | |
| T7.3 | Admin elimina qualquer reserva | Permissão | |
| T7.4 | Dashboard sem login | Permissão | |
| T8.1 | Página pública | Válido | |

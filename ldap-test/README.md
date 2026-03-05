# Servidor LDAP de Teste

## Utilizadores de Teste (Já incluídos na imagem)

A imagem `rroemhild/test-openldap` já vem com utilizadores pré-configurados:

| Username | Password | Nome |
|----------|----------|------|
| fry | fry | Philip J. Fry |
| leela | leela | Turanga Leela |
| zoidberg | zoidberg | John A. Zoidberg |
| bender | bender | Bender Bending Rodríguez |
| amy | amy | Amy Wong |
| hermes | hermes | Hermes Conrad |
| professor | professor | Hubert J. Farnsworth |

## Iniciar o Servidor

### Opção 1: Docker Compose (recomendado)

```bash
cd ldap-test/local_ldap
docker-compose up -d
```

### Opção 2: Docker run

```bash
docker run -d -p 1389:10389 --name ldap-test-local rroemhild/test-openldap
```

## Parar o Servidor

```bash
cd ldap-test/local_ldap
docker-compose down
# ou
docker stop ldap-test-local
```

## Configuração da Aplicação

O ficheiro `ldap-test/.env` já está configurado:

```env
LDAP_SERVER_URI=ldap://127.0.0.1:1389
LDAP_BASE_DN=ou=people,dc=planetexpress,dc=com
LDAP_USER_DN_TEMPLATE=
LDAP_USER_DOMAIN=
LDAP_DEBUG=true
```

## Testar Ligação

```bash
# Python
python -c "from app.routers.auth import authenticator; print(authenticator.authenticate('fry', 'fry'))"
```

## Utilizadores na Aplicação

1. **Inicia o servidor LDAP:**
   ```bash
   cd ldap-test/local_ldap
   docker-compose up -d
   ```

2. **Inicia a aplicação:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Faz login:**
   - Vai a: http://127.0.0.1:8000/login
   - Username: `fry`
   - Password: `fry`

4. **O utilizador é criado automaticamente** na BD local após o primeiro login.

## Notas

- A autenticação LDAP é tentada **depois** da autenticação local
- Admin local (`admin@salas.pt`) usa password da BD
- Utilizadores LDAP não têm password na BD (autenticam no servidor LDAP)

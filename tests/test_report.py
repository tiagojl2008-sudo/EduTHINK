"""
Testes para Relatório do Projeto EduTHINK
==========================================
Sistema de Gestão de Reservas de Salas

Execução: pytest tests/test_report.py -v -s

Cada teste imprime uma tabela formatada com:
- Nome do teste
- Valores de entrada
- Resultado esperado
- Resultado obtido
- PASSA / FALHA
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app import models
from app.database import get_db
from app.utils import hash_password, verify_password, times_overlap, time_in_range


# ===================================================================
# CONFIGURAÇÃO DA BASE DE DADOS DE TESTE
# ===================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_report.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()




# ===================================================================
# FUNÇÃO AUXILIAR DE IMPRESSÃO
# ===================================================================

def imprimir_resultado(nome, entrada, esperado, obtido, passou):
    """Imprime o resultado de um teste formatado para o relatório."""
    estado = "PASSA" if passou else "FALHA"
    print()
    print("+==================================================")
    print(f"| TESTE: {nome}")
    print(f"| Entrada:   {entrada}")
    print(f"| Esperado:  {esperado}")
    print(f"| Obtido:    {obtido}")
    print(f"| Resultado: {estado}")
    print("+==================================================")


# ===================================================================
# CSRF TEST CLIENT
# ===================================================================

class CSRFTestClient:
    """Wrapper do TestClient que inclui automaticamente o token CSRF nos POST."""
    def __init__(self, client):
        self._client = client
        self._csrf_token = None

    def _ensure_csrf_token(self):
        if not self._csrf_token:
            resp = self._client.get("/login")
            self._csrf_token = resp.cookies.get("csrftoken", "")
        return self._csrf_token

    def get(self, *args, **kwargs):
        resp = self._client.get(*args, **kwargs)
        if "csrftoken" in resp.cookies:
            self._csrf_token = resp.cookies["csrftoken"]
        return resp

    def post(self, *args, **kwargs):
        token = self._ensure_csrf_token()
        headers = kwargs.pop("headers", {})
        headers["x-csrftoken"] = token
        kwargs["headers"] = headers
        resp = self._client.post(*args, **kwargs)
        if "csrftoken" in resp.cookies:
            self._csrf_token = resp.cookies["csrftoken"]
        return resp

    @property
    def cookies(self):
        return self._client.cookies


# ===================================================================
# FIXTURES
# ===================================================================

@pytest.fixture(scope="function")
def db():
    app.dependency_overrides[get_db] = override_get_db
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client(db):
    with TestClient(app) as c:
        yield CSRFTestClient(c)


@pytest.fixture
def admin_user(db):
    hashed = hash_password("admin123")
    user = models.User(name="Admin", email="admin@salas.pt", password=hashed, role="admin")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def normal_user(db):
    hashed = hash_password("user123")
    user = models.User(name="User", email="user@test.pt", password=hashed, role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def manager_user(db):
    hashed = hash_password("manager123")
    user = models.User(name="Manager", email="manager@salas.pt", password=hashed, role="manager")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def room(db):
    room = models.Room(
        name="Sala A", capacity=10, location="Piso 1",
        color="#0066cc", start_time="08:00", end_time="18:00",
        work_days="1,2,3,4,5"
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def _login(client, email, password):
    """Faz login via POST e retorna a resposta."""
    return client.post("/login", data={"username": email, "password": password}, follow_redirects=False)


def _login_as_user(client, user):
    """Define o cookie de sessão diretamente (evita rate limiting do /login)."""
    client._client.cookies.set("user_id", str(user.id))


# ===================================================================
# 1. FUNÇÕES UTILITÁRIAS (times_overlap, time_in_range)
# ===================================================================

class TestRelatorioUtilitarios:
    """Testes unitários das funções de validação de horários."""

    def test_sobreposicao_total(self):
        entrada = '("09:00","12:00","09:00","12:00")'
        resultado = times_overlap("09:00", "12:00", "09:00", "12:00")
        imprimir_resultado("Sobreposição total", entrada, "True", str(resultado), resultado is True)
        assert resultado is True

    def test_sobreposicao_parcial_inicio(self):
        entrada = '("09:00","11:00","10:00","12:00")'
        resultado = times_overlap("09:00", "11:00", "10:00", "12:00")
        imprimir_resultado("Sobreposição parcial (início)", entrada, "True", str(resultado), resultado is True)
        assert resultado is True

    def test_sobreposicao_parcial_fim(self):
        entrada = '("10:00","12:00","09:00","11:00")'
        resultado = times_overlap("10:00", "12:00", "09:00", "11:00")
        imprimir_resultado("Sobreposição parcial (fim)", entrada, "True", str(resultado), resultado is True)
        assert resultado is True

    def test_intervalo_contido(self):
        entrada = '("09:00","12:00","10:00","11:00")'
        resultado = times_overlap("09:00", "12:00", "10:00", "11:00")
        imprimir_resultado("Intervalo contido noutro", entrada, "True", str(resultado), resultado is True)
        assert resultado is True

    def test_intervalo_contem(self):
        entrada = '("10:00","11:00","09:00","12:00")'
        resultado = times_overlap("10:00", "11:00", "09:00", "12:00")
        imprimir_resultado("Intervalo contém outro", entrada, "True", str(resultado), resultado is True)
        assert resultado is True

    def test_sem_sobreposicao_antes(self):
        entrada = '("09:00","10:00","11:00","12:00")'
        resultado = times_overlap("09:00", "10:00", "11:00", "12:00")
        imprimir_resultado("Sem sobreposição (antes)", entrada, "False", str(resultado), resultado is False)
        assert resultado is False

    def test_sem_sobreposicao_depois(self):
        entrada = '("13:00","14:00","09:00","10:00")'
        resultado = times_overlap("13:00", "14:00", "09:00", "10:00")
        imprimir_resultado("Sem sobreposição (depois)", entrada, "False", str(resultado), resultado is False)
        assert resultado is False

    def test_sem_sobreposicao_adjacente(self):
        entrada = '("09:00","10:00","10:00","11:00")'
        resultado = times_overlap("09:00", "10:00", "10:00", "11:00")
        imprimir_resultado("Adjacente (fim=início)", entrada, "False", str(resultado), resultado is False)
        assert resultado is False

    def test_dentro_horario(self):
        entrada = '("09:00","17:00","08:00","18:00")'
        resultado = time_in_range("09:00", "17:00", "08:00", "18:00")
        imprimir_resultado("Dentro do horário da sala", entrada, "True", str(resultado), resultado is True)
        assert resultado is True

    def test_limites_exatos_horario(self):
        entrada = '("08:00","18:00","08:00","18:00")'
        resultado = time_in_range("08:00", "18:00", "08:00", "18:00")
        imprimir_resultado("Limites exatos do horário", entrada, "True", str(resultado), resultado is True)
        assert resultado is True

    def test_inicio_antes_sala_abrir(self):
        entrada = '("07:00","09:00","08:00","18:00")'
        resultado = time_in_range("07:00", "09:00", "08:00", "18:00")
        imprimir_resultado("Início antes da sala abrir", entrada, "False", str(resultado), resultado is False)
        assert resultado is False

    def test_fim_depois_sala_fechar(self):
        entrada = '("17:00","19:00","08:00","18:00")'
        resultado = time_in_range("17:00", "19:00", "08:00", "18:00")
        imprimir_resultado("Fim depois da sala fechar", entrada, "False", str(resultado), resultado is False)
        assert resultado is False

    def test_totalmente_fora_horario(self):
        entrada = '("19:00","20:00","08:00","18:00")'
        resultado = time_in_range("19:00", "20:00", "08:00", "18:00")
        imprimir_resultado("Totalmente fora do horário", entrada, "False", str(resultado), resultado is False)
        assert resultado is False


# ===================================================================
# 2. LOGIN
# ===================================================================

class TestRelatorioLogin:
    """Testes do formulário de login."""

    def test_login_valido_email(self, client, admin_user):
        entrada = "username=admin@salas.pt, password=admin123"
        resp = _login(client, "admin@salas.pt", "admin123")
        passou = resp.status_code == 303
        imprimir_resultado("Login válido (email)", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_login_valido_nome(self, client, admin_user):
        entrada = "username=Admin, password=admin123"
        resp = _login(client, "Admin", "admin123")
        passou = resp.status_code == 303
        imprimir_resultado("Login válido (nome)", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_login_password_errada(self, client, admin_user):
        entrada = "username=admin@salas.pt, password=errada"
        resp = _login(client, "admin@salas.pt", "errada")
        passou = resp.status_code == 401
        imprimir_resultado("Password errada", entrada, "Status 401", f"Status {resp.status_code}", passou)
        assert passou

    def test_login_utilizador_inexistente(self, client, admin_user):
        entrada = "username=naoexiste@x.pt, password=abc"
        resp = _login(client, "naoexiste@x.pt", "abc")
        passou = resp.status_code == 401
        imprimir_resultado("Utilizador inexistente", entrada, "Status 401", f"Status {resp.status_code}", passou)
        assert passou

    def test_login_campos_vazios(self, client, admin_user):
        entrada = 'username="", password=""'
        resp = _login(client, "", "")
        passou = resp.status_code == 401
        imprimir_resultado("Campos vazios", entrada, "Status 401", f"Status {resp.status_code}", passou)
        assert passou

    def test_login_sql_injection(self, client, admin_user):
        entrada = "username=' OR 1=1 --, password=x"
        resp = _login(client, "' OR 1=1 --", "x")
        passou = resp.status_code in (401, 429)
        imprimir_resultado("SQL Injection no username", entrada, "Status 401 ou 429 (protegido)", f"Status {resp.status_code}", passou)
        assert passou

    def test_login_xss_username(self, client, admin_user):
        entrada = "username=<script>alert(1)</script>, password=x"
        resp = _login(client, "<script>alert(1)</script>", "x")
        passou = resp.status_code in (401, 429)
        imprimir_resultado("XSS no username", entrada, "Status 401 ou 429 (protegido)", f"Status {resp.status_code}", passou)
        assert passou

    def test_login_username_muito_longo(self, client, admin_user):
        entrada = "username='A'*10000, password=x"
        resp = _login(client, "A" * 10000, "x")
        passou = resp.status_code in (401, 429)
        imprimir_resultado("Username muito longo (10000 chars)", entrada, "Status 401 ou 429", f"Status {resp.status_code}", passou)
        assert passou


# ===================================================================
# 3. CRIAÇÃO DE RESERVAS
# ===================================================================

class TestRelatorioReservas:
    """Testes do formulário de criação de reservas."""

    def _criar_reserva(self, client, room_id, date, start, end, title):
        return client.post("/reservations/create", data={
            "room_id": room_id,
            "date": date,
            "start_time": start,
            "end_time": end,
            "title": title,
        }, follow_redirects=False)

    def test_reserva_valida(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = "room=Sala A, date=2026-06-01, 09:00-10:00, title=Reunião"
        resp = self._criar_reserva(client, room.id, "2026-06-01", "09:00", "10:00", "Reunião Teste")
        passou = resp.status_code == 303
        imprimir_resultado("Reserva válida", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_titulo_vazio(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = 'title=""'
        resp = self._criar_reserva(client, room.id, "2026-06-01", "09:00", "10:00", "")
        passou = resp.status_code == 200 and "obrigat" in resp.text.lower()
        imprimir_resultado("Título vazio", entrada, "Erro: título obrigatório", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_titulo_espacos(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = 'title="   "'
        resp = self._criar_reserva(client, room.id, "2026-06-01", "09:00", "10:00", "   ")
        passou = resp.status_code == 200 and "obrigat" in resp.text.lower()
        imprimir_resultado("Título só espaços", entrada, "Erro: título obrigatório", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_titulo_100_caracteres(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        titulo = "A" * 100
        entrada = f"title='A'*100 ({len(titulo)} chars)"
        resp = self._criar_reserva(client, room.id, "2026-06-01", "09:00", "10:00", titulo)
        passou = resp.status_code == 303
        imprimir_resultado("Título com 100 caracteres (limite)", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_titulo_101_caracteres(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        titulo = "A" * 101
        entrada = f"title='A'*101 ({len(titulo)} chars)"
        resp = self._criar_reserva(client, room.id, "2026-06-01", "09:00", "10:00", titulo)
        passou = resp.status_code == 200 and "longo" in resp.text.lower()
        imprimir_resultado("Título com 101 caracteres (acima do limite)", entrada, "Erro: título muito longo", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_titulo_1_caracter(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = 'title="X"'
        resp = self._criar_reserva(client, room.id, "2026-06-01", "11:00", "12:00", "X")
        passou = resp.status_code == 303
        imprimir_resultado("Título com 1 carácter", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_hora_inicio_depois_fim(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = "start=11:00, end=09:00"
        resp = self._criar_reserva(client, room.id, "2026-06-01", "11:00", "09:00", "Teste")
        passou = resp.status_code == 200 and "anterior" in resp.text.lower()
        imprimir_resultado("Hora início depois da hora fim", entrada, "Erro: hora início > fim", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_hora_inicio_igual_fim(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = "start=09:00, end=09:00"
        resp = self._criar_reserva(client, room.id, "2026-06-01", "09:00", "09:00", "Teste")
        passou = resp.status_code == 200 and "anterior" in resp.text.lower()
        imprimir_resultado("Hora início igual à hora fim", entrada, "Erro: hora início = fim", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_fora_horario_antes(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = "start=07:00, end=07:30 (sala abre às 08:00)"
        resp = self._criar_reserva(client, room.id, "2026-06-01", "07:00", "07:30", "Teste")
        passou = resp.status_code == 200 and "hor" in resp.text.lower()
        imprimir_resultado("Fora do horário (antes de abrir)", entrada, "Erro: fora do horário", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_fora_horario_depois(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = "start=18:30, end=19:00 (sala fecha às 18:00)"
        resp = self._criar_reserva(client, room.id, "2026-06-01", "18:30", "19:00", "Teste")
        passou = resp.status_code == 200 and "hor" in resp.text.lower()
        imprimir_resultado("Fora do horário (depois de fechar)", entrada, "Erro: fora do horário", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_limites_exatos_sala(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = "start=08:00, end=18:00 (limites exatos)"
        resp = self._criar_reserva(client, room.id, "2026-06-01", "08:00", "18:00", "Dia Inteiro")
        passou = resp.status_code == 303
        imprimir_resultado("Limites exatos da sala (08:00-18:00)", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_conflito_horario(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        self._criar_reserva(client, room.id, "2026-06-02", "09:00", "10:00", "Primeira")
        entrada = "09:30-10:30 (conflito com 09:00-10:00 existente)"
        resp = self._criar_reserva(client, room.id, "2026-06-02", "09:30", "10:30", "Segunda")
        passou = resp.status_code == 200 and "conflito" in resp.text.lower()
        imprimir_resultado("Conflito de horário", entrada, "Erro: conflito", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_horarios_adjacentes(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        self._criar_reserva(client, room.id, "2026-06-03", "09:00", "10:00", "Primeira")
        entrada = "10:00-11:00 (adjacente a 09:00-10:00)"
        resp = self._criar_reserva(client, room.id, "2026-06-03", "10:00", "11:00", "Segunda")
        passou = resp.status_code == 303
        imprimir_resultado("Horários adjacentes (sem conflito)", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_sala_inexistente(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = "room_id=99999"
        resp = self._criar_reserva(client, 99999, "2026-06-01", "09:00", "10:00", "Teste")
        passou = resp.status_code == 200 and "encontrada" in resp.text.lower()
        imprimir_resultado("Sala inexistente", entrada, "Erro: sala não encontrada", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_data_passada(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = "date=2020-01-01"
        resp = self._criar_reserva(client, room.id, "2020-01-01", "09:00", "10:00", "Teste")
        passou = resp.status_code == 200 and "passad" in resp.text.lower()
        imprimir_resultado("Data passada", entrada, "Erro: data passada", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_dia_fim_semana(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        # 2026-06-06 é sábado
        entrada = "date=2026-06-06 (sábado, sala só dias úteis)"
        resp = self._criar_reserva(client, room.id, "2026-06-06", "09:00", "10:00", "Teste")
        passou = resp.status_code == 200 and "encerrada" in resp.text.lower()
        imprimir_resultado("Dia de fim de semana (sábado)", entrada, "Erro: sala encerrada", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_sala_id_zero(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = "room_id=0"
        resp = self._criar_reserva(client, 0, "2026-06-01", "09:00", "10:00", "Teste")
        passou = resp.status_code == 200 and "inv" in resp.text.lower()
        imprimir_resultado("Sala ID zero", entrada, "Erro: sala inválida", f"Status {resp.status_code}", passou)
        assert passou

    def test_reserva_sem_login(self, client, room):
        entrada = "Sem cookie user_id"
        resp = self._criar_reserva(client, room.id, "2026-06-01", "09:00", "10:00", "Teste")
        passou = resp.status_code == 401
        imprimir_resultado("Reserva sem login", entrada, "Status 401", f"Status {resp.status_code}", passou)
        assert passou


# ===================================================================
# 4. GESTÃO DE SALAS (ADMIN)
# ===================================================================

class TestRelatorioSalas:
    """Testes do formulário de gestão de salas (painel admin)."""

    def _criar_sala(self, client, name="Sala Nova", capacity=10, location="Piso 1",
                    color="#ff0000", start_time="08:00", end_time="18:00", work_days=None):
        if work_days is None:
            work_days = ["1", "2", "3", "4", "5"]
        return client.post("/admin/rooms/create", data={
            "name": name,
            "capacity": capacity,
            "location": location,
            "color": color,
            "start_time": start_time,
            "end_time": end_time,
            "work_days": work_days,
        }, follow_redirects=False)

    def test_sala_valida(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = "name=Sala Nova, capacity=10, color=#ff0000, 08:00-18:00, dias 1-5"
        resp = self._criar_sala(client)
        passou = resp.status_code == 303
        imprimir_resultado("Sala válida", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_cor_invalida_texto(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = 'color="nao-e-cor"'
        resp = self._criar_sala(client, color="nao-e-cor")
        passou = resp.status_code == 200 and "cor" in resp.text.lower()
        imprimir_resultado("Cor inválida (texto)", entrada, "Erro: cor inválida", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_cor_invalida_curta(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = 'color="#fff"'
        resp = self._criar_sala(client, color="#fff")
        passou = resp.status_code == 200 and "cor" in resp.text.lower()
        imprimir_resultado("Cor inválida (3 dígitos)", entrada, "Erro: cor inválida", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_cor_invalida_sem_hash(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = 'color="ff0000"'
        resp = self._criar_sala(client, color="ff0000")
        passou = resp.status_code == 200 and "cor" in resp.text.lower()
        imprimir_resultado("Cor inválida (sem #)", entrada, "Erro: cor inválida", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_cor_valida_minuscula(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = 'color="#aabb00"'
        resp = self._criar_sala(client, color="#aabb00")
        passou = resp.status_code == 303
        imprimir_resultado("Cor válida (minúscula)", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_cor_valida_maiuscula(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = 'color="#AABB00"'
        resp = self._criar_sala(client, color="#AABB00")
        passou = resp.status_code == 303
        imprimir_resultado("Cor válida (maiúscula)", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_cor_valida_mista(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = 'color="#aAbB00"'
        resp = self._criar_sala(client, color="#aAbB00")
        passou = resp.status_code == 303
        imprimir_resultado("Cor válida (maiúsculas e minúsculas)", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_hora_inicio_depois_fim(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = "start=18:00, end=08:00"
        resp = self._criar_sala(client, start_time="18:00", end_time="08:00")
        passou = resp.status_code == 200 and "anterior" in resp.text.lower()
        imprimir_resultado("Hora início depois da hora fim", entrada, "Erro: hora início > fim", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_hora_inicio_igual_fim(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = "start=12:00, end=12:00"
        resp = self._criar_sala(client, start_time="12:00", end_time="12:00")
        passou = resp.status_code == 200 and "anterior" in resp.text.lower()
        imprimir_resultado("Hora início igual à hora fim", entrada, "Erro: hora início = fim", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_sem_dias_uteis(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = "work_days=[] (vazio)"
        resp = self._criar_sala(client, work_days=[])
        passou = resp.status_code == 200 and "dia" in resp.text.lower()
        imprimir_resultado("Sem dias úteis selecionados", entrada, "Erro: selecione pelo menos um dia", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_todos_dias(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = "work_days=[0,1,2,3,4,5,6] (todos)"
        resp = self._criar_sala(client, work_days=["0", "1", "2", "3", "4", "5", "6"])
        passou = resp.status_code == 303
        imprimir_resultado("Todos os dias da semana", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_so_fim_semana(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = "work_days=[0,6] (só fim de semana)"
        resp = self._criar_sala(client, work_days=["0", "6"])
        passou = resp.status_code == 303
        imprimir_resultado("Só fim de semana", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_sala_utilizador_normal_bloqueado(self, client, normal_user):
        _login_as_user(client, normal_user)
        entrada = "role=user tenta criar sala"
        resp = self._criar_sala(client)
        passou = resp.status_code == 403
        imprimir_resultado("Utilizador normal tenta criar sala", entrada, "Status 403", f"Status {resp.status_code}", passou)
        assert passou


# ===================================================================
# 5. GESTÃO DE UTILIZADORES (ADMIN)
# ===================================================================

class TestRelatorioUtilizadores:
    """Testes do formulário de gestão de utilizadores (painel admin)."""

    def test_criar_utilizador_valido(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = "name=Novo User, email=novo@test.pt, role=user"
        resp = client.post("/admin/users/create", data={
            "name": "Novo User", "email": "novo@test.pt", "role": "user"
        }, follow_redirects=False)
        passou = resp.status_code == 303
        imprimir_resultado("Criar utilizador válido", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_criar_utilizador_email_duplicado(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = "email=admin@salas.pt (já existe)"
        resp = client.post("/admin/users/create", data={
            "name": "Duplicado", "email": "admin@salas.pt", "role": "user"
        }, follow_redirects=False)
        passou = resp.status_code == 200 and "registado" in resp.text.lower()
        imprimir_resultado("Email duplicado na criação", entrada, "Erro: email já registado", f"Status {resp.status_code}", passou)
        assert passou

    def test_criar_utilizador_admin(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = "name=Novo Admin, email=admin2@test.pt, role=admin"
        resp = client.post("/admin/users/create", data={
            "name": "Novo Admin", "email": "admin2@test.pt", "role": "admin"
        }, follow_redirects=False)
        passou = resp.status_code == 303
        imprimir_resultado("Criar utilizador com role admin", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_atualizar_email_duplicado(self, client, admin_user, normal_user):
        _login_as_user(client, admin_user)
        entrada = f"user_id={normal_user.id}, email=admin@salas.pt (duplicado)"
        resp = client.post(f"/admin/users/update/{normal_user.id}", data={
            "name": "User", "email": "admin@salas.pt", "role": "user"
        }, follow_redirects=False)
        passou = resp.status_code == 200 and "uso" in resp.text.lower()
        imprimir_resultado("Atualizar email para duplicado", entrada, "Erro: email em uso", f"Status {resp.status_code}", passou)
        assert passou

    def test_eliminar_utilizador(self, client, admin_user, normal_user):
        _login_as_user(client, admin_user)
        entrada = f"user_id={normal_user.id}"
        resp = client.post(f"/admin/users/delete/{normal_user.id}", follow_redirects=False)
        passou = resp.status_code == 303
        imprimir_resultado("Eliminar utilizador", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_admin_nao_pode_eliminar_se_proprio(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = f"admin elimina self (user_id={admin_user.id})"
        resp = client.post(f"/admin/users/delete/{admin_user.id}", follow_redirects=False)
        passou = resp.status_code == 400
        imprimir_resultado("Admin não pode eliminar-se", entrada, "Status 400", f"Status {resp.status_code}", passou)
        assert passou


# ===================================================================
# 6. PERFIL DO UTILIZADOR
# ===================================================================

class TestRelatorioPerfil:
    """Testes do formulário de atualização de perfil."""

    def _atualizar_perfil(self, client, name, email, password="", avatar=None):
        data = {"name": name, "email": email, "password": password}
        files = {}
        if avatar:
            files["avatar"] = avatar
        return client.post("/user/update", data=data, files=files if files else None, follow_redirects=False)

    def test_atualizar_nome(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = 'name="Novo Nome"'
        resp = self._atualizar_perfil(client, "Novo Nome", "admin@salas.pt")
        passou = resp.status_code == 200 and "sucesso" in resp.text.lower()
        imprimir_resultado("Atualizar nome", entrada, "Sucesso", f"Status {resp.status_code}", passou)
        assert passou

    def test_perfil_email_duplicado(self, client, admin_user, normal_user):
        _login_as_user(client, admin_user)
        entrada = f'email="{normal_user.email}" (de outro utilizador)'
        resp = self._atualizar_perfil(client, "Admin", normal_user.email)
        passou = resp.status_code == 200 and "uso" in resp.text.lower()
        imprimir_resultado("Email duplicado no perfil", entrada, "Erro: email em uso", f"Status {resp.status_code}", passou)
        assert passou

    def test_alterar_password(self, client, admin_user, db):
        _login_as_user(client, admin_user)
        entrada = 'password="novapass123"'
        resp = self._atualizar_perfil(client, "Admin", "admin@salas.pt", password="novapass123")
        passou = resp.status_code == 200 and "sucesso" in resp.text.lower()
        imprimir_resultado("Alterar password", entrada, "Sucesso", f"Status {resp.status_code}", passou)
        assert passou

    def test_avatar_extensao_invalida(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = 'avatar="test.exe"'
        resp = client.post("/user/update", data={"name": "Admin", "email": "admin@salas.pt", "password": ""},
                          files={"avatar": ("test.exe", b"fake content", "application/octet-stream")},
                          follow_redirects=False)
        passou = resp.status_code == 200 and "formato" in resp.text.lower()
        imprimir_resultado("Avatar com extensão inválida (.exe)", entrada, "Erro: formato não permitido", f"Status {resp.status_code}", passou)
        assert passou

    def test_avatar_muito_grande(self, client, admin_user):
        _login_as_user(client, admin_user)
        big_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * (2 * 1024 * 1024 + 1)
        entrada = "avatar > 2MB (2097153 bytes)"
        resp = client.post("/user/update", data={"name": "Admin", "email": "admin@salas.pt", "password": ""},
                          files={"avatar": ("big.png", big_content, "image/png")},
                          follow_redirects=False)
        passou = resp.status_code == 200 and "grande" in resp.text.lower()
        imprimir_resultado("Avatar muito grande (> 2MB)", entrada, "Erro: ficheiro muito grande", f"Status {resp.status_code}", passou)
        assert passou

    def test_avatar_conteudo_falso(self, client, admin_user):
        _login_as_user(client, admin_user)
        entrada = 'avatar="evil.jpg" com bytes de texto'
        resp = client.post("/user/update", data={"name": "Admin", "email": "admin@salas.pt", "password": ""},
                          files={"avatar": ("evil.jpg", b"this is not a jpg", "image/jpeg")},
                          follow_redirects=False)
        passou = resp.status_code == 200 and "conte" in resp.text.lower()
        imprimir_resultado("Avatar com conteúdo falso (bytes inválidos)", entrada, "Erro: conteúdo não corresponde", f"Status {resp.status_code}", passou)
        assert passou

    def test_avatar_png_valido(self, client, admin_user):
        _login_as_user(client, admin_user)
        png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        entrada = "avatar PNG válido (magic bytes corretos)"
        resp = client.post("/user/update", data={"name": "Admin", "email": "admin@salas.pt", "password": ""},
                          files={"avatar": ("foto.png", png_content, "image/png")},
                          follow_redirects=False)
        passou = resp.status_code == 200 and "sucesso" in resp.text.lower()
        imprimir_resultado("Avatar PNG válido", entrada, "Sucesso", f"Status {resp.status_code}", passou)
        assert passou

    def test_avatar_jpg_valido(self, client, admin_user):
        _login_as_user(client, admin_user)
        jpg_content = b"\xff\xd8\xff" + b"\x00" * 100
        entrada = "avatar JPG válido (magic bytes corretos)"
        resp = client.post("/user/update", data={"name": "Admin", "email": "admin@salas.pt", "password": ""},
                          files={"avatar": ("foto.jpg", jpg_content, "image/jpeg")},
                          follow_redirects=False)
        passou = resp.status_code == 200 and "sucesso" in resp.text.lower()
        imprimir_resultado("Avatar JPG válido", entrada, "Sucesso", f"Status {resp.status_code}", passou)
        assert passou

    def test_avatar_exatamente_2mb(self, client, admin_user):
        _login_as_user(client, admin_user)
        png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * (2 * 1024 * 1024 - 8)  # exatamente 2MB
        entrada = f"avatar exatamente 2MB ({len(png_content)} bytes)"
        resp = client.post("/user/update", data={"name": "Admin", "email": "admin@salas.pt", "password": ""},
                          files={"avatar": ("foto.png", png_content, "image/png")},
                          follow_redirects=False)
        passou = resp.status_code == 200 and "sucesso" in resp.text.lower()
        imprimir_resultado("Avatar exatamente 2MB (limite)", entrada, "Sucesso", f"Status {resp.status_code}", passou)
        assert passou

    def test_avatar_2mb_mais_1(self, client, admin_user):
        _login_as_user(client, admin_user)
        png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * (2 * 1024 * 1024 - 7)  # 2MB + 1
        entrada = f"avatar 2MB + 1 byte ({len(png_content)} bytes)"
        resp = client.post("/user/update", data={"name": "Admin", "email": "admin@salas.pt", "password": ""},
                          files={"avatar": ("foto.png", png_content, "image/png")},
                          follow_redirects=False)
        passou = resp.status_code == 200 and "grande" in resp.text.lower()
        imprimir_resultado("Avatar 2MB + 1 byte (acima do limite)", entrada, "Erro: ficheiro muito grande", f"Status {resp.status_code}", passou)
        assert passou


# ===================================================================
# 7. GESTÃO DE EQUIPAMENTO
# ===================================================================

class TestRelatorioEquipamento:
    """Testes do formulário de gestão de equipamento."""

    def test_criar_equipamento_valido(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = f"name=Projetor, description=Full HD, room_id={room.id}"
        resp = client.post("/admin/inventory/create", data={
            "name": "Projetor", "description": "Full HD", "room_id": room.id
        }, follow_redirects=False)
        passou = resp.status_code == 303
        imprimir_resultado("Criar equipamento válido", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_criar_equipamento_sem_descricao(self, client, admin_user, room):
        _login_as_user(client, admin_user)
        entrada = f'name=Quadro, description="" (vazio), room_id={room.id}'
        resp = client.post("/admin/inventory/create", data={
            "name": "Quadro", "description": "", "room_id": room.id
        }, follow_redirects=False)
        passou = resp.status_code == 303
        imprimir_resultado("Criar equipamento sem descrição", entrada, "Status 303 (campo opcional)", f"Status {resp.status_code}", passou)
        assert passou

    def test_atribuir_equipamento_valido(self, client, admin_user, normal_user, room, db):
        _login_as_user(client, admin_user)
        equip = models.Equipment(name="Monitor", description="", room_id=room.id)
        db.add(equip)
        db.commit()
        db.refresh(equip)
        entrada = f"equipment_id={equip.id}, user_id={normal_user.id}"
        resp = client.post(f"/admin/inventory/assign-to-user/{equip.id}", data={
            "user_id": normal_user.id, "notes": "Para uso diário"
        }, follow_redirects=False)
        passou = resp.status_code == 303
        imprimir_resultado("Atribuir equipamento a utilizador", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_atribuir_equipamento_duplicado(self, client, admin_user, normal_user, room, db):
        _login_as_user(client, admin_user)
        equip = models.Equipment(name="Teclado", description="", room_id=room.id)
        db.add(equip)
        db.commit()
        db.refresh(equip)
        # Primeira atribuição
        client.post(f"/admin/inventory/assign-to-user/{equip.id}", data={
            "user_id": normal_user.id, "notes": ""
        }, follow_redirects=False)
        # Segunda atribuição (duplicada)
        entrada = f"equipment_id={equip.id}, user_id={normal_user.id} (duplicado)"
        resp = client.post(f"/admin/inventory/assign-to-user/{equip.id}", data={
            "user_id": normal_user.id, "notes": ""
        }, follow_redirects=False)
        passou = resp.status_code in (400, 500)
        imprimir_resultado("Atribuição duplicada", entrada, "Erro (400 ou 500)", f"Status {resp.status_code}", passou)
        assert passou

    def test_equipamento_utilizador_normal_bloqueado(self, client, normal_user, room):
        _login_as_user(client, normal_user)
        entrada = "role=user tenta criar equipamento"
        resp = client.post("/admin/inventory/create", data={
            "name": "Teste", "description": "", "room_id": room.id
        }, follow_redirects=False)
        passou = resp.status_code == 403
        imprimir_resultado("Utilizador normal tenta criar equipamento", entrada, "Status 403", f"Status {resp.status_code}", passou)
        assert passou


# ===================================================================
# 8. PERMISSÕES
# ===================================================================

class TestRelatorioPermissoes:
    """Testes de permissões e controlo de acesso."""

    def test_user_elimina_propria_reserva(self, client, normal_user, room, db):
        _login_as_user(client, normal_user)
        res = models.Reservation(
            title="Minha Reserva", date="2026-06-01",
            start_time="09:00", end_time="10:00",
            room_id=room.id, user_id=normal_user.id
        )
        db.add(res)
        db.commit()
        db.refresh(res)
        entrada = f"user elimina reserva própria (res_id={res.id})"
        resp = client.post(f"/reservations/delete/{res.id}", follow_redirects=False)
        passou = resp.status_code == 303
        imprimir_resultado("User elimina própria reserva", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_user_nao_elimina_reserva_alheia(self, client, admin_user, normal_user, room, db):
        _login_as_user(client, normal_user)
        res = models.Reservation(
            title="Reserva Admin", date="2026-06-01",
            start_time="09:00", end_time="10:00",
            room_id=room.id, user_id=admin_user.id
        )
        db.add(res)
        db.commit()
        db.refresh(res)
        entrada = f"user tenta eliminar reserva de outro (res_id={res.id})"
        resp = client.post(f"/reservations/delete/{res.id}", follow_redirects=False)
        passou = resp.status_code == 403
        imprimir_resultado("User não elimina reserva alheia", entrada, "Status 403", f"Status {resp.status_code}", passou)
        assert passou

    def test_admin_elimina_qualquer_reserva(self, client, admin_user, normal_user, room, db):
        _login_as_user(client, admin_user)
        res = models.Reservation(
            title="Reserva User", date="2026-06-01",
            start_time="09:00", end_time="10:00",
            room_id=room.id, user_id=normal_user.id
        )
        db.add(res)
        db.commit()
        db.refresh(res)
        entrada = f"admin elimina reserva de outro (res_id={res.id})"
        resp = client.post(f"/reservations/delete/{res.id}", follow_redirects=False)
        passou = resp.status_code == 303
        imprimir_resultado("Admin elimina qualquer reserva", entrada, "Status 303", f"Status {resp.status_code}", passou)
        assert passou

    def test_dashboard_requer_login(self, client):
        entrada = "GET /dashboard sem cookie"
        resp = client.get("/dashboard")
        passou = resp.status_code == 401
        imprimir_resultado("Dashboard requer login", entrada, "Status 401", f"Status {resp.status_code}", passou)
        assert passou

    def test_admin_requer_role_admin(self, client, normal_user):
        _login_as_user(client, normal_user)
        entrada = "role=user tenta aceder /admin"
        resp = client.get("/admin")
        passou = resp.status_code == 403
        imprimir_resultado("Painel admin requer role admin", entrada, "Status 403", f"Status {resp.status_code}", passou)
        assert passou

    def test_manager_acede_admin(self, client, manager_user):
        _login_as_user(client, manager_user)
        entrada = "role=manager acede /admin"
        resp = client.get("/admin")
        passou = resp.status_code == 200
        imprimir_resultado("Manager acede ao painel admin", entrada, "Status 200", f"Status {resp.status_code}", passou)
        assert passou

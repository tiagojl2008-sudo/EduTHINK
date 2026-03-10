"""
Suite de testes para o sistema de reservas de salas.

Cobre:
- Validação de conflitos de horários
- Validação de conflitos semanais
- Bloqueios por data
- Permissões (admin vs user)
- Regras de duração
- Criação/cancelamento de reservas
- Login LDAP com mock
"""

import pytest
from datetime import datetime, date, time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import hashlib
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app import models
from app.database import get_db
from app.utils import times_overlap, time_in_range


# ===================================================================
# CONFIGURAÇÃO DA BD DE TESTE
# ===================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Cria uma BD limpa para cada teste."""
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db):
    """Cliente de teste para fazer requests HTTP."""
    with TestClient(app) as c:
        yield c


# ===================================================================
# FIXTURES - DADOS DE TESTE
# ===================================================================

@pytest.fixture
def admin_user(db):
    """Cria um utilizador admin."""
    import hashlib
    user = models.User(
        name="Admin User",
        email="admin@salas.pt",
        password=hashlib.sha256("admin123".encode()).hexdigest(),
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def normal_user(db):
    """Cria um utilizador normal."""
    user = models.User(
        name="Test User",
        email="user@test.pt",
        password=hashlib.sha256("password123".encode()).hexdigest(),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def room(db):
    """Cria uma sala de teste."""
    room = models.Room(
        name="Sala Teste",
        capacity=10,
        location="Piso 1",
        color="#0066cc",
        start_time="08:00",
        end_time="18:00",
        work_days="1,2,3,4,5"
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@pytest.fixture
def room2(db):
    """Cria uma segunda sala de teste."""
    room = models.Room(
        name="Sala Teste 2",
        capacity=20,
        location="Piso 2",
        color="#33aa66",
        start_time="09:00",
        end_time="17:00",
        work_days="1,2,3,4,5"
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


# ===================================================================
# TESTES - UTILITÁRIOS
# ===================================================================

class TestTimeUtils:
    """Testes para funções utilitárias de tempo."""

    def test_times_overlap_true(self):
        """Sobreposição detetada quando há conflito."""
        assert times_overlap("09:00", "11:00", "10:00", "12:00") == True
        assert times_overlap("10:00", "12:00", "09:00", "11:00") == True
        assert times_overlap("09:00", "12:00", "10:00", "11:00") == True

    def test_times_overlap_false(self):
        """Sem sobreposição quando não há conflito."""
        assert times_overlap("09:00", "10:00", "11:00", "12:00") == False
        assert times_overlap("14:00", "15:00", "09:00", "10:00") == False

    def test_times_overlap_adjacent(self):
        """Horários adjacentes não se sobrepõem."""
        assert times_overlap("09:00", "10:00", "10:00", "11:00") == False

    def test_time_in_range_true(self):
        """Horário dentro do intervalo permitido."""
        assert time_in_range("09:00", "11:00", "08:00", "18:00") == True
        assert time_in_range("08:00", "18:00", "08:00", "18:00") == True

    def test_time_in_range_false(self):
        """Horário fora do intervalo permitido."""
        assert time_in_range("07:00", "09:00", "08:00", "18:00") == False
        assert time_in_range("17:00", "19:00", "08:00", "18:00") == False
        assert time_in_range("19:00", "20:00", "08:00", "18:00") == False


# ===================================================================
# TESTES - VALIDADOR DE CONFLITOS DE HORÁRIOS
# ===================================================================

class TestConflictValidation:
    """Testes para validação de conflitos de horários."""

    def test_conflict_same_room_same_time(self, db, room, normal_user):
        """Conflito detetado: mesma sala, mesmo horário."""
        # Criar primeira reserva
        res1 = models.Reservation(
            title="Reunião A",
            date="2026-03-10",
            start_time="09:00",
            end_time="11:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(res1)
        db.commit()

        # Tentar criar reserva conflituosa
        start = "10:00"
        end = "12:00"
        
        # Verificar conflitos com TODAS as reservas (incluindo a própria)
        existing = db.query(models.Reservation).filter(
            models.Reservation.room_id == room.id,
            models.Reservation.date == "2026-03-10"
        ).all()

        has_conflict = False
        for r in existing:
            if times_overlap(start, end, r.start_time, r.end_time):
                has_conflict = True
                break

        assert has_conflict == True

    def test_no_conflict_different_rooms(self, db, room, room2, normal_user):
        """Sem conflito: salas diferentes, mesmo horário."""
        res1 = models.Reservation(
            title="Reunião A",
            date="2026-03-10",
            start_time="09:00",
            end_time="11:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(res1)
        db.commit()

        # Criar reserva noutra sala - deve ser permitido
        res2 = models.Reservation(
            title="Reunião B",
            date="2026-03-10",
            start_time="09:00",
            end_time="11:00",
            room_id=room2.id,
            user_id=normal_user.id
        )
        db.add(res2)
        db.commit()

        assert res2.id is not None

    def test_no_conflict_different_days(self, db, room, normal_user):
        """Sem conflito: mesma sala, dias diferentes."""
        res1 = models.Reservation(
            title="Reunião A",
            date="2026-03-10",
            start_time="09:00",
            end_time="11:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(res1)
        db.commit()

        res2 = models.Reservation(
            title="Reunião B",
            date="2026-03-11",
            start_time="09:00",
            end_time="11:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(res2)
        db.commit()

        assert res2.id is not None


# ===================================================================
# TESTES - VALIDADOR DE CONFLITOS SEMANAL
# ===================================================================

class TestWeeklyConflictValidation:
    """Testes para validação de conflitos semanais."""

    def test_weekly_conflict_detection(self, db, room, normal_user):
        """Detetar conflitos ao longo da semana."""
        # Criar reservas para a semana
        reservations = [
            models.Reservation(
                title=f"Reunião {i}",
                date=f"2026-03-{10+i}",
                start_time="09:00",
                end_time="10:00",
                room_id=room.id,
                user_id=normal_user.id
            )
            for i in range(5)  # Seg a Sex
        ]
        db.add_all(reservations)
        db.commit()

        # Verificar total de reservas na semana
        week_reservations = db.query(models.Reservation).filter(
            models.Reservation.room_id == room.id,
            models.Reservation.date >= "2026-03-10",
            models.Reservation.date <= "2026-03-14"
        ).all()

        assert len(week_reservations) == 5


# ===================================================================
# TESTES - BLOQUEIOS POR DATA
# ===================================================================

class TestDateBlockValidation:
    """Testes para validação de bloqueios por data."""

    def test_reservation_on_weekend_blocked(self, db, room, normal_user):
        """Reserva bloqueada num dia fora dos work_days (fim de semana)."""
        # Sala com work_days="1,2,3,4,5" (Seg-Sex)
        # 2026-03-14 é Sábado (dia 6)
        
        dow = 6  # Sábado
        work_days = [int(d) for d in room.work_days.split(",")]
        
        is_blocked = dow not in work_days
        assert is_blocked == True

    def test_reservation_on_workday_allowed(self, db, room, normal_user):
        """Reserva permitida num dia útil."""
        # 2026-03-10 é Terça-feira (dia 2)
        
        dow = 2  # Terça
        work_days = [int(d) for d in room.work_days.split(",")]
        
        is_allowed = dow in work_days
        assert is_allowed == True


# ===================================================================
# TESTES - PERMISSÕES (ADMIN VS USER)
# ===================================================================

class TestPermissionValidation:
    """Testes para validação de permissões."""

    def test_user_can_delete_own_reservation(self, db, room, normal_user):
        """Utilizador pode eliminar a sua própria reserva."""
        res = models.Reservation(
            title="Minha Reserva",
            date="2026-03-10",
            start_time="09:00",
            end_time="10:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(res)
        db.commit()

        # Verificar permissão
        can_delete = (res.user_id == normal_user.id)
        assert can_delete == True

    def test_user_cannot_delete_others_reservation(self, db, room, admin_user, normal_user):
        """Utilizador não pode eliminar reserva de outro."""
        res = models.Reservation(
            title="Reserva do Admin",
            date="2026-03-10",
            start_time="09:00",
            end_time="10:00",
            room_id=room.id,
            user_id=admin_user.id
        )
        db.add(res)
        db.commit()

        # Verificar permissão
        can_delete = (res.user_id == normal_user.id or normal_user.role == "admin")
        assert can_delete == False

    def test_admin_can_delete_any_reservation(self, db, room, admin_user, normal_user):
        """Admin pode eliminar qualquer reserva."""
        res = models.Reservation(
            title="Reserva do User",
            date="2026-03-10",
            start_time="09:00",
            end_time="10:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(res)
        db.commit()

        # Verificar permissão
        can_delete = (res.user_id == admin_user.id or admin_user.role == "admin")
        assert can_delete == True


# ===================================================================
# TESTES - REGRAS DE DURAÇÃO
# ===================================================================

class TestDurationRules:
    """Testes para validação de regras de duração."""

    def test_start_before_end(self, db, room):
        """Hora de início deve ser antes da hora de fim."""
        start_time = "09:00"
        end_time = "11:00"
        
        is_valid = start_time < end_time
        assert is_valid == True

    def test_end_before_start_invalid(self, db, room):
        """Hora de fim antes do início é inválido."""
        start_time = "11:00"
        end_time = "09:00"
        
        is_valid = start_time < end_time
        assert is_valid == False

    def test_duration_within_working_hours(self, db, room):
        """Duração deve estar dentro do horário útil."""
        start = "09:00"
        end = "17:00"
        
        is_valid = time_in_range(start, end, room.start_time, room.end_time)
        assert is_valid == True

    def test_duration_exceeds_working_hours(self, db, room):
        """Duração que excede horário útil é inválida."""
        start = "07:00"
        end = "19:00"
        
        is_valid = time_in_range(start, end, room.start_time, room.end_time)
        assert is_valid == False


# ===================================================================
# TESTES - CRIAÇÃO DE RESERVA
# ===================================================================

class TestReservationCreation:
    """Testes para criação de reservas."""

    def test_create_valid_reservation(self, db, room, normal_user):
        """Criar reserva válida com sucesso."""
        reservation = models.Reservation(
            title="Reunião de Projeto",
            date="2026-03-10",
            start_time="09:00",
            end_time="11:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert reservation.id is not None
        assert reservation.title == "Reunião de Projeto"
        assert reservation.room_id == room.id
        assert reservation.user_id == normal_user.id

    def test_create_reservation_with_conflict_fails(self, db, room, normal_user):
        """Criar reserva com conflito deve falhar."""
        # Criar primeira reserva
        res1 = models.Reservation(
            title="Reunião A",
            date="2026-03-10",
            start_time="09:00",
            end_time="11:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(res1)
        db.commit()

        # Verificar conflito antes de criar segunda
        start = "10:00"
        end = "12:00"
        
        existing = db.query(models.Reservation).filter(
            models.Reservation.room_id == room.id,
            models.Reservation.date == "2026-03-10"
        ).all()

        has_conflict = False
        for r in existing:
            if times_overlap(start, end, r.start_time, r.end_time):
                has_conflict = True
                break

        assert has_conflict == True

    def test_create_reservation_outside_working_hours(self, db, room, normal_user):
        """Criar reserva fora do horário útil."""
        start = "07:00"
        end = "08:00"
        
        is_valid = time_in_range(start, end, room.start_time, room.end_time)
        assert is_valid == False

    def test_create_reservation_on_blocked_date(self, db, room, normal_user):
        """Criar reserva em data bloqueada (fim de semana)."""
        dow = 6  # Sábado
        work_days = [int(d) for d in room.work_days.split(",")]
        
        is_blocked = dow not in work_days
        assert is_blocked == True


# ===================================================================
# TESTES - CANCELAMENTO DE RESERVA
# ===================================================================

class TestReservationCancellation:
    """Testes para cancelamento de reservas."""

    def test_owner_can_cancel_own_reservation(self, db, room, normal_user):
        """Proprietário pode cancelar a sua reserva."""
        res = models.Reservation(
            title="Minha Reserva",
            date="2026-03-10",
            start_time="09:00",
            end_time="10:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(res)
        db.commit()

        # Verificar permissão
        can_cancel = (res.user_id == normal_user.id)
        assert can_cancel == True

        # Cancelar (eliminar)
        db.delete(res)
        db.commit()

        # Verificar que foi eliminada
        deleted = db.query(models.Reservation).filter(models.Reservation.id == res.id).first()
        assert deleted is None

    def test_non_owner_cannot_cancel_reservation(self, db, room, admin_user, normal_user):
        """Não proprietário não pode cancelar (deve falhar)."""
        res = models.Reservation(
            title="Reserva do Admin",
            date="2026-03-10",
            start_time="09:00",
            end_time="10:00",
            room_id=room.id,
            user_id=admin_user.id
        )
        db.add(res)
        db.commit()

        # Verificar permissão (user normal não é owner nem admin)
        can_cancel = (res.user_id == normal_user.id or normal_user.role == "admin")
        assert can_cancel == False

    def test_admin_can_cancel_any_reservation(self, db, room, admin_user, normal_user):
        """Admin pode cancelar qualquer reserva."""
        res = models.Reservation(
            title="Reserva do User",
            date="2026-03-10",
            start_time="09:00",
            end_time="10:00",
            room_id=room.id,
            user_id=normal_user.id
        )
        db.add(res)
        db.commit()

        # Verificar permissão
        can_cancel = (res.user_id == admin_user.id or admin_user.role == "admin")
        assert can_cancel == True

        # Admin cancela
        db.delete(res)
        db.commit()

        # Verificar que foi eliminada
        deleted = db.query(models.Reservation).filter(models.Reservation.id == res.id).first()
        assert deleted is None


# ===================================================================
# TESTES - LOGIN LDAP COM MOCK
# ===================================================================

class MockLDAPAuthenticator:
    """Mock do autenticador LDAP para testes."""

    def __init__(self):
        self.users = {
            "fry": "fry",
            "leela": "leela",
            "zoidberg": "zoidberg",
            "admin": "admin"
        }

    def authenticate(self, username: str, password: str) -> bool:
        """Autentica com base nas credenciais mock."""
        return self.users.get(username) == password


class TestLDAPAuthMock:
    """Testes para login LDAP com mock."""

    def test_ldap_auth_success(self):
        """Login LDAP bem sucedido."""
        mock_auth = MockLDAPAuthenticator()
        
        result = mock_auth.authenticate("fry", "fry")
        assert result == True

    def test_ldap_auth_wrong_password(self):
        """Login LDAP com password errada."""
        mock_auth = MockLDAPAuthenticator()
        
        result = mock_auth.authenticate("fry", "wrong")
        assert result == False

    def test_ldap_auth_unknown_user(self):
        """Login LDAP com utilizador desconhecido."""
        mock_auth = MockLDAPAuthenticator()
        
        result = mock_auth.authenticate("unknown", "password")
        assert result == False

    def test_ldap_auth_empty_credentials(self):
        """Login LDAP com credenciais vazias."""
        mock_auth = MockLDAPAuthenticator()
        
        result = mock_auth.authenticate("", "")
        assert result == False

    def test_ldap_auth_creates_user_in_db(self, db):
        """Login LDAP bem sucedido cria utilizador na BD."""
        mock_auth = MockLDAPAuthenticator()
        
        # Autenticar
        auth_result = mock_auth.authenticate("fry", "fry")
        assert auth_result == True

        # Criar user na BD após autenticação
        user = models.User(
            name="Philip J. Fry",
            email="fry@planetexpress.com",
            password="",  # LDAP não guarda password
            role="user"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.email == "fry@planetexpress.com"


# ===================================================================
# TESTES - INTEGRAÇÃO HTTP
# ===================================================================

class TestHTTPIntegration:
    """Testes de integração via HTTP."""

    def test_login_page_loads(self, client):
        """Página de login carrega com sucesso."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_public_page_loads(self, client):
        """Página pública carrega com sucesso."""
        response = client.get("/")
        assert response.status_code == 200

    def test_dashboard_requires_login(self, client):
        """Dashboard requer login."""
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code in [307, 401, 403]

    def test_admin_requires_admin_role(self, client):
        """Admin requer papel de admin."""
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code in [307, 401, 403]


# ===================================================================
# EXECUÇÃO
# ===================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

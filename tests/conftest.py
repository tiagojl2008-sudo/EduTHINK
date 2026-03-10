"""
Configuração global dos testes.
"""

import pytest
import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def test_config():
    """Configuração de teste reutilizável."""
    return {
        "ldap_users": {
            "fry": "fry",
            "leela": "leela",
            "zoidberg": "zoidberg",
            "bender": "bender",
            "amy": "amy",
            "hermes": "hermes",
            "professor": "professor",
        },
        "admin_email": "admin@salas.pt",
        "admin_password": "admin123",
        "test_db_url": "sqlite:///./test.db",
    }

"""
Script de Backup Automático para Google Drive
Requer autenticação OAuth2 do Google.

CONFIGURAÇÃO INICIAL (apenas uma vez):
1. Abre https://console.cloud.google.com/
2. Cria um novo projeto
3. Ativa a Google Drive API
4. Cria credenciais OAuth2 (Desktop app)
5. Download do ficheiro JSON e renomeia para 'credentials.json'
6. Coloca na mesma pasta deste script

EXECUTAR:
python backup_drive.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Verificar se a biblioteca do Google está instalada
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import ResumableUploadError
except ImportError:
    print("❌ Biblioteca do Google não instalada!")
    print("\nInstala com:")
    print("  pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    print("\nOU usa o script backup.py simples (sem Drive)")
    sys.exit(1)

# Configurações
SCOPES = ['https://www.googleapis.com/auth/drive.file']
PROJECT_ROOT = Path(__file__).parent
BACKUP_FOLDER = PROJECT_ROOT / "backups"
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "token.json"


def authenticate():
    """Autentica com o Google Drive."""
    creds = None
    
    # Carregar token existente
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Se não houver creds válidas, fazer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("❌ Ficheiro 'credentials.json' não encontrado!")
                print("\nInstruções:")
                print("1. Abre https://console.cloud.google.com/")
                print("2. Cria um projeto e ativa a Drive API")
                print("3. Cria credenciais OAuth2 (Desktop)")
                print("4. Download do JSON → guarda como 'credentials.json'")
                input("\nPressiona Enter após guardar o ficheiro...")
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar token para próxima vez
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def upload_to_drive(file_path: Path, folder_name: str = "Backups Projeto"):
    """Faz upload de um ficheiro para o Google Drive."""
    print("🔐 A autenticar com Google Drive...")
    creds = authenticate()
    
    print("📡 A ligar ao Google Drive...")
    service = build('drive', 'v3', credentials=creds)
    
    # Criar/findar pasta de backups
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    
    if folders:
        folder_id = folders[0]['id']
        print(f"📁 Pasta encontrada: {folder_name}")
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"📁 Pasta criada: {folder_name}")
    
    # Upload do ficheiro
    print(f"📤 A fazer upload de {file_path.name}...")
    
    file_metadata = {
        'name': file_path.name,
        'parents': [folder_id]
    }
    
    media = MediaFileUpload(str(file_path), mimetype='application/zip', resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    # Tornar acessível apenas para o dono
    service.permissions().create(
        fileId=file.get('id'),
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    
    print("-" * 50)
    print("✅ Upload concluído!")
    print(f"🔗 Link: {file.get('webViewLink')}")
    print("-" * 50)
    
    return file.get('id')


def main():
    """Função principal."""
    print("=" * 50)
    print("🔄 BACKUP AUTOMÁTICO - GOOGLE DRIVE")
    print("=" * 50)
    
    # Passo 1: Criar backup ZIP
    print("\n📦 PASSO 1: Criar backup ZIP...")
    from backup import create_backup, clean_old_backups
    
    backup_path = create_backup()
    clean_old_backups(keep_last=3)
    
    # Passo 2: Upload para Drive
    print("\n📤 PASSO 2: Upload para Google Drive...")
    
    try:
        upload_to_drive(backup_path)
    except Exception as e:
        print(f"\n❌ Erro no upload: {e}")
        print("\n💡 O backup ZIP foi criado localmente:")
        print(f"   {backup_path}")
        print("\n   Podes fazer upload manual em: https://drive.google.com")
    
    input("\nPressiona Enter para sair...")


if __name__ == "__main__":
    main()

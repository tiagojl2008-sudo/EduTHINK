"""
Script de Backup do Projeto Gestão de Salas
Cria um arquivo ZIP com todos os ficheiros importantes do projeto.
"""

import os
import zipfile
from datetime import datetime
from pathlib import Path

# Configurações
PROJECT_ROOT = Path(__file__).parent
BACKUP_FOLDER = PROJECT_ROOT / "backups"
BACKUP_FOLDER.mkdir(exist_ok=True)

# Pastas e ficheiros a incluir
INCLUDE_PATTERNS = [
    "app/**/*.py",
    "app/**/*.html",
    "app/**/*.md",
    "*.txt",
    "*.md",
    "*.db",
]

# Pastas e ficheiros a excluir
EXCLUDE_PATTERNS = [
    "**/__pycache__/**",
    "**/*.pyc",
    "**/.venv/**",
    "**/venv/**",
    "**/node_modules/**",
    "**/*.zip",
    "**/backups/**",
    "**/.git/**",
]


def should_include(file_path: Path, project_root: Path) -> bool:
    """Verifica se o ficheiro deve ser incluído no backup."""
    rel_path = file_path.relative_to(project_root)
    rel_str = str(rel_path)
    
    # Verificar exclusões
    for pattern in EXCLUDE_PATTERNS:
        pattern_clean = pattern.replace("**/", "").replace("/**", "")
        if pattern_clean in rel_str:
            return False
    
    return True


def create_backup():
    """Cria um backup ZIP do projeto."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"projeto_backup_{timestamp}.zip"
    backup_path = BACKUP_FOLDER / backup_name
    
    files_count = 0
    total_size = 0
    
    print(f"🔍 A procurar ficheiros em: {PROJECT_ROOT}")
    print("-" * 50)
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            # Remover diretórios excluídos da pesquisa
            dirs[:] = [d for d in dirs if not any(
                exc in os.path.join(root, d) 
                for exc in ['__pycache__', '.venv', 'venv', 'node_modules', '.git', 'backups']
            )]
            
            for file in files:
                file_path = Path(root) / file
                
                # Ignorar o próprio script de backup e arquivos ZIP
                if file == "backup.py" or file.endswith(".zip"):
                    continue
                
                if should_include(file_path, PROJECT_ROOT):
                    rel_path = file_path.relative_to(PROJECT_ROOT)
                    zipf.write(file_path, rel_path)
                    files_count += 1
                    total_size += file_path.stat().st_size
                    print(f"  ✅ {rel_path}")
    
    print("-" * 50)
    print(f"📦 Backup criado: {backup_path}")
    print(f"📊 Ficheiros: {files_count}")
    print(f"💾 Tamanho: {total_size / 1024:.2f} KB")
    print(f"📁 Pasta de backups: {BACKUP_FOLDER}")
    print("-" * 50)
    print("✅ Backup concluído com sucesso!")
    
    return backup_path


def clean_old_backups(keep_last: int = 5):
    """Mantém apenas os últimos N backups, apaga os antigos."""
    backups = sorted(BACKUP_FOLDER.glob("projeto_backup_*.zip"))
    
    if len(backups) > keep_last:
        to_delete = backups[:-keep_last]
        print(f"\n🧹 A limpar {len(to_delete)} backup(s) antigo(s)...")
        for backup in to_delete:
            backup.unlink()
            print(f"  🗑️ {backup.name}")


if __name__ == "__main__":
    try:
        backup_path = create_backup()
        clean_old_backups(keep_last=5)
        
        print("\n💡 Dica: Agora faz upload deste ficheiro para o Google Drive:")
        print(f"   {backup_path}")
        print("\n   1. Abre https://drive.google.com")
        print(f"   2. Arrasta o ficheiro para o browser")
        print("   OU usa 'Novo' → 'Upload de ficheiro'")
        
    except Exception as e:
        print(f"\n❌ Erro ao criar backup: {e}")
        input("Pressiona Enter para sair...")

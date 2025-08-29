#!/usr/bin/env python3
"""
Script de backup automático do banco de dados PostgreSQL
Academia Amigo do Povo
"""

import os
import sys
import subprocess
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import zipfile
import shutil

# Carregar variáveis de ambiente
load_dotenv()

class DatabaseBackup:
    def __init__(self):
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'postgres')
        self.db_name = os.getenv('DB_NAME', 'academia_amigo_povo')
        
        # Configurações de backup
        self.backup_dir = 'backups'
        self.max_backups = 10  # Manter apenas os últimos 10 backups
        self.backup_format = 'sql'
        
        # Criar diretório de backup se não existir
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def get_backup_filename(self, backup_type='full'):
        """Gera nome do arquivo de backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"academia_backup_{backup_type}_{timestamp}.{self.backup_format}"
    
    def create_full_backup(self):
        """Cria backup completo do banco de dados"""
        print("🔄 Criando backup completo...")
        
        backup_file = os.path.join(self.backup_dir, self.get_backup_filename('full'))
        
        try:
            # Comando pg_dump
            cmd = [
                'pg_dump',
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', self.db_user,
                '-d', self.db_name,
                '-f', backup_file,
                '--verbose',
                '--no-password'
            ]
            
            # Configurar variável de ambiente para senha
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password
            
            # Executar backup
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(backup_file)
                print(f"✅ Backup completo criado: {backup_file}")
                print(f"📊 Tamanho: {self.format_size(file_size)}")
                return backup_file
            else:
                print(f"❌ Erro no backup: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return None
    
    def create_data_backup(self):
        """Cria backup apenas dos dados (sem estrutura)"""
        print("🔄 Criando backup de dados...")
        
        backup_file = os.path.join(self.backup_dir, self.get_backup_filename('data'))
        
        try:
            # Comando pg_dump apenas dados
            cmd = [
                'pg_dump',
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', self.db_user,
                '-d', self.db_name,
                '--data-only',
                '--verbose',
                '--no-password',
                '-f', backup_file
            ]
            
            # Configurar variável de ambiente para senha
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password
            
            # Executar backup
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(backup_file)
                print(f"✅ Backup de dados criado: {backup_file}")
                print(f"📊 Tamanho: {self.format_size(file_size)}")
                return backup_file
            else:
                print(f"❌ Erro no backup: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return None
    
    def create_structure_backup(self):
        """Cria backup apenas da estrutura (sem dados)"""
        print("🔄 Criando backup de estrutura...")
        
        backup_file = os.path.join(self.backup_dir, self.get_backup_filename('structure'))
        
        try:
            # Comando pg_dump apenas estrutura
            cmd = [
                'pg_dump',
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', self.db_user,
                '-d', self.db_name,
                '--schema-only',
                '--verbose',
                '--no-password',
                '-f', backup_file
            ]
            
            # Configurar variável de ambiente para senha
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password
            
            # Executar backup
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(backup_file)
                print(f"✅ Backup de estrutura criado: {backup_file}")
                print(f"📊 Tamanho: {self.format_size(file_size)}")
                return backup_file
            else:
                print(f"❌ Erro no backup: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return None
    
    def create_json_backup(self):
        """Cria backup em formato JSON (para compatibilidade)"""
        print("🔄 Criando backup JSON...")
        
        try:
            from models import SessionLocal, Usuario, Atividade, Turma, Aluno, Presenca
            
            db = SessionLocal()
            
            # Coletar dados
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'usuarios': [],
                'atividades': [],
                'turmas': [],
                'alunos': [],
                'presencas': []
            }
            
            # Usuários
            usuarios = db.query(Usuario).all()
            for usuario in usuarios:
                backup_data['usuarios'].append({
                    'id': usuario.id,
                    'username': usuario.username,
                    'nome': usuario.nome,
                    'nivel': usuario.nivel,
                    'permissoes': usuario.permissoes,
                    'atividade_responsavel': usuario.atividade_responsavel,
                    'ativo': usuario.ativo,
                    'data_criacao': usuario.data_criacao.isoformat() if usuario.data_criacao else None
                })
            
            # Atividades
            atividades = db.query(Atividade).all()
            for atividade in atividades:
                backup_data['atividades'].append({
                    'id': atividade.id,
                    'nome': atividade.nome,
                    'descricao': atividade.descricao,
                    'ativa': atividade.ativa,
                    'total_alunos': atividade.total_alunos,
                    'data_criacao': atividade.data_criacao.isoformat() if atividade.data_criacao else None
                })
            
            # Turmas
            turmas = db.query(Turma).all()
            for turma in turmas:
                backup_data['turmas'].append({
                    'id': turma.id,
                    'nome': turma.nome,
                    'atividade_id': turma.atividade_id,
                    'horario': turma.horario,
                    'dias_semana': turma.dias_semana,
                    'periodo': turma.periodo,
                    'capacidade_maxima': turma.capacidade_maxima,
                    'ativa': turma.ativa,
                    'total_alunos': turma.total_alunos
                })
            
            # Alunos
            alunos = db.query(Aluno).all()
            for aluno in alunos:
                backup_data['alunos'].append({
                    'id': aluno.id,
                    'nome': aluno.nome,
                    'telefone': aluno.telefone,
                    'endereco': aluno.endereco,
                    'email': aluno.email,
                    'data_nascimento': aluno.data_nascimento.isoformat() if aluno.data_nascimento else None,
                    'data_cadastro': aluno.data_cadastro.isoformat() if aluno.data_cadastro else None,
                    'atividade_id': aluno.atividade_id,
                    'turma_id': aluno.turma_id,
                    'status_frequencia': aluno.status_frequencia,
                    'observacoes': aluno.observacoes,
                    'ativo': aluno.ativo
                })
            
            # Presenças
            presencas = db.query(Presenca).all()
            for presenca in presencas:
                backup_data['presencas'].append({
                    'id': presenca.id,
                    'aluno_id': presenca.aluno_id,
                    'data_presenca': presenca.data_presenca.isoformat() if presenca.data_presenca else None,
                    'horario': presenca.horario.isoformat() if presenca.horario else None,
                    'turma_id': presenca.turma_id,
                    'atividade_id': presenca.atividade_id,
                    'status': presenca.status,
                    'observacoes': presenca.observacoes,
                    'tipo_registro': presenca.tipo_registro,
                    'data_registro': presenca.data_registro.isoformat() if presenca.data_registro else None
                })
            
            db.close()
            
            # Salvar arquivo JSON
            backup_file = os.path.join(self.backup_dir, self.get_backup_filename('json'))
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            file_size = os.path.getsize(backup_file)
            print(f"✅ Backup JSON criado: {backup_file}")
            print(f"📊 Tamanho: {self.format_size(file_size)}")
            print(f"📈 Estatísticas:")
            print(f"   - Usuários: {len(backup_data['usuarios'])}")
            print(f"   - Atividades: {len(backup_data['atividades'])}")
            print(f"   - Turmas: {len(backup_data['turmas'])}")
            print(f"   - Alunos: {len(backup_data['alunos'])}")
            print(f"   - Presenças: {len(backup_data['presencas'])}")
            
            return backup_file
            
        except Exception as e:
            print(f"❌ Erro ao criar backup JSON: {e}")
            return None
    
    def create_compressed_backup(self, backup_file):
        """Comprime o arquivo de backup"""
        if not backup_file or not os.path.exists(backup_file):
            return None
        
        try:
            compressed_file = backup_file + '.zip'
            
            with zipfile.ZipFile(compressed_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_file, os.path.basename(backup_file))
            
            # Remover arquivo original
            os.remove(backup_file)
            
            original_size = os.path.getsize(backup_file)
            compressed_size = os.path.getsize(compressed_file)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            print(f"📦 Backup comprimido: {compressed_file}")
            print(f"📊 Compressão: {compression_ratio:.1f}%")
            
            return compressed_file
            
        except Exception as e:
            print(f"❌ Erro ao comprimir backup: {e}")
            return backup_file
    
    def cleanup_old_backups(self):
        """Remove backups antigos mantendo apenas os mais recentes"""
        print("🧹 Limpando backups antigos...")
        
        try:
            # Listar arquivos de backup
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('academia_backup_') and (file.endswith('.sql') or file.endswith('.json') or file.endswith('.zip')):
                    file_path = os.path.join(self.backup_dir, file)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Ordenar por data de modificação (mais recente primeiro)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remover backups antigos
            if len(backup_files) > self.max_backups:
                files_to_remove = backup_files[self.max_backups:]
                for file_path, _ in files_to_remove:
                    os.remove(file_path)
                    print(f"🗑️ Removido: {os.path.basename(file_path)}")
                
                print(f"✅ Mantidos os {self.max_backups} backups mais recentes")
            else:
                print(f"✅ Nenhum backup antigo para remover (total: {len(backup_files)})")
                
        except Exception as e:
            print(f"❌ Erro ao limpar backups antigos: {e}")
    
    def format_size(self, size_bytes):
        """Formata tamanho de arquivo em formato legível"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def list_backups(self):
        """Lista todos os backups existentes"""
        print("📋 Listando backups existentes...")
        
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('academia_backup_'):
                    file_path = os.path.join(self.backup_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    backup_files.append((file, file_size, file_time))
            
            if not backup_files:
                print("📭 Nenhum backup encontrado")
                return
            
            # Ordenar por data (mais recente primeiro)
            backup_files.sort(key=lambda x: x[2], reverse=True)
            
            print(f"{'Arquivo':<40} {'Tamanho':<10} {'Data':<20}")
            print("-" * 70)
            
            for file, size, time in backup_files:
                print(f"{file:<40} {self.format_size(size):<10} {time.strftime('%d/%m/%Y %H:%M:%S'):<20}")
                
        except Exception as e:
            print(f"❌ Erro ao listar backups: {e}")
    
    def restore_backup(self, backup_file):
        """Restaura um backup"""
        print(f"🔄 Restaurando backup: {backup_file}")
        
        if not os.path.exists(backup_file):
            print(f"❌ Arquivo de backup não encontrado: {backup_file}")
            return False
        
        try:
            # Verificar se é arquivo comprimido
            if backup_file.endswith('.zip'):
                import tempfile
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    temp_dir = tempfile.mkdtemp()
                    zipf.extractall(temp_dir)
                    extracted_file = os.path.join(temp_dir, os.listdir(temp_dir)[0])
                    backup_file = extracted_file
            
            # Comando psql para restaurar
            cmd = [
                'psql',
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', self.db_user,
                '-d', self.db_name,
                '-f', backup_file
            ]
            
            # Configurar variável de ambiente para senha
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password
            
            # Executar restauração
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Backup restaurado com sucesso!")
                return True
            else:
                print(f"❌ Erro na restauração: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao restaurar backup: {e}")
            return False

def main():
    """Função principal"""
    print("=== Sistema de Backup PostgreSQL ===")
    print("Academia Amigo do Povo")
    print()
    
    backup_system = DatabaseBackup()
    
    if len(sys.argv) < 2:
        print("Uso: python backup_db.py [comando]")
        print()
        print("Comandos disponíveis:")
        print("  full      - Backup completo")
        print("  data      - Backup apenas dados")
        print("  structure - Backup apenas estrutura")
        print("  json      - Backup em formato JSON")
        print("  list      - Listar backups existentes")
        print("  cleanup   - Limpar backups antigos")
        print("  restore   - Restaurar backup (especificar arquivo)")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'full':
        backup_file = backup_system.create_full_backup()
        if backup_file:
            backup_system.create_compressed_backup(backup_file)
        backup_system.cleanup_old_backups()
        
    elif command == 'data':
        backup_file = backup_system.create_data_backup()
        if backup_file:
            backup_system.create_compressed_backup(backup_file)
        backup_system.cleanup_old_backups()
        
    elif command == 'structure':
        backup_file = backup_system.create_structure_backup()
        if backup_file:
            backup_system.create_compressed_backup(backup_file)
        backup_system.cleanup_old_backups()
        
    elif command == 'json':
        backup_file = backup_system.create_json_backup()
        if backup_file:
            backup_system.create_compressed_backup(backup_file)
        backup_system.cleanup_old_backups()
        
    elif command == 'list':
        backup_system.list_backups()
        
    elif command == 'cleanup':
        backup_system.cleanup_old_backups()
        
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Especificar arquivo de backup para restaurar")
            print("Exemplo: python backup_db.py restore backups/academia_backup_full_20241201_120000.sql")
            return
        
        backup_file = sys.argv[2]
        backup_system.restore_backup(backup_file)
        
    else:
        print(f"❌ Comando desconhecido: {command}")

if __name__ == "__main__":
    main()

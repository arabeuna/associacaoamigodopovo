#!/usr/bin/env python3
"""
Script de configuração do banco de dados PostgreSQL para Academia Amigo do Povo
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
from datetime import datetime
import hashlib

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
    'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
}

def criar_banco_dados():
    """Cria o banco de dados se não existir"""
    try:
        # Conecta ao PostgreSQL sem especificar banco
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verifica se o banco existe
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"Banco de dados '{DB_CONFIG['database']}' criado com sucesso!")
        else:
            print(f"Banco de dados '{DB_CONFIG['database']}' já existe.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")
        return False
    
    return True

def criar_tabelas():
    """Cria todas as tabelas do sistema"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                senha_hash VARCHAR(255) NOT NULL,
                nome VARCHAR(100) NOT NULL,
                nivel VARCHAR(20) NOT NULL CHECK (nivel IN ('admin_master', 'admin', 'usuario')),
                permissoes TEXT[],
                atividade_responsavel VARCHAR(100),
                alunos_atribuidos INTEGER[],
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por VARCHAR(50),
                ultimo_acesso TIMESTAMP
            )
        """)
        
        # Tabela de atividades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atividades (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) UNIQUE NOT NULL,
                descricao TEXT,
                ativa BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por VARCHAR(50),
                professores_vinculados INTEGER[],
                total_alunos INTEGER DEFAULT 0
            )
        """)
        
        # Tabela de turmas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turmas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                atividade_id INTEGER REFERENCES atividades(id),
                horario VARCHAR(20) NOT NULL,
                dias_semana VARCHAR(100),
                periodo VARCHAR(20),
                capacidade_maxima INTEGER DEFAULT 20,
                professor_responsavel INTEGER REFERENCES usuarios(id),
                ativa BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por VARCHAR(50),
                total_alunos INTEGER DEFAULT 0,
                descricao TEXT
            )
        """)
        
        # Tabela de alunos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(200) NOT NULL,
                telefone VARCHAR(20),
                endereco TEXT,
                email VARCHAR(200),
                data_nascimento DATE,
                data_cadastro DATE DEFAULT CURRENT_DATE,
                atividade_id INTEGER REFERENCES atividades(id),
                turma_id INTEGER REFERENCES turmas(id),
                status_frequencia VARCHAR(200),
                observacoes TEXT,
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por VARCHAR(50)
            )
        """)
        
        # Tabela de presenças
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presencas (
                id SERIAL PRIMARY KEY,
                aluno_id INTEGER REFERENCES alunos(id),
                data_presenca DATE NOT NULL,
                horario TIME,
                turma_id INTEGER REFERENCES turmas(id),
                atividade_id INTEGER REFERENCES atividades(id),
                status VARCHAR(10) CHECK (status IN ('P', 'F', 'J')), -- Presente, Faltou, Justificado
                observacoes TEXT,
                tipo_registro VARCHAR(20) DEFAULT 'MANUAL',
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                registrado_por VARCHAR(50)
            )
        """)
        
        # Índices para melhor performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alunos_atividade ON alunos(atividade_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alunos_turma ON alunos(turma_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_presencas_aluno ON presencas(aluno_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_presencas_data ON presencas(data_presenca)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_turmas_atividade ON turmas(atividade_id)")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Tabelas criadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        return False

def inserir_dados_iniciais():
    """Insere dados iniciais do sistema"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Inserir usuários padrão
        usuarios_padrao = [
            ('admin_master', hashlib.sha256('master123'.encode()).hexdigest(), 'Admin Master', 'admin_master', 
             ['gerenciar_colaboradores', 'todas_funcoes'], None, None, True, 'admin_master'),
            ('admin_master2', hashlib.sha256('master456'.encode()).hexdigest(), 'Admin Master 2', 'admin_master',
             ['gerenciar_colaboradores', 'todas_funcoes'], None, None, True, 'admin_master'),
            ('admin_master3', hashlib.sha256('master789'.encode()).hexdigest(), 'Admin Master 3', 'admin_master',
             ['gerenciar_colaboradores', 'todas_funcoes'], None, None, True, 'admin_master'),
            ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'Administrador Geral', 'admin',
             ['cadastrar_alunos', 'editar_alunos', 'excluir_alunos', 'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas'], 
             None, None, True, 'admin_master'),
            ('prof_natacao', hashlib.sha256('natacao123'.encode()).hexdigest(), 'Professor de Natação', 'usuario',
             ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos'], 'Natação', None, True, 'admin_master'),
            ('prof_informatica', hashlib.sha256('info123'.encode()).hexdigest(), 'Professor de Informática', 'usuario',
             ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos'], 'Informática', None, True, 'admin_master')
        ]
        
        for usuario in usuarios_padrao:
            cursor.execute("""
                INSERT INTO usuarios (username, senha_hash, nome, nivel, permissoes, atividade_responsavel, alunos_atribuidos, ativo, criado_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, usuario)
        
        # Inserir atividades do JSON
        with open('atividades_sistema.json', 'r', encoding='utf-8') as f:
            atividades = json.load(f)
        
        for nome_atividade, dados in atividades.items():
            cursor.execute("""
                INSERT INTO atividades (nome, descricao, ativa, criado_por, total_alunos)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (nome) DO NOTHING
            """, (dados['nome'], dados['descricao'], dados['ativa'], dados['criado_por'], dados['total_alunos']))
        
        # Inserir turmas do JSON
        with open('turmas_sistema.json', 'r', encoding='utf-8') as f:
            turmas = json.load(f)
        
        for turma_id, dados in turmas.items():
            # Buscar ID da atividade
            cursor.execute("SELECT id FROM atividades WHERE nome = %s", (dados['atividade'],))
            atividade_result = cursor.fetchone()
            if atividade_result:
                atividade_id = atividade_result[0]
                
                cursor.execute("""
                    INSERT INTO turmas (nome, atividade_id, horario, dias_semana, periodo, capacidade_maxima, 
                                      professor_responsavel, ativa, criado_por, total_alunos, descricao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (dados['nome'], atividade_id, dados['horario'], dados['dias_semana'], 
                     dados['periodo'], dados['capacidade_maxima'], None, dados['ativa'], 
                     dados['criado_por'], dados['total_alunos'], dados['descricao']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Dados iniciais inseridos com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao inserir dados iniciais: {e}")
        return False

def migrar_alunos():
    """Migra alunos do JSON para o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        with open('dados_alunos.json', 'r', encoding='utf-8') as f:
            alunos = json.load(f)
        
        for aluno in alunos:
            # Buscar IDs das atividades e turmas
            atividade_id = None
            turma_id = None
            
            if aluno.get('atividade'):
                cursor.execute("SELECT id FROM atividades WHERE nome = %s", (aluno['atividade'],))
                atividade_result = cursor.fetchone()
                if atividade_result:
                    atividade_id = atividade_result[0]
            
            if aluno.get('turma') and aluno['turma'] != 'A definir':
                cursor.execute("SELECT id FROM turmas WHERE horario = %s AND atividade_id = %s", 
                             (aluno['turma'], atividade_id))
                turma_result = cursor.fetchone()
                if turma_result:
                    turma_id = turma_result[0]
            
            # Converter data de nascimento
            data_nascimento = None
            if aluno.get('data_nascimento'):
                try:
                    data_nascimento = datetime.strptime(aluno['data_nascimento'], '%d/%m/%Y').date()
                except:
                    pass
            
            # Converter data de cadastro
            data_cadastro = None
            if aluno.get('data_cadastro'):
                try:
                    if len(aluno['data_cadastro']) == 8:  # formato dd/mm/yy
                        data_cadastro = datetime.strptime(aluno['data_cadastro'], '%d/%m/%y').date()
                    else:  # formato dd/mm/yyyy
                        data_cadastro = datetime.strptime(aluno['data_cadastro'], '%d/%m/%Y').date()
                except:
                    data_cadastro = datetime.now().date()
            
            cursor.execute("""
                INSERT INTO alunos (nome, telefone, endereco, email, data_nascimento, data_cadastro,
                                  atividade_id, turma_id, status_frequencia, observacoes, criado_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (aluno['nome'], aluno.get('telefone'), aluno.get('endereco'), aluno.get('email'),
                 data_nascimento, data_cadastro, atividade_id, turma_id, 
                 aluno.get('status_frequencia'), aluno.get('observacoes'), 'sistema_migracao'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"Migrados {len(alunos)} alunos com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao migrar alunos: {e}")
        return False

def migrar_presencas():
    """Migra dados de presença do CSV para o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        import csv
        with open('presencas_detalhadas.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Buscar aluno
                cursor.execute("SELECT id FROM alunos WHERE nome = %s", (row['NOME'],))
                aluno_result = cursor.fetchone()
                if not aluno_result:
                    continue
                
                aluno_id = aluno_result[0]
                
                # Buscar atividade
                atividade_id = None
                if row.get('ATIVIDADE'):
                    cursor.execute("SELECT id FROM atividades WHERE nome = %s", (row['ATIVIDADE'],))
                    atividade_result = cursor.fetchone()
                    if atividade_result:
                        atividade_id = atividade_result[0]
                
                # Buscar turma
                turma_id = None
                if row.get('TURMA') and row['TURMA'] != 'A definir':
                    cursor.execute("SELECT id FROM turmas WHERE horario = %s", (row['TURMA'],))
                    turma_result = cursor.fetchone()
                    if turma_result:
                        turma_id = turma_result[0]
                
                # Converter data
                data_presenca = None
                if row.get('DATA'):
                    try:
                        data_presenca = datetime.strptime(row['DATA'], '%d/%m/%Y').date()
                    except:
                        continue
                
                # Converter horário
                horario = None
                if row.get('HORARIO'):
                    try:
                        horario = datetime.strptime(row['HORARIO'], '%H:%M').time()
                    except:
                        pass
                
                cursor.execute("""
                    INSERT INTO presencas (aluno_id, data_presenca, horario, turma_id, atividade_id, 
                                         status, observacoes, tipo_registro, registrado_por)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (aluno_id, data_presenca, horario, turma_id, atividade_id,
                     row.get('STATUS'), row.get('OBSERVACOES'), row.get('TIPO', 'MANUAL'), 'sistema_migracao'))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Dados de presença migrados com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao migrar presenças: {e}")
        return False

def main():
    """Função principal para configurar o banco de dados"""
    print("=== Configuração do Banco de Dados PostgreSQL ===")
    print("Academia Amigo do Povo")
    print()
    
    # Verificar se PostgreSQL está instalado
    try:
        import psycopg2
        print("✓ psycopg2 encontrado")
    except ImportError:
        print("✗ psycopg2 não encontrado. Instale com: pip install psycopg2-binary")
        return False
    
    # Criar banco de dados
    print("\n1. Criando banco de dados...")
    if not criar_banco_dados():
        return False
    
    # Criar tabelas
    print("\n2. Criando tabelas...")
    if not criar_tabelas():
        return False
    
    # Inserir dados iniciais
    print("\n3. Inserindo dados iniciais...")
    if not inserir_dados_iniciais():
        return False
    
    # Migrar alunos
    print("\n4. Migrando alunos...")
    if not migrar_alunos():
        return False
    
    # Migrar presenças
    print("\n5. Migrando dados de presença...")
    if not migrar_presencas():
        return False
    
    print("\n=== Configuração concluída com sucesso! ===")
    print("O banco de dados PostgreSQL está pronto para uso.")
    print("\nPróximos passos:")
    print("1. Instale as dependências: pip install psycopg2-binary sqlalchemy")
    print("2. Configure as variáveis de ambiente do banco de dados")
    print("3. Execute o script de atualização do app.py")
    
    return True

if __name__ == "__main__":
    main()

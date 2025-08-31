#!/usr/bin/env python3
"""
Script de configuração do banco de dados SQLite para Academia Amigo do Povo
"""

import os
import sqlite3
import json
from datetime import datetime
import hashlib

# Configurações do banco de dados SQLite
DB_FILE = 'academia_amigo_povo.db'

def criar_banco_dados():
    """Cria o banco de dados SQLite se não existir"""
    try:
        # Conecta ao SQLite (cria o arquivo se não existir)
        conn = sqlite3.connect(DB_FILE)
        print(f"Banco de dados SQLite '{DB_FILE}' criado/conectado com sucesso!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")
        return False

def criar_tabelas():
    """Cria todas as tabelas do sistema"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                nome TEXT NOT NULL,
                nivel TEXT NOT NULL CHECK (nivel IN ('admin_master', 'admin', 'usuario')),
                permissoes TEXT,
                atividade_responsavel TEXT,
                alunos_atribuidos TEXT,
                ativo INTEGER DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por TEXT,
                ultimo_acesso TIMESTAMP
            )
        """)
        
        # Tabela de atividades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT,
                ativa INTEGER DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por TEXT,
                professores_vinculados TEXT,
                total_alunos INTEGER DEFAULT 0
            )
        """)
        
        # Tabela de turmas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turmas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                atividade_id INTEGER REFERENCES atividades(id),
                horario TEXT NOT NULL,
                dias_semana TEXT,
                periodo TEXT,
                capacidade_maxima INTEGER DEFAULT 20,
                professor_responsavel INTEGER REFERENCES usuarios(id),
                ativa INTEGER DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por TEXT,
                total_alunos INTEGER DEFAULT 0,
                descricao TEXT
            )
        """)
        
        # Tabela de alunos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                endereco TEXT,
                email TEXT,
                data_nascimento DATE,
                data_cadastro DATE DEFAULT CURRENT_DATE,
                atividade_id INTEGER REFERENCES atividades(id),
                turma_id INTEGER REFERENCES turmas(id),
                status_frequencia TEXT,
                observacoes TEXT,
                ativo INTEGER DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por TEXT
            )
        """)
        
        # Tabela de presenças
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presencas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER REFERENCES alunos(id),
                data_presenca DATE NOT NULL,
                horario TIME,
                turma_id INTEGER REFERENCES turmas(id),
                atividade_id INTEGER REFERENCES atividades(id),
                status TEXT CHECK (status IN ('P', 'F', 'J')),
                observacoes TEXT,
                tipo_registro TEXT DEFAULT 'MANUAL',
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                registrado_por TEXT
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
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Inserir usuários padrão
        usuarios_padrao = [
            ('admin_master', hashlib.sha256('master123'.encode()).hexdigest(), 'Admin Master', 'admin_master', 
             '["gerenciar_colaboradores", "todas_funcoes"]', None, None, 1, 'admin_master'),
            ('admin_master2', hashlib.sha256('master456'.encode()).hexdigest(), 'Admin Master 2', 'admin_master',
             '["gerenciar_colaboradores", "todas_funcoes"]', None, None, 1, 'admin_master'),
            ('admin_master3', hashlib.sha256('master789'.encode()).hexdigest(), 'Admin Master 3', 'admin_master',
             '["gerenciar_colaboradores", "todas_funcoes"]', None, None, 1, 'admin_master'),
            ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'Administrador Geral', 'admin',
             '["cadastrar_alunos", "editar_alunos", "excluir_alunos", "ver_todos_alunos", "gerar_relatorios", "backup_planilhas"]', 
             None, None, 1, 'admin_master'),
            ('prof_natacao', hashlib.sha256('natacao123'.encode()).hexdigest(), 'Professor de Natação', 'usuario',
             '["consultar_meus_alunos", "gerenciar_frequencia_meus_alunos"]', 'Natação', None, 1, 'admin_master'),
            ('prof_informatica', hashlib.sha256('info123'.encode()).hexdigest(), 'Professor de Informática', 'usuario',
             '["consultar_meus_alunos", "gerenciar_frequencia_meus_alunos"]', 'Informática', None, 1, 'admin_master')
        ]
        
        for usuario in usuarios_padrao:
            cursor.execute("""
                INSERT OR IGNORE INTO usuarios (username, senha_hash, nome, nivel, permissoes, atividade_responsavel, alunos_atribuidos, ativo, criado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, usuario)
        
        # Inserir atividades do JSON
        if os.path.exists('atividades_sistema.json'):
            with open('atividades_sistema.json', 'r', encoding='utf-8') as f:
                atividades = json.load(f)
            
            for nome_atividade, dados in atividades.items():
                cursor.execute("""
                    INSERT OR IGNORE INTO atividades (nome, descricao, ativa, criado_por, total_alunos)
                    VALUES (?, ?, ?, ?, ?)
                """, (dados['nome'], dados['descricao'], dados['ativa'], dados['criado_por'], dados['total_alunos']))
        
        # Inserir turmas do JSON
        if os.path.exists('turmas_sistema.json'):
            with open('turmas_sistema.json', 'r', encoding='utf-8') as f:
                turmas = json.load(f)
            
            for turma_id, dados in turmas.items():
                # Buscar ID da atividade
                cursor.execute("SELECT id FROM atividades WHERE nome = ?", (dados['atividade'],))
                atividade_result = cursor.fetchone()
                if atividade_result:
                    atividade_id = atividade_result[0]
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO turmas (nome, atividade_id, horario, dias_semana, periodo, capacidade_maxima, 
                                          professor_responsavel, ativa, criado_por, total_alunos, descricao)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        if not os.path.exists('dados_alunos.json'):
            print("Arquivo dados_alunos.json não encontrado. Pulando migração de alunos.")
            return True
        
        with open('dados_alunos.json', 'r', encoding='utf-8') as f:
            alunos = json.load(f)
        
        for aluno in alunos:
            # Buscar IDs das atividades e turmas
            atividade_id = None
            turma_id = None
            
            if aluno.get('atividade'):
                cursor.execute("SELECT id FROM atividades WHERE nome = ?", (aluno['atividade'],))
                atividade_result = cursor.fetchone()
                if atividade_result:
                    atividade_id = atividade_result[0]
            
            if aluno.get('turma') and aluno['turma'] != 'A definir':
                cursor.execute("SELECT id FROM turmas WHERE horario = ? AND atividade_id = ?", 
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        if not os.path.exists('presencas_detalhadas.csv'):
            print("Arquivo presencas_detalhadas.csv não encontrado. Pulando migração de presenças.")
            return True
        
        import csv
        with open('presencas_detalhadas.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Buscar aluno
                cursor.execute("SELECT id FROM alunos WHERE nome = ?", (row['NOME'],))
                aluno_result = cursor.fetchone()
                if not aluno_result:
                    continue
                
                aluno_id = aluno_result[0]
                
                # Buscar atividade
                atividade_id = None
                if row.get('ATIVIDADE'):
                    cursor.execute("SELECT id FROM atividades WHERE nome = ?", (row['ATIVIDADE'],))
                    atividade_result = cursor.fetchone()
                    if atividade_result:
                        atividade_id = atividade_result[0]
                
                # Buscar turma
                turma_id = None
                if row.get('TURMA') and row['TURMA'] != 'A definir':
                    cursor.execute("SELECT id FROM turmas WHERE horario = ?", (row['TURMA'],))
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
                        horario = row['HORARIO']  # Manter como string
                    except:
                        pass
                
                cursor.execute("""
                    INSERT INTO presencas (aluno_id, data_presenca, horario, turma_id, atividade_id, 
                                         status, observacoes, tipo_registro, registrado_por)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    print("=== Configuração do Banco de Dados SQLite ===")
    print("Academia Amigo do Povo")
    print()
    
    # Criar banco de dados
    print("1. Criando banco de dados...")
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
    print(f"O banco de dados SQLite '{DB_FILE}' está pronto para uso.")
    print("\nPróximos passos:")
    print("1. Configure o app.py para usar SQLite")
    print("2. Execute o sistema: python app.py")
    print("\nCredenciais de acesso:")
    print("- Admin Master: admin_master / master123")
    print("- Admin: admin / admin123")
    print("- Professor Natação: prof_natacao / natacao123")
    print("- Professor Informática: prof_informatica / info123")
    
    return True

if __name__ == "__main__":
    main()

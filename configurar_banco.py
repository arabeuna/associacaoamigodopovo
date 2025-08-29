#!/usr/bin/env python3
"""
Script para configurar o banco de dados PostgreSQL e migrar dados dos arquivos JSON
Academia Amigo do Povo
"""

import os
import json
import psycopg2
from datetime import datetime
from sqlalchemy import create_engine, text
from models import Base, SessionLocal, engine

# Configurações do banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'postgres',
    'database': 'academia_amigo_povo'
}

def criar_banco_dados():
    """Cria o banco de dados se não existir"""
    try:
        # Conectar ao PostgreSQL sem especificar banco
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verificar se o banco existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"✅ Banco de dados '{DB_CONFIG['database']}' criado com sucesso!")
        else:
            print(f"✅ Banco de dados '{DB_CONFIG['database']}' já existe!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar banco de dados: {e}")
        return False

def criar_tabelas():
    """Cria todas as tabelas no banco de dados"""
    try:
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def migrar_usuarios():
    """Migra usuários do arquivo JSON para PostgreSQL"""
    try:
        if not os.path.exists('usuarios_sistema.json'):
            print("⚠️ Arquivo usuarios_sistema.json não encontrado")
            return False
        
        with open('usuarios_sistema.json', 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
        
        db = SessionLocal()
        usuarios_migrados = 0
        
        for username, dados in usuarios.items():
            # Verificar se usuário já existe
            usuario_existente = db.execute(
                text("SELECT id FROM usuarios WHERE username = :username"),
                {"username": username}
            ).fetchone()
            
            if not usuario_existente:
                db.execute(text("""
                    INSERT INTO usuarios (username, senha_hash, nome, nivel, permissoes, 
                                        atividade_responsavel, alunos_atribuidos, ativo, 
                                        data_criacao, criado_por)
                    VALUES (:username, :senha_hash, :nome, :nivel, :permissoes, 
                           :atividade_responsavel, :alunos_atribuidos, :ativo, 
                           :data_criacao, :criado_por)
                """), {
                    "username": username,
                    "senha_hash": dados.get('senha', ''),
                    "nome": dados.get('nome', ''),
                    "nivel": dados.get('nivel', 'usuario'),
                    "permissoes": dados.get('permissoes', []),
                    "atividade_responsavel": dados.get('atividade_responsavel'),
                    "alunos_atribuidos": dados.get('alunos_atribuidos', []),
                    "ativo": dados.get('ativo', True),
                    "data_criacao": datetime.now(),
                    "criado_por": dados.get('criado_por', 'sistema')
                })
                usuarios_migrados += 1
                print(f"Usuário {username} migrado")
            else:
                print(f"Usuário {username} já existe")
        
        db.commit()
        print(f"✅ {usuarios_migrados} usuários migrados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao migrar usuários: {e}")
        return False
    finally:
        db.close()

def migrar_atividades():
    """Migra atividades do arquivo JSON para PostgreSQL"""
    try:
        if not os.path.exists('atividades_sistema.json'):
            print("⚠️ Arquivo atividades_sistema.json não encontrado")
            return False
        
        with open('atividades_sistema.json', 'r', encoding='utf-8') as f:
            atividades = json.load(f)
        
        db = SessionLocal()
        atividades_migradas = 0
        
        for nome, dados in atividades.items():
            # Verificar se atividade já existe
            atividade_existente = db.execute(
                text("SELECT id FROM atividades WHERE nome = :nome"),
                {"nome": nome}
            ).fetchone()
            
            if not atividade_existente:
                db.execute(text("""
                    INSERT INTO atividades (nome, descricao, ativa, data_criacao, 
                                          criado_por, professores_vinculados, total_alunos)
                    VALUES (:nome, :descricao, :ativa, :data_criacao, 
                           :criado_por, :professores_vinculados, :total_alunos)
                """), {
                    "nome": nome,
                    "descricao": dados.get('descricao', ''),
                    "ativa": dados.get('ativa', True),
                    "data_criacao": datetime.now(),
                    "criado_por": dados.get('criado_por', 'sistema'),
                    "professores_vinculados": dados.get('professores_vinculados', []),
                    "total_alunos": dados.get('total_alunos', 0)
                })
                atividades_migradas += 1
                print(f"Atividade {nome} migrada")
            else:
                print(f"Atividade {nome} já existe")
        
        db.commit()
        print(f"✅ {atividades_migradas} atividades migradas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao migrar atividades: {e}")
        return False
    finally:
        db.close()

def migrar_alunos():
    """Migra alunos do arquivo JSON para PostgreSQL"""
    try:
        if not os.path.exists('dados_alunos.json'):
            print("⚠️ Arquivo dados_alunos.json não encontrado")
            return False
        
        with open('dados_alunos.json', 'r', encoding='utf-8') as f:
            alunos = json.load(f)
        
        db = SessionLocal()
        alunos_migrados = 0
        
        for aluno_dados in alunos:
            # Buscar IDs das atividades
            atividade_id = None
            if aluno_dados.get('atividade'):
                atividade = db.execute(
                    text("SELECT id FROM atividades WHERE nome = :nome"),
                    {"nome": aluno_dados['atividade']}
                ).fetchone()
                if atividade:
                    atividade_id = atividade[0]
            
            # Converter data de nascimento
            data_nascimento = None
            if aluno_dados.get('data_nascimento'):
                try:
                    if '/' in aluno_dados['data_nascimento']:
                        data_nascimento = datetime.strptime(aluno_dados['data_nascimento'], '%d/%m/%Y').date()
                    else:
                        data_nascimento = datetime.strptime(aluno_dados['data_nascimento'], '%Y-%m-%d').date()
                except:
                    pass
            
            # Converter data de cadastro
            data_cadastro = None
            if aluno_dados.get('data_cadastro'):
                try:
                    if '/' in aluno_dados['data_cadastro']:
                        data_cadastro = datetime.strptime(aluno_dados['data_cadastro'], '%d/%m/%Y').date()
                    else:
                        data_cadastro = datetime.strptime(aluno_dados['data_cadastro'], '%Y-%m-%d').date()
                except:
                    data_cadastro = datetime.now().date()
            
            # Verificar se aluno já existe
            aluno_existente = db.execute(
                text("SELECT id FROM alunos WHERE nome = :nome"),
                {"nome": aluno_dados['nome']}
            ).fetchone()
            
            if not aluno_existente:
                db.execute(text("""
                    INSERT INTO alunos (nome, telefone, endereco, email, data_nascimento,
                                      data_cadastro, atividade_id, turma_id, status_frequencia,
                                      observacoes, ativo, data_criacao, criado_por)
                    VALUES (:nome, :telefone, :endereco, :email, :data_nascimento,
                           :data_cadastro, :atividade_id, :turma_id, :status_frequencia,
                           :observacoes, :ativo, :data_criacao, :criado_por)
                """), {
                    "nome": aluno_dados['nome'],
                    "telefone": aluno_dados.get('telefone'),
                    "endereco": aluno_dados.get('endereco'),
                    "email": aluno_dados.get('email'),
                    "data_nascimento": data_nascimento,
                    "data_cadastro": data_cadastro,
                    "atividade_id": atividade_id,
                    "turma_id": None,  # Será atualizado depois
                    "status_frequencia": aluno_dados.get('status_frequencia'),
                    "observacoes": aluno_dados.get('observacoes'),
                    "ativo": True,
                    "data_criacao": datetime.now(),
                    "criado_por": 'sistema_migracao'
                })
                alunos_migrados += 1
                print(f"Aluno {aluno_dados['nome']} migrado")
            else:
                print(f"Aluno {aluno_dados['nome']} já existe")
        
        db.commit()
        print(f"✅ {alunos_migrados} alunos migrados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao migrar alunos: {e}")
        return False
    finally:
        db.close()

def migrar_presencas():
    """Migra presenças dos arquivos CSV para PostgreSQL"""
    try:
        db = SessionLocal()
        presencas_migradas = 0
        
        # Migrar presenças manuais
        if os.path.exists('presencas_manuais.csv'):
            import csv
            with open('presencas_manuais.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Buscar aluno
                    aluno = db.execute(
                        text("SELECT id FROM alunos WHERE nome = :nome"),
                        {"nome": row['NOME']}
                    ).fetchone()
                    
                    if aluno:
                        # Converter data
                        data_presenca = None
                        try:
                            data_presenca = datetime.strptime(row['DATA'], '%d/%m/%Y').date()
                        except:
                            continue
                        
                        # Verificar se presença já existe
                        presenca_existente = db.execute(
                            text("SELECT id FROM presencas WHERE aluno_id = :aluno_id AND data_presenca = :data"),
                            {"aluno_id": aluno[0], "data": data_presenca}
                        ).fetchone()
                        
                        if not presenca_existente:
                            db.execute(text("""
                                INSERT INTO presencas (aluno_id, data_presenca, horario, status, 
                                                     tipo_registro, data_registro, registrado_por)
                                VALUES (:aluno_id, :data_presenca, :horario, :status, 
                                       :tipo_registro, :data_registro, :registrado_por)
                            """), {
                                "aluno_id": aluno[0],
                                "data_presenca": data_presenca,
                                "horario": row.get('HORARIO'),
                                "status": 'P',
                                "tipo_registro": 'MANUAL',
                                "data_registro": datetime.now(),
                                "registrado_por": 'sistema_migracao'
                            })
                            presencas_migradas += 1
        
        db.commit()
        print(f"✅ {presencas_migradas} presenças migradas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao migrar presenças: {e}")
        return False
    finally:
        db.close()

def verificar_migracao():
    """Verifica se a migração foi bem-sucedida"""
    try:
        db = SessionLocal()
        
        # Contar registros
        total_usuarios = db.execute(text("SELECT COUNT(*) FROM usuarios")).fetchone()[0]
        total_atividades = db.execute(text("SELECT COUNT(*) FROM atividades")).fetchone()[0]
        total_alunos = db.execute(text("SELECT COUNT(*) FROM alunos")).fetchone()[0]
        total_presencas = db.execute(text("SELECT COUNT(*) FROM presencas")).fetchone()[0]
        
        print("\n📊 RESUMO DA MIGRAÇÃO:")
        print(f"   Usuários: {total_usuarios}")
        print(f"   Atividades: {total_atividades}")
        print(f"   Alunos: {total_alunos}")
        print(f"   Presenças: {total_presencas}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar migração: {e}")
        return False
    finally:
        db.close()

def main():
    """Função principal"""
    print("=== CONFIGURAÇÃO DO BANCO DE DADOS ===")
    print("Academia Amigo do Povo")
    print()
    
    # 1. Criar banco de dados
    print("1. Criando banco de dados...")
    if not criar_banco_dados():
        print("❌ Falha ao criar banco de dados")
        return False
    
    # 2. Criar tabelas
    print("\n2. Criando tabelas...")
    if not criar_tabelas():
        print("❌ Falha ao criar tabelas")
        return False
    
    # 3. Migrar dados
    print("\n3. Migrando dados...")
    migrar_usuarios()
    migrar_atividades()
    migrar_alunos()
    migrar_presencas()
    
    # 4. Verificar migração
    print("\n4. Verificando migração...")
    verificar_migracao()
    
    print("\n✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("\nPróximos passos:")
    print("1. Execute o sistema com: python app.py")
    print("2. Teste as funcionalidades")
    print("3. Os dados agora estão no banco PostgreSQL")
    
    return True

if __name__ == "__main__":
    main()


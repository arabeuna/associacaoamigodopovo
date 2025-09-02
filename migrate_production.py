#!/usr/bin/env python3
"""
Script de migração para produção
Executa apenas as operações seguras necessárias para sincronizar o banco
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text
from models import SessionLocal, Base, engine, Usuario, Atividade, Turma, Aluno, Presenca
import json
from datetime import datetime

# Carregar variáveis de ambiente de produção
load_dotenv('.env.production')

def verificar_conexao_db():
    """Verifica se a conexão com o banco está funcionando"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Conexão com banco de dados OK")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def verificar_e_adicionar_colunas():
    """Verifica e adiciona colunas que possam estar faltando"""
    try:
        # Conectar ao banco
        connection = engine.connect()
        
        # Verificar se a tabela usuarios existe e suas colunas
        try:
            # Tentar uma consulta simples para verificar a estrutura
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios'"))
            colunas_existentes = [row[0] for row in result]
            
            # Colunas necessárias que podem estar faltando
            colunas_necessarias = {
                'permissoes': 'VARCHAR(500)',
                'atividade_responsavel': 'VARCHAR(100)',
                'alunos_atribuidos': 'VARCHAR(500)',
                'criado_por': 'VARCHAR(50)',
                'ultimo_acesso': 'TIMESTAMP'
            }
            
            # Adicionar colunas que estão faltando
            for coluna, tipo in colunas_necessarias.items():
                if coluna not in colunas_existentes:
                    try:
                        connection.execute(text(f"ALTER TABLE usuarios ADD COLUMN {coluna} {tipo}"))
                        print(f"✅ Coluna '{coluna}' adicionada à tabela usuarios")
                    except Exception as e:
                        print(f"⚠️ Erro ao adicionar coluna '{coluna}': {e}")
                        
        except Exception as e:
            print(f"⚠️ Não foi possível verificar colunas (pode ser SQLite): {e}")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar colunas: {e}")
        return False

def criar_tabelas_se_necessario():
    """Cria tabelas se não existirem"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas verificadas/criadas")
        
        # Verificar e adicionar colunas que possam estar faltando
        verificar_e_adicionar_colunas()
        
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def migrar_usuarios_basicos():
    """Migra apenas usuários essenciais se não existirem"""
    db = SessionLocal()
    try:
        # Verificar se já existem usuários usando SQL direto para evitar problemas de ORM
        try:
            result = db.execute(text("SELECT COUNT(*) FROM usuarios"))
            usuarios_existentes = result.scalar()
            if usuarios_existentes > 0:
                print(f"✅ {usuarios_existentes} usuários já existem")
                return True
        except Exception as e:
            print(f"⚠️ Erro ao verificar usuários existentes: {e}")
            # Continuar com a criação se não conseguir verificar
            
        # Criar usuários básicos
        usuarios_basicos = {
            'admin_master': {
                'senha_hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                'nome': 'Admin Master',
                'nivel': 'admin_master',
                'permissoes': json.dumps(['gerenciar_colaboradores', 'todas_funcoes']),
                'ativo': True
            },
            'admin': {
                'senha_hash': 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
                'nome': 'Administrador Geral', 
                'nivel': 'admin',
                'permissoes': json.dumps(['cadastrar_alunos', 'editar_alunos', 'excluir_alunos', 'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas']),
                'ativo': True,
                'criado_por': 'admin_master'
            }
        }
        
        for username, dados in usuarios_basicos.items():
            try:
                # Usar SQL direto para inserir usuários
                sql = text("""
                    INSERT INTO usuarios (username, senha_hash, nome, nivel, permissoes, ativo, criado_por, data_criacao)
                    VALUES (:username, :senha_hash, :nome, :nivel, :permissoes, :ativo, :criado_por, :data_criacao)
                """)
                
                db.execute(sql, {
                    'username': username,
                    'senha_hash': dados['senha_hash'],
                    'nome': dados['nome'],
                    'nivel': dados['nivel'],
                    'permissoes': dados['permissoes'],
                    'ativo': dados['ativo'],
                    'criado_por': dados.get('criado_por', 'sistema'),
                    'data_criacao': datetime.now()
                })
                print(f"✅ Usuário '{username}' criado")
                
            except Exception as e:
                print(f"⚠️ Erro ao criar usuário '{username}': {e}")
                continue
            
        db.commit()
        print(f"✅ Usuários básicos processados")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao migrar usuários: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def migrar_atividades_basicas():
    """Migra atividades básicas se não existirem"""
    db = SessionLocal()
    try:
        # Verificar se já existem atividades
        atividades_existentes = db.query(Atividade).count()
        if atividades_existentes > 0:
            print(f"✅ {atividades_existentes} atividades já existem")
            return True
            
        # Criar atividades básicas
        atividades_basicas = {
            'Natação': {
                'descricao': 'Aulas de natação para todas as idades',
                'ativa': True
            },
            'Informática': {
                'descricao': 'Curso de informática básica e avançada', 
                'ativa': True
            }
        }
        
        for nome, dados in atividades_basicas.items():
            nova_atividade = Atividade(
                nome=nome,
                descricao=dados['descricao'],
                ativa=dados['ativa'],
                criado_por='sistema',
                data_criacao=datetime.now()
            )
            db.add(nova_atividade)
            
        db.commit()
        print("✅ Atividades básicas criadas")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao migrar atividades: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def migrar_alunos_existentes():
    """Migra alunos do arquivo JSON local para o banco de produção (se existir)"""
    db = SessionLocal()
    try:
        # Verificar se já existem alunos
        alunos_existentes = db.query(Aluno).count()
        if alunos_existentes > 0:
            print(f"✅ {alunos_existentes} alunos já existem no banco")
            return True
            
        # Tentar carregar alunos do arquivo JSON local
        arquivo_alunos = 'dados_alunos.json'
        if not os.path.exists(arquivo_alunos):
            print("⚠️ Arquivo dados_alunos.json não encontrado - pulando migração de alunos")
            return True
            
        with open(arquivo_alunos, 'r', encoding='utf-8') as f:
            dados_alunos = json.load(f)
            
        if not dados_alunos:
            print("⚠️ Nenhum aluno encontrado no arquivo JSON")
            return True
            
        # Migrar alunos
        import uuid
        alunos_migrados = 0
        
        for aluno_data in dados_alunos:
            try:
                # Buscar atividade e turma por nome
                atividade = None
                if aluno_data.get('atividade'):
                    atividade = db.query(Atividade).filter(
                        Atividade.nome == aluno_data['atividade']
                    ).first()
                    
                turma = None
                if aluno_data.get('turma'):
                    turma = db.query(Turma).filter(
                        Turma.nome == aluno_data['turma']
                    ).first()
                
                # Converter data de nascimento
                data_nascimento = None
                if aluno_data.get('data_nascimento'):
                    try:
                        data_nascimento = datetime.strptime(
                            aluno_data['data_nascimento'], '%Y-%m-%d'
                        ).date()
                    except:
                        pass
                        
                # Gerar ID único se não existir
                id_unico = aluno_data.get('id_unico') or str(uuid.uuid4())[:8]
                
                # Criar aluno
                novo_aluno = Aluno(
                    id_unico=id_unico,
                    nome=aluno_data.get('nome', ''),
                    telefone=aluno_data.get('telefone', ''),
                    endereco=aluno_data.get('endereco', ''),
                    email=aluno_data.get('email', ''),
                    data_nascimento=data_nascimento,
                    data_cadastro=datetime.now().date(),
                    titulo_eleitor=aluno_data.get('titulo_eleitor', ''),
                    atividade_id=atividade.id if atividade else None,
                    turma_id=turma.id if turma else None,
                    status_frequencia=aluno_data.get('status_frequencia', 'Ativo'),
                    observacoes=aluno_data.get('observacoes', ''),
                    ativo=aluno_data.get('ativo', True),
                    criado_por='migração_produção',
                    data_criacao=datetime.now()
                )
                
                db.add(novo_aluno)
                alunos_migrados += 1
                
            except Exception as e:
                print(f"⚠️ Erro ao migrar aluno {aluno_data.get('nome', 'desconhecido')}: {e}")
                continue
                
        db.commit()
        print(f"✅ {alunos_migrados} alunos migrados com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao migrar alunos: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def executar_migracao_producao():
    """Executa migração segura para produção"""
    print("🚀 Iniciando migração para produção...")
    print("=" * 50)
    
    # 1. Verificar conexão
    if not verificar_conexao_db():
        return False
        
    # 2. Criar tabelas
    if not criar_tabelas_se_necessario():
        return False
        
    # 3. Migrar usuários básicos
    if not migrar_usuarios_basicos():
        return False
        
    # 4. Migrar atividades básicas
    if not migrar_atividades_basicas():
        return False
        
    # 5. Migrar alunos existentes
    if not migrar_alunos_existentes():
        return False
        
    print("=" * 50)
    print("✅ Migração para produção concluída com sucesso!")
    return True

if __name__ == "__main__":
    success = executar_migracao_producao()
    sys.exit(0 if success else 1)
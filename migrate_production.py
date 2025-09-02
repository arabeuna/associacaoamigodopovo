#!/usr/bin/env python3
"""
Script de migração para produção
Executa apenas as operações seguras necessárias para sincronizar o banco
"""

import os
import sys
from dotenv import load_dotenv
from models import SessionLocal, Base, engine, Usuario, Atividade, Turma, Aluno, Presenca
from sqlalchemy import text
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

def criar_tabelas_se_necessario():
    """Cria tabelas se não existirem"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas verificadas/criadas")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def migrar_usuarios_basicos():
    """Migra apenas usuários essenciais se não existirem"""
    db = SessionLocal()
    try:
        # Verificar se já existem usuários
        usuarios_existentes = db.query(Usuario).count()
        if usuarios_existentes > 0:
            print(f"✅ {usuarios_existentes} usuários já existem")
            return True
            
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
            novo_usuario = Usuario(
                username=username,
                senha_hash=dados['senha_hash'],
                nome=dados['nome'],
                nivel=dados['nivel'],
                permissoes=dados['permissoes'],
                ativo=dados['ativo'],
                criado_por=dados.get('criado_por', 'sistema'),
                data_criacao=datetime.now()
            )
            db.add(novo_usuario)
            
        db.commit()
        print("✅ Usuários básicos criados")
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
        
    print("=" * 50)
    print("✅ Migração para produção concluída com sucesso!")
    return True

if __name__ == "__main__":
    success = executar_migracao_producao()
    sys.exit(0 if success else 1)
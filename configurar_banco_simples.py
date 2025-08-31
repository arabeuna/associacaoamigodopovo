#!/usr/bin/env python3
"""
Script simples para configurar o banco PostgreSQL 17
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Carregar configurações
load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'admin123'),
    'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
}

def criar_tabelas():
    """Cria as tabelas principais do sistema"""
    print("Criando tabelas...")
    
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
                nivel VARCHAR(20) NOT NULL DEFAULT 'usuario',
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabela usuarios criada")
        
        # Tabela de atividades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atividades (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) UNIQUE NOT NULL,
                descricao TEXT,
                ativa BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabela atividades criada")
        
        # Tabela de turmas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turmas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                atividade_id INTEGER REFERENCES atividades(id),
                horario VARCHAR(20),
                dias_semana VARCHAR(100),
                ativa BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabela turmas criada")
        
        # Tabela de alunos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id SERIAL PRIMARY KEY,
                id_unico VARCHAR(50) UNIQUE NOT NULL,
                nome VARCHAR(100) NOT NULL,
                telefone VARCHAR(20),
                endereco TEXT,
                email VARCHAR(100),
                data_nascimento DATE,
                data_cadastro DATE DEFAULT CURRENT_DATE,
                atividade_id INTEGER REFERENCES atividades(id),
                turma_id INTEGER REFERENCES turmas(id),
                status_frequencia VARCHAR(20) DEFAULT 'Ativo',
                observacoes TEXT,
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                criado_por VARCHAR(50)
            )
        """)
        print("✅ Tabela alunos criada")
        
        # Tabela de presenças
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presencas (
                id SERIAL PRIMARY KEY,
                aluno_id VARCHAR(50) NOT NULL,
                data_presenca DATE NOT NULL,
                horario VARCHAR(10),
                atividade_id INTEGER REFERENCES atividades(id),
                turma_id INTEGER REFERENCES turmas(id),
                observacoes TEXT,
                registrado_por VARCHAR(50),
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabela presencas criada")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Todas as tabelas criadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def inserir_dados_iniciais():
    """Insere dados iniciais no sistema"""
    print("Inserindo dados iniciais...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Inserir usuário admin
        import hashlib
        senha_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO usuarios (username, senha_hash, nome, nivel) 
            VALUES (%s, %s, %s, %s) 
            ON CONFLICT (username) DO NOTHING
        """, ('admin', senha_hash, 'Administrador', 'admin_master'))
        print("✅ Usuário admin criado")
        
        # Inserir atividades básicas
        atividades = [
            ('Musculação', 'Treinamento de força e hipertrofia'),
            ('Pilates', 'Método de condicionamento físico e mental'),
            ('Natação', 'Atividade física na água'),
            ('Aeróbico', 'Exercícios aeróbicos'),
            ('Funcional', 'Treinamento funcional')
        ]
        
        for nome, descricao in atividades:
            cursor.execute("""
                INSERT INTO atividades (nome, descricao) 
                VALUES (%s, %s) 
                ON CONFLICT (nome) DO NOTHING
            """, (nome, descricao))
        
        print("✅ Atividades básicas criadas")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Dados iniciais inseridos com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados iniciais: {e}")
        return False

def main():
    print("=" * 60)
    print("    CONFIGURAÇÃO DO BANCO POSTGRESQL 17")
    print("=" * 60)
    
    # Criar tabelas
    if not criar_tabelas():
        return
    
    # Inserir dados iniciais
    if not inserir_dados_iniciais():
        return
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    
    print("\n🚀 Próximos passos:")
    print("1. Execute: python app.py")
    print("2. Acesse: http://127.0.0.1:5000")
    print("3. Login: admin / admin123")

if __name__ == "__main__":
    main()

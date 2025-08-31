#!/usr/bin/env python3
"""
Script para adicionar a coluna status à tabela presencas
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
    'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
}

def adicionar_coluna_status():
    """Adiciona a coluna status à tabela presencas"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, client_encoding='utf8')
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'presencas' AND column_name = 'status'
        """)
        
        if cursor.fetchone():
            print("✅ Coluna 'status' já existe na tabela presencas")
            return True
        
        # Adicionar a coluna status
        cursor.execute("""
            ALTER TABLE presencas 
            ADD COLUMN status VARCHAR(10) CHECK (status IN ('P', 'F', 'J'))
        """)
        
        # Adicionar a coluna tipo_registro se não existir
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'presencas' AND column_name = 'tipo_registro'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE presencas 
                ADD COLUMN tipo_registro VARCHAR(20) DEFAULT 'MANUAL'
            """)
            print("✅ Coluna 'tipo_registro' adicionada")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Coluna 'status' adicionada com sucesso à tabela presencas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna status: {e}")
        return False

def verificar_estrutura_tabela():
    """Verifica a estrutura atual da tabela presencas"""
    try:
        conn = psycopg2.connect(**DB_CONFIG, client_encoding='utf8')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'presencas'
            ORDER BY ordinal_position
        """)
        
        colunas = cursor.fetchall()
        
        print("📋 Estrutura atual da tabela presencas:")
        for coluna in colunas:
            print(f"  - {coluna[0]}: {coluna[1]} (nullable: {coluna[2]}, default: {coluna[3]})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")

if __name__ == "__main__":
    print("🔧 Adicionando coluna status à tabela presencas...")
    
    # Verificar estrutura atual
    verificar_estrutura_tabela()
    
    # Adicionar coluna
    if adicionar_coluna_status():
        print("\n✅ Verificando estrutura final:")
        verificar_estrutura_tabela()
    else:
        print("❌ Falha ao adicionar coluna")

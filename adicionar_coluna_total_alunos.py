#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar a coluna total_alunos à tabela atividades
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def adicionar_coluna_total_alunos():
    """Adiciona a coluna total_alunos à tabela atividades"""
    
    # Configurações do banco
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'academia_amigo_povo')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'atividades' 
            AND column_name = 'total_alunos'
        """)
        
        if cursor.fetchone():
            print("✅ Coluna 'total_alunos' já existe na tabela 'atividades'")
        else:
            # Adicionar a coluna
            cursor.execute("""
                ALTER TABLE atividades 
                ADD COLUMN total_alunos INTEGER DEFAULT 0
            """)
            
            conn.commit()
            print("✅ Coluna 'total_alunos' adicionada com sucesso!")
        
        # Verificar a estrutura atual da tabela
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'atividades' 
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Estrutura atual da tabela 'atividades':")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")

if __name__ == "__main__":
    print("🔧 Adicionando coluna 'total_alunos' à tabela 'atividades'...")
    adicionar_coluna_total_alunos()

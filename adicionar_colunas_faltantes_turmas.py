#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar todas as colunas faltantes à tabela turmas
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def adicionar_colunas_faltantes_turmas():
    """Adiciona todas as colunas faltantes à tabela turmas"""
    
    # Configurações do banco
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'academia_amigo_povo')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Colunas faltantes e seus tipos
    colunas_faltantes = [
        ('capacidade_maxima', 'INTEGER DEFAULT 20'),
        ('professor_responsavel', 'INTEGER'),
        ('criado_por', 'VARCHAR(50)'),
        ('total_alunos', 'INTEGER DEFAULT 0'),
        ('descricao', 'TEXT')
    ]
    
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
        
        for coluna, tipo in colunas_faltantes:
            # Verificar se a coluna já existe
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'turmas' 
                AND column_name = %s
            """, (coluna,))
            
            if cursor.fetchone():
                print(f"✅ Coluna '{coluna}' já existe na tabela 'turmas'")
            else:
                # Adicionar a coluna
                cursor.execute(f"""
                    ALTER TABLE turmas 
                    ADD COLUMN {coluna} {tipo}
                """)
                
                conn.commit()
                print(f"✅ Coluna '{coluna}' adicionada com sucesso!")
        
        # Verificar a estrutura final da tabela
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'turmas' 
            ORDER BY ordinal_position
        """)
        
        print("\n📋 Estrutura final da tabela 'turmas':")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao adicionar colunas: {e}")

if __name__ == "__main__":
    print("🔧 Adicionando colunas faltantes à tabela 'turmas'...")
    adicionar_colunas_faltantes_turmas()

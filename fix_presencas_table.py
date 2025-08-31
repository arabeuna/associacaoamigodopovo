#!/usr/bin/env python3
"""
Script simples para adicionar coluna status à tabela presencas
"""

import os
import psycopg2

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
    'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
}

def fix_presencas_table():
    """Adiciona colunas faltantes à tabela presencas"""
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verificar se a coluna status existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'presencas' AND column_name = 'status'
        """)
        
        if cursor.fetchone():
            print("Column 'status' already exists")
        else:
            print("Adding column 'status'...")
            cursor.execute("""
                ALTER TABLE presencas 
                ADD COLUMN status VARCHAR(10) CHECK (status IN ('P', 'F', 'J'))
            """)
            print("Column 'status' added successfully")
        
        # Verificar se a coluna tipo_registro existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'presencas' AND column_name = 'tipo_registro'
        """)
        
        if cursor.fetchone():
            print("Column 'tipo_registro' already exists")
        else:
            print("Adding column 'tipo_registro'...")
            cursor.execute("""
                ALTER TABLE presencas 
                ADD COLUMN tipo_registro VARCHAR(20) DEFAULT 'MANUAL'
            """)
            print("Column 'tipo_registro' added successfully")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Table presencas fixed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    fix_presencas_table()

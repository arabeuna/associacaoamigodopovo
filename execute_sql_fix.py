#!/usr/bin/env python3
"""
Script para executar SQL e corrigir a tabela presencas
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

def execute_sql_fix():
    """Executa o SQL para corrigir a tabela presencas"""
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # SQL para adicionar colunas
        sql_commands = [
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'presencas' AND column_name = 'status'
                ) THEN
                    ALTER TABLE presencas ADD COLUMN status VARCHAR(10) CHECK (status IN ('P', 'F', 'J'));
                    RAISE NOTICE 'Coluna status adicionada com sucesso';
                ELSE
                    RAISE NOTICE 'Coluna status já existe';
                END IF;
            END $$;
            """,
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'presencas' AND column_name = 'tipo_registro'
                ) THEN
                    ALTER TABLE presencas ADD COLUMN tipo_registro VARCHAR(20) DEFAULT 'MANUAL';
                    RAISE NOTICE 'Coluna tipo_registro adicionada com sucesso';
                ELSE
                    RAISE NOTICE 'Coluna tipo_registro já existe';
                END IF;
            END $$;
            """
        ]
        
        for sql in sql_commands:
            print("Executing SQL command...")
            cursor.execute(sql)
            conn.commit()
            print("SQL command executed successfully")
        
        # Verificar estrutura final
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'presencas'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\nFinal table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        cursor.close()
        conn.close()
        
        print("\nTable presencas fixed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    execute_sql_fix()

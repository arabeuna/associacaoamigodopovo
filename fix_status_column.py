#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def fix_status_column():
    """Adiciona a coluna status na tabela presencas se ela não existir"""
    
    # Configurações do banco
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'postgres'),
        'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
    }
    
    try:
        print("Conectando ao banco de dados...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Verificar se a coluna status existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'presencas' AND column_name = 'status'
        """)
        
        if cursor.fetchone():
            print("✅ Coluna 'status' já existe")
        else:
            print("➕ Adicionando coluna 'status'...")
            cursor.execute("""
                ALTER TABLE presencas 
                ADD COLUMN status VARCHAR(10) CHECK (status IN ('P', 'F', 'J'))
            """)
            conn.commit()
            print("✅ Coluna 'status' adicionada com sucesso")
        
        cursor.close()
        conn.close()
        print("🎉 Operação concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_status_column()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def fix_tipo_registro_column():
    """Adiciona a coluna tipo_registro na tabela presencas se ela não existir"""
    
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
        
        # Verificar se a coluna tipo_registro existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'presencas' AND column_name = 'tipo_registro'
        """)
        
        if cursor.fetchone():
            print("✅ Coluna 'tipo_registro' já existe")
        else:
            print("➕ Adicionando coluna 'tipo_registro'...")
            cursor.execute("""
                ALTER TABLE presencas 
                ADD COLUMN tipo_registro VARCHAR(20) DEFAULT 'MANUAL'
            """)
            conn.commit()
            print("✅ Coluna 'tipo_registro' adicionada com sucesso")
        
        cursor.close()
        conn.close()
        print("🎉 Operação concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_tipo_registro_column()
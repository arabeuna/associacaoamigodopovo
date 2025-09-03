#!/usr/bin/env python3

import psycopg2
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

def testar_conexao():
    try:
        # Configurações do banco
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'admin123'),
            'database': os.getenv('DB_NAME', 'academia_amigo_povo')
        }
        
        print(f"Tentando conectar com:")
        print(f"Host: {db_config['host']}")
        print(f"Port: {db_config['port']}")
        print(f"User: {db_config['user']}")
        print(f"Database: {db_config['database']}")
        print()
        
        # Tentar conectar
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Testar consulta simples
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Conexão bem-sucedida!")
        print(f"Versão do PostgreSQL: {version[0]}")
        
        # Verificar se o banco existe
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()
        print(f"Banco atual: {current_db[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("=== Teste de Conexão PostgreSQL ===")
    testar_conexao()
#!/usr/bin/env python3
"""
Script de inicialização do banco de dados PostgreSQL
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Função principal de inicialização"""
    print("=== Inicialização do Banco de Dados PostgreSQL ===")
    print("Academia Amigo do Povo")
    print()
    
    # Verificar se PostgreSQL está instalado
    try:
        import psycopg2
        print("✓ psycopg2 encontrado")
    except ImportError:
        print("✗ psycopg2 não encontrado")
        print("Instale com: pip install psycopg2-binary")
        return False
    
    # Verificar se SQLAlchemy está instalado
    try:
        import sqlalchemy
        print("✓ SQLAlchemy encontrado")
    except ImportError:
        print("✗ SQLAlchemy não encontrado")
        print("Instale com: pip install SQLAlchemy")
        return False
    
    # Verificar configurações do banco
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_name = os.getenv('DB_NAME', 'academia_amigo_povo')
    
    print(f"Configurações do banco:")
    print(f"- Host: {db_host}")
    print(f"- Porta: {db_port}")
    print(f"- Usuário: {db_user}")
    print(f"- Banco: {db_name}")
    print()
    
    # Executar configuração do banco
    try:
        from database_setup import main as setup_db
        if setup_db():
            print("✓ Banco de dados configurado com sucesso!")
        else:
            print("✗ Erro na configuração do banco de dados")
            return False
    except Exception as e:
        print(f"✗ Erro ao configurar banco: {e}")
        return False
    
    # Executar migração de dados
    try:
        from migrar_dados import main as migrar_dados
        if migrar_dados():
            print("✓ Dados migrados com sucesso!")
        else:
            print("✗ Erro na migração de dados")
            return False
    except Exception as e:
        print(f"✗ Erro ao migrar dados: {e}")
        return False
    
    print()
    print("=== Inicialização concluída com sucesso! ===")
    print("O sistema está pronto para uso.")
    print()
    print("Próximos passos:")
    print("1. Configure as variáveis de ambiente no arquivo .env")
    print("2. Execute: python app.py")
    print("3. Acesse: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

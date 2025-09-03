#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Carregar variáveis de ambiente
load_dotenv()

def testar_sqlalchemy():
    try:
        # Configurar URL do banco de dados
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if not DATABASE_URL:
            db_host = os.environ.get('DB_HOST', 'localhost')
            db_port = os.environ.get('DB_PORT', '5432')
            db_user = os.environ.get('DB_USER', 'postgres')
            db_password = os.environ.get('DB_PASSWORD', 'admin123')
            db_name = os.environ.get('DB_NAME', 'academia_amigo_povo')
            DATABASE_URL = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        
        print(f"URL do banco: {DATABASE_URL}")
        print()
        
        # Criar engine
        engine = create_engine(DATABASE_URL)
        
        # Testar conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()
            print(f"✅ SQLAlchemy conectou com sucesso!")
            print(f"Versão: {version[0]}")
            
            # Verificar tabelas existentes
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            print(f"\nTabelas no banco ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
        
        # Testar SessionLocal
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Testar uma consulta simples
        result = session.execute(text("SELECT current_database();"))
        db_name = result.fetchone()
        print(f"\n✅ Session funcionando! Banco atual: {db_name[0]}")
        
        session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no SQLAlchemy: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("=== Teste SQLAlchemy ===")
    testar_sqlalchemy()
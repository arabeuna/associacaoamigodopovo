#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def verificar_tabela_presencas():
    """Verifica a estrutura da tabela presencas"""
    
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
        
        # Verificar colunas da tabela presencas
        print("\n📋 COLUNAS DA TABELA PRESENCAS:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'presencas'
            ORDER BY ordinal_position
        """)
        
        colunas = cursor.fetchall()
        for coluna in colunas:
            print(f"  - {coluna[0]} ({coluna[1]}) - Nullable: {coluna[2]} - Default: {coluna[3]}")
        
        # Verificar constraints
        print("\n🔒 CONSTRAINTS DA TABELA PRESENCAS:")
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'presencas'
        """)
        
        constraints = cursor.fetchall()
        for constraint in constraints:
            print(f"  - {constraint[0]} ({constraint[1]})")
        
        # Verificar se há dados na tabela
        print("\n📊 DADOS NA TABELA PRESENCAS:")
        cursor.execute("SELECT COUNT(*) FROM presencas")
        total = cursor.fetchone()[0]
        print(f"  Total de registros: {total}")
        
        if total > 0:
            cursor.execute("SELECT * FROM presencas LIMIT 3")
            registros = cursor.fetchall()
            print("  Primeiros 3 registros:")
            for i, registro in enumerate(registros, 1):
                print(f"    {i}. {registro}")
        
        cursor.close()
        conn.close()
        print("\n✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

if __name__ == "__main__":
    verificar_tabela_presencas()
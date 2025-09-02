#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a estrutura do banco de dados local
"""

import sqlite3
import os

def verificar_estrutura_banco():
    """Verifica a estrutura das tabelas no banco SQLite local"""
    print("🔍 Verificando estrutura do banco de dados local...")
    
    db_path = 'academia.db'
    if not os.path.exists(db_path):
        print(f"❌ Arquivo de banco {db_path} não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        print("\n📋 Tabelas disponíveis:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        for tabela in tabelas:
            print(f"  - {tabela[0]}")
        
        # Verificar estrutura da tabela alunos
        print("\n👤 Estrutura da tabela 'alunos':")
        cursor.execute("PRAGMA table_info(alunos)")
        colunas = cursor.fetchall()
        
        if colunas:
            for coluna in colunas:
                cid, nome, tipo, notnull, default, pk = coluna
                print(f"  - {nome} ({tipo}) {'NOT NULL' if notnull else ''} {'PRIMARY KEY' if pk else ''}")
        else:
            print("  ❌ Tabela 'alunos' não encontrada ou sem colunas")
        
        # Verificar se existe coluna id_unico
        nomes_colunas = [col[1] for col in colunas]
        if 'id_unico' in nomes_colunas:
            print("  ✅ Coluna 'id_unico' existe")
        else:
            print("  ❌ Coluna 'id_unico' NÃO existe")
        
        # Contar registros
        try:
            cursor.execute("SELECT COUNT(*) FROM alunos")
            count = cursor.fetchone()[0]
            print(f"\n📊 Total de alunos no banco: {count}")
        except Exception as e:
            print(f"\n❌ Erro ao contar alunos: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

if __name__ == "__main__":
    verificar_estrutura_banco()
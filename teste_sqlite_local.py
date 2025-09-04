#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste direto do banco SQLite local
"""

import sqlite3
import os
from datetime import datetime

def testar_sqlite_local():
    """Testa diretamente o banco SQLite local"""
    print("🚀 TESTE DIRETO - BANCO SQLITE LOCAL")
    print("=" * 60)
    
    # Caminho do banco SQLite
    db_path = 'academia_amigo_povo.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Arquivo {db_path} não encontrado")
        return
    
    try:
        # Conectar ao SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"✅ Conectado ao banco: {db_path}")
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        print(f"📋 Tabelas encontradas: {[t[0] for t in tabelas]}")
        
        # Contar alunos
        cursor.execute("SELECT COUNT(*) FROM alunos")
        total_alunos = cursor.fetchone()[0]
        print(f"📊 Total de alunos: {total_alunos}")
        
        # Verificar estrutura da tabela alunos primeiro
        cursor.execute("PRAGMA table_info(alunos)")
        colunas = cursor.fetchall()
        print("\n🔍 Estrutura da tabela alunos:")
        for coluna in colunas:
            print(f"  - {coluna[1]} ({coluna[2]})")
        
        # Verificar se existe coluna atividade ou atividade_id
        nomes_colunas = [col[1] for col in colunas]
        
        if 'atividade' in nomes_colunas:
            cursor.execute("SELECT nome, atividade FROM alunos LIMIT 10")
            alunos_amostra = cursor.fetchall()
            print("\n📋 Primeiros 10 alunos:")
            for i, (nome, atividade) in enumerate(alunos_amostra, 1):
                print(f"  {i}. {nome} - {atividade}")
        elif 'atividade_id' in nomes_colunas:
            cursor.execute("SELECT nome, atividade_id FROM alunos LIMIT 10")
            alunos_amostra = cursor.fetchall()
            print("\n📋 Primeiros 10 alunos:")
            for i, (nome, atividade_id) in enumerate(alunos_amostra, 1):
                print(f"  {i}. {nome} - ID Atividade: {atividade_id}")
        else:
            cursor.execute("SELECT nome FROM alunos LIMIT 10")
            alunos_amostra = cursor.fetchall()
            print("\n📋 Primeiros 10 alunos (apenas nomes):")
            for i, (nome,) in enumerate(alunos_amostra, 1):
                print(f"  {i}. {nome}")
        print("\n🏗️  Estrutura da tabela alunos:")
        for coluna in colunas:
            print(f"  - {coluna[1]} ({coluna[2]})")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print(f"🎯 RESULTADO: {total_alunos} alunos encontrados no SQLite")
        
        return total_alunos
        
    except Exception as e:
        print(f"❌ Erro ao acessar SQLite: {e}")
        return 0

if __name__ == "__main__":
    testar_sqlite_local()
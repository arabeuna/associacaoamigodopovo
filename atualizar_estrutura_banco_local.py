#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar a estrutura do banco SQLite local
Adicionando colunas que faltam para compatibilidade com o modelo atual
"""

import sqlite3
import os
from datetime import datetime

def atualizar_estrutura_banco():
    """Atualiza a estrutura do banco SQLite local"""
    print("🔧 Atualizando estrutura do banco SQLite local...")
    
    db_path = 'academia_amigo_povo.db'
    if not os.path.exists(db_path):
        print(f"❌ Arquivo de banco {db_path} não encontrado!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar colunas existentes
        cursor.execute("PRAGMA table_info(alunos)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        print(f"📋 Colunas existentes: {colunas_existentes}")
        
        # Lista de colunas que devem existir
        colunas_necessarias = {
            'id_unico': 'VARCHAR(50)',
            'titulo_eleitor': 'VARCHAR(50)'
        }
        
        # Adicionar colunas que faltam
        colunas_adicionadas = []
        for coluna, tipo in colunas_necessarias.items():
            if coluna not in colunas_existentes:
                try:
                    cursor.execute(f"ALTER TABLE alunos ADD COLUMN {coluna} {tipo}")
                    colunas_adicionadas.append(coluna)
                    print(f"✅ Coluna '{coluna}' adicionada")
                except Exception as e:
                    print(f"❌ Erro ao adicionar coluna '{coluna}': {e}")
        
        if colunas_adicionadas:
            # Gerar id_unico para registros existentes que não possuem
            print("🔄 Gerando id_unico para registros existentes...")
            cursor.execute("SELECT id FROM alunos WHERE id_unico IS NULL OR id_unico = ''")
            registros_sem_id = cursor.fetchall()
            
            import uuid
            for registro in registros_sem_id:
                id_aluno = registro[0]
                id_unico = str(uuid.uuid4())[:8]
                cursor.execute("UPDATE alunos SET id_unico = ? WHERE id = ?", (id_unico, id_aluno))
            
            print(f"✅ {len(registros_sem_id)} registros atualizados com id_unico")
        
        # Verificar se a tabela usuarios existe e tem as colunas necessárias
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if cursor.fetchone():
            print("\n👥 Verificando tabela usuarios...")
            cursor.execute("PRAGMA table_info(usuarios)")
            colunas_usuarios = [col[1] for col in cursor.fetchall()]
            
            colunas_usuarios_necessarias = {
                'permissoes': 'VARCHAR(500)',
                'atividade_responsavel': 'VARCHAR(500)',
                'alunos_atribuidos': 'VARCHAR(500)',
                'criado_por': 'VARCHAR(50)',
                'ultimo_acesso': 'DATETIME'
            }
            
            for coluna, tipo in colunas_usuarios_necessarias.items():
                if coluna not in colunas_usuarios:
                    try:
                        cursor.execute(f"ALTER TABLE usuarios ADD COLUMN {coluna} {tipo}")
                        print(f"✅ Coluna '{coluna}' adicionada à tabela usuarios")
                    except Exception as e:
                        print(f"❌ Erro ao adicionar coluna '{coluna}' à tabela usuarios: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Estrutura do banco atualizada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar estrutura do banco: {e}")
        return False

def verificar_estrutura_final():
    """Verifica a estrutura final do banco"""
    print("\n🔍 Verificando estrutura final...")
    
    try:
        conn = sqlite3.connect('academia_amigo_povo.db')
        cursor = conn.cursor()
        
        # Verificar tabela alunos
        cursor.execute("PRAGMA table_info(alunos)")
        colunas = cursor.fetchall()
        print("\n👤 Estrutura final da tabela 'alunos':")
        for coluna in colunas:
            cid, nome, tipo, notnull, default, pk = coluna
            print(f"  - {nome} ({tipo})")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM alunos")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total de alunos: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")

if __name__ == "__main__":
    if atualizar_estrutura_banco():
        verificar_estrutura_final()
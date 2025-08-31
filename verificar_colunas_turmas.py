#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar colunas faltantes na tabela turmas
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def verificar_colunas_turmas():
    """Verifica quais colunas estão faltando na tabela turmas"""
    
    # Configurações do banco
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'academia_amigo_povo')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Colunas que deveriam existir no modelo Turma
    colunas_esperadas = [
        'id', 'nome', 'atividade_id', 'horario', 'dias_semana', 'periodo',
        'capacidade_maxima', 'professor_responsavel', 'ativa', 'data_criacao',
        'criado_por', 'total_alunos', 'descricao'
    ]
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Obter colunas existentes
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'turmas' 
            ORDER BY ordinal_position
        """)
        
        colunas_existentes = [row[0] for row in cursor.fetchall()]
        
        print("📋 Colunas existentes na tabela 'turmas':")
        for coluna in colunas_existentes:
            print(f"  ✅ {coluna}")
        
        print("\n🔍 Verificando colunas faltantes...")
        colunas_faltantes = []
        
        for coluna in colunas_esperadas:
            if coluna not in colunas_existentes:
                colunas_faltantes.append(coluna)
                print(f"  ❌ {coluna} - FALTANDO")
            else:
                print(f"  ✅ {coluna} - OK")
        
        if colunas_faltantes:
            print(f"\n⚠️ Colunas faltantes: {colunas_faltantes}")
        else:
            print("\n✅ Todas as colunas estão presentes!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar colunas: {e}")

if __name__ == "__main__":
    print("🔍 Verificando colunas da tabela 'turmas'...")
    verificar_colunas_turmas()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste detalhado da função obter_alunos_usuario()
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def testar_obter_alunos_detalhado():
    """Testa a função obter_alunos_usuario() com diferentes cenários"""
    
    # Configurações do banco
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'academia_amigo_povo')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
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
        
        print("🔍 Testando cenários da função obter_alunos_usuario()...")
        
        # Teste 1: Verificar se há alunos ativos
        print("\n==================================================")
        print("TESTE 1: Verificar alunos ativos")
        print("==================================================")
        
        cursor.execute("""
            SELECT COUNT(*) FROM alunos WHERE ativo = true
        """)
        total_alunos_ativos = cursor.fetchone()[0]
        print(f"✅ Total de alunos ativos: {total_alunos_ativos}")
        
        # Teste 2: Verificar se há atividades
        print("\n==================================================")
        print("TESTE 2: Verificar atividades")
        print("==================================================")
        
        cursor.execute("""
            SELECT id, nome, ativa FROM atividades ORDER BY nome
        """)
        atividades = cursor.fetchall()
        print(f"✅ Total de atividades: {len(atividades)}")
        for atividade in atividades:
            print(f"  - ID: {atividade[0]}, Nome: {atividade[1]}, Ativa: {atividade[2]}")
        
        # Teste 3: Verificar relacionamentos
        print("\n==================================================")
        print("TESTE 3: Verificar relacionamentos")
        print("==================================================")
        
        cursor.execute("""
            SELECT 
                a.id,
                a.nome,
                a.atividade_id,
                ativ.nome as atividade_nome,
                a.turma_id,
                t.nome as turma_nome
            FROM alunos a
            LEFT JOIN atividades ativ ON a.atividade_id = ativ.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true
            LIMIT 10
        """)
        
        relacionamentos = cursor.fetchall()
        print(f"✅ Verificando relacionamentos (primeiros 10):")
        for rel in relacionamentos:
            print(f"  - Aluno: {rel[1]} | Atividade ID: {rel[2]} ({rel[3]}) | Turma ID: {rel[4]} ({rel[5]})")
        
        # Teste 4: Simular busca de admin
        print("\n==================================================")
        print("TESTE 4: Simular busca de admin")
        print("==================================================")
        
        cursor.execute("""
            SELECT 
                a.id,
                a.nome,
                a.telefone,
                a.endereco,
                a.email,
                a.data_nascimento,
                a.data_cadastro,
                ativ.nome as atividade_nome,
                t.nome as turma_nome,
                a.status_frequencia,
                a.observacoes
            FROM alunos a
            LEFT JOIN atividades ativ ON a.atividade_id = ativ.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true
            ORDER BY a.nome
            LIMIT 5
        """)
        
        alunos_admin = cursor.fetchall()
        print(f"✅ Alunos para admin (primeiros 5):")
        for aluno in alunos_admin:
            print(f"  - {aluno[1]} | {aluno[7]} | {aluno[8]}")
        
        # Teste 5: Simular busca de usuário específico (Informática)
        print("\n==================================================")
        print("TESTE 5: Simular busca de usuário (Informática)")
        print("==================================================")
        
        cursor.execute("""
            SELECT 
                a.id,
                a.nome,
                a.telefone,
                a.endereco,
                a.email,
                a.data_nascimento,
                a.data_cadastro,
                ativ.nome as atividade_nome,
                t.nome as turma_nome,
                a.status_frequencia,
                a.observacoes
            FROM alunos a
            LEFT JOIN atividades ativ ON a.atividade_id = ativ.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true 
            AND ativ.nome ILIKE '%Informática%'
            ORDER BY a.nome
            LIMIT 5
        """)
        
        alunos_informatica = cursor.fetchall()
        print(f"✅ Alunos de Informática (primeiros 5):")
        for aluno in alunos_informatica:
            print(f"  - {aluno[1]} | {aluno[7]} | {aluno[8]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Teste detalhado concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    testar_obter_alunos_detalhado()

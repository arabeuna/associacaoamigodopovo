#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de debug da função obter_alunos_usuario
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def testar_obter_alunos_debug():
    """Testa a função obter_alunos_usuario com debug detalhado"""
    
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
        
        print("🔍 Testando consulta direta no banco...")
        
        # Testar consulta simples
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE ativo = true")
        total_alunos = cursor.fetchone()[0]
        print(f"✅ Total de alunos ativos: {total_alunos}")
        
        # Testar consulta com JOIN
        cursor.execute("""
            SELECT a.id, a.nome, a.telefone, a.endereco, a.email, 
                   a.data_nascimento, a.data_cadastro, a.observacoes,
                   at.nome as atividade_nome, t.nome as turma_nome
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true
            LIMIT 5
        """)
        
        alunos = cursor.fetchall()
        print(f"✅ Consulta com JOIN retornou {len(alunos)} alunos")
        
        for i, aluno in enumerate(alunos):
            print(f"   {i+1}. {aluno[1]} - {aluno[8]} - {aluno[9]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_obter_alunos_debug()

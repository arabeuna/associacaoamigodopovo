#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'academia_amigo_povo'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'admin123')
}

def obter_alunos_admin():
    """Simula a função obter_alunos_usuario() para admin"""
    print("🔍 Testando busca de alunos para admin...")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco de dados!")
        
        # Buscar todos os alunos ativos (como admin)
        cursor.execute("""
            SELECT a.id, a.nome, a.telefone, a.endereco, a.email, 
                   a.data_nascimento, a.data_cadastro, a.status_frequencia, a.observacoes,
                   at.nome as atividade, t.nome as turma
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true
            ORDER BY a.nome
            LIMIT 10
        """)
        
        alunos = cursor.fetchall()
        print(f"\n📋 Encontrados {len(alunos)} alunos (primeiros 10):")
        
        for aluno in alunos:
            print(f"   ID: {aluno[0]}, Nome: {aluno[1]}, Atividade: {aluno[9]}, Turma: {aluno[10]}")
        
        cursor.close()
        conn.close()
        
        return len(alunos)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 0

def obter_alunos_por_atividade(atividade_nome):
    """Simula a função obter_alunos_usuario() para usuário específico"""
    print(f"🔍 Testando busca de alunos para atividade: {atividade_nome}")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco de dados!")
        
        # Buscar atividade primeiro
        cursor.execute("""
            SELECT id, nome FROM atividades 
            WHERE LOWER(nome) LIKE %s AND ativa = true
        """, (f'%{atividade_nome.lower()}%',))
        
        atividade = cursor.fetchone()
        
        if not atividade:
            print(f"❌ Atividade '{atividade_nome}' não encontrada!")
            return 0
        
        print(f"✅ Atividade encontrada: ID {atividade[0]}, Nome: {atividade[1]}")
        
        # Buscar alunos da atividade
        cursor.execute("""
            SELECT a.id, a.nome, a.telefone, a.endereco, a.email, 
                   a.data_nascimento, a.data_cadastro, a.status_frequencia, a.observacoes,
                   at.nome as atividade, t.nome as turma
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true AND a.atividade_id = %s
            ORDER BY a.nome
            LIMIT 10
        """, (atividade[0],))
        
        alunos = cursor.fetchall()
        print(f"\n📋 Encontrados {len(alunos)} alunos da atividade '{atividade[1]}' (primeiros 10):")
        
        for aluno in alunos:
            print(f"   ID: {aluno[0]}, Nome: {aluno[1]}, Turma: {aluno[10]}")
        
        cursor.close()
        conn.close()
        
        return len(alunos)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 0

def testar_busca_por_nome():
    """Testa busca por nome nos alunos"""
    print("\n🔍 Testando busca por nome...")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Testar busca por "joão"
        termo_busca = "joão"
        cursor.execute("""
            SELECT a.id, a.nome, a.telefone, a.endereco, 
                   at.nome as atividade, t.nome as turma
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true 
            AND (LOWER(a.nome) LIKE %s OR LOWER(a.telefone) LIKE %s OR LOWER(a.endereco) LIKE %s)
            ORDER BY a.nome
            LIMIT 5
        """, (f'%{termo_busca.lower()}%', f'%{termo_busca.lower()}%', f'%{termo_busca.lower()}%'))
        
        alunos = cursor.fetchall()
        print(f"\n🔍 Busca por '{termo_busca}': {len(alunos)} resultados")
        
        for aluno in alunos:
            print(f"   Nome: {aluno[1]}, Atividade: {aluno[4]}, Turma: {aluno[5]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na busca por nome: {e}")

if __name__ == "__main__":
    print("🧪 Testando sistema de busca de alunos após correção...")
    
    # Testar busca para admin
    total_admin = obter_alunos_admin()
    
    # Testar busca para atividade específica
    total_musculacao = obter_alunos_por_atividade("musculação")
    
    # Testar busca por nome
    testar_busca_por_nome()
    
    print(f"\n✅ Testes concluídos!")
    print(f"   - Admin: {total_admin} alunos")
    print(f"   - Musculação: {total_musculacao} alunos")

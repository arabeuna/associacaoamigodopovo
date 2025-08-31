#!/usr/bin/env python3
"""
Script para testar a busca de alunos diretamente no banco de dados
"""
import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
    'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
}

def obter_alunos_admin():
    """Busca todos os alunos ativos (como admin)"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.nome, a.telefone, a.endereco, a.email,
                   a.data_nascimento, a.data_cadastro, a.status_frequencia, a.observacoes,
                   at.nome as atividade, t.nome as turma
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true
            ORDER BY a.nome
        """)
        
        alunos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{
            'id': aluno[0],
            'nome': aluno[1],
            'telefone': aluno[2] or '',
            'endereco': aluno[3] or '',
            'email': aluno[4] or '',
            'data_nascimento': aluno[5].strftime('%d/%m/%Y') if aluno[5] else '',
            'data_cadastro': aluno[6].strftime('%d/%m/%Y') if aluno[6] else '',
            'atividade': aluno[9] or '',
            'turma': aluno[10] or '',
            'status_frequencia': aluno[7] or '',
            'observacoes': aluno[8] or ''
        } for aluno in alunos]
        
    except Exception as e:
        print(f"❌ Erro ao buscar alunos: {e}")
        return []

def obter_alunos_por_atividade(atividade_nome):
    """Busca alunos de uma atividade específica"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.nome, a.telefone, a.endereco, a.email,
                   a.data_nascimento, a.data_cadastro, a.status_frequencia, a.observacoes,
                   at.nome as atividade, t.nome as turma
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true AND at.nome ILIKE %s
            ORDER BY a.nome
        """, (f'%{atividade_nome}%',))
        
        alunos = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{
            'id': aluno[0],
            'nome': aluno[1],
            'telefone': aluno[2] or '',
            'endereco': aluno[3] or '',
            'email': aluno[4] or '',
            'data_nascimento': aluno[5].strftime('%d/%m/%Y') if aluno[5] else '',
            'data_cadastro': aluno[6].strftime('%d/%m/%Y') if aluno[6] else '',
            'atividade': aluno[9] or '',
            'turma': aluno[10] or '',
            'status_frequencia': aluno[7] or '',
            'observacoes': aluno[8] or ''
        } for aluno in alunos]
        
    except Exception as e:
        print(f"❌ Erro ao buscar alunos da atividade {atividade_nome}: {e}")
        return []

def testar_obter_alunos():
    """Testa a busca de alunos"""
    print("🔍 Testando busca de alunos no banco de dados...")
    
    # Testar busca como admin (todos os alunos)
    print("\n👑 Testando busca como ADMIN (todos os alunos)...")
    alunos_admin = obter_alunos_admin()
    print(f"   📊 Total de alunos encontrados: {len(alunos_admin)}")
    
    if alunos_admin:
        print("   📋 Primeiros 3 alunos:")
        for i, aluno in enumerate(alunos_admin[:3]):
            print(f"      {i+1}. {aluno['nome']} - {aluno['atividade']}")
    
    # Testar busca por atividade específica
    print("\n👨‍🏫 Testando busca por atividade 'Informática'...")
    alunos_info = obter_alunos_por_atividade('Informática')
    print(f"   📊 Total de alunos de Informática: {len(alunos_info)}")
    
    if alunos_info:
        print("   📋 Primeiros 3 alunos de Informática:")
        for i, aluno in enumerate(alunos_info[:3]):
            print(f"      {i+1}. {aluno['nome']} - {aluno['turma']}")
    
    # Testar busca por outra atividade
    print("\n🏊 Testando busca por atividade 'Natação'...")
    alunos_natacao = obter_alunos_por_atividade('Natação')
    print(f"   📊 Total de alunos de Natação: {len(alunos_natacao)}")
    
    if alunos_natacao:
        print("   📋 Primeiros 3 alunos de Natação:")
        for i, aluno in enumerate(alunos_natacao[:3]):
            print(f"      {i+1}. {aluno['nome']} - {aluno['turma']}")
    
    print("\n✅ Teste concluído com sucesso!")

if __name__ == "__main__":
    testar_obter_alunos()

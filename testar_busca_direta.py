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

def testar_busca_direta():
    """Testa a busca de alunos diretamente no banco de dados"""
    print("🔍 Testando busca direta no banco de dados...")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco de dados!")
        
        # Verificar se existem dados na tabela alunos
        cursor.execute("SELECT COUNT(*) FROM alunos")
        total_alunos = cursor.fetchone()[0]
        print(f"📊 Total de alunos no banco: {total_alunos}")
        
        if total_alunos == 0:
            print("⚠️ Nenhum aluno encontrado no banco!")
            return
        
        # Buscar alguns alunos de exemplo
        cursor.execute("""
            SELECT a.id, a.nome, a.telefone, a.endereco, 
                   at.nome as atividade, t.nome as turma
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true
            LIMIT 5
        """)
        
        alunos = cursor.fetchall()
        print(f"\n📋 Primeiros 5 alunos:")
        for aluno in alunos:
            print(f"   ID: {aluno[0]}, Nome: {aluno[1]}, Atividade: {aluno[4]}, Turma: {aluno[5]}")
        
        # Testar busca por nome
        termo_busca = "joão"
        cursor.execute("""
            SELECT a.id, a.nome, a.telefone, a.endereco, 
                   at.nome as atividade, t.nome as turma
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.ativo = true 
            AND (LOWER(a.nome) LIKE %s OR LOWER(a.telefone) LIKE %s OR LOWER(a.endereco) LIKE %s)
        """, (f'%{termo_busca}%', f'%{termo_busca}%', f'%{termo_busca}%'))
        
        alunos_busca = cursor.fetchall()
        print(f"\n🔍 Busca por '{termo_busca}': {len(alunos_busca)} resultados")
        for aluno in alunos_busca:
            print(f"   Nome: {aluno[1]}, Atividade: {aluno[4]}")
        
        # Verificar atividades disponíveis
        cursor.execute("SELECT id, nome FROM atividades WHERE ativa = true")
        atividades = cursor.fetchall()
        print(f"\n🏃 Atividades disponíveis:")
        for atividade in atividades:
            print(f"   ID: {atividade[0]}, Nome: {atividade[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_busca_direta()

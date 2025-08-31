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

def simular_busca_alunos(termo_busca='', nivel_usuario='admin'):
    """Simula a função buscar_alunos do Flask"""
    print(f"🔍 Simulando busca de alunos...")
    print(f"   Termo de busca: '{termo_busca}'")
    print(f"   Nível de usuário: {nivel_usuario}")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco de dados!")
        
        # Construir query base
        if nivel_usuario in ['admin_master', 'admin']:
            # Admin vê todos os alunos
            query = """
                SELECT a.id, a.nome, a.telefone, a.endereco, a.email, 
                       a.data_nascimento, a.data_cadastro, a.status_frequencia, a.observacoes,
                       at.nome as atividade, t.nome as turma
                FROM alunos a
                LEFT JOIN atividades at ON a.atividade_id = at.id
                LEFT JOIN turmas t ON a.turma_id = t.id
                WHERE a.ativo = true
            """
            params = []
        else:
            # Usuário vê apenas alunos da sua atividade
            query = """
                SELECT a.id, a.nome, a.telefone, a.endereco, a.email, 
                       a.data_nascimento, a.data_cadastro, a.status_frequencia, a.observacoes,
                       at.nome as atividade, t.nome as turma
                FROM alunos a
                LEFT JOIN atividades at ON a.atividade_id = at.id
                LEFT JOIN turmas t ON a.turma_id = t.id
                WHERE a.ativo = true AND at.nome ILIKE %s
            """
            params = ['%Informática%']  # Exemplo para professor de informática
        
        # Adicionar filtro de busca se fornecido
        if termo_busca:
            if nivel_usuario in ['admin_master', 'admin']:
                query += " AND (LOWER(a.nome) LIKE %s OR LOWER(a.telefone) LIKE %s OR LOWER(a.endereco) LIKE %s OR LOWER(at.nome) LIKE %s)"
                params.extend([f'%{termo_busca.lower()}%'] * 4)
            else:
                query += " AND (LOWER(a.nome) LIKE %s OR LOWER(a.telefone) LIKE %s OR LOWER(a.endereco) LIKE %s OR LOWER(at.nome) LIKE %s)"
                params.extend([f'%{termo_busca.lower()}%'] * 4)
        
        query += " ORDER BY a.nome"
        
        # Executar query
        cursor.execute(query, params)
        alunos = cursor.fetchall()
        
        # Converter para formato JSON
        alunos_json = []
        for aluno in alunos:
            alunos_json.append({
                'id': aluno[0],
                'nome': aluno[1],
                'telefone': aluno[2] or '',
                'endereco': aluno[3] or '',
                'email': aluno[4] or '',
                'data_nascimento': aluno[5].strftime('%d/%m/%Y') if aluno[5] else '',
                'data_cadastro': aluno[6].strftime('%d/%m/%Y') if aluno[6] else '',
                'status_frequencia': aluno[7] or '',
                'observacoes': aluno[8] or '',
                'atividade': aluno[9] or '',
                'turma': aluno[10] or ''
            })
        
        print(f"✅ Busca concluída! Encontrados {len(alunos_json)} alunos")
        
        # Mostrar primeiros resultados
        if alunos_json:
            print(f"\n📋 Primeiros 5 resultados:")
            for i, aluno in enumerate(alunos_json[:5]):
                print(f"   {i+1}. {aluno['nome']} - {aluno['atividade']} - {aluno['turma']}")
        
        if len(alunos_json) > 5:
            print(f"   ... e mais {len(alunos_json) - 5} alunos")
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'alunos': alunos_json,
            'total_encontrado': len(alunos_json),
            'termo_busca': termo_busca
        }
        
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return {
            'success': False,
            'message': f'Erro na busca: {str(e)}',
            'alunos': [],
            'total_encontrado': 0
        }

def testar_diferentes_buscas():
    """Testa diferentes cenários de busca"""
    print("🧪 Testando diferentes cenários de busca...\n")
    
    # Teste 1: Admin sem filtro
    print("=" * 50)
    print("TESTE 1: Admin sem filtro")
    print("=" * 50)
    resultado1 = simular_busca_alunos('', 'admin')
    
    # Teste 2: Admin com filtro "joão"
    print("\n" + "=" * 50)
    print("TESTE 2: Admin com filtro 'joão'")
    print("=" * 50)
    resultado2 = simular_busca_alunos('joão', 'admin')
    
    # Teste 3: Usuário sem filtro
    print("\n" + "=" * 50)
    print("TESTE 3: Usuário sem filtro")
    print("=" * 50)
    resultado3 = simular_busca_alunos('', 'usuario')
    
    # Teste 4: Usuário com filtro "alexandre"
    print("\n" + "=" * 50)
    print("TESTE 4: Usuário com filtro 'alexandre'")
    print("=" * 50)
    resultado4 = simular_busca_alunos('alexandre', 'usuario')
    
    # Resumo
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)
    print(f"Admin sem filtro: {resultado1['total_encontrado']} alunos")
    print(f"Admin com 'joão': {resultado2['total_encontrado']} alunos")
    print(f"Usuário sem filtro: {resultado3['total_encontrado']} alunos")
    print(f"Usuário com 'alexandre': {resultado4['total_encontrado']} alunos")
    
    print("\n✅ Todos os testes concluídos!")

if __name__ == "__main__":
    testar_diferentes_buscas()

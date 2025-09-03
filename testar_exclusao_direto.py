#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def testar_exclusao_direto():
    """Testa a exclusão de aluno diretamente no banco"""
    
    # Configurações do banco
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'postgres'),
        'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
    }
    
    try:
        print("Conectando ao banco de dados...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Verificar se existe aluno com ID 454
        print("\n🔍 Verificando aluno ID 454...")
        cursor.execute("SELECT id, nome FROM alunos WHERE id = %s", (454,))
        aluno = cursor.fetchone()
        
        if aluno:
            print(f"✅ Aluno encontrado: {aluno[1]} (ID: {aluno[0]})")
            
            # Verificar registros de presença
            print("\n📋 Verificando registros de presença...")
            cursor.execute("SELECT COUNT(*) FROM presencas WHERE aluno_id = %s", (str(454),))
            total_presencas = cursor.fetchone()[0]
            print(f"  Total de registros de presença: {total_presencas}")
            
            if total_presencas > 0:
                print("  ⚠️  Há registros de presença que precisam ser removidos primeiro")
                cursor.execute("DELETE FROM presencas WHERE aluno_id = %s", (str(454),))
                print(f"  ✅ {total_presencas} registros de presença removidos")
            
            # Tentar excluir o aluno
            print("\n🗑️  Tentando excluir o aluno...")
            cursor.execute("DELETE FROM alunos WHERE id = %s", (454,))
            
            if cursor.rowcount > 0:
                conn.commit()
                print("✅ Aluno excluído com sucesso!")
            else:
                print("❌ Nenhum aluno foi excluído")
                
        else:
            print("❌ Aluno com ID 454 não encontrado")
            
            # Listar alguns alunos disponíveis
            print("\n📋 Primeiros 5 alunos disponíveis:")
            cursor.execute("SELECT id, nome FROM alunos ORDER BY id LIMIT 5")
            alunos = cursor.fetchall()
            for aluno in alunos:
                print(f"  - ID: {aluno[0]}, Nome: {aluno[1]}")
        
        cursor.close()
        conn.close()
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

if __name__ == "__main__":
    testar_exclusao_direto()
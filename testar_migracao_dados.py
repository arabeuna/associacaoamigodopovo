#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste - Migração de Dados para Produção
Testa a extração de dados do SQLite local e a migração
"""

import os
import sys
import json
from datetime import datetime

def testar_arquivo_json():
    """Testa se o arquivo dados_alunos.json existe e tem dados"""
    print("📄 Testando arquivo dados_alunos.json...")
    
    arquivo = 'dados_alunos.json'
    if not os.path.exists(arquivo):
        print("❌ Arquivo dados_alunos.json não encontrado")
        return False
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        print(f"✅ Arquivo JSON encontrado com {len(dados)} registros")
        
        # Mostrar exemplo de registro
        if dados:
            primeiro = dados[0]
            print(f"📋 Exemplo de registro:")
            print(f"   Nome: {primeiro.get('nome', 'N/A')}")
            print(f"   ID Único: {primeiro.get('id_unico', 'N/A')}")
            print(f"   Atividade: {primeiro.get('atividade', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo JSON: {e}")
        return False

def testar_postgresql_local():
    """Testa a extração de dados do PostgreSQL local"""
    print("\n🗄️ Testando extração do PostgreSQL local...")
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        # Carregar configurações locais
        load_dotenv()
        
        # Configurações do PostgreSQL local
        db_config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'port': os.environ.get('DB_PORT', '5432'),
            'user': os.environ.get('DB_USER', 'postgres'),
            'password': os.environ.get('DB_PASSWORD', 'admin123'),
            'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
        }
        
        print(f"🔗 Tentando conectar: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela alunos
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'alunos'
        """)
        colunas = cursor.fetchall()
        print(f"📊 Estrutura da tabela alunos: {len(colunas)} colunas")
        
        # Contar alunos ativos
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE ativo = true")
        total_alunos = cursor.fetchone()[0]
        print(f"👥 Total de alunos ativos: {total_alunos}")
        
        # Testar extração com JOIN
        cursor.execute("""
            SELECT a.id_unico, a.nome, a.telefone, a.endereco, a.email, 
                   a.data_nascimento, a.data_cadastro, a.titulo_eleitor,
                   at.nome as atividade_nome, a.status_frequencia, a.observacoes, a.ativo
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            WHERE a.ativo = true
            LIMIT 3
        """)
        
        exemplos = cursor.fetchall()
        print(f"📋 Exemplos de registros extraídos:")
        for i, row in enumerate(exemplos, 1):
            print(f"   {i}. {row[1]} - {row[8] or 'Sem atividade'} - ID: {row[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao acessar PostgreSQL: {e}")
        return False

def testar_funcao_extracao():
    """Testa a função de extração implementada no migrate_production.py"""
    print("\n🔧 Testando função de extração...")
    
    try:
        # Importar a função do script de migração
        sys.path.append('.')
        from migrate_production import extrair_alunos_postgresql
        
        # Executar extração
        alunos_extraidos = extrair_alunos_postgresql()
        
        if alunos_extraidos:
            print(f"✅ Função de extração funcionando: {len(alunos_extraidos)} alunos")
            
            # Mostrar exemplo
            primeiro = alunos_extraidos[0]
            print(f"📋 Exemplo de aluno extraído:")
            print(f"   Nome: {primeiro.get('nome', 'N/A')}")
            print(f"   ID Único: {primeiro.get('id_unico', 'N/A')}")
            print(f"   Atividade: {primeiro.get('atividade', 'N/A')}")
            print(f"   Telefone: {primeiro.get('telefone', 'N/A')}")
            
            return True
        else:
            print("❌ Função de extração não retornou dados")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar função de extração: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 TESTE DE MIGRAÇÃO DE DADOS PARA PRODUÇÃO")
    print("=" * 50)
    
    resultados = {
        'json': testar_arquivo_json(),
        'postgresql': testar_postgresql_local(),
        'funcao': testar_funcao_extracao()
    }
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print("=" * 50)
    
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"  {teste.upper()}: {status}")
    
    todos_passaram = all(resultados.values())
    
    if todos_passaram:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A migração de dados está funcionando corretamente")
        print("🚀 Os dados do localhost serão migrados para produção")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima antes do deploy")
    
    return todos_passaram

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
#!/usr/bin/env python3
"""
Script de teste pré-produção
Verifica se o sistema está pronto para deploy
"""

import os
import sys
from dotenv import load_dotenv
import importlib.util

def verificar_arquivos_essenciais():
    """Verifica se todos os arquivos essenciais existem"""
    print("🔍 Verificando arquivos essenciais...")
    
    arquivos_essenciais = [
        '.env.production',
        'migrate_production.py',
        'render.yaml',
        'requirements.txt',
        'app.py',
        'models.py',
        'Procfile'
    ]
    
    arquivos_faltando = []
    for arquivo in arquivos_essenciais:
        if os.path.exists(arquivo):
            print(f"  ✅ {arquivo}")
        else:
            print(f"  ❌ {arquivo} - FALTANDO")
            arquivos_faltando.append(arquivo)
    
    return len(arquivos_faltando) == 0

def verificar_dependencias():
    """Verifica se o requirements.txt contém as dependências necessárias"""
    print("\n📦 Verificando requirements.txt...")
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        dependencias_necessarias = [
            'Flask',
            'gunicorn',
            'SQLAlchemy', 
            'psycopg2-binary',
            'pandas',
            'openpyxl',
            'python-dotenv'
        ]
        
        dependencias_faltando = []
        for dep in dependencias_necessarias:
            if dep.lower() in conteudo.lower():
                print(f"  ✅ {dep}")
            else:
                print(f"  ❌ {dep} - NÃO ENCONTRADO")
                dependencias_faltando.append(dep)
        
        print(f"  ✅ Requirements.txt contém {len(dependencias_necessarias) - len(dependencias_faltando)}/{len(dependencias_necessarias)} dependências")
        return len(dependencias_faltando) == 0
        
    except Exception as e:
        print(f"  ❌ Erro ao verificar requirements.txt: {e}")
        return False

def verificar_configuracoes():
    """Verifica configurações de produção"""
    print("\n⚙️ Verificando configurações...")
    
    # Carregar .env.production
    load_dotenv('.env.production')
    
    configs_necessarias = [
        'DB_HOST',
        'DB_PORT', 
        'DB_USER',
        'DB_PASSWORD',
        'DB_NAME',
        'DATABASE_URL',
        'SECRET_KEY',
        'FLASK_ENV',
        'FLASK_DEBUG'
    ]
    
    configs_ok = True
    for config in configs_necessarias:
        valor = os.getenv(config)
        if valor and valor != f"${{{config}}}":
            print(f"  ✅ {config} = {valor[:20]}..." if len(str(valor)) > 20 else f"  ✅ {config} = {valor}")
        else:
            print(f"  ⚠️ {config} - Será definido pelo Render")
    
    # Verificar configurações específicas
    flask_env = os.getenv('FLASK_ENV')
    flask_debug = os.getenv('FLASK_DEBUG')
    
    if flask_env == 'production':
        print(f"  ✅ FLASK_ENV = production")
    else:
        print(f"  ⚠️ FLASK_ENV = {flask_env} (deveria ser 'production')")
        
    if flask_debug == 'False':
        print(f"  ✅ FLASK_DEBUG = False")
    else:
        print(f"  ⚠️ FLASK_DEBUG = {flask_debug} (deveria ser 'False')")
    
    return configs_ok

def verificar_script_migracao():
    """Verifica se o script de migração está funcional"""
    print("\n🔄 Verificando script de migração...")
    
    try:
        # Verificar se o script pode ser importado
        spec = importlib.util.spec_from_file_location("migrate_production", "migrate_production.py")
        migrate_module = importlib.util.module_from_spec(spec)
        
        # Verificar se as funções principais existem
        funcoes_necessarias = [
            'verificar_conexao_db',
            'criar_tabelas_se_necessario',
            'migrar_usuarios_basicos',
            'migrar_atividades_basicas',
            'executar_migracao_producao'
        ]
        
        spec.loader.exec_module(migrate_module)
        
        for funcao in funcoes_necessarias:
            if hasattr(migrate_module, funcao):
                print(f"  ✅ Função {funcao} encontrada")
            else:
                print(f"  ❌ Função {funcao} não encontrada")
                return False
                
        print("  ✅ Script de migração está completo")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao verificar script de migração: {e}")
        return False

def verificar_render_config():
    """Verifica configuração do Render"""
    print("\n🚀 Verificando configuração do Render...")
    
    try:
        with open('render.yaml', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        # Verificar elementos essenciais
        elementos_necessarios = [
            'type: web',
            'env: python',
            'buildCommand:',
            'migrate_production.py',
            'startCommand: gunicorn app:app',
            'type: postgres',
            'healthCheckPath: /health'
        ]
        
        for elemento in elementos_necessarios:
            if elemento in conteudo:
                print(f"  ✅ {elemento}")
            else:
                print(f"  ❌ {elemento} - NÃO ENCONTRADO")
                return False
                
        print("  ✅ Configuração do Render está correta")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao verificar render.yaml: {e}")
        return False

def main():
    """Executa todos os testes pré-produção"""
    print("🔧 TESTE PRÉ-PRODUÇÃO - Sistema Academia Amigo do Povo")
    print("=" * 60)
    
    testes = [
        ("Arquivos Essenciais", verificar_arquivos_essenciais),
        ("Dependências", verificar_dependencias),
        ("Configurações", verificar_configuracoes),
        ("Script de Migração", verificar_script_migracao),
        ("Configuração Render", verificar_render_config)
    ]
    
    resultados = []
    
    for nome, teste in testes:
        try:
            resultado = teste()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"❌ Erro no teste {nome}: {e}")
            resultados.append((nome, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print("=" * 60)
    
    todos_ok = True
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"  {nome}: {status}")
        if not resultado:
            todos_ok = False
    
    print("\n" + "=" * 60)
    if todos_ok:
        print("🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
        print("✅ Todos os testes passaram")
        print("🚀 Pode fazer o push para deploy")
    else:
        print("⚠️ SISTEMA NÃO ESTÁ PRONTO")
        print("❌ Alguns testes falharam")
        print("🔧 Corrija os problemas antes do deploy")
    
    print("=" * 60)
    return todos_ok

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
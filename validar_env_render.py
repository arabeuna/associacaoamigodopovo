#!/usr/bin/env python3
"""
Script para validar variáveis de ambiente no Render
Este script verifica se todas as variáveis necessárias estão configuradas corretamente
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

def carregar_variaveis_ambiente():
    """Carrega variáveis de ambiente seguindo a mesma lógica do app.py"""
    if os.path.exists('.env.production'):
        load_dotenv('.env.production')
        print("✅ Carregando variáveis de ambiente de produção (.env.production)")
        return 'production'
    else:
        load_dotenv()
        print("✅ Carregando variáveis de ambiente de desenvolvimento (.env)")
        return 'development'

def validar_variaveis_obrigatorias():
    """Valida se todas as variáveis obrigatórias estão definidas"""
    variaveis_obrigatorias = {
        'MONGO_USERNAME': 'Nome de usuário do MongoDB',
        'MONGO_PASSWORD': 'Senha do MongoDB',
        'MONGO_CLUSTER': 'Cluster do MongoDB',
        'MONGO_DATABASE': 'Nome do banco de dados',
        'MONGO_URI': 'URI completa de conexão',
        'SECRET_KEY': 'Chave secreta do Flask',
        'FLASK_ENV': 'Ambiente do Flask',
        'FLASK_DEBUG': 'Debug do Flask'
    }
    
    print("\n🔍 Validando variáveis de ambiente obrigatórias:")
    print("=" * 60)
    
    todas_definidas = True
    for var, descricao in variaveis_obrigatorias.items():
        valor = os.environ.get(var)
        if valor:
            # Mascarar senhas e chaves sensíveis
            if 'PASSWORD' in var or 'SECRET' in var:
                valor_exibido = f"{valor[:4]}...{valor[-4:]}" if len(valor) > 8 else "***"
            else:
                valor_exibido = valor
            print(f"✅ {var:<15}: {valor_exibido}")
        else:
            print(f"❌ {var:<15}: NÃO DEFINIDA ({descricao})")
            todas_definidas = False
    
    return todas_definidas

def testar_conexao_mongodb():
    """Testa a conexão com MongoDB usando as variáveis de ambiente"""
    print("\n🔗 Testando conexão com MongoDB Atlas:")
    print("=" * 60)
    
    # Obter variáveis
    mongo_uri = os.environ.get('MONGO_URI')
    mongo_username = os.environ.get('MONGO_USERNAME')
    mongo_password = os.environ.get('MONGO_PASSWORD')
    mongo_cluster = os.environ.get('MONGO_CLUSTER')
    mongo_database = os.environ.get('MONGO_DATABASE')
    
    if not mongo_uri:
        print("❌ MONGO_URI não definida")
        return False
    
    # URIs para testar (mesma lógica do models.py)
    uris_para_testar = [
        mongo_uri,
        f'mongodb+srv://{mongo_username}:{mongo_password}@cluster0.mongodb.net/{mongo_database}?retryWrites=true&w=majority',
        f'mongodb+srv://{mongo_username}:{mongo_password}@cluster0.mongodb.net/?retryWrites=true&w=majority'
    ]
    
    for i, uri in enumerate(uris_para_testar):
        try:
            print(f"🔄 Tentativa {i+1}: Testando conexão...")
            
            # Mascarar URI para exibição
            uri_masked = uri.replace(mongo_password, "***") if mongo_password else uri
            print(f"   URI: {uri_masked}")
            
            client = MongoClient(uri, serverSelectionTimeoutMS=10000)
            db = client[mongo_database]
            
            # Testar conexão
            result = client.admin.command('ping')
            print(f"✅ Conexão bem-sucedida! Ping result: {result}")
            
            # Testar acesso ao banco
            collections = db.list_collection_names()
            print(f"📊 Collections encontradas: {len(collections)}")
            if collections:
                print(f"   Exemplos: {collections[:3]}")
            
            client.close()
            return True
            
        except Exception as e:
            print(f"❌ Tentativa {i+1} falhou: {str(e)}")
            if i < len(uris_para_testar) - 1:
                print("🔄 Tentando próxima URI...")
            continue
    
    return False

def verificar_configuracao_render():
    """Verifica configurações específicas do Render"""
    print("\n🚀 Verificando configuração do Render:")
    print("=" * 60)
    
    # Verificar se estamos em ambiente de produção
    flask_env = os.environ.get('FLASK_ENV', 'development')
    flask_debug = os.environ.get('FLASK_DEBUG', 'True')
    
    print(f"🌍 Ambiente Flask: {flask_env}")
    print(f"🐛 Debug Flask: {flask_debug}")
    
    if flask_env == 'production':
        print("✅ Configurado para produção")
        if flask_debug.lower() in ['false', '0', 'no']:
            print("✅ Debug desabilitado (recomendado para produção)")
        else:
            print("⚠️ Debug habilitado em produção (não recomendado)")
    else:
        print("⚠️ Ambiente não é produção")
    
    # Verificar variáveis específicas do Render
    render_vars = {
        'PORT': 'Porta do servidor',
        'PYTHON_VERSION': 'Versão do Python',
        'RENDER': 'Indicador do ambiente Render'
    }
    
    print("\n🔧 Variáveis específicas do Render:")
    for var, desc in render_vars.items():
        valor = os.environ.get(var)
        if valor:
            print(f"✅ {var}: {valor}")
        else:
            print(f"ℹ️ {var}: Não definida ({desc})")

def main():
    """Função principal"""
    print("🔍 VALIDADOR DE VARIÁVEIS DE AMBIENTE - RENDER")
    print("=" * 60)
    
    # Carregar variáveis
    ambiente = carregar_variaveis_ambiente()
    
    # Validar variáveis obrigatórias
    variaveis_ok = validar_variaveis_obrigatorias()
    
    # Verificar configuração do Render
    verificar_configuracao_render()
    
    # Testar conexão MongoDB
    conexao_ok = testar_conexao_mongodb()
    
    # Resumo final
    print("\n📋 RESUMO DA VALIDAÇÃO:")
    print("=" * 60)
    print(f"🌍 Ambiente detectado: {ambiente}")
    print(f"📝 Variáveis de ambiente: {'✅ OK' if variaveis_ok else '❌ PROBLEMAS'}")
    print(f"🔗 Conexão MongoDB: {'✅ OK' if conexao_ok else '❌ FALHOU'}")
    
    if variaveis_ok and conexao_ok:
        print("\n🎉 TODAS AS VALIDAÇÕES PASSARAM!")
        print("✅ O ambiente está configurado corretamente para o Render")
        sys.exit(0)
    else:
        print("\n⚠️ PROBLEMAS ENCONTRADOS!")
        if not variaveis_ok:
            print("❌ Algumas variáveis de ambiente estão faltando")
        if not conexao_ok:
            print("❌ Não foi possível conectar ao MongoDB Atlas")
            print("\n💡 Possíveis soluções:")
            print("   - Verificar se o cluster MongoDB Atlas está ativo")
            print("   - Confirmar credenciais (username/password)")
            print("   - Verificar whitelist de IPs (0.0.0.0/0 para Render)")
            print("   - Cluster M0 pode estar pausado após 60 dias")
        sys.exit(1)

if __name__ == '__main__':
    main()
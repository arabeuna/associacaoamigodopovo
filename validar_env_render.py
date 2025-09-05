#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para validar variáveis de ambiente do Render
e identificar possíveis problemas de configuração
"""

import os
import sys
from dotenv import load_dotenv
import pymongo
from urllib.parse import quote_plus

print("🔍 VALIDAÇÃO DAS VARIÁVEIS DE AMBIENTE RENDER")
print("="*60)

# Carregar variáveis de ambiente de produção
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
    print("✅ Arquivo .env.production carregado")
else:
    print("❌ Arquivo .env.production não encontrado")
    sys.exit(1)

print("\n📋 VERIFICAÇÃO DAS VARIÁVEIS CRÍTICAS:")
print("-" * 40)

# Variáveis críticas para verificar
variables_to_check = [
    'MONGO_URI',
    'MONGO_DATABASE', 
    'SECRET_KEY',
    'FLASK_ENV',
    'PORT'
]

for var in variables_to_check:
    value = os.getenv(var)
    if value:
        if var == 'MONGO_URI':
            # Mascarar senha na URI
            masked_uri = value
            if '@' in masked_uri:
                parts = masked_uri.split('@')
                if ':' in parts[0]:
                    user_pass = parts[0].split('//')[-1]
                    if ':' in user_pass:
                        user, password = user_pass.split(':', 1)
                        masked_password = '*' * len(password)
                        masked_uri = masked_uri.replace(password, masked_password)
            print(f"✅ {var}: {masked_uri}")
        elif var == 'SECRET_KEY':
            print(f"✅ {var}: {'*' * len(value)} (mascarado)")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: NÃO DEFINIDA")

print("\n🔗 TESTE DE CONEXÃO MONGODB:")
print("-" * 40)

try:
    # Testar conexão com MongoDB
    mongodb_uri = os.getenv('MONGO_URI')
    db_name = os.getenv('MONGO_DATABASE')
    
    if not mongodb_uri:
        print("❌ MONGO_URI não está definida")
        sys.exit(1)
    
    if not db_name:
        print("❌ MONGO_DATABASE não está definida")
        sys.exit(1)
    
    print(f"🔌 Tentando conectar ao MongoDB...")
    print(f"📊 Database: {db_name}")
    
    # Criar cliente MongoDB
    client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
    
    # Testar conexão
    client.admin.command('ping')
    print("✅ Conexão com MongoDB estabelecida com sucesso")
    
    # Acessar database
    db = client[db_name]
    print(f"✅ Database '{db_name}' acessada")
    
    # Verificar coleções
    collections = db.list_collection_names()
    print(f"📚 Coleções encontradas: {len(collections)}")
    for collection in collections:
        print(f"   - {collection}")
    
    # Verificar dados de alunos
    if 'alunos' in collections:
        alunos_count = db.alunos.count_documents({})
        print(f"👥 Total de alunos na coleção: {alunos_count}")
        
        if alunos_count > 0:
            # Pegar um exemplo de aluno
            sample_aluno = db.alunos.find_one()
            print(f"📝 Exemplo de aluno (campos): {list(sample_aluno.keys()) if sample_aluno else 'Nenhum'}")
            
            # Verificar se há alunos com dados básicos
            alunos_com_nome = db.alunos.count_documents({'nome': {'$exists': True, '$ne': ''}})
            print(f"✅ Alunos com nome: {alunos_com_nome}")
            
            alunos_ativos = db.alunos.count_documents({'status': 'ativo'})
            print(f"✅ Alunos ativos: {alunos_ativos}")
        else:
            print("❌ PROBLEMA: Coleção de alunos está vazia")
    else:
        print("❌ PROBLEMA: Coleção 'alunos' não encontrada")
    
    # Verificar outras coleções importantes
    for col_name in ['turmas', 'atividades', 'presencas']:
        if col_name in collections:
            count = db[col_name].count_documents({})
            print(f"📊 {col_name.capitalize()}: {count} documentos")
        else:
            print(f"⚠️  Coleção '{col_name}' não encontrada")
    
    client.close()
    print("✅ Conexão fechada")
    
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"❌ ERRO: Timeout na conexão com MongoDB")
    print(f"🔍 Detalhes: {e}")
    print("💡 Possíveis causas:")
    print("   - URI de conexão incorreta")
    print("   - Problemas de rede no Render")
    print("   - MongoDB Atlas com restrições de IP")
    print("   - Credenciais inválidas")
except pymongo.errors.ConfigurationError as e:
    print(f"❌ ERRO: Configuração inválida do MongoDB")
    print(f"🔍 Detalhes: {e}")
except pymongo.errors.OperationFailure as e:
    print(f"❌ ERRO: Falha na autenticação")
    print(f"🔍 Detalhes: {e}")
    print("💡 Verifique as credenciais no MongoDB Atlas")
except Exception as e:
    print(f"❌ ERRO INESPERADO: {e}")
    import traceback
    traceback.print_exc()

print("\n🌐 VERIFICAÇÃO DE AMBIENTE:")
print("-" * 40)

# Verificar ambiente Flask
flask_env = os.getenv('FLASK_ENV', 'production')
print(f"🏗️  FLASK_ENV: {flask_env}")

# Verificar porta
port = os.getenv('PORT', '5000')
print(f"🔌 PORT: {port}")

# Verificar se estamos no Render
if os.getenv('RENDER'):
    print("✅ Executando no ambiente Render")
    print(f"🏷️  RENDER_SERVICE_NAME: {os.getenv('RENDER_SERVICE_NAME', 'N/A')}")
    print(f"🔗 RENDER_EXTERNAL_URL: {os.getenv('RENDER_EXTERNAL_URL', 'N/A')}")
else:
    print("⚠️  Não detectado ambiente Render (executando localmente)")

print("\n💡 RECOMENDAÇÕES PARA O RENDER:")
print("-" * 40)
print("1. Verificar se todas as variáveis de ambiente estão configuradas no painel do Render")
print("2. Confirmar se o MongoDB Atlas permite conexões do IP do Render (0.0.0.0/0)")
print("3. Verificar se não há timeout nas conexões de rede")
print("4. Confirmar se o build e deploy foram executados corretamente")
print("5. Verificar logs do Render para erros específicos")

print("\n🎯 PRÓXIMOS PASSOS:")
print("-" * 40)
if 'alunos_count' in locals() and alunos_count > 0:
    print("✅ Dados estão presentes no MongoDB")
    print("🔍 O problema pode estar na aplicação Flask ou no ambiente Render")
    print("💡 Sugestões:")
    print("   - Verificar logs da aplicação no Render")
    print("   - Testar endpoints específicos")
    print("   - Verificar se há problemas de cache ou sessão")
else:
    print("❌ Dados não encontrados no MongoDB")
    print("🔍 O problema está na conexão ou nos dados")
    print("💡 Sugestões:")
    print("   - Recarregar dados no MongoDB Atlas")
    print("   - Verificar configurações de rede")
    print("   - Confirmar credenciais de acesso")

print("\n" + "="*60)
print("🏁 VALIDAÇÃO CONCLUÍDA")
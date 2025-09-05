#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar conexão MongoDB no ambiente de produção
Verifica se as variáveis de ambiente estão sendo carregadas corretamente
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

print("🔍 TESTE DE CONEXÃO MONGODB - AMBIENTE DE PRODUÇÃO")
print("=" * 60)

# 1. Verificar se .env.production existe
if os.path.exists('.env.production'):
    print("✅ Arquivo .env.production encontrado")
    load_dotenv('.env.production')
    print("✅ Variáveis de ambiente carregadas de .env.production")
else:
    print("❌ Arquivo .env.production NÃO encontrado")
    load_dotenv()
    print("⚠️ Usando variáveis de ambiente padrão")

print("\n📋 VARIÁVEIS DE AMBIENTE CARREGADAS:")
print("-" * 40)

# 2. Verificar variáveis de ambiente
vars_to_check = [
    'MONGO_USERNAME',
    'MONGO_PASSWORD', 
    'MONGO_CLUSTER',
    'MONGO_DATABASE',
    'MONGO_URI',
    'FLASK_ENV',
    'SECRET_KEY'
]

for var in vars_to_check:
    value = os.environ.get(var)
    if var == 'MONGO_PASSWORD' and value:
        # Mascarar senha
        masked_value = value[:3] + '*' * (len(value) - 6) + value[-3:] if len(value) > 6 else '*' * len(value)
        print(f"{var}: {masked_value}")
    elif var == 'SECRET_KEY' and value:
        # Mascarar chave secreta
        masked_value = value[:5] + '*' * (len(value) - 10) + value[-5:] if len(value) > 10 else '*' * len(value)
        print(f"{var}: {masked_value}")
    else:
        print(f"{var}: {value}")

# 3. Construir URI do MongoDB
MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
MONGO_CLUSTER = os.environ.get('MONGO_CLUSTER')
MONGO_DATABASE = os.environ.get('MONGO_DATABASE')
MONGO_URI = os.environ.get('MONGO_URI')

print("\n🔗 TESTE DE CONEXÃO MONGODB:")
print("-" * 40)

if not MONGO_URI:
    if MONGO_USERNAME and MONGO_PASSWORD and MONGO_CLUSTER and MONGO_DATABASE:
        MONGO_URI = f'mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_DATABASE}?retryWrites=true&w=majority'
        print("✅ URI construída a partir das variáveis individuais")
    else:
        print("❌ Variáveis de ambiente insuficientes para construir URI")
        sys.exit(1)
else:
    print("✅ URI carregada diretamente da variável MONGO_URI")

# Mascarar URI para exibição
if MONGO_URI:
    # Extrair e mascarar a senha da URI
    import re
    uri_pattern = r'mongodb\+srv://([^:]+):([^@]+)@(.+)'
    match = re.match(uri_pattern, MONGO_URI)
    if match:
        username, password, rest = match.groups()
        masked_password = password[:3] + '*' * (len(password) - 6) + password[-3:] if len(password) > 6 else '*' * len(password)
        masked_uri = f'mongodb+srv://{username}:{masked_password}@{rest}'
        print(f"URI: {masked_uri}")
    else:
        print(f"URI: {MONGO_URI[:20]}...{MONGO_URI[-20:]}")

# 4. Testar conexão
print("\n🔄 TESTANDO CONEXÃO...")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    
    # Testar ping
    client.admin.command('ping')
    print("✅ Ping ao MongoDB Atlas: SUCESSO")
    
    # Conectar ao banco
    db = client[MONGO_DATABASE]
    print(f"✅ Conectado ao banco: {MONGO_DATABASE}")
    
    # Listar coleções
    collections = db.list_collection_names()
    print(f"✅ Coleções encontradas: {len(collections)}")
    for col in collections:
        count = db[col].count_documents({})
        print(f"   - {col}: {count} documentos")
    
    # Testar consulta de alunos
    alunos_count = db.alunos.count_documents({})
    print(f"\n📊 DADOS ENCONTRADOS:")
    print(f"   - Total de alunos: {alunos_count}")
    
    if alunos_count > 0:
        # Mostrar alguns alunos
        alunos_sample = list(db.alunos.find({}, {'nome': 1, 'atividade': 1}).limit(5))
        print(f"   - Primeiros 5 alunos:")
        for i, aluno in enumerate(alunos_sample, 1):
            nome = aluno.get('nome', 'N/A')
            atividade = aluno.get('atividade', 'N/A')
            print(f"     {i}. {nome} - {atividade}")
    
    print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("✅ MongoDB Atlas está funcionando corretamente")
    
except Exception as e:
    print(f"❌ ERRO na conexão: {e}")
    print("\n🔧 POSSÍVEIS SOLUÇÕES:")
    print("1. Verificar se o cluster MongoDB Atlas está ativo")
    print("2. Confirmar credenciais (username/password)")
    print("3. Verificar whitelist de IPs no MongoDB Atlas")
    print("4. Verificar se as variáveis de ambiente estão corretas")
    sys.exit(1)

finally:
    if 'client' in locals():
        client.close()
        print("🔒 Conexão MongoDB fechada")

print("\n" + "=" * 60)
print("TESTE FINALIZADO")
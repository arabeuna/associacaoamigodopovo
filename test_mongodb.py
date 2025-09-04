#!/usr/bin/env python3
"""Script para testar a conexão com MongoDB Atlas"""

from models import init_mongodb, verificar_conexao
import os

print('=== TESTE DE CONEXÃO MONGODB ATLAS ===')
print(f'Username: {os.environ.get("MONGO_USERNAME", "amigodopovoassociacao_db_user")}')
print(f'Cluster: {os.environ.get("MONGO_CLUSTER", "cluster0.mongodb.net")}')
print(f'Database: {os.environ.get("MONGO_DATABASE", "amigodopovoassociacao_db")}')
print()

print('Iniciando conexão...')
db = init_mongodb()

if db:
    print('✅ Conexão inicializada com sucesso!')
    print('Verificando conexão...')
    if verificar_conexao():
        print('✅ Conexão verificada com sucesso!')
        print('🎉 MongoDB Atlas está funcionando!')
    else:
        print('❌ Falha na verificação da conexão')
else:
    print('❌ Falha na inicialização da conexão')
    print('Verifique as credenciais do MongoDB Atlas')

print('\n=== FIM DO TESTE ===')
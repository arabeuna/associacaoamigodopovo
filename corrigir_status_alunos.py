#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o status dos alunos no MongoDB
Definindo todos os alunos como ativos (ativo: true)
"""

import os
import sys
from dotenv import load_dotenv
import pymongo
from datetime import datetime

print("🔧 CORREÇÃO DO STATUS DOS ALUNOS NO MONGODB")
print("="*60)

# Carregar variáveis de ambiente de produção
if os.path.exists('.env.production'):
    load_dotenv('.env.production')
    print("✅ Arquivo .env.production carregado")
else:
    print("❌ Arquivo .env.production não encontrado")
    sys.exit(1)

try:
    # Conectar ao MongoDB
    mongodb_uri = os.getenv('MONGO_URI')
    db_name = os.getenv('MONGO_DATABASE')
    
    if not mongodb_uri or not db_name:
        print("❌ Variáveis de ambiente MongoDB não encontradas")
        sys.exit(1)
    
    print(f"🔌 Conectando ao MongoDB...")
    client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=10000)
    db = client[db_name]
    
    # Testar conexão
    client.admin.command('ping')
    print("✅ Conexão estabelecida com sucesso")
    
    # Verificar estado atual dos alunos
    print("\n📊 ESTADO ATUAL DOS ALUNOS:")
    print("-" * 40)
    
    total_alunos = db.alunos.count_documents({})
    alunos_ativos = db.alunos.count_documents({'ativo': True})
    alunos_inativos = db.alunos.count_documents({'ativo': False})
    alunos_sem_status = db.alunos.count_documents({'ativo': {'$exists': False}})
    
    print(f"📊 Total de alunos: {total_alunos}")
    print(f"✅ Alunos ativos (ativo: true): {alunos_ativos}")
    print(f"❌ Alunos inativos (ativo: false): {alunos_inativos}")
    print(f"⚠️  Alunos sem campo 'ativo': {alunos_sem_status}")
    
    if alunos_ativos == total_alunos:
        print("\n🎉 TODOS OS ALUNOS JÁ ESTÃO ATIVOS!")
        print("✅ Não é necessário fazer correções")
    else:
        print("\n🔧 INICIANDO CORREÇÃO...")
        print("-" * 40)
        
        # Atualizar todos os alunos para ativo: true
        resultado = db.alunos.update_many(
            {},  # Filtro vazio = todos os documentos
            {
                '$set': {
                    'ativo': True,
                    'data_atualizacao': datetime.now()
                }
            }
        )
        
        print(f"✅ Documentos atualizados: {resultado.modified_count}")
        
        # Verificar resultado
        print("\n📊 ESTADO APÓS CORREÇÃO:")
        print("-" * 40)
        
        alunos_ativos_depois = db.alunos.count_documents({'ativo': True})
        alunos_inativos_depois = db.alunos.count_documents({'ativo': False})
        
        print(f"✅ Alunos ativos: {alunos_ativos_depois}")
        print(f"❌ Alunos inativos: {alunos_inativos_depois}")
        
        if alunos_ativos_depois == total_alunos:
            print("\n🎉 CORREÇÃO REALIZADA COM SUCESSO!")
            print("✅ Todos os alunos agora estão marcados como ativos")
        else:
            print("\n⚠️  CORREÇÃO PARCIAL")
            print(f"❌ Ainda há {alunos_inativos_depois} alunos inativos")
    
    # Mostrar alguns exemplos de alunos
    print("\n📋 EXEMPLOS DE ALUNOS (primeiros 5):")
    print("-" * 40)
    
    exemplos = list(db.alunos.find({}).limit(5))
    for i, aluno in enumerate(exemplos, 1):
        nome = aluno.get('nome', 'N/A')
        ativo = aluno.get('ativo', 'N/A')
        atividade = aluno.get('atividade', 'N/A')
        status_str = "✅ ATIVO" if ativo else "❌ INATIVO"
        print(f"   {i}. {nome} - {atividade} - {status_str}")
    
    client.close()
    print("\n✅ Conexão fechada")
    
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"❌ ERRO: Timeout na conexão com MongoDB")
    print(f"🔍 Detalhes: {e}")
except Exception as e:
    print(f"❌ ERRO INESPERADO: {e}")
    import traceback
    traceback.print_exc()

print("\n💡 PRÓXIMOS PASSOS:")
print("-" * 40)
print("1. Testar a aplicação localmente para verificar se os alunos aparecem")
print("2. Fazer deploy no Render para aplicar as correções em produção")
print("3. Verificar se a interface web agora mostra os 315 alunos")
print("4. Monitorar logs do Render para confirmar funcionamento")

print("\n" + "="*60)
print("🏁 CORREÇÃO CONCLUÍDA")
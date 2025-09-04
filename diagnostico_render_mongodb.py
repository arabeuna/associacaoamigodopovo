#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico de Conexão MongoDB Atlas para Render
Associação Amigo do Povo

Este script testa a conexão MongoDB Atlas usando exatamente as mesmas
credenciais configuradas no render.yaml para identificar problemas.
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime
import traceback

def testar_conexao_render():
    """Testa conexão usando credenciais do render.yaml"""
    print("🔍 DIAGNÓSTICO: Conexão MongoDB Atlas para Render")
    print("=" * 60)
    
    # Credenciais exatas do render.yaml
    MONGO_USERNAME = "amigodopovoassociacao_db_user"
    MONGO_PASSWORD = "Lp816oHvdl2nHVeO"
    MONGO_CLUSTER = "cluster0.ifuorpv.mongodb.net"
    MONGO_DATABASE = "amigodopovoassociacao_db"
    MONGO_URI = "mongodb+srv://amigodopovoassociacao_db_user:Lp816oHvdl2nHVeO@cluster0.ifuorpv.mongodb.net/amigodopovoassociacao_db?retryWrites=true&w=majority&appName=Cluster0"
    
    print(f"📍 Cluster: {MONGO_CLUSTER}")
    print(f"👤 Usuário: {MONGO_USERNAME}")
    print(f"🗄️ Database: {MONGO_DATABASE}")
    print(f"🔗 URI: {MONGO_URI[:50]}...")
    print()
    
    try:
        print("🔄 Tentando conectar ao MongoDB Atlas...")
        
        # Configurar timeout mais baixo para teste rápido
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000,  # 10 segundos
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Testar conexão
        print("📡 Testando ping ao servidor...")
        client.admin.command('ping')
        print("✅ Ping bem-sucedido!")
        
        # Acessar database
        db = client[MONGO_DATABASE]
        print(f"✅ Conectado ao database: {MONGO_DATABASE}")
        
        # Listar coleções
        print("📋 Listando coleções...")
        collections = db.list_collection_names()
        print(f"✅ Coleções encontradas: {collections}")
        
        # Testar contagem de alunos
        if 'alunos' in collections:
            count_alunos = db.alunos.count_documents({})
            print(f"👥 Total de alunos: {count_alunos}")
            
            if count_alunos > 0:
                # Mostrar um aluno de exemplo
                aluno_exemplo = db.alunos.find_one()
                print(f"📄 Exemplo de aluno: {aluno_exemplo.get('nome', 'N/A')}")
            else:
                print("⚠️ Nenhum aluno encontrado na coleção")
        else:
            print("⚠️ Coleção 'alunos' não encontrada")
        
        # Testar outras coleções
        for collection_name in ['atividades', 'turmas', 'presencas']:
            if collection_name in collections:
                count = db[collection_name].count_documents({})
                print(f"📊 {collection_name}: {count} documentos")
        
        print("\n✅ DIAGNÓSTICO: Conexão MongoDB Atlas FUNCIONANDO!")
        print("🎯 O problema pode estar em:")
        print("   1. Configuração de variáveis de ambiente no Render")
        print("   2. Whitelist de IPs no MongoDB Atlas")
        print("   3. Timeout de conexão no ambiente de produção")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO na conexão MongoDB Atlas:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        print(f"\n🔍 Detalhes do erro:")
        traceback.print_exc()
        
        print(f"\n💡 Possíveis soluções:")
        print(f"   1. Verificar se o cluster MongoDB Atlas está ativo")
        print(f"   2. Verificar whitelist de IPs (permitir 0.0.0.0/0)")
        print(f"   3. Verificar se as credenciais estão corretas")
        print(f"   4. Verificar se o cluster não está pausado")
        
        return False

def verificar_ips_render():
    """Mostra informações sobre IPs do Render"""
    print("\n🌐 INFORMAÇÕES SOBRE IPs DO RENDER")
    print("=" * 40)
    print("📍 Para whitelist no MongoDB Atlas, use:")
    print("   IP: 0.0.0.0/0 (permitir todos os IPs)")
    print("   Ou consulte os IPs específicos do Render em:")
    print("   https://render.com/docs/static-outbound-ip-addresses")
    print()
    print("🔧 No MongoDB Atlas:")
    print("   1. Acesse Network Access")
    print("   2. Clique em 'Add IP Address'")
    print("   3. Selecione 'Allow Access from Anywhere'")
    print("   4. Ou adicione: 0.0.0.0/0")

def main():
    """Função principal"""
    print(f"🕐 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Testar conexão
    sucesso = testar_conexao_render()
    
    # Mostrar informações sobre IPs
    verificar_ips_render()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("✅ RESULTADO: Conexão local funcionando")
        print("🎯 Problema provavelmente está no ambiente Render")
    else:
        print("❌ RESULTADO: Problema na conexão MongoDB")
        print("🔧 Verificar configurações do MongoDB Atlas")
    
    print(f"\n🕐 Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
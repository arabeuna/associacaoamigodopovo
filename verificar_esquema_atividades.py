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

def verificar_esquema_atividades():
    """Verifica a estrutura atual da tabela atividades"""
    print("🔍 Verificando estrutura da tabela 'atividades'...")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco de dados!")
        
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'atividades'
            );
        """)
        
        tabela_existe = cursor.fetchone()[0]
        print(f"📋 Tabela 'atividades' existe: {tabela_existe}")
        
        if not tabela_existe:
            print("❌ Tabela 'atividades' não existe!")
            return
        
        # Obter estrutura da tabela
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'atividades'
            ORDER BY ordinal_position;
        """)
        
        colunas = cursor.fetchall()
        print(f"\n📊 Estrutura da tabela 'atividades':")
        print("   Coluna | Tipo | Nullable | Default")
        print("   -------|------|----------|---------")
        
        for coluna in colunas:
            nome, tipo, nullable, default = coluna
            print(f"   {nome} | {tipo} | {nullable} | {default or 'NULL'}")
        
        # Verificar se a coluna criado_por existe
        colunas_nomes = [col[0] for col in colunas]
        if 'criado_por' in colunas_nomes:
            print(f"\n✅ Coluna 'criado_por' existe na tabela!")
        else:
            print(f"\n❌ Coluna 'criado_por' NÃO existe na tabela!")
            print("   Colunas encontradas:", colunas_nomes)
        
        # Verificar dados na tabela
        cursor.execute("SELECT COUNT(*) FROM atividades")
        total_atividades = cursor.fetchone()[0]
        print(f"\n📈 Total de atividades na tabela: {total_atividades}")
        
        if total_atividades > 0:
            cursor.execute("SELECT id, nome, ativa FROM atividades LIMIT 5")
            atividades = cursor.fetchall()
            print(f"\n📋 Primeiras 5 atividades:")
            for atividade in atividades:
                print(f"   ID: {atividade[0]}, Nome: {atividade[1]}, Ativa: {atividade[2]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_esquema_atividades()

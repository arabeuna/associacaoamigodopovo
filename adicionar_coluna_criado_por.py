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

def adicionar_coluna_criado_por():
    """Adiciona a coluna criado_por à tabela atividades"""
    print("🔧 Adicionando coluna 'criado_por' à tabela 'atividades'...")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco de dados!")
        
        # Verificar se a coluna já existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'atividades' 
                AND column_name = 'criado_por'
            );
        """)
        
        coluna_existe = cursor.fetchone()[0]
        
        if coluna_existe:
            print("✅ Coluna 'criado_por' já existe na tabela!")
            return
        
        # Adicionar a coluna criado_por
        print("📝 Adicionando coluna 'criado_por'...")
        cursor.execute("""
            ALTER TABLE atividades 
            ADD COLUMN criado_por VARCHAR(100) DEFAULT 'admin';
        """)
        
        # Atualizar registros existentes com um valor padrão
        print("🔄 Atualizando registros existentes...")
        cursor.execute("""
            UPDATE atividades 
            SET criado_por = 'admin' 
            WHERE criado_por IS NULL;
        """)
        
        # Confirmar as mudanças
        conn.commit()
        
        print("✅ Coluna 'criado_por' adicionada com sucesso!")
        
        # Verificar a nova estrutura
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'atividades'
            ORDER BY ordinal_position;
        """)
        
        colunas = cursor.fetchall()
        print(f"\n📊 Nova estrutura da tabela 'atividades':")
        print("   Coluna | Tipo | Nullable | Default")
        print("   -------|------|----------|---------")
        
        for coluna in colunas:
            nome, tipo, nullable, default = coluna
            print(f"   {nome} | {tipo} | {nullable} | {default or 'NULL'}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Operação concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    adicionar_coluna_criado_por()

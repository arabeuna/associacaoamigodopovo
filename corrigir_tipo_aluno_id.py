#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def corrigir_tipo_aluno_id():
    """Corrige o tipo da coluna aluno_id na tabela presencas para INTEGER"""
    
    # Configurações do banco
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'postgres'),
        'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
    }
    
    try:
        print("Conectando ao banco de dados...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Verificar o tipo atual da coluna aluno_id
        print("\n🔍 Verificando tipo atual da coluna aluno_id...")
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'presencas' AND column_name = 'aluno_id'
        """)
        
        tipo_atual = cursor.fetchone()[0]
        print(f"  Tipo atual: {tipo_atual}")
        
        if tipo_atual != 'integer':
            print("\n🔧 Alterando tipo da coluna aluno_id para INTEGER...")
            
            # Primeiro, verificar se há dados na tabela
            cursor.execute("SELECT COUNT(*) FROM presencas")
            total_registros = cursor.fetchone()[0]
            
            if total_registros > 0:
                print(f"  ⚠️  Encontrados {total_registros} registros na tabela")
                print("  🗑️  Removendo registros existentes para permitir alteração de tipo...")
                cursor.execute("DELETE FROM presencas")
                print("  ✅ Registros removidos")
            
            # Alterar o tipo da coluna
            cursor.execute("""
                ALTER TABLE presencas 
                ALTER COLUMN aluno_id TYPE INTEGER USING aluno_id::INTEGER
            """)
            
            conn.commit()
            print("  ✅ Tipo da coluna aluno_id alterado para INTEGER")
        else:
            print("  ✅ Coluna aluno_id já é do tipo INTEGER")
        
        # Verificar se a foreign key existe
        print("\n🔗 Verificando foreign key constraint...")
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'presencas' 
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name LIKE '%aluno%'
        """)
        
        fk_constraint = cursor.fetchone()
        if not fk_constraint:
            print("  ➕ Adicionando foreign key constraint...")
            cursor.execute("""
                ALTER TABLE presencas 
                ADD CONSTRAINT fk_presencas_aluno_id 
                FOREIGN KEY (aluno_id) REFERENCES alunos(id)
            """)
            conn.commit()
            print("  ✅ Foreign key constraint adicionada")
        else:
            print(f"  ✅ Foreign key constraint já existe: {fk_constraint[0]}")
        
        cursor.close()
        conn.close()
        print("\n🎉 Correção concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

if __name__ == "__main__":
    corrigir_tipo_aluno_id()
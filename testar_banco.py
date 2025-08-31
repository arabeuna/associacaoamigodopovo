#!/usr/bin/env python3
"""
Script para testar o banco de dados SQLite da Academia Amigo do Povo
"""
import sqlite3
import json
from datetime import datetime

def testar_conexao_banco():
    """Testa a conexão com o banco de dados"""
    try:
        conn = sqlite3.connect('academia_amigo_povo.db')
        cursor = conn.cursor()
        print("✅ Conexão com banco de dados estabelecida com sucesso!")
        return conn, cursor
    except Exception as e:
        print(f"❌ Erro ao conectar com banco de dados: {e}")
        return None, None

def verificar_tabelas(cursor):
    """Verifica se as tabelas existem no banco"""
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        print(f"\n📋 Tabelas encontradas no banco:")
        for tabela in tabelas:
            print(f"   - {tabela[0]}")
        return [t[0] for t in tabelas]
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return []

def contar_registros(cursor, tabela):
    """Conta registros em uma tabela"""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"❌ Erro ao contar registros em {tabela}: {e}")
        return 0

def mostrar_estrutura_tabela(cursor, tabela):
    """Mostra a estrutura de uma tabela"""
    try:
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = cursor.fetchall()
        print(f"\n📊 Estrutura da tabela '{tabela}':")
        for coluna in colunas:
            print(f"   - {coluna[1]} ({coluna[2]})")
    except Exception as e:
        print(f"❌ Erro ao mostrar estrutura de {tabela}: {e}")

def mostrar_amostra_dados(cursor, tabela, limite=5):
    """Mostra uma amostra dos dados de uma tabela"""
    try:
        cursor.execute(f"SELECT * FROM {tabela} LIMIT {limite}")
        registros = cursor.fetchall()
        
        # Obter nomes das colunas
        cursor.execute(f"PRAGMA table_info({tabela})")
        colunas = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📄 Amostra de dados da tabela '{tabela}':")
        for i, registro in enumerate(registros, 1):
            print(f"   Registro {i}:")
            for j, valor in enumerate(registro):
                if j < len(colunas):
                    print(f"     {colunas[j]}: {valor}")
            print()
    except Exception as e:
        print(f"❌ Erro ao mostrar dados de {tabela}: {e}")

def testar_insercao_dados(cursor, conn):
    """Testa inserção de dados no banco"""
    try:
        # Testar inserção de um aluno
        cursor.execute("""
            INSERT OR IGNORE INTO alunos (
                id_unico, nome, data_nascimento, telefone, email, 
                endereco, atividade, turma, data_cadastro, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'TESTE_001', 'Aluno Teste', '1990-01-01', '11999999999',
            'teste@email.com', 'Endereço Teste', 'Musculação', 'Manhã',
            datetime.now().strftime('%Y-%m-%d'), 'Ativo'
        ))
        
        # Testar inserção de uma presença
        cursor.execute("""
            INSERT OR IGNORE INTO presencas (
                aluno_id, data_presenca, horario, atividade, turma, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'TESTE_001', datetime.now().strftime('%Y-%m-%d'), 
            '08:00', 'Musculação', 'Manhã', 'Presença de teste'
        ))
        
        conn.commit()
        print("✅ Dados de teste inseridos com sucesso!")
        
        # Verificar se os dados foram inseridos
        cursor.execute("SELECT COUNT(*) FROM alunos WHERE id_unico = 'TESTE_001'")
        count_alunos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM presencas WHERE aluno_id = 'TESTE_001'")
        count_presencas = cursor.fetchone()[0]
        
        print(f"   - Alunos de teste: {count_alunos}")
        print(f"   - Presenças de teste: {count_presencas}")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados de teste: {e}")

def limpar_dados_teste(cursor, conn):
    """Remove dados de teste do banco"""
    try:
        cursor.execute("DELETE FROM presencas WHERE aluno_id = 'TESTE_001'")
        cursor.execute("DELETE FROM alunos WHERE id_unico = 'TESTE_001'")
        conn.commit()
        print("✅ Dados de teste removidos!")
    except Exception as e:
        print(f"❌ Erro ao remover dados de teste: {e}")

def main():
    """Função principal do teste"""
    print("=" * 60)
    print("    TESTE DO BANCO DE DADOS - ACADEMIA AMIGO DO POVO")
    print("=" * 60)
    
    # Testar conexão
    conn, cursor = testar_conexao_banco()
    if not conn:
        return
    
    # Verificar tabelas
    tabelas = verificar_tabelas(cursor)
    
    if not tabelas:
        print("❌ Nenhuma tabela encontrada no banco!")
        return
    
    # Mostrar estatísticas gerais
    print(f"\n📊 ESTATÍSTICAS DO BANCO:")
    for tabela in tabelas:
        count = contar_registros(cursor, tabela)
        print(f"   - {tabela}: {count} registros")
    
    # Mostrar estrutura das principais tabelas
    tabelas_principais = ['alunos', 'presencas', 'usuarios', 'atividades', 'turmas']
    for tabela in tabelas_principais:
        if tabela in tabelas:
            mostrar_estrutura_tabela(cursor, tabela)
    
    # Mostrar amostra de dados
    for tabela in tabelas_principais:
        if tabela in tabelas:
            mostrar_amostra_dados(cursor, tabela, 3)
    
    # Testar inserção de dados
    print("\n🧪 TESTANDO INSERÇÃO DE DADOS:")
    testar_insercao_dados(cursor, conn)
    
    # Perguntar se quer limpar dados de teste
    resposta = input("\n❓ Deseja remover os dados de teste? (s/n): ").lower()
    if resposta == 's':
        limpar_dados_teste(cursor, conn)
    
    # Fechar conexão
    conn.close()
    print("\n✅ Teste do banco de dados concluído!")

if __name__ == "__main__":
    main()

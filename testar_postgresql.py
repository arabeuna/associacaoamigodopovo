#!/usr/bin/env python3
"""
Script para testar o banco de dados PostgreSQL da Academia Amigo do Povo
"""
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

def carregar_configuracoes():
    """Carrega configurações do arquivo .env"""
    try:
        load_dotenv()
        
        config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'port': os.environ.get('DB_PORT', '5432'),
            'user': os.environ.get('DB_USER', 'postgres'),
            'password': os.environ.get('DB_PASSWORD', 'admin123'),
            'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
        }
        
        print("✅ Configurações carregadas do arquivo .env")
        return config
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        return None

def testar_conexao_postgresql(config):
    """Testa conexão com PostgreSQL"""
    try:
        print(f"\n🔗 Conectando ao PostgreSQL...")
        print(f"   Host: {config['host']}:{config['port']}")
        print(f"   Usuário: {config['user']}")
        print(f"   Banco: {config['database']}")
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Testar versão do PostgreSQL
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Conexão estabelecida!")
        print(f"   Versão: {version.split(',')[0]}")
        
        return conn, cursor
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None, None

def verificar_tabelas(cursor):
    """Verifica se as tabelas existem no banco"""
    try:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
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
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{tabela}'
            ORDER BY ordinal_position;
        """)
        colunas = cursor.fetchall()
        
        print(f"\n📊 Estrutura da tabela '{tabela}':")
        for coluna in colunas:
            nullable = "NULL" if coluna[2] == "YES" else "NOT NULL"
            print(f"   - {coluna[0]} ({coluna[1]}) {nullable}")
    except Exception as e:
        print(f"❌ Erro ao mostrar estrutura de {tabela}: {e}")

def mostrar_amostra_dados(cursor, tabela, limite=3):
    """Mostra uma amostra dos dados de uma tabela"""
    try:
        cursor.execute(f"SELECT * FROM {tabela} LIMIT {limite}")
        registros = cursor.fetchall()
        
        # Obter nomes das colunas
        cursor.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{tabela}'
            ORDER BY ordinal_position;
        """)
        colunas = [col[0] for col in cursor.fetchall()]
        
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
        print("\n🧪 TESTANDO INSERÇÃO DE DADOS:")
        
        # Testar inserção de um aluno
        cursor.execute("""
            INSERT INTO alunos (
                id_unico, nome, telefone, endereco, email, 
                data_nascimento, data_cadastro, atividade_id, turma_id, 
                status_frequencia, observacoes, ativo, data_criacao, criado_por
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON CONFLICT (id_unico) DO NOTHING
        """, (
            'TESTE_001', 'Aluno Teste PostgreSQL 17', '11999999999',
            'Endereço Teste', 'teste@email.com', '1990-01-01', 
            datetime.now().date(), 1, 1, 'Ativo', 'Teste PostgreSQL 17',
            True, datetime.now(), 'sistema'
        ))
        
        # Testar inserção de uma presença
        cursor.execute("""
            INSERT INTO presencas (
                aluno_id, data_presenca, horario, atividade_id, turma_id, 
                observacoes, registrado_por, data_registro
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            'TESTE_001', datetime.now().date(), '08:00', 1, 1,
            'Presença de teste PostgreSQL 17', 'sistema', datetime.now()
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

def testar_consultas_avancadas(cursor):
    """Testa consultas avançadas"""
    try:
        print("\n🔍 TESTANDO CONSULTAS AVANÇADAS:")
        
        # Contar alunos por atividade
        cursor.execute("""
            SELECT a.nome as atividade, COUNT(al.id) as total_alunos
            FROM atividades a
            LEFT JOIN alunos al ON a.id = al.atividade_id
            GROUP BY a.id, a.nome
            ORDER BY total_alunos DESC;
        """)
        
        resultados = cursor.fetchall()
        print("   📊 Alunos por atividade:")
        for atividade, total in resultados:
            print(f"     - {atividade}: {total} alunos")
        
        # Contar presenças por mês
        cursor.execute("""
            SELECT 
                DATE_TRUNC('month', data_presenca) as mes,
                COUNT(*) as total_presencas
            FROM presencas
            WHERE data_presenca >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY DATE_TRUNC('month', data_presenca)
            ORDER BY mes DESC;
        """)
        
        resultados = cursor.fetchall()
        print("   📅 Presenças por mês:")
        for mes, total in resultados:
            print(f"     - {mes.strftime('%B/%Y')}: {total} presenças")
            
    except Exception as e:
        print(f"❌ Erro ao executar consultas avançadas: {e}")

def main():
    """Função principal do teste"""
    print("=" * 70)
    print("    TESTE DO BANCO POSTGRESQL 17 - ACADEMIA AMIGO DO POVO")
    print("=" * 70)
    
    # 1. Carregar configurações
    config = carregar_configuracoes()
    if not config:
        return
    
    # 2. Testar conexão
    conn, cursor = testar_conexao_postgresql(config)
    if not conn:
        return
    
    # 3. Verificar tabelas
    tabelas = verificar_tabelas(cursor)
    if not tabelas:
        print("❌ Nenhuma tabela encontrada no banco!")
        return
    
    # 4. Mostrar estatísticas gerais
    print(f"\n📊 ESTATÍSTICAS DO BANCO:")
    for tabela in tabelas:
        count = contar_registros(cursor, tabela)
        print(f"   - {tabela}: {count} registros")
    
    # 5. Mostrar estrutura das principais tabelas
    tabelas_principais = ['alunos', 'presencas', 'usuarios', 'atividades', 'turmas']
    for tabela in tabelas_principais:
        if tabela in tabelas:
            mostrar_estrutura_tabela(cursor, tabela)
    
    # 6. Mostrar amostra de dados
    for tabela in tabelas_principais:
        if tabela in tabelas:
            mostrar_amostra_dados(cursor, tabela, 2)
    
    # 7. Testar inserção de dados
    testar_insercao_dados(cursor, conn)
    
    # 8. Testar consultas avançadas
    testar_consultas_avancadas(cursor)
    
    # 9. Perguntar se quer limpar dados de teste
    resposta = input("\n❓ Deseja remover os dados de teste? (s/n): ").lower()
    if resposta == 's':
        limpar_dados_teste(cursor, conn)
    
    # 10. Fechar conexão
    conn.close()
    print("\n✅ Teste do PostgreSQL 17 concluído com sucesso!")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Script para migrar dados da planilha CSV para o banco PostgreSQL
"""
import csv
import psycopg2
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Carregar configurações
load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'admin123'),
    'database': os.environ.get('DB_NAME', 'academia_amigo_povo')
}

def gerar_id_unico():
    """Gera um ID único para o aluno"""
    return str(uuid.uuid4()).replace('-', '')[:12]

def converter_data(data_str):
    """Converte string de data para formato PostgreSQL"""
    if not data_str or data_str.strip() == '':
        return None
    
    try:
        # Tentar diferentes formatos de data
        formatos = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d', '%d/%m']
        
        for formato in formatos:
            try:
                return datetime.strptime(data_str.strip(), formato).date()
            except:
                continue
        
        return None
    except:
        return None

def limpar_telefone(telefone):
    """Limpa e formata o telefone"""
    if not telefone or telefone.strip() == '':
        return None
    
    # Remove caracteres especiais
    telefone_limpo = ''.join(filter(str.isdigit, telefone))
    
    # Adiciona formatação se necessário
    if len(telefone_limpo) >= 10:
        return telefone_limpo
    else:
        return telefone_limpo

def obter_id_atividade(cursor, nome_atividade):
    """Obtém o ID da atividade ou cria se não existir"""
    if not nome_atividade or nome_atividade.strip() == '':
        return None
    
    # Buscar atividade existente
    cursor.execute("SELECT id FROM atividades WHERE LOWER(nome) = LOWER(%s)", (nome_atividade.strip(),))
    resultado = cursor.fetchone()
    
    if resultado:
        return resultado[0]
    
    # Criar nova atividade
    cursor.execute("""
        INSERT INTO atividades (nome, descricao) 
        VALUES (%s, %s) 
        RETURNING id
    """, (nome_atividade.strip(), f'Atividade: {nome_atividade}'))
    
    return cursor.fetchone()[0]

def obter_id_turma(cursor, horario, atividade_id):
    """Obtém o ID da turma ou cria se não existir"""
    if not horario or horario.strip() == '':
        return None
    
    # Buscar turma existente
    cursor.execute("""
        SELECT id FROM turmas 
        WHERE horario = %s AND atividade_id = %s
    """, (horario.strip(), atividade_id))
    
    resultado = cursor.fetchone()
    
    if resultado:
        return resultado[0]
    
    # Criar nova turma
    nome_turma = f"Turma {horario.strip()}"
    cursor.execute("""
        INSERT INTO turmas (nome, atividade_id, horario) 
        VALUES (%s, %s, %s) 
        RETURNING id
    """, (nome_turma, atividade_id, horario.strip()))
    
    return cursor.fetchone()[0]

def migrar_dados_csv():
    """Migra os dados do CSV para o banco PostgreSQL"""
    print("=" * 70)
    print("    MIGRAÇÃO DE DADOS CSV - ACADEMIA AMIGO DO POVO")
    print("=" * 70)
    
    arquivo_csv = "outros/Cadastros_Unificados_GOOGLE_v2.csv"
    
    if not os.path.exists(arquivo_csv):
        print(f"❌ Arquivo não encontrado: {arquivo_csv}")
        return False
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"✅ Conectado ao banco PostgreSQL")
        
        # Ler arquivo CSV
        alunos_migrados = 0
        alunos_erro = 0
        
        with open(arquivo_csv, 'r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            
            for linha in leitor:
                try:
                    # Pular linhas vazias
                    if not linha.get('gitNOME') or linha['gitNOME'].strip() == '':
                        continue
                    
                    # Gerar ID único
                    id_unico = gerar_id_unico()
                    
                    # Processar dados
                    nome = linha['gitNOME'].strip()
                    data_nascimento = converter_data(linha.get('DATA DE NASCIMENTO', ''))
                    telefone = limpar_telefone(linha.get('TELEFONE', ''))
                    endereco = linha.get('ENDEREÇO', '').strip() if linha.get('ENDEREÇO') else None
                    atividade = linha.get('ATIVIDADE', '').strip()
                    data_matricula = converter_data(linha.get('DATA MATRICULA', ''))
                    turma_horario = linha.get('TURMA', '').strip()
                    
                    # Obter IDs das atividades e turmas
                    atividade_id = obter_id_atividade(cursor, atividade)
                    turma_id = obter_id_turma(cursor, turma_horario, atividade_id) if atividade_id else None
                    
                    # Inserir aluno
                    cursor.execute("""
                        INSERT INTO alunos (
                            id_unico, nome, telefone, endereco, 
                            data_nascimento, data_cadastro, atividade_id, turma_id,
                            status_frequencia, observacoes, ativo, criado_por
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        ) ON CONFLICT (id_unico) DO NOTHING
                    """, (
                        id_unico, nome, telefone, endereco,
                        data_nascimento, data_matricula or datetime.now().date(),
                        atividade_id, turma_id, 'Ativo', 
                        f'Migrado do CSV - Atividade: {atividade}', True, 'sistema'
                    ))
                    
                    alunos_migrados += 1
                    
                    if alunos_migrados % 10 == 0:
                        print(f"   ✅ {alunos_migrados} alunos migrados...")
                    
                except Exception as e:
                    alunos_erro += 1
                    print(f"   ❌ Erro ao migrar aluno '{linha.get('gitNOME', 'N/A')}': {e}")
                    continue
        
        # Commit das alterações
        conn.commit()
        
        print(f"\n📊 RESUMO DA MIGRAÇÃO:")
        print(f"   ✅ Alunos migrados com sucesso: {alunos_migrados}")
        print(f"   ❌ Erros na migração: {alunos_erro}")
        
        # Verificar estatísticas finais
        cursor.execute("SELECT COUNT(*) FROM alunos")
        total_alunos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM atividades")
        total_atividades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM turmas")
        total_turmas = cursor.fetchone()[0]
        
        print(f"\n📈 ESTATÍSTICAS DO BANCO:")
        print(f"   👥 Total de alunos: {total_alunos}")
        print(f"   🏃 Total de atividades: {total_atividades}")
        print(f"   🕐 Total de turmas: {total_turmas}")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

def mostrar_amostra_dados():
    """Mostra uma amostra dos dados migrados"""
    print(f"\n📄 AMOSTRA DOS DADOS MIGRADOS:")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Mostrar alguns alunos
        cursor.execute("""
            SELECT a.nome, a.telefone, at.nome as atividade, t.horario
            FROM alunos a
            LEFT JOIN atividades at ON a.atividade_id = at.id
            LEFT JOIN turmas t ON a.turma_id = t.id
            ORDER BY a.id
            LIMIT 5
        """)
        
        alunos = cursor.fetchall()
        
        for i, aluno in enumerate(alunos, 1):
            nome, telefone, atividade, horario = aluno
            print(f"   {i}. {nome}")
            print(f"      📞 {telefone or 'N/A'}")
            print(f"      🏃 {atividade or 'N/A'}")
            print(f"      🕐 {horario or 'N/A'}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao mostrar amostra: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando migração de dados...")
    
    # Executar migração
    if migrar_dados_csv():
        # Mostrar amostra dos dados
        mostrar_amostra_dados()
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"1. Execute: python app.py")
        print(f"2. Acesse: http://127.0.0.1:5000")
        print(f"3. Login: admin / admin123")
        print(f"4. Verifique os alunos migrados na seção 'Alunos'")
    else:
        print(f"❌ Falha na migração!")

if __name__ == "__main__":
    main()

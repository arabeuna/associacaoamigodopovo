#!/usr/bin/env python3
"""
Script para testar o upload e processamento de planilhas no MongoDB
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.append('.')

# Importar módulos do sistema
from models import init_mongodb, AlunoDAO, AtividadeDAO
from database_integration import get_db_integration

def testar_processamento_planilha():
    """Testa o processamento da planilha de teste"""
    print('=== TESTE DE PROCESSAMENTO DE PLANILHA ===')
    
    # Inicializar MongoDB
    print('🔄 Inicializando MongoDB...')
    db = init_mongodb()
    if db is None:
        print('❌ Falha ao conectar com MongoDB')
        return False
    
    # Obter integração do banco
    db_integration = get_db_integration()
    
    # Ler arquivo de teste
    arquivo_teste = 'teste_planilha.csv'
    if not os.path.exists(arquivo_teste):
        print(f'❌ Arquivo {arquivo_teste} não encontrado')
        return False
    
    print(f'📄 Lendo arquivo: {arquivo_teste}')
    try:
        df = pd.read_csv(arquivo_teste)
        print(f'✅ Arquivo lido com sucesso: {len(df)} linhas')
        print(f'📋 Colunas encontradas: {list(df.columns)}')
    except Exception as e:
        print(f'❌ Erro ao ler arquivo: {e}')
        return False
    
    # Contar alunos antes do processamento
    alunos_antes = db_integration.aluno_dao.contar_ativos()
    print(f'👥 Alunos no banco antes: {alunos_antes}')
    
    # Processar cada linha da planilha
    novos_cadastros = 0
    atualizados = 0
    erros = 0
    
    for index, row in df.iterrows():
        try:
            nome = str(row.get('nome', '')).strip()
            telefone = str(row.get('telefone', '')).strip()
            email = str(row.get('email', '')).strip()
            endereco = str(row.get('endereco', '')).strip()
            atividade_nome = str(row.get('atividade', '')).strip()
            
            if not nome:
                print(f'⚠️ Linha {index + 1}: Nome vazio, pulando...')
                continue
            
            # Processar data de nascimento
            data_nascimento = None
            if 'data_nascimento' in row and pd.notna(row['data_nascimento']):
                try:
                    data_nascimento = datetime.strptime(str(row['data_nascimento']), '%d/%m/%Y').date()
                except:
                    print(f'⚠️ Linha {index + 1}: Data de nascimento inválida')
            
            # Buscar atividade
            atividade_obj = None
            if atividade_nome:
                atividade_obj = db_integration.atividade_dao.buscar_por_nome(atividade_nome)
                if not atividade_obj:
                    # Criar atividade se não existir
                    atividade_id = db_integration.atividade_dao.criar({
                        'nome': atividade_nome,
                        'descricao': f'Atividade criada automaticamente: {atividade_nome}',
                        'ativo': True
                    })
                    atividade_obj = {'_id': atividade_id, 'nome': atividade_nome}
            
            # Verificar se aluno já existe
            aluno_existente = db_integration.aluno_dao.buscar_por_nome_telefone(nome, telefone)
            
            if aluno_existente:
                # Atualizar aluno existente
                dados_atualizacao = {
                    'email': email if email != 'nan' else aluno_existente.get('email'),
                    'endereco': endereco if endereco != 'nan' else aluno_existente.get('endereco'),
                    'atividade_id': atividade_obj.get('_id') if atividade_obj else None,
                    'ativo': True
                }
                if data_nascimento:
                    dados_atualizacao['data_nascimento'] = data_nascimento
                
                db_integration.aluno_dao.atualizar(aluno_existente.get('_id'), dados_atualizacao)
                atualizados += 1
                print(f'🔄 Linha {index + 1}: Aluno {nome} atualizado')
            else:
                # Criar novo aluno
                novo_aluno = {
                    'id_unico': f'TEST_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{index}',
                    'nome': nome,
                    'telefone': telefone if telefone != 'nan' else None,
                    'email': email if email != 'nan' else None,
                    'endereco': endereco if endereco != 'nan' else None,
                    'data_nascimento': data_nascimento,
                    'data_cadastro': datetime.now().date(),
                    'atividade_id': atividade_obj.get('_id') if atividade_obj else None,
                    'ativo': True
                }
                
                aluno_id = db_integration.aluno_dao.criar(novo_aluno)
                if aluno_id:
                    novos_cadastros += 1
                    print(f'✅ Linha {index + 1}: Aluno {nome} criado (ID: {aluno_id})')
                else:
                    erros += 1
                    print(f'❌ Linha {index + 1}: Erro ao criar aluno {nome}')
            
        except Exception as e:
            erros += 1
            print(f'❌ Linha {index + 1}: Erro - {str(e)}')
    
    # Contar alunos depois do processamento
    alunos_depois = db_integration.aluno_dao.contar_ativos()
    print(f'👥 Alunos no banco depois: {alunos_depois}')
    
    # Resumo
    print('\n📊 RESUMO DO PROCESSAMENTO:')
    print(f'   ✅ Novos cadastros: {novos_cadastros}')
    print(f'   🔄 Atualizações: {atualizados}')
    print(f'   ❌ Erros: {erros}')
    print(f'   📈 Diferença no banco: {alunos_depois - alunos_antes}')
    
    return True

if __name__ == '__main__':
    try:
        import pandas as pd
        testar_processamento_planilha()
    except ImportError:
        print('❌ Pandas não instalado. Execute: pip install pandas')
    except Exception as e:
        print(f'❌ Erro durante o teste: {e}')
#!/usr/bin/env python3
"""
Script para migrar dados existentes do sistema JSON para PostgreSQL
"""

import json
import csv
from datetime import datetime
import hashlib
from models import SessionLocal, Usuario, Atividade, Turma, Aluno, Presenca, AlunoDAO, PresencaDAO, AtividadeDAO, TurmaDAO

def migrar_usuarios():
    """Migra usuários do sistema antigo para o PostgreSQL"""
    print("Migrando usuários...")
    
    # Usuários padrão do sistema
    usuarios_padrao = {
        'admin_master': {
            'senha': hashlib.sha256('master123'.encode()).hexdigest(),
            'nome': 'Admin Master',
            'nivel': 'admin_master',
            'permissoes': ['gerenciar_colaboradores', 'todas_funcoes'],
            'ativo': True,
            'data_criacao': '01/01/2024'
        },
        'admin_master2': {
            'senha': hashlib.sha256('master456'.encode()).hexdigest(),
            'nome': 'Admin Master 2',
            'nivel': 'admin_master',
            'permissoes': ['gerenciar_colaboradores', 'todas_funcoes'],
            'ativo': True,
            'data_criacao': '01/01/2024'
        },
        'admin_master3': {
            'senha': hashlib.sha256('master789'.encode()).hexdigest(),
            'nome': 'Admin Master 3',
            'nivel': 'admin_master',
            'permissoes': ['gerenciar_colaboradores', 'todas_funcoes'],
            'ativo': True,
            'data_criacao': '01/01/2024'
        },
        'admin': {
            'senha': hashlib.sha256('admin123'.encode()).hexdigest(),
            'nome': 'Administrador Geral',
            'nivel': 'admin',
            'permissoes': ['cadastrar_alunos', 'editar_alunos', 'excluir_alunos', 'ver_todos_alunos', 'gerar_relatorios', 'backup_planilhas'],
            'ativo': True,
            'data_criacao': '02/01/2024',
            'criado_por': 'admin_master'
        },
        'prof_natacao': {
            'senha': hashlib.sha256('natacao123'.encode()).hexdigest(),
            'nome': 'Professor de Natação',
            'nivel': 'usuario',
            'permissoes': ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos'],
            'atividade_responsavel': 'Natação',
            'alunos_atribuidos': [],
            'ativo': True,
            'data_criacao': '03/01/2024',
            'criado_por': 'admin_master'
        },
        'prof_informatica': {
            'senha': hashlib.sha256('info123'.encode()).hexdigest(),
            'nome': 'Professor de Informática',
            'nivel': 'usuario',
            'permissoes': ['consultar_meus_alunos', 'gerenciar_frequencia_meus_alunos'],
            'atividade_responsavel': 'Informática',
            'alunos_atribuidos': [],
            'ativo': True,
            'data_criacao': '03/01/2024',
            'criado_por': 'admin_master'
        }
    }
    
    db = SessionLocal()
    try:
        for username, dados in usuarios_padrao.items():
            # Verificar se usuário já existe
            usuario_existente = db.query(Usuario).filter(Usuario.username == username).first()
            if not usuario_existente:
                usuario = Usuario(
                    username=username,
                    senha_hash=dados['senha'],
                    nome=dados['nome'],
                    nivel=dados['nivel'],
                    permissoes=dados['permissoes'],
                    atividade_responsavel=dados.get('atividade_responsavel'),
                    alunos_atribuidos=dados.get('alunos_atribuidos'),
                    ativo=dados['ativo'],
                    criado_por=dados.get('criado_por')
                )
                db.add(usuario)
                print(f"Usuário {username} migrado")
            else:
                print(f"Usuário {username} já existe")
        
        db.commit()
        print("Usuários migrados com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao migrar usuários: {e}")
    finally:
        db.close()

def migrar_atividades():
    """Migra atividades do JSON para PostgreSQL"""
    print("Migrando atividades...")
    
    try:
        with open('atividades_sistema.json', 'r', encoding='utf-8') as f:
            atividades = json.load(f)
        
        db = SessionLocal()
        
        for nome_atividade, dados in atividades.items():
            # Verificar se atividade já existe
            atividade_existente = db.query(Atividade).filter(Atividade.nome == dados['nome']).first()
            if not atividade_existente:
                atividade = Atividade(
                    nome=dados['nome'],
                    descricao=dados['descricao'],
                    ativa=dados['ativa'],
                    criado_por=dados['criado_por'],
                    professores_vinculados=dados['professores_vinculados'],
                    total_alunos=dados['total_alunos']
                )
                db.add(atividade)
                print(f"Atividade {dados['nome']} migrada")
            else:
                print(f"Atividade {dados['nome']} já existe")
        
        db.commit()
        print("Atividades migradas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao migrar atividades: {e}")
    finally:
        db.close()

def migrar_turmas():
    """Migra turmas do JSON para PostgreSQL"""
    print("Migrando turmas...")
    
    try:
        with open('turmas_sistema.json', 'r', encoding='utf-8') as f:
            turmas = json.load(f)
        
        db = SessionLocal()
        
        for turma_id, dados in turmas.items():
            # Buscar ID da atividade
            atividade = db.query(Atividade).filter(Atividade.nome == dados['atividade']).first()
            if not atividade:
                print(f"Atividade {dados['atividade']} não encontrada para turma {dados['nome']}")
                continue
            
            # Verificar se turma já existe
            turma_existente = db.query(Turma).filter(Turma.nome == dados['nome']).first()
            if not turma_existente:
                turma = Turma(
                    nome=dados['nome'],
                    atividade_id=atividade.id,
                    horario=dados['horario'],
                    dias_semana=dados['dias_semana'],
                    periodo=dados['periodo'],
                    capacidade_maxima=dados['capacidade_maxima'],
                    ativa=dados['ativa'],
                    criado_por=dados['criado_por'],
                    total_alunos=dados['total_alunos'],
                    descricao=dados['descricao']
                )
                db.add(turma)
                print(f"Turma {dados['nome']} migrada")
            else:
                print(f"Turma {dados['nome']} já existe")
        
        db.commit()
        print("Turmas migradas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao migrar turmas: {e}")
    finally:
        db.close()

def migrar_alunos():
    """Migra alunos do JSON para PostgreSQL"""
    print("Migrando alunos...")
    
    try:
        with open('dados_alunos.json', 'r', encoding='utf-8') as f:
            alunos = json.load(f)
        
        db = SessionLocal()
        alunos_migrados = 0
        
        for aluno_dados in alunos:
            # Buscar IDs das atividades e turmas
            atividade_id = None
            turma_id = None
            
            if aluno_dados.get('atividade'):
                atividade = db.query(Atividade).filter(Atividade.nome == aluno_dados['atividade']).first()
                if atividade:
                    atividade_id = atividade.id
            
            if aluno_dados.get('turma') and aluno_dados['turma'] != 'A definir':
                # Buscar turma pelo horário e atividade
                if atividade_id:
                    turma = db.query(Turma).filter(
                        Turma.horario == aluno_dados['turma'],
                        Turma.atividade_id == atividade_id
                    ).first()
                    if turma:
                        turma_id = turma.id
            
            # Converter data de nascimento
            data_nascimento = None
            if aluno_dados.get('data_nascimento'):
                try:
                    data_nascimento = datetime.strptime(aluno_dados['data_nascimento'], '%d/%m/%Y').date()
                except:
                    pass
            
            # Converter data de cadastro
            data_cadastro = None
            if aluno_dados.get('data_cadastro'):
                try:
                    if len(aluno_dados['data_cadastro']) == 8:  # formato dd/mm/yy
                        data_cadastro = datetime.strptime(aluno_dados['data_cadastro'], '%d/%m/%y').date()
                    else:  # formato dd/mm/yyyy
                        data_cadastro = datetime.strptime(aluno_dados['data_cadastro'], '%d/%m/%Y').date()
                except:
                    data_cadastro = datetime.now().date()
            
            # Verificar se aluno já existe
            aluno_existente = db.query(Aluno).filter(Aluno.nome == aluno_dados['nome']).first()
            if not aluno_existente:
                aluno = Aluno(
                    nome=aluno_dados['nome'],
                    telefone=aluno_dados.get('telefone'),
                    endereco=aluno_dados.get('endereco'),
                    email=aluno_dados.get('email'),
                    data_nascimento=data_nascimento,
                    data_cadastro=data_cadastro,
                    atividade_id=atividade_id,
                    turma_id=turma_id,
                    status_frequencia=aluno_dados.get('status_frequencia'),
                    observacoes=aluno_dados.get('observacoes'),
                    criado_por='sistema_migracao'
                )
                db.add(aluno)
                alunos_migrados += 1
                print(f"Aluno {aluno_dados['nome']} migrado")
            else:
                print(f"Aluno {aluno_dados['nome']} já existe")
        
        db.commit()
        print(f"{alunos_migrados} alunos migrados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao migrar alunos: {e}")
    finally:
        db.close()

def migrar_presencas():
    """Migra dados de presença do CSV para PostgreSQL"""
    print("Migrando dados de presença...")
    
    try:
        db = SessionLocal()
        presencas_migradas = 0
        
        with open('presencas_detalhadas.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Buscar aluno
                aluno = db.query(Aluno).filter(Aluno.nome == row['NOME']).first()
                if not aluno:
                    print(f"Aluno {row['NOME']} não encontrado para presença")
                    continue
                
                # Buscar atividade
                atividade_id = None
                if row.get('ATIVIDADE'):
                    atividade = db.query(Atividade).filter(Atividade.nome == row['ATIVIDADE']).first()
                    if atividade:
                        atividade_id = atividade.id
                
                # Buscar turma
                turma_id = None
                if row.get('TURMA') and row['TURMA'] != 'A definir':
                    turma = db.query(Turma).filter(Turma.horario == row['TURMA']).first()
                    if turma:
                        turma_id = turma.id
                
                # Converter data
                data_presenca = None
                if row.get('DATA'):
                    try:
                        data_presenca = datetime.strptime(row['DATA'], '%d/%m/%Y').date()
                    except:
                        print(f"Data inválida para presença: {row['DATA']}")
                        continue
                
                # Converter horário
                horario = None
                if row.get('HORARIO'):
                    try:
                        horario = datetime.strptime(row['HORARIO'], '%H:%M').time()
                    except:
                        pass
                
                # Verificar se presença já existe
                presenca_existente = db.query(Presenca).filter(
                    Presenca.aluno_id == aluno.id,
                    Presenca.data_presenca == data_presenca
                ).first()
                
                if not presenca_existente:
                    presenca = Presenca(
                        aluno_id=aluno.id,
                        data_presenca=data_presenca,
                        horario=horario,
                        turma_id=turma_id,
                        atividade_id=atividade_id,
                        status=row.get('STATUS'),
                        observacoes=row.get('OBSERVACOES'),
                        tipo_registro=row.get('TIPO', 'MANUAL'),
                        registrado_por='sistema_migracao'
                    )
                    db.add(presenca)
                    presencas_migradas += 1
                    print(f"Presença de {row['NOME']} em {row['DATA']} migrada")
                else:
                    print(f"Presença de {row['NOME']} em {row['DATA']} já existe")
        
        db.commit()
        print(f"{presencas_migradas} presenças migradas com sucesso!")
        
    except Exception as e:
        print(f"Erro ao migrar presenças: {e}")
    finally:
        db.close()

def atualizar_contadores():
    """Atualiza contadores de alunos nas atividades e turmas"""
    print("Atualizando contadores...")
    
    db = SessionLocal()
    try:
        # Atualizar contadores de atividades
        atividades = db.query(Atividade).all()
        for atividade in atividades:
            AtividadeDAO.atualizar_total_alunos(db, atividade.id)
        
        # Atualizar contadores de turmas
        turmas = db.query(Turma).all()
        for turma in turmas:
            TurmaDAO.atualizar_total_alunos(db, turma.id)
        
        print("Contadores atualizados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao atualizar contadores: {e}")
    finally:
        db.close()

def verificar_migracao():
    """Verifica se a migração foi bem-sucedida"""
    print("Verificando migração...")
    
    db = SessionLocal()
    try:
        # Contar registros
        total_usuarios = db.query(Usuario).count()
        total_atividades = db.query(Atividade).count()
        total_turmas = db.query(Turma).count()
        total_alunos = db.query(Aluno).count()
        total_presencas = db.query(Presenca).count()
        
        print(f"Resumo da migração:")
        print(f"- Usuários: {total_usuarios}")
        print(f"- Atividades: {total_atividades}")
        print(f"- Turmas: {total_turmas}")
        print(f"- Alunos: {total_alunos}")
        print(f"- Presenças: {total_presencas}")
        
        # Verificar alguns dados
        print(f"\nVerificações:")
        
        # Verificar se há alunos sem atividade
        alunos_sem_atividade = db.query(Aluno).filter(Aluno.atividade_id.is_(None)).count()
        print(f"- Alunos sem atividade: {alunos_sem_atividade}")
        
        # Verificar se há turmas sem alunos
        turmas_sem_alunos = db.query(Turma).filter(Turma.total_alunos == 0).count()
        print(f"- Turmas sem alunos: {turmas_sem_alunos}")
        
        # Verificar atividades mais populares
        atividades_populares = db.query(Atividade).order_by(Atividade.total_alunos.desc()).limit(5).all()
        print(f"- Atividades mais populares:")
        for atividade in atividades_populares:
            print(f"  * {atividade.nome}: {atividade.total_alunos} alunos")
        
    except Exception as e:
        print(f"Erro ao verificar migração: {e}")
    finally:
        db.close()

def main():
    """Função principal da migração"""
    print("=== Migração de Dados para PostgreSQL ===")
    print("Academia Amigo do Povo")
    print()
    
    # Verificar se os arquivos existem
    arquivos_necessarios = ['atividades_sistema.json', 'turmas_sistema.json', 'dados_alunos.json', 'presencas_detalhadas.csv']
    for arquivo in arquivos_necessarios:
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                pass
            print(f"✓ {arquivo} encontrado")
        except FileNotFoundError:
            print(f"✗ {arquivo} não encontrado")
            return False
    
    print()
    
    # Executar migração
    try:
        migrar_usuarios()
        print()
        
        migrar_atividades()
        print()
        
        migrar_turmas()
        print()
        
        migrar_alunos()
        print()
        
        migrar_presencas()
        print()
        
        atualizar_contadores()
        print()
        
        verificar_migracao()
        print()
        
        print("=== Migração concluída com sucesso! ===")
        print("Todos os dados foram migrados para o PostgreSQL.")
        print("\nPróximos passos:")
        print("1. Atualize o app.py para usar o novo sistema de banco de dados")
        print("2. Teste as funcionalidades do sistema")
        print("3. Faça backup dos dados antigos antes de remover")
        
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()

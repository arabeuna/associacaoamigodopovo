#!/usr/bin/env python3
"""
Integração do banco de dados PostgreSQL com o sistema Academia Amigo do Povo
Este módulo substitui o sistema de arquivos JSON/CSV por operações no banco de dados
"""

import os
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from models import (
    get_db, AlunoDAO, PresencaDAO, AtividadeDAO, TurmaDAO, LogAtividadeDAO, UsuarioDAO
)

class DatabaseIntegration:
    """
    Classe para integrar o sistema existente com o banco de dados MongoDB
    Substitui os métodos de salvamento em JSON por operações no banco
    """
    
    def __init__(self):
        self.db = get_db()
        # Inicializar DAOs do MongoDB
        self.aluno_dao = AlunoDAO()
        self.atividade_dao = AtividadeDAO()
        self.turma_dao = TurmaDAO()
        self.presenca_dao = PresencaDAO()
        self.log_atividade_dao = LogAtividadeDAO()
        self.usuario_dao = UsuarioDAO()
    
    def migrar_dados_json_para_db(self):
        """
        Migra dados existentes dos arquivos JSON para o banco de dados
        """
        print("🔄 Iniciando migração de dados JSON para PostgreSQL...")
        
        try:
            # Migrar atividades
            self._migrar_atividades()
            
            # Migrar turmas
            self._migrar_turmas()
            
            # Migrar alunos
            self._migrar_alunos()
            
            # Migrar presenças (se existirem em CSV)
            self._migrar_presencas()
            
            print("✅ Migração concluída com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro durante a migração: {str(e)}")
            self.db.rollback()
            raise
    
    def _migrar_atividades(self):
        """Migra atividades do arquivo JSON para o banco"""
        try:
            with open('atividades_sistema.json', 'r', encoding='utf-8') as f:
                atividades_json = json.load(f)
            
            for ativ_data in atividades_json:
                # Verificar se a atividade já existe
                atividade_existente = self.db.query(Atividade).filter(
                    Atividade.nome == ativ_data.get('nome')
                ).first()
                
                if not atividade_existente:
                    nova_atividade = Atividade(
                        nome=ativ_data.get('nome', ''),
                        descricao=ativ_data.get('descricao', ''),
                        ativa=ativ_data.get('ativa', True),
                        criado_por='sistema_migracao',
                        professores_vinculados=json.dumps(ativ_data.get('professores_vinculados', [])),
                        total_alunos=ativ_data.get('total_alunos', 0)
                    )
                    self.db.add(nova_atividade)
            
            self.db.commit()
            print("✅ Atividades migradas com sucesso")
            
        except FileNotFoundError:
            print("⚠️ Arquivo atividades_sistema.json não encontrado")
        except Exception as e:
            print(f"❌ Erro ao migrar atividades: {str(e)}")
            self.db.rollback()
    
    def _migrar_turmas(self):
        """Migra turmas do arquivo JSON para o banco"""
        try:
            with open('turmas_sistema.json', 'r', encoding='utf-8') as f:
                turmas_json = json.load(f)
            
            for turma_data in turmas_json:
                # Buscar atividade correspondente
                atividade = self.db.query(Atividade).filter(
                    Atividade.nome == turma_data.get('atividade')
                ).first()
                
                if atividade:
                    # Verificar se a turma já existe
                    turma_existente = self.db.query(Turma).filter(
                        Turma.nome == turma_data.get('nome'),
                        Turma.atividade_id == atividade.id
                    ).first()
                    
                    if not turma_existente:
                        nova_turma = Turma(
                            nome=turma_data.get('nome', ''),
                            atividade_id=atividade.id,
                            horario=turma_data.get('horario', ''),
                            dias_semana=turma_data.get('dias_semana', ''),
                            periodo=turma_data.get('periodo', ''),
                            capacidade_maxima=turma_data.get('capacidade_maxima', 20),
                            ativa=turma_data.get('ativa', True),
                            criado_por='sistema_migracao',
                            total_alunos=turma_data.get('total_alunos', 0),
                            descricao=turma_data.get('descricao', '')
                        )
                        self.db.add(nova_turma)
            
            self.db.commit()
            print("✅ Turmas migradas com sucesso")
            
        except FileNotFoundError:
            print("⚠️ Arquivo turmas_sistema.json não encontrado")
        except Exception as e:
            print(f"❌ Erro ao migrar turmas: {str(e)}")
            self.db.rollback()
    
    def _migrar_alunos(self):
        """Migra alunos do arquivo JSON para o banco"""
        try:
            with open('dados_alunos.json', 'r', encoding='utf-8') as f:
                alunos_json = json.load(f)
            
            for aluno_data in alunos_json:
                # Verificar se o aluno já existe
                aluno_existente = self.db.query(Aluno).filter(
                    Aluno.nome == aluno_data.get('nome'),
                    Aluno.telefone == aluno_data.get('telefone')
                ).first()
                
                if not aluno_existente:
                    # Buscar atividade e turma correspondentes
                    atividade = None
                    turma = None
                    
                    if aluno_data.get('atividade'):
                        atividade = self.db.query(Atividade).filter(
                            Atividade.nome == aluno_data.get('atividade')
                        ).first()
                    
                    if aluno_data.get('turma') and atividade:
                        turma = self.db.query(Turma).filter(
                            Turma.nome == aluno_data.get('turma'),
                            Turma.atividade_id == atividade.id
                        ).first()
                    
                    # Converter data de nascimento
                    data_nascimento = None
                    if aluno_data.get('data_nascimento'):
                        try:
                            data_nascimento = datetime.strptime(
                                aluno_data['data_nascimento'], '%Y-%m-%d'
                            ).date()
                        except:
                            pass
                    
                    # Converter data de cadastro
                    data_cadastro = date.today()
                    if aluno_data.get('data_cadastro'):
                        try:
                            data_cadastro = datetime.strptime(
                                aluno_data['data_cadastro'], '%Y-%m-%d'
                            ).date()
                        except:
                            pass
                    
                    novo_aluno = Aluno(
                        nome=aluno_data.get('nome', ''),
                        telefone=aluno_data.get('telefone', ''),
                        endereco=aluno_data.get('endereco', ''),
                        email=aluno_data.get('email', ''),
                        data_nascimento=data_nascimento,
                        data_cadastro=data_cadastro,
                        atividade_id=atividade.id if atividade else None,
                        turma_id=turma.id if turma else None,
                        status_frequencia=aluno_data.get('status_frequencia', ''),
                        observacoes=aluno_data.get('observacoes', ''),
                        ativo=aluno_data.get('ativo', True),
                        criado_por='sistema_migracao'
                    )
                    self.db.add(novo_aluno)
            
            self.db.commit()
            print("✅ Alunos migrados com sucesso")
            
        except FileNotFoundError:
            print("⚠️ Arquivo dados_alunos.json não encontrado")
        except Exception as e:
            print(f"❌ Erro ao migrar alunos: {str(e)}")
            self.db.rollback()
    
    def _migrar_presencas(self):
        """Migra presenças dos arquivos CSV para o banco (se existirem)"""
        print("⚠️ Migração de presenças CSV não implementada nesta versão")
        # TODO: Implementar migração de presenças dos CSVs se necessário
    
    def salvar_aluno_db(self, dados_aluno: Dict[str, Any]) -> Optional[int]:
        """
        Salva um aluno no banco de dados PostgreSQL
        Substitui o método salvar_dados() para alunos
        """
        try:
            print(f"[DEBUG DB] Iniciando salvamento no banco: {dados_aluno.get('nome')}")
            # Buscar atividade
            atividade = None
            if dados_aluno.get('atividade'):
                print(f"[DEBUG DB] Buscando atividade: {dados_aluno['atividade']}")
                atividade = self.db.query(Atividade).filter(
                    Atividade.nome == dados_aluno['atividade']
                ).first()
                print(f"[DEBUG DB] Atividade encontrada: {atividade.nome if atividade else 'Não encontrada'}")
            
            # Buscar turma
            turma = None
            if dados_aluno.get('turma'):
                print(f"[DEBUG DB] Buscando turma: {dados_aluno['turma']}")
                turma = self.db.query(Turma).filter(
                    Turma.nome == dados_aluno['turma']
                ).first()
                print(f"[DEBUG DB] Turma encontrada: {turma.nome if turma else 'Não encontrada'}")
            
            # Converter datas
            data_nascimento = None
            if dados_aluno.get('data_nascimento'):
                if isinstance(dados_aluno['data_nascimento'], str):
                    try:
                        data_nascimento = datetime.strptime(
                            dados_aluno['data_nascimento'], '%Y-%m-%d'
                        ).date()
                    except:
                        pass
                elif isinstance(dados_aluno['data_nascimento'], date):
                    data_nascimento = dados_aluno['data_nascimento']
            
            data_cadastro = date.today()
            if dados_aluno.get('data_cadastro'):
                if isinstance(dados_aluno['data_cadastro'], str):
                    try:
                        data_cadastro = datetime.strptime(
                            dados_aluno['data_cadastro'], '%Y-%m-%d'
                        ).date()
                    except:
                        pass
                elif isinstance(dados_aluno['data_cadastro'], date):
                    data_cadastro = dados_aluno['data_cadastro']
            
            # Gerar ID único
            import uuid
            id_unico = dados_aluno.get('id_unico') or str(uuid.uuid4())[:8]
            
            # Criar novo aluno
            print(f"[DEBUG DB] Criando objeto aluno com id_unico={id_unico}, atividade_id={atividade.id if atividade else None}, turma_id={turma.id if turma else None}")
            novo_aluno = Aluno(
                id_unico=id_unico,
                nome=dados_aluno.get('nome', ''),
                telefone=dados_aluno.get('telefone', ''),
                endereco=dados_aluno.get('endereco', ''),
                email=dados_aluno.get('email', ''),
                data_nascimento=data_nascimento,
                data_cadastro=data_cadastro,
                titulo_eleitor=dados_aluno.get('titulo_eleitor', ''),
                atividade_id=atividade.id if atividade else None,
                turma_id=turma.id if turma else None,
                status_frequencia=dados_aluno.get('status_frequencia', ''),
                observacoes=dados_aluno.get('observacoes', ''),
                ativo=dados_aluno.get('ativo', True),
                criado_por=dados_aluno.get('criado_por', 'sistema')
            )
            
            print(f"[DEBUG DB] Adicionando aluno à sessão")
            self.db.add(novo_aluno)
            print(f"[DEBUG DB] Fazendo commit")
            self.db.commit()
            print(f"[DEBUG DB] Aluno salvo com ID: {novo_aluno.id}")
            
            # Atualizar contadores
            if atividade:
                AtividadeDAO.atualizar_total_alunos(self.db, atividade.id)
            if turma:
                TurmaDAO.atualizar_total_alunos(self.db, turma.id)
            
            return novo_aluno.id
            
        except Exception as e:
            print(f"❌ Erro ao salvar aluno no banco: {str(e)}")
            self.db.rollback()
            return None
    
    def atualizar_aluno_db(self, aluno_id: int, dados_aluno: Dict[str, Any]) -> bool:
        """
        Atualiza um aluno no banco de dados PostgreSQL
        Substitui o método atualizar_aluno() 
        """
        try:
            aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
            if not aluno:
                return False
            
            # Buscar atividade e turma
            atividade = None
            turma = None
            
            if dados_aluno.get('atividade'):
                atividade = self.db.query(Atividade).filter(
                    Atividade.nome == dados_aluno['atividade']
                ).first()
            
            if dados_aluno.get('turma') and atividade:
                turma = self.db.query(Turma).filter(
                    Turma.nome == dados_aluno['turma'],
                    Turma.atividade_id == atividade.id
                ).first()
            
            # Atualizar campos
            aluno.nome = dados_aluno.get('nome', aluno.nome)
            aluno.telefone = dados_aluno.get('telefone', aluno.telefone)
            aluno.endereco = dados_aluno.get('endereco', aluno.endereco)
            aluno.email = dados_aluno.get('email', aluno.email)
            aluno.titulo_eleitor = dados_aluno.get('titulo_eleitor', aluno.titulo_eleitor)
            
            # Converter data de nascimento
            if dados_aluno.get('data_nascimento'):
                if isinstance(dados_aluno['data_nascimento'], str):
                    try:
                        aluno.data_nascimento = datetime.strptime(
                            dados_aluno['data_nascimento'], '%Y-%m-%d'
                        ).date()
                    except:
                        pass
                elif isinstance(dados_aluno['data_nascimento'], date):
                    aluno.data_nascimento = dados_aluno['data_nascimento']
            
            aluno.atividade_id = atividade.id if atividade else aluno.atividade_id
            aluno.turma_id = turma.id if turma else aluno.turma_id
            aluno.status_frequencia = dados_aluno.get('status_frequencia', aluno.status_frequencia)
            aluno.observacoes = dados_aluno.get('observacoes', aluno.observacoes)
            aluno.ativo = dados_aluno.get('ativo', aluno.ativo)
            
            self.db.commit()
            
            # Atualizar contadores
            if atividade:
                AtividadeDAO.atualizar_total_alunos(self.db, atividade.id)
            if turma:
                TurmaDAO.atualizar_total_alunos(self.db, turma.id)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar aluno no banco: {str(e)}")
            self.db.rollback()
            return False
    
    def registrar_presenca_db(self, dados_presenca: Dict[str, Any]) -> bool:
        """
        Registra presença no banco de dados PostgreSQL
        Substitui o sistema de CSV
        """
        try:
            return PresencaDAO.registrar_presenca(
                db=self.db,
                aluno_id=dados_presenca['aluno_id'],
                data_presenca=dados_presenca['data_presenca'],
                status=dados_presenca['status'],
                turma_id=dados_presenca.get('turma_id'),
                atividade_id=dados_presenca.get('atividade_id'),
                observacoes=dados_presenca.get('observacoes'),
                registrado_por=dados_presenca.get('registrado_por')
            )
        except Exception as e:
            print(f"❌ Erro ao registrar presença no banco: {str(e)}")
            return False
    
    def listar_alunos_db(self, atividade_nome: str = None, turma_nome: str = None) -> List[Dict]:
        """
        Lista alunos do banco de dados
        Substitui o carregamento de JSON
        """
        try:
            query = self.db.query(Aluno).filter(Aluno.ativo == True)
            
            if atividade_nome:
                atividade = self.db.query(Atividade).filter(
                    Atividade.nome == atividade_nome
                ).first()
                if atividade:
                    query = query.filter(Aluno.atividade_id == atividade.id)
            
            if turma_nome and atividade_nome:
                atividade = self.db.query(Atividade).filter(
                    Atividade.nome == atividade_nome
                ).first()
                if atividade:
                    turma = self.db.query(Turma).filter(
                        Turma.nome == turma_nome,
                        Turma.atividade_id == atividade.id
                    ).first()
                    if turma:
                        query = query.filter(Aluno.turma_id == turma.id)
            
            alunos = query.all()
            
            # Converter para formato compatível
            resultado = []
            for aluno in alunos:
                aluno_dict = {
                    'id': aluno.id,
                    'nome': aluno.nome,
                    'telefone': aluno.telefone,
                    'endereco': aluno.endereco,
                    'email': aluno.email,
                    'data_nascimento': aluno.data_nascimento.strftime('%Y-%m-%d') if aluno.data_nascimento else '',
                    'data_cadastro': aluno.data_cadastro.strftime('%Y-%m-%d') if aluno.data_cadastro else '',
                    'atividade': aluno.atividade.nome if aluno.atividade else '',
                    'turma': aluno.turma.nome if aluno.turma else '',
                    'status_frequencia': aluno.status_frequencia,
                    'observacoes': aluno.observacoes,
                    'ativo': aluno.ativo
                }
                resultado.append(aluno_dict)
            
            return resultado
            
        except Exception as e:
            print(f"❌ Erro ao listar alunos do banco: {str(e)}")
            return []
    
    def contar_alunos_db(self) -> int:
        """Conta o total de alunos ativos no banco de dados"""
        try:
            total = self.db.query(Aluno).filter(Aluno.ativo == True).count()
            return total
        except Exception as e:
            print(f"❌ Erro ao contar alunos no banco: {str(e)}")
            return 0
    
    def contar_atividades_db(self) -> int:
        """Conta o total de atividades ativas no banco de dados"""
        try:
            total = self.db.query(Atividade).filter(Atividade.ativa == True).count()
            return total
        except Exception as e:
            print(f"❌ Erro ao contar atividades no banco: {str(e)}")
            return 0
    
    def contar_turmas_db(self) -> int:
        """Conta o total de turmas ativas no banco de dados"""
        try:
            total = self.db.query(Turma).filter(Turma.ativa == True).count()
            return total
        except Exception as e:
            print(f"❌ Erro ao contar turmas no banco: {str(e)}")
            return 0
    
    def registrar_atividade_db(self, usuario: str, acao: str, detalhes: str, tipo_usuario: str = "usuario") -> bool:
        """Registra uma atividade no sistema de logs do banco de dados"""
        try:
            LogAtividadeDAO.registrar_log(
                db=self.db,
                usuario=usuario,
                acao=acao,
                detalhes=detalhes,
                tipo_usuario=tipo_usuario
            )
            return True
        except Exception as e:
            print(f"Erro ao registrar atividade no banco: {e}")
            self.db.rollback()
            return False
    
    def listar_logs_db(self, filtro: str = None, limite: int = 1000) -> List[Dict]:
        """Lista logs de atividades do banco de dados"""
        try:
            logs = LogAtividadeDAO.listar_logs(
                db=self.db,
                filtro=filtro,
                limite=limite
            )
            
            logs_dict = []
            for log in logs:
                logs_dict.append({
                    'id': log.id,
                    'timestamp': log.timestamp.isoformat(),
                    'data_hora': log.timestamp.strftime('%d/%m/%Y às %H:%M:%S'),
                    'usuario': log.usuario,
                    'tipo_usuario': log.tipo_usuario,
                    'acao': log.acao,
                    'detalhes': log.detalhes
                })
            
            return logs_dict
        except Exception as e:
            print(f"Erro ao listar logs: {e}")
            return []
    
    def limpar_logs_antigos_db(self, dias_manter: int = 90) -> int:
        """Remove logs mais antigos que o número de dias especificado"""
        try:
            return LogAtividadeDAO.limpar_logs_antigos(
                db=self.db,
                dias_manter=dias_manter
            )
        except Exception as e:
            print(f"Erro ao limpar logs antigos: {e}")
            return 0
    
    def listar_atividades_db(self) -> List[Dict]:
        """Lista atividades do banco de dados"""
        try:
            atividades = self.db.query(Atividade).filter(Atividade.ativa == True).all()
            
            resultado = []
            for atividade in atividades:
                atividade_dict = {
                    'id': atividade.id,
                    'nome': atividade.nome,
                    'descricao': atividade.descricao,
                    'professores_vinculados': atividade.professores_vinculados,
                    'ativa': atividade.ativa,
                    'total_alunos': atividade.total_alunos,
                    'data_criacao': atividade.data_criacao.strftime('%d/%m/%Y') if atividade.data_criacao else '',
                    'criado_por': atividade.criado_por
                }
                resultado.append(atividade_dict)
            
            return resultado
        except Exception as e:
            print(f"❌ Erro ao listar atividades do banco: {str(e)}")
            return []
    
    def listar_turmas_db(self) -> List[Dict]:
        """Lista turmas do banco de dados"""
        try:
            turmas = self.db.query(Turma).filter(Turma.ativa == True).all()
            
            resultado = []
            for turma in turmas:
                turma_dict = {
                    'id': turma.id,
                    'nome': turma.nome,
                    'atividade': turma.atividade.nome if turma.atividade else '',
                    'atividade_id': turma.atividade_id,
                    'horario': turma.horario,
                    'dias_semana': turma.dias_semana,
                    'periodo': turma.periodo,
                    'capacidade_maxima': turma.capacidade_maxima,
                    'professor_responsavel': turma.professor_responsavel,
                    'ativa': turma.ativa,
                    'total_alunos': turma.total_alunos,
                    'descricao': turma.descricao,
                    'data_criacao': turma.data_criacao.strftime('%d/%m/%Y') if turma.data_criacao else '',
                    'criado_por': turma.criado_por
                }
                resultado.append(turma_dict)
            
            return resultado
        except Exception as e:
            print(f"❌ Erro ao listar turmas do banco: {str(e)}")
            return []

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.db:
            self.db.close()

# Instância global para uso no sistema
db_integration = DatabaseIntegration()

def get_db_integration():
    """Retorna a instância de integração do banco de dados"""
    return db_integration
#!/usr/bin/env python3
"""
Versão robusta do database_integration.py com tratamento avançado de erros
Incluindo retry automático, fallback e recuperação de falhas de conexão
"""

import os
import json
import time
import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Any, Union

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from models import (
        get_db, AlunoDAO, PresencaDAO, AtividadeDAO, TurmaDAO, LogAtividadeDAO, UsuarioDAO
    )
except ImportError as e:
    logger.error(f"Erro ao importar models: {e}")
    raise

class DatabaseConnectionError(Exception):
    """Exceção customizada para erros de conexão com o banco"""
    pass

class DatabaseIntegrationRobusto:
    """
    Versão robusta da integração com banco de dados
    Inclui tratamento avançado de erros, retry automático e fallback
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.db = None
        self.fallback_file = 'cadastros_fallback.json'
        
        # Inicializar DAOs (são classes estáticas)
        self.aluno_dao = AlunoDAO
        self.atividade_dao = AtividadeDAO
        self.turma_dao = TurmaDAO
        self.presenca_dao = PresencaDAO
        self.log_atividade_dao = LogAtividadeDAO
        self.usuario_dao = UsuarioDAO
        
        self._init_connection()
    
    def _init_connection(self):
        """Inicializa a conexão com o banco de dados e os DAOs"""
        try:
            # Obter conexão do banco
            db_connection = get_db()
            if db_connection is None:
                # Modo fallback - usar None como conexão
                self.db = None
                logger.warning("⚠️ Usando modo fallback - MongoDB não disponível")
            else:
                # Usar generator se necessário
                try:
                    if hasattr(db_connection, '__next__'):
                        self.db = next(db_connection)
                    else:
                        self.db = db_connection
                except TypeError:
                    # Se não for iterável, usar diretamente
                    self.db = db_connection
            
            # Inicializar todos os DAOs (são classes estáticas)
            self.aluno_dao = AlunoDAO
            self.atividade_dao = AtividadeDAO
            self.turma_dao = TurmaDAO
            self.presenca_dao = PresencaDAO
            self.log_atividade_dao = LogAtividadeDAO()
            self.usuario_dao = UsuarioDAO
            
            if self.db is None:
                logger.info("✅ DAOs inicializados em modo fallback (memória)")
            else:
                logger.info("✅ Conexão com banco de dados e DAOs estabelecida")
                
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com banco: {e}")
            self.db = None
            # Inicializar DAOs mesmo em caso de erro (são classes estáticas)
            self.aluno_dao = AlunoDAO
            self.atividade_dao = AtividadeDAO
            self.turma_dao = TurmaDAO
            self.presenca_dao = PresencaDAO
            self.log_atividade_dao = LogAtividadeDAO()
            self.usuario_dao = UsuarioDAO
            logger.info("✅ DAOs inicializados em modo fallback após erro")
    
    def _test_connection(self) -> bool:
        """Testa se a conexão com o banco está ativa"""
        try:
            if self.db is None:
                return False
            
            # Teste simples de conexão MongoDB
            self.db.command('ping')
            return True
            
        except Exception as e:
            logger.warning(f"Conexão com banco perdida: {e}")
            return False
    
    def _reconnect(self) -> bool:
        """Tenta reconectar com o banco de dados e reinicializar DAOs"""
        try:
            if self.db is not None:
                self.db.close()
            
            # Obter nova conexão do banco
            db_connection = get_db()
            if db_connection is None:
                # Modo fallback - usar None como conexão
                self.db = None
                logger.warning("⚠️ Reconexão em modo fallback - MongoDB não disponível")
            else:
                # Usar generator se necessário
                if hasattr(db_connection, '__next__'):
                    self.db = next(db_connection)
                else:
                    self.db = db_connection
            
            # Reinicializar todos os DAOs (são classes estáticas)
            self.aluno_dao = AlunoDAO
            self.atividade_dao = AtividadeDAO
            self.turma_dao = TurmaDAO
            self.presenca_dao = PresencaDAO
            self.log_atividade_dao = LogAtividadeDAO
            self.usuario_dao = UsuarioDAO
            
            # Testar a nova conexão (ou confirmar modo fallback)
            connection_ok = self.db is None or self._test_connection()
            if connection_ok:
                if self.db is None:
                    logger.info("✅ Reconexão em modo fallback bem-sucedida")
                else:
                    logger.info("✅ Reconexão com banco e DAOs bem-sucedida")
                return True
            else:
                logger.error("❌ Falha na reconexão")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro durante reconexão: {e}")
            self.db = None
            # Manter DAOs inicializados mesmo em caso de erro (são classes estáticas)
            self.aluno_dao = AlunoDAO
            self.atividade_dao = AtividadeDAO
            self.turma_dao = TurmaDAO
            self.presenca_dao = PresencaDAO
            self.log_atividade_dao = LogAtividadeDAO
            self.usuario_dao = UsuarioDAO
            return False
    
    def _is_connection_error(self, error: Exception) -> bool:
        """Verifica se o erro é relacionado à conexão"""
        error_str = str(error).lower()
        connection_errors = [
            'connection refused',
            'connection reset',
            'connection lost',
            'server closed the connection',
            'connection timeout',
            'connection broken',
            'no connection to the server',
            'connection terminated',
            'connection aborted',
            'não foi possível reconectar',
            'database connection error',
            'could not connect',
            'connection failed',
            'database is not available',
            'mongodb connection',
            'dns query name does not exist',
            'serverselectiontimeouterror'
        ]
        
        return any(err in error_str for err in connection_errors)
    
    def _save_to_fallback(self, dados_aluno: Dict[str, Any]) -> str:
        """Salva dados no arquivo de fallback quando o banco está indisponível"""
        try:
            # Adicionar timestamp e ID único
            fallback_data = {
                **dados_aluno,
                'fallback_timestamp': datetime.now().isoformat(),
                'fallback_id': f"fallback_{int(time.time())}_{hash(dados_aluno.get('nome', ''))}",
                'status': 'pending_database_save'
            }
            
            # Carregar dados existentes do fallback
            fallback_records = []
            if os.path.exists(self.fallback_file):
                try:
                    with open(self.fallback_file, 'r', encoding='utf-8') as f:
                        fallback_records = json.load(f)
                except:
                    fallback_records = []
            
            # Adicionar novo registro
            fallback_records.append(fallback_data)
            
            # Salvar de volta
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                json.dump(fallback_records, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 Dados salvos no fallback: {self.fallback_file}")
            return fallback_data['fallback_id']
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar no fallback: {e}")
            raise
    
    def _execute_with_retry(self, operation_func, *args, **kwargs):
        """Executa uma operação com retry automático"""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Verificar conexão antes da operação
                if not self._test_connection():
                    logger.warning(f"Conexão perdida, tentando reconectar (tentativa {attempt + 1})")
                    if not self._reconnect():
                        raise DatabaseConnectionError("Não foi possível reconectar com o banco")
                
                # Executar operação
                return operation_func(*args, **kwargs)
                
            except Exception as e:
                last_error = e
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                
                # Se é erro de conexão e ainda há tentativas, tentar reconectar
                if self._is_connection_error(e) and attempt < self.max_retries:
                    logger.info(f"Erro de conexão detectado, aguardando {self.retry_delay}s antes da próxima tentativa")
                    time.sleep(self.retry_delay)
                    
                    # Tentar reconectar
                    if self._reconnect():
                        continue
                
                # Se não é erro de conexão ou esgotaram as tentativas, re-raise
                if attempt == self.max_retries:
                    break
        
        # Se chegou aqui, todas as tentativas falharam
        raise last_error
    
    def salvar_aluno_db_robusto(self, dados_aluno: Dict[str, Any]) -> Dict[str, Any]:
        """
        Versão robusta do salvamento de aluno com tratamento avançado de erros
        
        Returns:
            Dict com 'success', 'message', 'aluno_id' ou 'fallback_id'
        """
        def _salvar_operacao():
            """Operação interna de salvamento"""
            logger.info(f"[ROBUSTO] Iniciando salvamento: {dados_aluno.get('nome')}")
            
            # Buscar atividade usando DAO do MongoDB
            atividade = None
            atividade_id = None
            if dados_aluno.get('atividade'):
                atividades = self.atividade_dao.listar_todas()
                for ativ in atividades:
                    if ativ.get('nome') == dados_aluno['atividade']:
                        atividade = ativ
                        atividade_id = ativ.get('_id')
                        break
            
            # Buscar turma usando DAO do MongoDB
            turma = None
            turma_id = None
            if dados_aluno.get('turma'):
                turmas = self.turma_dao.listar_todas()
                for t in turmas:
                    if t.get('nome') == dados_aluno['turma']:
                        turma = t
                        turma_id = t.get('_id')
                        break
            
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
            
            # Criar dados do novo aluno para MongoDB
            dados_novo_aluno = {
                'id_unico': id_unico,
                'nome': dados_aluno.get('nome', ''),
                'telefone': dados_aluno.get('telefone', ''),
                'endereco': dados_aluno.get('endereco', ''),
                'email': dados_aluno.get('email', ''),
                'data_nascimento': data_nascimento.isoformat() if data_nascimento else None,
                'data_cadastro': data_cadastro.isoformat() if data_cadastro else None,
                'titulo_eleitor': dados_aluno.get('titulo_eleitor', ''),
                'atividade': dados_aluno.get('atividade', ''),
                'atividade_id': atividade_id,
                'turma': dados_aluno.get('turma', ''),
                'turma_id': turma_id,
                'status_frequencia': dados_aluno.get('status_frequencia', ''),
                'observacoes': dados_aluno.get('observacoes', ''),
                'ativo': dados_aluno.get('ativo', True),
                'criado_por': dados_aluno.get('criado_por', 'sistema'),
                'criado_em': datetime.now().isoformat()
            }
            
            # Salvar usando DAO do MongoDB
            resultado = self.aluno_dao.criar(dados_novo_aluno)
            
            # Atualizar contadores
            if atividade_id:
                self.atividade_dao.atualizar_total_alunos(atividade_id)
            if turma_id:
                self.turma_dao.atualizar_total_alunos(turma_id)
            
            logger.info(f"[ROBUSTO] ✅ Aluno salvo com ID: {resultado}")
            return resultado
        
        try:
            # Tentar salvar no banco com retry
            aluno_id = self._execute_with_retry(_salvar_operacao)
            
            return {
                'success': True,
                'message': 'Aluno cadastrado com sucesso no banco de dados',
                'aluno_id': aluno_id,
                'method': 'database'
            }
            
        except Exception as e:
            logger.error(f"[ROBUSTO] ❌ Falha definitiva no banco: {e}")
            
            # Se é erro de conexão, tentar fallback
            if self._is_connection_error(e):
                try:
                    fallback_id = self._save_to_fallback(dados_aluno)
                    
                    return {
                        'success': True,
                        'message': 'Banco indisponível. Dados salvos temporariamente e serão processados quando a conexão for restaurada.',
                        'fallback_id': fallback_id,
                        'method': 'fallback',
                        'warning': 'Dados salvos em modo fallback'
                    }
                    
                except Exception as fallback_error:
                    logger.error(f"[ROBUSTO] ❌ Falha no fallback: {fallback_error}")
                    
                    return {
                        'success': False,
                        'message': f'Erro crítico: Falha no banco de dados e no sistema de fallback. Erro original: {str(e)}',
                        'error': str(e),
                        'fallback_error': str(fallback_error)
                    }
            else:
                # Erro não relacionado à conexão
                return {
                    'success': False,
                    'message': f'Erro no cadastro: {str(e)}',
                    'error': str(e)
                }
    
    def processar_fallback_pendente(self) -> Dict[str, Any]:
        """Processa registros pendentes do fallback quando a conexão é restaurada"""
        if not os.path.exists(self.fallback_file):
            return {'processed': 0, 'message': 'Nenhum registro pendente'}
        
        try:
            with open(self.fallback_file, 'r', encoding='utf-8') as f:
                fallback_records = json.load(f)
        except:
            return {'processed': 0, 'error': 'Erro ao ler arquivo de fallback'}
        
        processed = 0
        errors = []
        remaining_records = []
        
        for record in fallback_records:
            if record.get('status') == 'pending_database_save':
                try:
                    # Remover campos de fallback antes de salvar
                    clean_data = {k: v for k, v in record.items() 
                                if not k.startswith('fallback_') and k != 'status'}
                    
                    result = self.salvar_aluno_db_robusto(clean_data)
                    
                    if result['success'] and result.get('method') == 'database':
                        processed += 1
                        logger.info(f"✅ Registro fallback processado: {record.get('nome')}")
                    else:
                        # Se ainda falhou, manter no fallback
                        remaining_records.append(record)
                        errors.append(f"Falha ao processar {record.get('nome')}: {result.get('message')}")
                        
                except Exception as e:
                    remaining_records.append(record)
                    errors.append(f"Erro ao processar {record.get('nome')}: {str(e)}")
            else:
                # Manter registros que não são pendentes
                remaining_records.append(record)
        
        # Atualizar arquivo de fallback
        try:
            if remaining_records:
                with open(self.fallback_file, 'w', encoding='utf-8') as f:
                    json.dump(remaining_records, f, ensure_ascii=False, indent=2, default=str)
            else:
                os.remove(self.fallback_file)
                logger.info("📁 Arquivo de fallback removido - todos os registros processados")
        except Exception as e:
            logger.error(f"Erro ao atualizar arquivo de fallback: {e}")
        
        return {
            'processed': processed,
            'remaining': len(remaining_records),
            'errors': errors,
            'message': f'Processados {processed} registros, {len(remaining_records)} restantes'
        }
    
    def get_status_sistema(self) -> Dict[str, Any]:
        """Retorna o status do sistema de banco de dados"""
        status = {
            'database_connected': self._test_connection(),
            'fallback_records': 0,
            'last_check': datetime.now().isoformat()
        }
        
        # Verificar registros pendentes no fallback
        if os.path.exists(self.fallback_file):
            try:
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    fallback_records = json.load(f)
                    status['fallback_records'] = len([r for r in fallback_records 
                                                    if r.get('status') == 'pending_database_save'])
            except:
                status['fallback_records'] = 'erro_leitura'
        
        return status
    
    # Métodos de compatibilidade com a interface existente
    def contar_alunos_db(self) -> int:
        """Conta o total de alunos no banco"""
        try:
            if not self._test_connection():
                return 0
            return self.aluno_dao.contar_total()
        except Exception as e:
            logger.error(f"Erro ao contar alunos: {e}")
            return 0
    
    def contar_atividades_db(self) -> int:
        """Conta o total de atividades no banco"""
        try:
            if not self._test_connection():
                return 0
            return self.atividade_dao.contar_total()
        except Exception as e:
            logger.error(f"Erro ao contar atividades: {e}")
            return 0
    
    def contar_turmas_db(self) -> int:
        """Conta o total de turmas no banco"""
        try:
            if not self._test_connection():
                return 0
            return self.turma_dao.contar_total()
        except Exception as e:
            logger.error(f"Erro ao contar turmas: {e}")
            return 0
    
    def listar_alunos_db(self) -> List[Dict[str, Any]]:
        """Lista todos os alunos do banco"""
        try:
            if not self._test_connection():
                return []
            return self.aluno_dao.listar_todos()
        except Exception as e:
            logger.error(f"Erro ao listar alunos: {e}")
            return []
    
    def listar_atividades_db(self) -> List[Dict[str, Any]]:
        """Lista todas as atividades do banco"""
        try:
            if not self._test_connection():
                return []
            return self.atividade_dao.listar_todas()
        except Exception as e:
            logger.error(f"Erro ao listar atividades: {e}")
            return []
    
    def listar_turmas_db(self) -> List[Dict[str, Any]]:
        """Lista todas as turmas do banco"""
        try:
            if not self._test_connection():
                return []
            return self.turma_dao.listar_todas()
        except Exception as e:
            logger.error(f"Erro ao listar turmas: {e}")
            return []
    
    def atualizar_aluno_db(self, aluno_id: str, dados_atualizados: Dict[str, Any]) -> bool:
        """Atualiza um aluno no banco"""
        try:
            if not self._test_connection():
                return False
            return self.aluno_dao.atualizar(aluno_id, dados_atualizados)
        except Exception as e:
            logger.error(f"Erro ao atualizar aluno: {e}")
            return False
    
    def registrar_atividade_db(self, usuario: str, acao: str, detalhes: str, tipo_usuario: str = "usuario") -> bool:
        """Registra uma atividade no log"""
        try:
            if not self._test_connection():
                return False
            dados_log = {
                'usuario': usuario,
                'acao': acao,
                'detalhes': detalhes,
                'tipo_usuario': tipo_usuario,
                'timestamp': datetime.now().isoformat()
            }
            self.log_atividade_dao.criar(dados_log)
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar atividade: {e}")
            return False

# Instância global para uso na aplicação
db_integration_robusto = DatabaseIntegrationRobusto()

# Função de compatibilidade para manter a interface existente
def get_db_integration():
    """Retorna a instância global do DatabaseIntegrationRobusto"""
    return db_integration_robusto
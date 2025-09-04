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
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DisconnectionError, TimeoutError as SQLTimeoutError
from sqlalchemy import create_engine, text
import psycopg2
from psycopg2 import OperationalError as PsycopgOperationalError

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
        self._init_connection()
    
    def _init_connection(self):
        """Inicializa a conexão com o banco de dados"""
        try:
            self.db = next(get_db())
            logger.info("✅ Conexão com banco de dados estabelecida")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com banco: {e}")
            self.db = None
    
    def _test_connection(self) -> bool:
        """Testa se a conexão com o banco está ativa"""
        try:
            if self.db is None:
                return False
            
            # Teste simples de conexão
            self.db.execute(text("SELECT 1"))
            return True
            
        except Exception as e:
            logger.warning(f"Conexão com banco perdida: {e}")
            return False
    
    def _reconnect(self) -> bool:
        """Tenta reconectar com o banco de dados"""
        try:
            if self.db:
                self.db.close()
            
            self.db = next(get_db())
            
            # Testar a nova conexão
            if self._test_connection():
                logger.info("✅ Reconexão com banco bem-sucedida")
                return True
            else:
                logger.error("❌ Falha na reconexão")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro durante reconexão: {e}")
            self.db = None
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
            'postgresql connection'
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
            
            # Buscar atividade
            atividade = None
            if dados_aluno.get('atividade'):
                atividade = self.db.query(Atividade).filter(
                    Atividade.nome == dados_aluno['atividade']
                ).first()
            
            # Buscar turma
            turma = None
            if dados_aluno.get('turma'):
                turma = self.db.query(Turma).filter(
                    Turma.nome == dados_aluno['turma']
                ).first()
            
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
            
            self.db.add(novo_aluno)
            self.db.commit()
            
            # Atualizar contadores
            if atividade:
                AtividadeDAO.atualizar_total_alunos(self.db, atividade.id)
            if turma:
                TurmaDAO.atualizar_total_alunos(self.db, turma.id)
            
            logger.info(f"[ROBUSTO] ✅ Aluno salvo com ID: {novo_aluno.id}")
            return novo_aluno.id
        
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

# Instância global para uso na aplicação
db_integration_robusto = DatabaseIntegrationRobusto()
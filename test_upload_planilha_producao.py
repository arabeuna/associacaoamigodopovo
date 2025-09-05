#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar e monitorar upload de planilhas no ambiente de produção
Registra logs detalhados do processo de upload e processamento
"""

import os
import json
from datetime import datetime
from models import init_mongodb, AlunoDAO, AtividadeDAO
from database_integration_robusto import get_db_integration

def registrar_log_upload(acao, detalhes, status="INFO"):
    """Registra log específico para upload de planilhas"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "data_hora": datetime.now().strftime("%d/%m/%Y às %H:%M:%S"),
        "acao": acao,
        "detalhes": detalhes,
        "status": status,
        "ambiente": "PRODUCAO",
        "tipo": "UPLOAD_PLANILHA"
    }
    
    # Salvar no arquivo de logs específico
    log_file = "logs_upload_planilha_producao.json"
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
            
        print(f"[{status}] {timestamp} - {acao}: {detalhes}")
        
    except Exception as e:
        print(f"❌ Erro ao registrar log: {e}")

def verificar_estado_inicial():
    """Verifica o estado inicial do banco antes do upload"""
    registrar_log_upload("VERIFICACAO_INICIAL", "Iniciando verificação do estado do banco")
    
    try:
        # Conectar ao MongoDB
        db = init_mongodb()
        registrar_log_upload("CONEXAO_DB", "Conexão com MongoDB estabelecida", "SUCCESS")
        
        # Contar alunos atuais
        alunos = AlunoDAO.listar_todos()
        total_alunos = len(alunos)
        registrar_log_upload("CONTAGEM_ALUNOS", f"Total de alunos no banco: {total_alunos}")
        
        # Verificar atividades
        atividades = AtividadeDAO.listar_todas()
        total_atividades = len(atividades)
        registrar_log_upload("CONTAGEM_ATIVIDADES", f"Total de atividades: {total_atividades}")
        
        # Distribuição por atividade
        distribuicao = {}
        for aluno in alunos:
            atividade = aluno.get('atividade', 'Sem atividade')
            distribuicao[atividade] = distribuicao.get(atividade, 0) + 1
        
        registrar_log_upload("DISTRIBUICAO_ATIVIDADES", f"Distribuição: {distribuicao}")
        
        return {
            'total_alunos': total_alunos,
            'total_atividades': total_atividades,
            'distribuicao': distribuicao
        }
        
    except Exception as e:
        registrar_log_upload("ERRO_VERIFICACAO", f"Erro na verificação inicial: {str(e)}", "ERROR")
        return None

def monitorar_upload_planilha(arquivo_planilha=None):
    """Monitora o processo de upload de planilha"""
    registrar_log_upload("INICIO_MONITORAMENTO", "Iniciando monitoramento de upload de planilha")
    
    # Verificar estado inicial
    estado_inicial = verificar_estado_inicial()
    
    if arquivo_planilha:
        registrar_log_upload("ARQUIVO_DETECTADO", f"Arquivo para upload: {arquivo_planilha}")
        
        # Verificar se arquivo existe
        if os.path.exists(arquivo_planilha):
            tamanho = os.path.getsize(arquivo_planilha)
            registrar_log_upload("ARQUIVO_VALIDADO", f"Arquivo válido - Tamanho: {tamanho} bytes", "SUCCESS")
        else:
            registrar_log_upload("ARQUIVO_NAO_ENCONTRADO", f"Arquivo não encontrado: {arquivo_planilha}", "ERROR")
    
    # Instruções para o usuário
    print("\n" + "="*60)
    print("🔍 MONITORAMENTO DE UPLOAD DE PLANILHA - PRODUÇÃO")
    print("="*60)
    print(f"📊 Estado inicial: {estado_inicial['total_alunos'] if estado_inicial else 'N/A'} alunos")
    print("\n📋 INSTRUÇÕES:")
    print("1. Acesse o sistema web em produção")
    print("2. Faça login como administrador")
    print("3. Vá para 'Backup de Planilhas'")
    print("4. Faça o upload da planilha com 404 alunos")
    print("5. Execute este script novamente após o upload")
    print("\n⚠️  IMPORTANTE: Este script registra logs em 'logs_upload_planilha_producao.json'")
    print("="*60)
    
    return estado_inicial

def verificar_pos_upload():
    """Verifica o estado após o upload"""
    registrar_log_upload("VERIFICACAO_POS_UPLOAD", "Verificando estado após upload")
    
    try:
        # Verificar novamente
        estado_final = verificar_estado_inicial()
        
        if estado_final:
            registrar_log_upload("ESTADO_FINAL", f"Total final de alunos: {estado_final['total_alunos']}")
            
            # Calcular diferença (se tivermos estado inicial salvo)
            try:
                with open('logs_upload_planilha_producao.json', 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                # Buscar último estado inicial
                for log in reversed(logs):
                    if log.get('acao') == 'CONTAGEM_ALUNOS':
                        inicial_str = log['detalhes']
                        if 'Total de alunos no banco:' in inicial_str:
                            inicial = int(inicial_str.split(':')[1].strip())
                            diferenca = estado_final['total_alunos'] - inicial
                            registrar_log_upload("DIFERENCA_CALCULADA", f"Diferença: +{diferenca} alunos", "SUCCESS" if diferenca > 0 else "WARNING")
                            break
                            
            except Exception as e:
                registrar_log_upload("ERRO_CALCULO_DIFERENCA", f"Erro ao calcular diferença: {e}", "WARNING")
        
        return estado_final
        
    except Exception as e:
        registrar_log_upload("ERRO_VERIFICACAO_FINAL", f"Erro na verificação final: {str(e)}", "ERROR")
        return None

if __name__ == "__main__":
    import sys
    
    print("🚀 Script de Monitoramento de Upload - Ambiente de Produção")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--pos-upload":
            print("📊 Verificando estado PÓS-UPLOAD...")
            verificar_pos_upload()
        elif sys.argv[1] == "--pre-upload":
            print("📊 Verificando estado PRÉ-UPLOAD...")
            monitorar_upload_planilha()
        else:
            arquivo = sys.argv[1]
            print(f"📁 Monitorando upload do arquivo: {arquivo}")
            monitorar_upload_planilha(arquivo)
    else:
        print("📊 Verificação geral do sistema...")
        monitorar_upload_planilha()
    
    print("\n✅ Monitoramento concluído!")
    print(f"📝 Logs salvos em: logs_upload_planilha_producao.json")
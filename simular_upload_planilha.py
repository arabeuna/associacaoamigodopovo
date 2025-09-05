#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para simular o upload de uma planilha e demonstrar o monitoramento
Cria uma planilha de exemplo e simula o processo de upload
"""

import pandas as pd
import os
from datetime import datetime
import json

def criar_planilha_exemplo(num_alunos=404):
    """Cria uma planilha de exemplo com o número especificado de alunos"""
    print(f"📝 Criando planilha de exemplo com {num_alunos} alunos...")
    
    # Dados de exemplo
    nomes = [
        "João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Ferreira",
        "Lucia Pereira", "Roberto Lima", "Fernanda Souza", "Marcos Alves", "Patricia Rocha"
    ]
    
    atividades = [
        "Natação", "Musculação", "Pilates", "Informática", "Fisioterapia",
        "Dança", "Hidroginástica", "Funcional", "Vôlei", "Futebol"
    ]
    
    dados = []
    
    for i in range(num_alunos):
        nome_base = nomes[i % len(nomes)]
        nome = f"{nome_base} {i+1:03d}"
        
        aluno = {
            'Nome': nome,
            'CPF': f"{(i+1):011d}",
            'Data_Nascimento': f"{(i % 28) + 1:02d}/{((i % 12) + 1):02d}/{1980 + (i % 40)}",
            'Telefone': f"(11) 9{(i+1):04d}-{(i*7) % 10000:04d}",
            'Email': f"{nome.lower().replace(' ', '.')}{i+1}@email.com",
            'Endereco': f"Rua {nome_base}, {(i+1)*10}",
            'Atividade': atividades[i % len(atividades)],
            'Status': 'Ativo'
        }
        dados.append(aluno)
    
    # Criar DataFrame e salvar
    df = pd.DataFrame(dados)
    filename = f"planilha_teste_{num_alunos}_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join('uploads', filename)
    
    # Criar pasta uploads se não existir
    os.makedirs('uploads', exist_ok=True)
    
    df.to_excel(filepath, index=False)
    
    print(f"✅ Planilha criada: {filepath}")
    print(f"📊 Colunas: {list(df.columns)}")
    print(f"📈 Total de registros: {len(df)}")
    
    return filepath

def registrar_simulacao_upload(arquivo_planilha):
    """Registra a simulação de upload nos logs"""
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "data_hora": datetime.now().strftime("%d/%m/%Y às %H:%M:%S"),
        "acao": "SIMULACAO_UPLOAD",
        "detalhes": f"Planilha de teste criada: {arquivo_planilha}",
        "status": "SUCCESS",
        "ambiente": "TESTE",
        "tipo": "UPLOAD_PLANILHA"
    }
    
    # Adicionar ao log existente
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
            
        print(f"📝 Log registrado: {log_entry['detalhes']}")
        
    except Exception as e:
        print(f"❌ Erro ao registrar log: {e}")

def mostrar_instrucoes_upload(arquivo_planilha):
    """Mostra instruções detalhadas para o upload"""
    print("\n" + "="*70)
    print("📋 INSTRUÇÕES PARA UPLOAD DA PLANILHA NO AMBIENTE DE PRODUÇÃO")
    print("="*70)
    print(f"📁 Arquivo criado: {arquivo_planilha}")
    print(f"📊 Tamanho: {os.path.getsize(arquivo_planilha)} bytes")
    
    print("\n🔄 PASSOS PARA O UPLOAD:")
    print("1. 🌐 Acesse o sistema em produção (URL do Render)")
    print("2. 🔐 Faça login como administrador (admin/admin123)")
    print("3. 📂 Navegue para 'Backup de Planilhas'")
    print("4. 📤 Selecione o arquivo criado para upload")
    print("5. 🎯 Escolha a atividade apropriada")
    print("6. ✅ Confirme o upload")
    
    print("\n📊 MONITORAMENTO:")
    print("• Execute: python test_upload_planilha_producao.py --pos-upload")
    print("• Verifique os logs em: logs_upload_planilha_producao.json")
    
    print("\n⚠️  IMPORTANTE:")
    print("• O sistema atual tem 314 alunos")
    print("• Após o upload, deve ter 314 + 404 = 718 alunos")
    print("• O script de monitoramento calculará a diferença automaticamente")
    
    print("="*70)

if __name__ == "__main__":
    import sys
    
    print("🧪 Simulador de Upload de Planilha")
    print("=" * 40)
    
    # Determinar número de alunos
    num_alunos = 404
    if len(sys.argv) > 1:
        try:
            num_alunos = int(sys.argv[1])
        except ValueError:
            print("⚠️  Número inválido, usando 404 como padrão")
    
    # Criar planilha
    arquivo = criar_planilha_exemplo(num_alunos)
    
    # Registrar nos logs
    registrar_simulacao_upload(arquivo)
    
    # Mostrar instruções
    mostrar_instrucoes_upload(arquivo)
    
    print("\n✅ Simulação concluída!")
    print("🚀 Agora você pode fazer o upload real no sistema de produção")
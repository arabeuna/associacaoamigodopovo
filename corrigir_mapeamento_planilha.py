#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o mapeamento de colunas da planilha de teste
Cria uma nova planilha com os nomes de colunas corretos que o sistema reconhece
"""

import csv
import os
from datetime import datetime
import json

def criar_planilha_corrigida(num_alunos=404):
    """Cria uma planilha CSV com os nomes de colunas corretos"""
    print(f"🔧 Criando planilha CSV corrigida com {num_alunos} alunos...")
    
    # Dados de exemplo
    nomes = [
        "João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Ferreira",
        "Lucia Pereira", "Roberto Lima", "Fernanda Souza", "Marcos Alves", "Patricia Rocha",
        "Bruno Martins", "Carla Dias", "Diego Nascimento", "Eliana Barbosa", "Fabio Cardoso",
        "Gabriela Moreira", "Henrique Teixeira", "Isabela Campos", "Jorge Ribeiro", "Karina Lopes"
    ]
    
    atividades = [
        "Natação", "Musculação", "Pilates", "Informática", "Fisioterapia",
        "Dança", "Hidroginástica", "Funcional", "Vôlei", "Futebol", "Cadastro Geral"
    ]
    
    # Criar pasta uploads se não existir
    os.makedirs('uploads', exist_ok=True)
    
    # Nome do arquivo
    filename = f"planilha_corrigida_{num_alunos}_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join('uploads', filename)
    
    # Criar arquivo CSV com nomes de colunas corretos
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        # Usar os nomes de colunas que o sistema reconhece
        fieldnames = ['nome', 'telefone', 'email', 'endereco', 'data_nascimento', 'titulo_eleitor', 'atividades', 'observacoes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escrever cabeçalho
        writer.writeheader()
        
        # Escrever dados
        for i in range(num_alunos):
            nome_base = nomes[i % len(nomes)]
            nome = f"{nome_base} {i+1:03d}"
            
            # Gerar título de eleitor fictício
            titulo_eleitor = f"{(i+1):012d}"
            
            aluno = {
                'nome': nome,
                'telefone': f"(11) 9{(i+1):04d}-{(i*7) % 10000:04d}",
                'email': f"{nome.lower().replace(' ', '.')}{i+1}@email.com",
                'endereco': f"Rua {nome_base}, {(i+1)*10}, São Paulo - SP",
                'data_nascimento': f"{(i % 28) + 1:02d}/{((i % 12) + 1):02d}/{1980 + (i % 40)}",
                'titulo_eleitor': titulo_eleitor,
                'atividades': atividades[i % len(atividades)],
                'observacoes': f"Aluno importado via planilha corrigida - {datetime.now().strftime('%d/%m/%Y')}"
            }
            
            writer.writerow(aluno)
    
    print(f"✅ Planilha CSV corrigida criada: {filepath}")
    print(f"📊 Colunas corretas: {fieldnames}")
    print(f"📈 Total de registros: {num_alunos}")
    print(f"📁 Tamanho do arquivo: {os.path.getsize(filepath)} bytes")
    
    return filepath

def registrar_log_correcao(arquivo_planilha):
    """Registra a correção da planilha nos logs"""
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "data_hora": datetime.now().strftime("%d/%m/%Y às %H:%M:%S"),
        "acao": "PLANILHA_CORRIGIDA_CRIADA",
        "detalhes": f"Planilha CSV com mapeamento correto criada: {arquivo_planilha}",
        "status": "SUCCESS",
        "ambiente": "TESTE",
        "tipo": "CORRECAO_MAPEAMENTO",
        "colunas_corretas": ['nome', 'telefone', 'email', 'endereco', 'data_nascimento', 'titulo_eleitor', 'atividades', 'observacoes']
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
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Log registrado em {log_file}")
        
    except Exception as e:
        print(f"⚠️ Erro ao registrar log: {e}")

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DO MAPEAMENTO DE COLUNAS DA PLANILHA")
    print("=" * 50)
    
    # Criar planilha corrigida
    arquivo_planilha = criar_planilha_corrigida(404)
    
    # Registrar nos logs
    registrar_log_correcao(arquivo_planilha)
    
    print("\n📋 RESUMO DA CORREÇÃO:")
    print("- Problema identificado: Mapeamento incorreto de colunas")
    print("- Colunas antigas: Nome, CPF, Data_Nascimento, Telefone, Email, Endereco, Atividade, Status")
    print("- Colunas corretas: nome, telefone, email, endereco, data_nascimento, titulo_eleitor, atividades, observacoes")
    print("- Nova planilha criada com mapeamento correto")
    print(f"- Arquivo: {arquivo_planilha}")
    print("\n✅ Correção concluída! Agora você pode testar o upload novamente.")

if __name__ == "__main__":
    main()
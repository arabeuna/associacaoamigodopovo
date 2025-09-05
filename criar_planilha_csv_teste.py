#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar planilha CSV de teste sem dependência do pandas
Cria um arquivo CSV com 404 alunos para testar o upload
"""

import csv
import os
from datetime import datetime
import json

def criar_planilha_csv(num_alunos=404):
    """Cria uma planilha CSV com o número especificado de alunos"""
    print(f"📝 Criando planilha CSV com {num_alunos} alunos...")
    
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
    filename = f"planilha_teste_{num_alunos}_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join('uploads', filename)
    
    # Criar arquivo CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Nome', 'CPF', 'Data_Nascimento', 'Telefone', 'Email', 'Endereco', 'Atividade', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escrever cabeçalho
        writer.writeheader()
        
        # Escrever dados
        for i in range(num_alunos):
            nome_base = nomes[i % len(nomes)]
            nome = f"{nome_base} {i+1:03d}"
            
            # Gerar CPF fictício
            cpf = f"{(i+1):011d}"
            cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
            
            aluno = {
                'Nome': nome,
                'CPF': cpf_formatado,
                'Data_Nascimento': f"{(i % 28) + 1:02d}/{((i % 12) + 1):02d}/{1980 + (i % 40)}",
                'Telefone': f"(11) 9{(i+1):04d}-{(i*7) % 10000:04d}",
                'Email': f"{nome.lower().replace(' ', '.')}{i+1}@email.com",
                'Endereco': f"Rua {nome_base}, {(i+1)*10}, São Paulo - SP",
                'Atividade': atividades[i % len(atividades)],
                'Status': 'Ativo'
            }
            
            writer.writerow(aluno)
    
    print(f"✅ Planilha CSV criada: {filepath}")
    print(f"📊 Colunas: {fieldnames}")
    print(f"📈 Total de registros: {num_alunos}")
    print(f"📁 Tamanho do arquivo: {os.path.getsize(filepath)} bytes")
    
    return filepath

def registrar_log_criacao(arquivo_planilha):
    """Registra a criação da planilha nos logs"""
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "data_hora": datetime.now().strftime("%d/%m/%Y às %H:%M:%S"),
        "acao": "PLANILHA_TESTE_CRIADA",
        "detalhes": f"Planilha CSV de teste criada: {arquivo_planilha}",
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

def mostrar_preview_planilha(arquivo_planilha, linhas=5):
    """Mostra preview das primeiras linhas da planilha"""
    print(f"\n👀 Preview das primeiras {linhas} linhas:")
    print("-" * 80)
    
    try:
        with open(arquivo_planilha, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Mostrar cabeçalho
            print(f"{'Nome':<25} {'CPF':<15} {'Atividade':<15} {'Telefone':<15}")
            print("-" * 80)
            
            # Mostrar primeiras linhas
            for i, row in enumerate(reader):
                if i >= linhas:
                    break
                print(f"{row['Nome']:<25} {row['CPF']:<15} {row['Atividade']:<15} {row['Telefone']:<15}")
            
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Erro ao ler preview: {e}")

def mostrar_instrucoes_completas(arquivo_planilha):
    """Mostra instruções completas para o upload"""
    print("\n" + "="*80)
    print("📋 INSTRUÇÕES COMPLETAS PARA TESTE DE UPLOAD - AMBIENTE DE PRODUÇÃO")
    print("="*80)
    
    print(f"📁 Arquivo criado: {arquivo_planilha}")
    print(f"📊 Formato: CSV (compatível com Excel)")
    print(f"💾 Tamanho: {os.path.getsize(arquivo_planilha)} bytes")
    
    print("\n🎯 OBJETIVO DO TESTE:")
    print("• Verificar se o sistema processa corretamente 404 novos alunos")
    print("• Estado atual: 314 alunos no banco")
    print("• Estado esperado após upload: 718 alunos (314 + 404)")
    
    print("\n🔄 PASSOS DETALHADOS:")
    print("1. 🌐 Acesse o sistema em produção")
    print("2. 🔐 Login: admin / admin123")
    print("3. 📂 Menu: 'Backup de Planilhas'")
    print("4. 📤 Upload do arquivo CSV criado")
    print("5. 🎯 Selecione atividade: 'Cadastro Geral' (recomendado)")
    print("6. ✅ Confirme o upload")
    print("7. ⏱️  Aguarde o processamento")
    
    print("\n📊 MONITORAMENTO PÓS-UPLOAD:")
    print("• Execute: python test_upload_planilha_producao.py --pos-upload")
    print("• Verifique diferença de alunos nos logs")
    print("• Confirme se todos os 404 alunos foram adicionados")
    
    print("\n⚠️  PONTOS DE ATENÇÃO:")
    print("• Verifique se não há duplicatas de CPF")
    print("• Confirme se as atividades foram atribuídas corretamente")
    print("• Monitore possíveis erros durante o processamento")
    
    print("\n📝 LOGS E MONITORAMENTO:")
    print("• Logs detalhados: logs_upload_planilha_producao.json")
    print("• Logs do sistema: logs_atividades.json")
    print("• Verificação: python test_mongodb_alunos.py")
    
    print("="*80)

if __name__ == "__main__":
    import sys
    
    print("📊 Criador de Planilha CSV para Teste de Upload")
    print("=" * 50)
    
    # Determinar número de alunos
    num_alunos = 404
    if len(sys.argv) > 1:
        try:
            num_alunos = int(sys.argv[1])
        except ValueError:
            print("⚠️  Número inválido, usando 404 como padrão")
    
    # Criar planilha CSV
    arquivo = criar_planilha_csv(num_alunos)
    
    # Registrar nos logs
    registrar_log_criacao(arquivo)
    
    # Mostrar preview
    mostrar_preview_planilha(arquivo)
    
    # Mostrar instruções completas
    mostrar_instrucoes_completas(arquivo)
    
    print("\n✅ Planilha CSV criada com sucesso!")
    print("🚀 Pronta para upload no ambiente de produção")
    print(f"📁 Localização: {os.path.abspath(arquivo)}")
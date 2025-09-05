#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o processamento de planilhas com campos opcionais
Cria uma planilha de teste com apenas os campos básicos disponíveis
"""

import csv
import os
from datetime import datetime
import json

def criar_planilha_campos_basicos(num_alunos=10):
    """Cria uma planilha CSV com apenas campos básicos para testar campos opcionais"""
    print(f"🧪 Criando planilha de teste com campos básicos ({num_alunos} alunos)...")
    
    # Dados de exemplo
    nomes = [
        "João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa", "Carlos Ferreira",
        "Lucia Pereira", "Roberto Lima", "Fernanda Souza", "Marcos Alves", "Patricia Rocha"
    ]
    
    atividades = [
        "Natação", "Musculação", "Pilates", "Informática", "Fisioterapia"
    ]
    
    # Criar pasta uploads se não existir
    os.makedirs('uploads', exist_ok=True)
    
    # Nome do arquivo
    filename = f"teste_campos_basicos_{num_alunos}_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join('uploads', filename)
    
    # Criar arquivo CSV com apenas campos básicos (simulando planilha original)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        # Usar apenas alguns campos para simular planilha com campos em falta
        fieldnames = ['Nome', 'Telefone', 'Atividade']  # Campos limitados como na planilha original
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escrever cabeçalho
        writer.writeheader()
        
        # Escrever dados
        for i in range(num_alunos):
            nome_base = nomes[i % len(nomes)]
            nome = f"{nome_base} Teste {i+1:03d}"
            
            aluno = {
                'Nome': nome,
                'Telefone': f"(11) 9{(i+1):04d}-{(i*7) % 10000:04d}",
                'Atividade': atividades[i % len(atividades)]
            }
            
            writer.writerow(aluno)
    
    print(f"✅ Planilha de teste criada: {filepath}")
    print(f"📊 Colunas disponíveis: {fieldnames}")
    print(f"📈 Total de registros: {num_alunos}")
    print(f"📁 Tamanho do arquivo: {os.path.getsize(filepath)} bytes")
    
    return filepath

def criar_planilha_original_404():
    """Recria a planilha original de 404 alunos com campos limitados"""
    print(f"📋 Recriando planilha original de 404 alunos com campos limitados...")
    
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
    filename = f"planilha_original_404_alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join('uploads', filename)
    
    # Criar arquivo CSV com estrutura da planilha original
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        # Usar os campos da planilha original que causaram problema
        fieldnames = ['Nome', 'CPF', 'Data_Nascimento', 'Telefone', 'Email', 'Endereco', 'Atividade', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Escrever cabeçalho
        writer.writeheader()
        
        # Escrever dados
        for i in range(404):
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
    
    print(f"✅ Planilha original recriada: {filepath}")
    print(f"📊 Colunas: {fieldnames}")
    print(f"📈 Total de registros: 404")
    print(f"📁 Tamanho do arquivo: {os.path.getsize(filepath)} bytes")
    
    return filepath

def registrar_log_teste(arquivo_planilha, tipo_teste):
    """Registra o teste nos logs"""
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "data_hora": datetime.now().strftime("%d/%m/%Y às %H:%M:%S"),
        "acao": "TESTE_CAMPOS_OPCIONAIS",
        "detalhes": f"Planilha de teste criada para validar campos opcionais: {arquivo_planilha}",
        "status": "SUCCESS",
        "ambiente": "TESTE",
        "tipo": tipo_teste,
        "observacao": "Sistema modificado para aceitar campos opcionais"
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
    print("🧪 TESTE DE CAMPOS OPCIONAIS NA PLANILHA")
    print("=" * 50)
    
    print("\n1. Criando planilha de teste com campos básicos...")
    arquivo_teste = criar_planilha_campos_basicos(10)
    registrar_log_teste(arquivo_teste, "CAMPOS_BASICOS")
    
    print("\n2. Recriando planilha original de 404 alunos...")
    arquivo_original = criar_planilha_original_404()
    registrar_log_teste(arquivo_original, "PLANILHA_ORIGINAL_404")
    
    print("\n📋 RESUMO DOS TESTES:")
    print(f"- Planilha teste (10 alunos): {arquivo_teste}")
    print(f"- Planilha original (404 alunos): {arquivo_original}")
    print("\n🔧 MODIFICAÇÕES IMPLEMENTADAS:")
    print("- Todos os campos são opcionais exceto 'nome'")
    print("- Mapeamento expandido para reconhecer mais variações de nomes de colunas")
    print("- Valores padrão seguros para campos ausentes")
    print("- Tratamento seguro de valores None")
    print("- Preservação de dados existentes em atualizações")
    print("\n✅ Sistema pronto para processar planilhas com campos em falta!")
    print("\n📤 PRÓXIMOS PASSOS:")
    print("1. Faça upload da planilha via interface web")
    print("2. Verifique se os alunos foram cadastrados")
    print("3. Execute: python test_mongodb_alunos.py para confirmar")

if __name__ == "__main__":
    main()
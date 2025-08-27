#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair dados das planilhas Excel da Academia Amigo do Povo
e preparar para migração para Google Sheets
"""

try:
    import pandas as pd
    import openpyxl
    import json
    from datetime import datetime
    import os
except ImportError as e:
    print(f"Erro: Biblioteca não encontrada - {e}")
    print("Execute: pip install openpyxl pandas")
    exit(1)

def extrair_cadastros():
    """Extrai dados do arquivo de cadastros"""
    try:
        # Lê o arquivo Excel de cadastros
        arquivo_cadastros = "Cadastros_Unificados_GOOGLE_v2.xlsx"
        if not os.path.exists(arquivo_cadastros):
            print(f"Arquivo não encontrado: {arquivo_cadastros}")
            return None
            
        # Tenta ler todas as abas
        excel_file = pd.ExcelFile(arquivo_cadastros)
        print(f"Abas encontradas em {arquivo_cadastros}: {excel_file.sheet_names}")
        
        dados_cadastros = {}
        for aba in excel_file.sheet_names:
            try:
                df = pd.read_excel(arquivo_cadastros, sheet_name=aba)
                print(f"\nAba '{aba}' - {len(df)} linhas, {len(df.columns)} colunas")
                print(f"Colunas: {list(df.columns)}")
                dados_cadastros[aba] = df.to_dict('records')
            except Exception as e:
                print(f"Erro ao ler aba '{aba}': {e}")
                continue
                
        return dados_cadastros
        
    except Exception as e:
        print(f"Erro ao extrair cadastros: {e}")
        return None

def extrair_presenca():
    """Extrai dados do arquivo de presença"""
    try:
        # Lê o arquivo Excel de presença
        arquivo_presenca = "FICHA_DE_PRESENCA_REMODELADA_CONSOLIDADA.xlsx"
        if not os.path.exists(arquivo_presenca):
            print(f"Arquivo não encontrado: {arquivo_presenca}")
            return None
            
        # Tenta ler todas as abas
        excel_file = pd.ExcelFile(arquivo_presenca)
        print(f"\nAbas encontradas em {arquivo_presenca}: {excel_file.sheet_names}")
        
        dados_presenca = {}
        for aba in excel_file.sheet_names:
            try:
                df = pd.read_excel(arquivo_presenca, sheet_name=aba)
                print(f"\nAba '{aba}' - {len(df)} linhas, {len(df.columns)} colunas")
                print(f"Colunas: {list(df.columns)}")
                dados_presenca[aba] = df.to_dict('records')
            except Exception as e:
                print(f"Erro ao ler aba '{aba}': {e}")
                continue
                
        return dados_presenca
        
    except Exception as e:
        print(f"Erro ao extrair presença: {e}")
        return None

def salvar_dados_json(dados, nome_arquivo):
    """Salva os dados em formato JSON para análise"""
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
        print(f"Dados salvos em: {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar {nome_arquivo}: {e}")

def main():
    print("=== EXTRAÇÃO DE DADOS - ACADEMIA AMIGO DO POVO ===\n")
    
    # Extrai dados de cadastros
    print("📋 Extraindo dados de cadastros...")
    cadastros = extrair_cadastros()
    if cadastros:
        salvar_dados_json(cadastros, "dados_cadastros.json")
    
    # Extrai dados de presença
    print("\n✅ Extraindo dados de presença...")
    presenca = extrair_presenca()
    if presenca:
        salvar_dados_json(presenca, "dados_presenca.json")
    
    print("\n🎉 Extração concluída!")
    print("Arquivos gerados:")
    print("- dados_cadastros.json")
    print("- dados_presenca.json")

if __name__ == "__main__":
    main()


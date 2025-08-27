#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para ler as planilhas Excel da Academia
e entender a estrutura dos dados
"""

try:
    # Tentar importar pandas usando diferentes métodos
    import subprocess
    import sys
    
    def instalar_biblioteca(nome):
        subprocess.check_call([sys.executable, "-m", "pip", "install", nome])
    
    try:
        import pandas as pd
    except ImportError:
        print("Instalando pandas...")
        instalar_biblioteca("pandas")
        import pandas as pd
    
    try:
        import openpyxl
    except ImportError:
        print("Instalando openpyxl...")
        instalar_biblioteca("openpyxl")
        import openpyxl
        
    import os
    
    print("=== ANÁLISE DAS PLANILHAS DA ACADEMIA ===\n")
    
    # Verificar se os arquivos existem
    arquivo_cadastros = "outros/Cadastros_Unificados_GOOGLE_v2.xlsx"
    arquivo_presenca = "outros/FICHA_DE_PRESENCA_REMODELADA_CONSOLIDADA.xlsx"
    
    print("📋 ANALISANDO CADASTROS...")
    if os.path.exists(arquivo_cadastros):
        try:
            # Ler o arquivo Excel
            excel_cadastros = pd.ExcelFile(arquivo_cadastros)
            print(f"✅ Arquivo encontrado: {arquivo_cadastros}")
            print(f"📊 Abas disponíveis: {excel_cadastros.sheet_names}")
            
            # Para cada aba, mostrar informações
            for aba in excel_cadastros.sheet_names:
                try:
                    df = pd.read_excel(arquivo_cadastros, sheet_name=aba)
                    print(f"\n--- ABA: {aba} ---")
                    print(f"📏 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
                    print(f"📝 Colunas: {list(df.columns)}")
                    
                    # Mostrar algumas amostras de dados
                    if len(df) > 0:
                        print(f"📋 Primeiras 3 linhas:")
                        for i in range(min(3, len(df))):
                            print(f"  Linha {i+1}: {df.iloc[i].to_dict()}")
                    
                except Exception as e:
                    print(f"❌ Erro ao ler aba {aba}: {e}")
                    
        except Exception as e:
            print(f"❌ Erro ao abrir arquivo de cadastros: {e}")
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_cadastros}")
    
    print("\n" + "="*50)
    print("✅ ANALISANDO PRESENÇA...")
    
    if os.path.exists(arquivo_presenca):
        try:
            excel_presenca = pd.ExcelFile(arquivo_presenca)
            print(f"✅ Arquivo encontrado: {arquivo_presenca}")
            print(f"📊 Abas disponíveis: {excel_presenca.sheet_names}")
            
            # Para cada aba, mostrar informações
            for aba in excel_presenca.sheet_names:
                try:
                    df = pd.read_excel(arquivo_presenca, sheet_name=aba)
                    print(f"\n--- ABA: {aba} ---")
                    print(f"📏 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
                    print(f"📝 Colunas: {list(df.columns)}")
                    
                    # Mostrar algumas amostras de dados
                    if len(df) > 0:
                        print(f"📋 Primeiras 3 linhas:")
                        for i in range(min(3, len(df))):
                            print(f"  Linha {i+1}: {df.iloc[i].to_dict()}")
                    
                except Exception as e:
                    print(f"❌ Erro ao ler aba {aba}: {e}")
                    
        except Exception as e:
            print(f"❌ Erro ao abrir arquivo de presença: {e}")
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_presenca}")
    
    print("\n" + "="*50)
    print("🎯 ANÁLISE CONCLUÍDA!")
    print("Agora posso adaptar o sistema para seus dados reais!")

except Exception as e:
    print(f"❌ Erro geral: {e}")
    print("Vou tentar uma abordagem alternativa...")
    
    # Abordagem alternativa sem pandas
    print("\n🔄 Tentando método alternativo...")
    
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        
        print("📁 Verificando estrutura dos arquivos Excel...")
        
        for arquivo in ["outros/Cadastros_Unificados_GOOGLE_v2.xlsx", 
                       "outros/FICHA_DE_PRESENCA_REMODELADA_CONSOLIDADA.xlsx"]:
            if os.path.exists(arquivo):
                print(f"✅ Arquivo existe: {arquivo}")
                try:
                    # Excel é um arquivo ZIP, vamos ver o que tem dentro
                    with zipfile.ZipFile(arquivo, 'r') as zip_ref:
                        print(f"📦 Conteúdo do arquivo: {zip_ref.namelist()[:10]}...")
                except:
                    print(f"⚠️ Não consegui abrir como ZIP: {arquivo}")
            else:
                print(f"❌ Arquivo não encontrado: {arquivo}")
                
    except Exception as e2:
        print(f"❌ Método alternativo também falhou: {e2}")
        print("\n💡 SOLUÇÃO: Você pode:")
        print("1. Abrir as planilhas no Google Sheets")
        print("2. Fazer Arquivo → Download → CSV")  
        print("3. Me dizer qual estrutura você vê")

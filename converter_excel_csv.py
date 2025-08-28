#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para converter Excel para CSV sem usar pandas
Usa apenas bibliotecas padrão do Python
"""

def converter_excel_para_csv():
    """Instrui como converter Excel para CSV manualmente"""
    
    print("=" * 60)
    print("🔄 CONVERSOR EXCEL PARA CSV - SEM PANDAS")
    print("=" * 60)
    
    print("\n📋 INSTRUÇÕES PARA CONVERTER:")
    print("=" * 40)
    
    print("\n1️⃣ OPÇÃO 1 - USANDO GOOGLE SHEETS (RECOMENDADO):")
    print("   • Acesse: https://sheets.google.com")
    print("   • Clique em 'Abrir' → 'Upload'")
    print("   • Selecione: outros/Cadastros_Unificados_GOOGLE_v2.xlsx")
    print("   • Após abrir, vá em: Arquivo → Download → CSV (.csv)")
    print("   • Salve como: outros/Cadastros_Unificados_GOOGLE_v2.csv")
    
    print("\n2️⃣ OPÇÃO 2 - USANDO EXCEL/LIBREOFFICE:")
    print("   • Abra o arquivo: outros/Cadastros_Unificados_GOOGLE_v2.xlsx")
    print("   • Vá em: Arquivo → Salvar Como")
    print("   • Escolha o tipo: CSV (separado por vírgulas)")
    print("   • Salve como: outros/Cadastros_Unificados_GOOGLE_v2.csv")
    
    print("\n3️⃣ OPÇÃO 3 - USAR ARQUIVO EXISTENTE:")
    print("   • Já existe: outros/Cadastros_Unificados_Backup_20250827_101547.csv")
    print("   • O sistema pode usar este arquivo automaticamente!")
    
    print("\n🎯 DEPOIS DE CONVERTER:")
    print("   • Execute: python app.py")
    print("   • O sistema vai detectar automaticamente o CSV")
    print("   • Todos os alunos serão importados!")
    
    print("\n" + "=" * 60)
    
    # Verificar arquivos existentes
    import os
    
    print("\n📁 ARQUIVOS ENCONTRADOS:")
    pasta_outros = 'outros'
    
    if os.path.exists(pasta_outros):
        arquivos = os.listdir(pasta_outros)
        
        for arquivo in arquivos:
            if arquivo.endswith('.xlsx'):
                print(f"   📊 Excel: {arquivo}")
            elif arquivo.endswith('.csv'):
                print(f"   ✅ CSV: {arquivo}")
    
    # Tentar ler CSV existente
    csv_backup = 'outros/Cadastros_Unificados_Backup_20250827_101547.csv'
    if os.path.exists(csv_backup):
        print(f"\n✅ ARQUIVO CSV ENCONTRADO: {csv_backup}")
        
        try:
            with open(csv_backup, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                print(f"   📊 Total de linhas: {len(linhas)}")
                
                # Mostrar cabeçalho
                for i, linha in enumerate(linhas[:10]):
                    print(f"   Linha {i+1}: {linha.strip()[:80]}...")
                    
        except Exception as e:
            print(f"   ❌ Erro ao ler: {e}")
    
    print("\n🚀 PRONTO! Execute o sistema com: python app.py")

if __name__ == "__main__":
    converter_excel_para_csv()

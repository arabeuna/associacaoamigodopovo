#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🔍 Testando carregamento de dados do sistema...")

try:
    from app import academia
    
    print(f"\n📊 DADOS CARREGADOS:")
    print(f"   - Total de alunos: {len(academia.alunos_reais)}")
    
    if len(academia.alunos_reais) > 0:
        print(f"\n👥 PRIMEIROS 5 ALUNOS:")
        for i, aluno in enumerate(academia.alunos_reais[:5], 1):
            nome = aluno.get('nome', 'N/A')
            atividade = aluno.get('atividade', 'N/A')
            print(f"   {i}. {nome} - {atividade}")
    else:
        print("\n❌ NENHUM ALUNO CARREGADO!")
        print("\n🔧 POSSÍVEIS CAUSAS:")
        print("   1. Problema na conexão com MongoDB")
        print("   2. Sistema usando dados embutidos/fallback")
        print("   3. Configuração incorreta do .env")
    
    print(f"\n🎯 RESULTADO: {'✅ DADOS CARREGADOS' if len(academia.alunos_reais) > 0 else '❌ SEM DADOS'}")
    
except Exception as e:
    print(f"❌ ERRO ao carregar sistema: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("TESTE FINALIZADO")
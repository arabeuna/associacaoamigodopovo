#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para identificar e remover alunos duplicados no banco de dados
Os 878 alunos parecem ser dados duplicados que precisam ser limpos
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict

# Carregar configurações de produção
print("📋 Carregando configurações de produção (.env.production)")
load_dotenv('.env.production', override=True)

# Importar módulos necessários
try:
    from app import app
    from models import SessionLocal, Aluno
    print("✅ Módulos importados com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar módulos: {e}")
    sys.exit(1)

def identificar_duplicatas():
    """Identifica alunos duplicados no banco de dados"""
    print("\n🔍 IDENTIFICANDO ALUNOS DUPLICADOS")
    print("=" * 50)
    
    try:
        with app.app_context():
            db_session = SessionLocal()
            
            try:
                # Buscar todos os alunos
                print("\n📊 Analisando alunos no banco...")
                todos_alunos = db_session.query(Aluno).all()
                total_alunos = len(todos_alunos)
                print(f"  Total de alunos: {total_alunos}")
                
                # Agrupar por critérios de duplicação
                duplicatas_nome = defaultdict(list)
                duplicatas_nome_atividade = defaultdict(list)
                duplicatas_id_unico = defaultdict(list)
                
                for aluno in todos_alunos:
                    # Agrupar por nome (case-insensitive)
                    nome_limpo = aluno.nome.strip().upper() if aluno.nome else "SEM_NOME"
                    duplicatas_nome[nome_limpo].append(aluno)
                    
                    # Agrupar por nome + atividade
                    chave_nome_atividade = f"{nome_limpo}_{aluno.atividade_id or 'SEM_ATIVIDADE'}"
                    duplicatas_nome_atividade[chave_nome_atividade].append(aluno)
                    
                    # Agrupar por id_unico (se existir)
                    if hasattr(aluno, 'id_unico') and aluno.id_unico:
                        duplicatas_id_unico[aluno.id_unico].append(aluno)
                
                # Analisar duplicatas por nome
                print("\n🔍 Duplicatas por NOME:")
                duplicatas_nome_encontradas = {k: v for k, v in duplicatas_nome.items() if len(v) > 1}
                print(f"  Nomes duplicados: {len(duplicatas_nome_encontradas)}")
                
                total_duplicatas_nome = sum(len(v) - 1 for v in duplicatas_nome_encontradas.values())
                print(f"  Total de registros duplicados por nome: {total_duplicatas_nome}")
                
                # Mostrar exemplos de duplicatas por nome
                if duplicatas_nome_encontradas:
                    print("\n📋 Exemplos de duplicatas por nome (primeiros 5):")
                    for i, (nome, alunos) in enumerate(list(duplicatas_nome_encontradas.items())[:5], 1):
                        print(f"  {i}. {nome} ({len(alunos)} registros)")
                        for j, aluno in enumerate(alunos[:3], 1):
                            print(f"     {j}. ID: {aluno.id}, Atividade: {aluno.atividade_id}, Data: {aluno.data_cadastro}")
                        if len(alunos) > 3:
                            print(f"     ... e mais {len(alunos) - 3} registros")
                
                # Analisar duplicatas por nome + atividade
                print("\n🔍 Duplicatas por NOME + ATIVIDADE:")
                duplicatas_nome_ativ_encontradas = {k: v for k, v in duplicatas_nome_atividade.items() if len(v) > 1}
                print(f"  Combinações nome+atividade duplicadas: {len(duplicatas_nome_ativ_encontradas)}")
                
                total_duplicatas_nome_ativ = sum(len(v) - 1 for v in duplicatas_nome_ativ_encontradas.values())
                print(f"  Total de registros duplicados por nome+atividade: {total_duplicatas_nome_ativ}")
                
                # Analisar duplicatas por id_unico
                if duplicatas_id_unico:
                    print("\n🔍 Duplicatas por ID_UNICO:")
                    duplicatas_id_encontradas = {k: v for k, v in duplicatas_id_unico.items() if len(v) > 1}
                    print(f"  IDs únicos duplicados: {len(duplicatas_id_encontradas)}")
                    
                    total_duplicatas_id = sum(len(v) - 1 for v in duplicatas_id_encontradas.values())
                    print(f"  Total de registros duplicados por id_unico: {total_duplicatas_id}")
                
                # Resumo geral
                print("\n📊 RESUMO DE DUPLICATAS:")
                print(f"  Total de alunos no banco: {total_alunos}")
                print(f"  Nomes únicos: {len(duplicatas_nome)}")
                print(f"  Combinações nome+atividade únicas: {len(duplicatas_nome_atividade)}")
                print(f"  Possíveis duplicatas por nome: {total_duplicatas_nome}")
                print(f"  Possíveis duplicatas por nome+atividade: {total_duplicatas_nome_ativ}")
                
                # Calcular alunos únicos estimados
                alunos_unicos_estimados = len(duplicatas_nome)
                print(f"  Alunos únicos estimados (por nome): {alunos_unicos_estimados}")
                print(f"  Registros a serem removidos: {total_alunos - alunos_unicos_estimados}")
                
                return duplicatas_nome_encontradas, duplicatas_nome_ativ_encontradas
                
            except Exception as e:
                print(f"❌ Erro durante a análise: {e}")
                import traceback
                traceback.print_exc()
                return None, None
            
            finally:
                db_session.close()
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def remover_duplicatas(duplicatas_nome, duplicatas_nome_ativ, criterio='nome'):
    """Remove duplicatas mantendo o registro mais antigo"""
    print(f"\n🗑️  REMOVENDO DUPLICATAS (critério: {criterio})")
    print("=" * 50)
    
    if criterio == 'nome':
        duplicatas_para_remover = duplicatas_nome
    else:
        duplicatas_para_remover = duplicatas_nome_ativ
    
    if not duplicatas_para_remover:
        print("✅ Nenhuma duplicata encontrada para remoção!")
        return
    
    try:
        with app.app_context():
            db_session = SessionLocal()
            
            try:
                total_removidos = 0
                
                for chave, alunos in duplicatas_para_remover.items():
                    if len(alunos) <= 1:
                        continue
                    
                    # Ordenar por data de cadastro (manter o mais antigo)
                    alunos_ordenados = sorted(alunos, key=lambda x: x.data_cadastro or datetime.min)
                    aluno_manter = alunos_ordenados[0]
                    alunos_remover = alunos_ordenados[1:]
                    
                    print(f"\n📝 {chave}:")
                    print(f"  Mantendo: ID {aluno_manter.id} (cadastrado em {aluno_manter.data_cadastro})")
                    print(f"  Removendo: {len(alunos_remover)} registros")
                    
                    # Remover duplicatas
                    for aluno in alunos_remover:
                        print(f"    - Removendo ID {aluno.id} (cadastrado em {aluno.data_cadastro})")
                        db_session.delete(aluno)
                        total_removidos += 1
                
                # Confirmar as mudanças
                print(f"\n💾 Confirmando remoção de {total_removidos} registros...")
                db_session.commit()
                
                print(f"✅ {total_removidos} alunos duplicados removidos com sucesso!")
                
                # Verificar status final
                print("\n📊 Status após limpeza:")
                total_final = db_session.query(Aluno).count()
                print(f"  Total de alunos restantes: {total_final}")
                
            except Exception as e:
                print(f"❌ Erro durante a remoção: {e}")
                db_session.rollback()
                import traceback
                traceback.print_exc()
            
            finally:
                db_session.close()
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("\n🧹 LIMPEZA DE ALUNOS DUPLICADOS")
    print("=" * 60)
    
    # Identificar duplicatas
    duplicatas_nome, duplicatas_nome_ativ = identificar_duplicatas()
    
    if duplicatas_nome is None:
        print("❌ Erro na identificação de duplicatas")
        return
    
    if not duplicatas_nome and not duplicatas_nome_ativ:
        print("✅ Nenhuma duplicata encontrada!")
        return
    
    # Perguntar ao usuário qual critério usar
    print("\n❓ Qual critério usar para remoção de duplicatas?")
    print("  1. Por NOME (mais agressivo - remove mais registros)")
    print("  2. Por NOME + ATIVIDADE (mais conservador)")
    print("  3. Apenas analisar (não remover)")
    
    escolha = input("\nEscolha (1/2/3): ").strip()
    
    if escolha == '1':
        print("\n⚠️  ATENÇÃO: Isso removerá duplicatas baseado apenas no NOME!")
        confirmar = input("Confirma a remoção? (s/N): ").strip().lower()
        if confirmar == 's':
            remover_duplicatas(duplicatas_nome, duplicatas_nome_ativ, 'nome')
    elif escolha == '2':
        print("\n⚠️  ATENÇÃO: Isso removerá duplicatas baseado em NOME + ATIVIDADE!")
        confirmar = input("Confirma a remoção? (s/N): ").strip().lower()
        if confirmar == 's':
            remover_duplicatas(duplicatas_nome, duplicatas_nome_ativ, 'nome_atividade')
    else:
        print("✅ Análise concluída sem remoções")
    
    print("\n" + "=" * 60)
    print(f"🏁 LIMPEZA CONCLUÍDA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
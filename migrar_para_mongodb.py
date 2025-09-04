#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Migrar Dados do Localhost para MongoDB Atlas
Associação Amigo do Povo

Este script migra os dados do arquivo dados_alunos.json para o MongoDB Atlas
usado na produção do Render.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Carregar configurações de produção
load_dotenv('.env.production')

# Importar modelos MongoDB
from models import init_mongodb, AlunoDAO, AtividadeDAO, TurmaDAO, LogAtividadeDAO

class MigradorMongoDB:
    def __init__(self):
        print('🔄 Inicializando migração para MongoDB Atlas...')
        self.db = init_mongodb()
        if self.db is None:
            raise Exception('❌ Não foi possível conectar ao MongoDB Atlas')
        
        self.aluno_dao = AlunoDAO()
        self.atividade_dao = AtividadeDAO()
        self.turma_dao = TurmaDAO()
        self.log_dao = LogAtividadeDAO()
        
    def migrar_atividades_basicas(self):
        """Migra atividades básicas para o MongoDB"""
        print('\n📚 Migrando atividades básicas...')
        
        atividades_basicas = [
            {'nome': 'Informática', 'descricao': 'Curso de informática básica', 'ativo': True},
            {'nome': 'Fisioterapia', 'descricao': 'Sessões de fisioterapia', 'ativo': True},
            {'nome': 'Dança', 'descricao': 'Aulas de dança', 'ativo': True},
            {'nome': 'Hidroginástica', 'descricao': 'Exercícios aquáticos', 'ativo': True},
            {'nome': 'Funcional', 'descricao': 'Treinamento funcional', 'ativo': True},
            {'nome': 'Vôlei', 'descricao': 'Aulas de vôlei', 'ativo': True},
            {'nome': 'Futebol', 'descricao': 'Aulas de futebol', 'ativo': True},
            {'nome': 'Natação', 'descricao': 'Aulas de natação', 'ativo': True}
        ]
        
        migradas = 0
        for atividade in atividades_basicas:
            try:
                # Verificar se já existe
                existente = self.atividade_dao.buscar_por_nome(atividade['nome'])
                if not existente:
                    self.atividade_dao.criar(atividade)
                    migradas += 1
                    print(f'  ✅ {atividade["nome"]}')
                else:
                    print(f'  ⚠️ {atividade["nome"]} (já existe)')
            except Exception as e:
                print(f'  ❌ Erro ao migrar {atividade["nome"]}: {e}')
        
        print(f'\n📊 {migradas} atividades migradas')
        return migradas
    
    def migrar_turmas_basicas(self):
        """Migra turmas básicas para o MongoDB"""
        print('\n🏫 Migrando turmas básicas...')
        
        turmas_basicas = [
            {'nome': '09:00', 'descricao': 'Turma da manhã - 09:00', 'ativo': True},
            {'nome': '14:00', 'descricao': 'Turma da tarde - 14:00', 'ativo': True},
            {'nome': '16:00', 'descricao': 'Turma da tarde - 16:00', 'ativo': True},
            {'nome': 'A definir', 'descricao': 'Turma a ser definida', 'ativo': True}
        ]
        
        migradas = 0
        for turma in turmas_basicas:
            try:
                # Verificar se já existe
                existente = self.turma_dao.buscar_por_nome(turma['nome'])
                if not existente:
                    self.turma_dao.criar(turma)
                    migradas += 1
                    print(f'  ✅ {turma["nome"]}')
                else:
                    print(f'  ⚠️ {turma["nome"]} (já existe)')
            except Exception as e:
                print(f'  ❌ Erro ao migrar {turma["nome"]}: {e}')
        
        print(f'\n📊 {migradas} turmas migradas')
        return migradas
    
    def migrar_alunos_do_json(self):
        """Migra alunos do arquivo dados_alunos.json"""
        print('\n👥 Migrando alunos do arquivo JSON...')
        
        arquivo_json = 'dados_alunos.json'
        if not os.path.exists(arquivo_json):
            print(f'❌ Arquivo {arquivo_json} não encontrado')
            return 0
        
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                alunos_data = json.load(f)
        except Exception as e:
            print(f'❌ Erro ao ler arquivo JSON: {e}')
            return 0
        
        print(f'📄 Encontrados {len(alunos_data)} alunos no arquivo')
        
        migrados = 0
        erros = 0
        
        for i, aluno_data in enumerate(alunos_data):
            try:
                # Verificar se aluno já existe (evitar duplicatas)
                aluno_existente = self.aluno_dao.buscar_por_nome_telefone(
                    aluno_data.get('nome', ''), 
                    aluno_data.get('telefone', '')
                )
                if aluno_existente:
                    print(f'  ⚠️ Aluno {aluno_data["nome"]} já existe')
                    continue
                
                # Preparar dados do aluno
                aluno_mongo = {
                    'nome': aluno_data.get('nome', ''),
                    'telefone': aluno_data.get('telefone', ''),
                    'endereco': aluno_data.get('endereco', ''),
                    'email': aluno_data.get('email', ''),
                    'data_nascimento': aluno_data.get('data_nascimento', ''),
                    'data_cadastro': aluno_data.get('data_cadastro', datetime.now().strftime('%d/%m/%Y')),
                    'atividade': aluno_data.get('atividade', ''),
                    'turma': aluno_data.get('turma', ''),
                    'observacoes': aluno_data.get('observacoes', ''),
                    'id_unico': aluno_data.get('id_unico', f'migrado_{i}'),
                    'ativo': True,
                    'migrado_em': datetime.now().isoformat()
                }
                
                # Criar aluno no MongoDB
                resultado = self.aluno_dao.criar(aluno_mongo)
                if resultado:
                    migrados += 1
                    if migrados % 50 == 0:
                        print(f'  📊 {migrados} alunos migrados...')
                else:
                    erros += 1
                    
            except Exception as e:
                erros += 1
                print(f'  ❌ Erro ao migrar aluno {i+1}: {e}')
        
        print(f'\n📊 Migração concluída:')
        print(f'  ✅ {migrados} alunos migrados com sucesso')
        print(f'  ❌ {erros} erros encontrados')
        
        # Registrar log da migração
        try:
            self.log_dao.criar({
                'acao': 'Migração de Dados',
                'detalhes': f'Migrados {migrados} alunos do localhost para MongoDB Atlas',
                'usuario': 'Sistema',
                'timestamp': datetime.now()
            })
        except:
            pass
        
        return migrados
    
    def executar_migracao_completa(self):
        """Executa a migração completa"""
        print('🚀 INICIANDO MIGRAÇÃO COMPLETA PARA MONGODB ATLAS')
        print('=' * 60)
        
        try:
            # Migrar atividades
            atividades_migradas = self.migrar_atividades_basicas()
            
            # Migrar turmas
            turmas_migradas = self.migrar_turmas_basicas()
            
            # Migrar alunos
            alunos_migrados = self.migrar_alunos_do_json()
            
            print('\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!')
            print('=' * 60)
            print(f'📊 RESUMO:')
            print(f'  • Atividades: {atividades_migradas}')
            print(f'  • Turmas: {turmas_migradas}')
            print(f'  • Alunos: {alunos_migrados}')
            print(f'\n💡 Os dados agora estão disponíveis no MongoDB Atlas')
            print(f'   e aparecerão no deploy do Render!')
            
            return True
            
        except Exception as e:
            print(f'\n❌ ERRO DURANTE A MIGRAÇÃO: {e}')
            return False

def main():
    """Função principal"""
    try:
        migrador = MigradorMongoDB()
        sucesso = migrador.executar_migracao_completa()
        
        if sucesso:
            print('\n✅ Migração realizada com sucesso!')
            print('🔄 Faça um novo deploy no Render para ver os dados')
        else:
            print('\n❌ Migração falhou')
            
    except Exception as e:
        print(f'❌ Erro fatal: {e}')
        print('\n💡 Verifique:')
        print('  - Conexão com internet')
        print('  - Credenciais do MongoDB Atlas')
        print('  - Se o cluster está ativo')

if __name__ == '__main__':
    main()
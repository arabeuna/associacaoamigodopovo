# Sistema de Banco de Dados PostgreSQL - Academia Amigo do Povo

Este documento descreve a implementação do sistema de banco de dados PostgreSQL para o projeto da Academia Amigo do Povo.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Instalação](#instalação)
3. [Configuração](#configuração)
4. [Estrutura do Banco](#estrutura-do-banco)
5. [Migração de Dados](#migração-de-dados)
6. [Uso](#uso)
7. [Manutenção](#manutenção)
8. [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O sistema foi migrado de arquivos JSON para um banco de dados PostgreSQL robusto, oferecendo:

- **Integridade de dados**: Relacionamentos e constraints
- **Performance**: Índices otimizados
- **Escalabilidade**: Suporte a grandes volumes de dados
- **Concorrência**: Múltiplos usuários simultâneos
- **Backup**: Sistema de backup nativo do PostgreSQL

## 🚀 Instalação

### Pré-requisitos

1. **PostgreSQL** instalado e rodando
2. **Python 3.8+**
3. **pip** para gerenciamento de dependências

### Passos de Instalação

1. **Instalar dependências Python:**
```bash
pip install -r requirements.txt
```

2. **Configurar PostgreSQL:**
```bash
# Criar usuário e banco (se necessário)
sudo -u postgres psql
CREATE USER academia_user WITH PASSWORD 'sua_senha';
CREATE DATABASE academia_amigo_povo OWNER academia_user;
GRANT ALL PRIVILEGES ON DATABASE academia_amigo_povo TO academia_user;
\q
```

3. **Configurar variáveis de ambiente:**
```bash
cp config.env.example .env
# Editar .env com suas configurações
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `config.env.example`:

```env
# Configurações do Banco de Dados PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=academia_user
DB_PASSWORD=sua_senha
DB_NAME=academia_amigo_povo

# URL completa do banco de dados
DATABASE_URL=postgresql://academia_user:sua_senha@localhost:5432/academia_amigo_povo

# Configurações do Flask
SECRET_KEY=sua_chave_secreta_aqui
FLASK_ENV=development
FLASK_DEBUG=True
```

### Inicialização Automática

Execute o script de inicialização:

```bash
python init_db.py
```

Este script irá:
- Verificar dependências
- Criar banco de dados e tabelas
- Migrar dados existentes
- Configurar usuários padrão

## 🗄️ Estrutura do Banco

### Tabelas Principais

#### 1. `usuarios`
- **Propósito**: Gerenciar usuários do sistema
- **Campos principais**: id, username, senha_hash, nome, nivel, permissoes
- **Níveis**: admin_master, admin, usuario

#### 2. `atividades`
- **Propósito**: Cadastro de atividades da academia
- **Campos principais**: id, nome, descricao, ativa, total_alunos
- **Relacionamentos**: turmas, alunos, presencas

#### 3. `turmas`
- **Propósito**: Gerenciar turmas das atividades
- **Campos principais**: id, nome, atividade_id, horario, dias_semana, capacidade_maxima
- **Relacionamentos**: atividade, professor, alunos, presencas

#### 4. `alunos`
- **Propósito**: Cadastro de alunos
- **Campos principais**: id, nome, telefone, email, atividade_id, turma_id
- **Relacionamentos**: atividade, turma, presencas

#### 5. `presencas`
- **Propósito**: Registro de frequência
- **Campos principais**: id, aluno_id, data_presenca, status, turma_id
- **Status**: P (Presente), F (Faltou), J (Justificado)

### Índices Criados

```sql
-- Índices para otimização de consultas
CREATE INDEX idx_alunos_atividade ON alunos(atividade_id);
CREATE INDEX idx_alunos_turma ON alunos(turma_id);
CREATE INDEX idx_presencas_aluno ON presencas(aluno_id);
CREATE INDEX idx_presencas_data ON presencas(data_presenca);
CREATE INDEX idx_turmas_atividade ON turmas(atividade_id);
```

## 📊 Migração de Dados

### Arquivos Migrados

1. **`dados_alunos.json`** → Tabela `alunos`
2. **`atividades_sistema.json`** → Tabela `atividades`
3. **`turmas_sistema.json`** → Tabela `turmas`
4. **`presencas_detalhadas.csv`** → Tabela `presencas`

### Executar Migração Manual

```bash
# Migração completa
python migrar_dados.py

# Ou migração por partes
python -c "
from migrar_dados import *
migrar_usuarios()
migrar_atividades()
migrar_turmas()
migrar_alunos()
migrar_presencas()
atualizar_contadores()
"
```

## 💻 Uso

### Conexão com o Banco

```python
from models import SessionLocal, Aluno, Atividade

# Obter sessão do banco
db = SessionLocal()
try:
    # Consultar alunos
    alunos = db.query(Aluno).filter(Aluno.ativo == True).all()
    
    # Consultar atividades
    atividades = db.query(Atividade).filter(Atividade.ativa == True).all()
finally:
    db.close()
```

### Operações Comuns

```python
from models import AlunoDAO, PresencaDAO, AtividadeDAO

# Buscar aluno por nome
alunos = AlunoDAO.buscar_por_nome(db, "João")

# Calcular frequência
frequencia = AlunoDAO.calcular_frequencia(db, aluno_id)

# Registrar presença
PresencaDAO.registrar_presenca(db, aluno_id, data, 'P')

# Listar atividades ativas
atividades = AtividadeDAO.listar_ativas(db)
```

## 🔧 Manutenção

### Backup do Banco

```bash
# Backup completo
pg_dump -h localhost -U academia_user -d academia_amigo_povo > backup_$(date +%Y%m%d).sql

# Backup apenas dados
pg_dump -h localhost -U academia_user -d academia_amigo_povo --data-only > dados_$(date +%Y%m%d).sql

# Restaurar backup
psql -h localhost -U academia_user -d academia_amigo_povo < backup_20241201.sql
```

### Limpeza de Dados

```sql
-- Remover presenças antigas (mais de 2 anos)
DELETE FROM presencas WHERE data_presenca < CURRENT_DATE - INTERVAL '2 years';

-- Desativar alunos inativos
UPDATE alunos SET ativo = false WHERE data_cadastro < CURRENT_DATE - INTERVAL '1 year';

-- Atualizar contadores
SELECT atualizar_contadores();
```

### Monitoramento

```sql
-- Verificar tamanho das tabelas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Verificar performance de consultas
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
```

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão
```
Error: could not connect to server
```
**Solução:**
- Verificar se PostgreSQL está rodando: `sudo systemctl status postgresql`
- Verificar credenciais no arquivo `.env`
- Testar conexão: `psql -h localhost -U academia_user -d academia_amigo_povo`

#### 2. Erro de Permissão
```
Error: permission denied for table
```
**Solução:**
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO academia_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO academia_user;
```

#### 3. Erro de Dependência
```
ImportError: No module named 'psycopg2'
```
**Solução:**
```bash
pip install psycopg2-binary
# ou
pip install -r requirements.txt
```

#### 4. Dados Duplicados na Migração
**Solução:**
```sql
-- Limpar dados duplicados
DELETE FROM presencas WHERE id NOT IN (
    SELECT MIN(id) FROM presencas 
    GROUP BY aluno_id, data_presenca
);

DELETE FROM alunos WHERE id NOT IN (
    SELECT MIN(id) FROM alunos 
    GROUP BY nome
);
```

### Logs e Debug

```python
# Habilitar logs do SQLAlchemy
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Verificar conexão
from models import verificar_conexao
if verificar_conexao():
    print("Conexão OK")
else:
    print("Erro na conexão")
```

## 📈 Performance

### Otimizações Implementadas

1. **Índices estratégicos** em campos de busca frequente
2. **Relacionamentos otimizados** com foreign keys
3. **Queries eficientes** usando SQLAlchemy ORM
4. **Paginação** para grandes volumes de dados

### Monitoramento de Performance

```sql
-- Verificar queries lentas
SELECT query, mean_time, calls
FROM pg_stat_statements 
WHERE mean_time > 100
ORDER BY mean_time DESC;

-- Verificar uso de índices
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## 🔒 Segurança

### Boas Práticas

1. **Usar variáveis de ambiente** para credenciais
2. **Limitar permissões** do usuário do banco
3. **Fazer backups regulares**
4. **Monitorar logs** de acesso
5. **Usar SSL** em produção

### Configuração de Segurança

```sql
-- Criar usuário com permissões limitadas
CREATE USER academia_app WITH PASSWORD 'senha_forte';
GRANT CONNECT ON DATABASE academia_amigo_povo TO academia_app;
GRANT USAGE ON SCHEMA public TO academia_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO academia_app;
```

## 📞 Suporte

Para dúvidas ou problemas:

1. Verificar logs do sistema
2. Consultar este documento
3. Verificar configurações do PostgreSQL
4. Testar conexão manualmente
5. Verificar permissões de usuário

---

**Versão**: 1.0  
**Data**: Dezembro 2024  
**Autor**: Sistema Academia Amigo do Povo

# Sincronização de Banco de Dados - Academia Amigo do Povo

## Visão Geral

Este documento descreve o processo completo de sincronização de dados entre o ambiente de desenvolvimento (localhost) e produção (Render) para o sistema da Academia Amigo do Povo.

## Arquitetura do Sistema

### Ambiente de Desenvolvimento (Localhost)
- **Banco**: PostgreSQL local ou SQLite (fallback)
- **Dados**: Arquivo JSON (`dados_alunos.json`) como backup
- **Configuração**: Arquivo `.env` com variáveis locais

### Ambiente de Produção (Render)
- **Banco**: PostgreSQL gerenciado pelo Render
- **Configuração**: Variáveis de ambiente definidas no painel do Render
- **Deploy**: Automático via Git push

## Processo de Migração Automática

### 1. Deploy Automático
Quando você faz push para o repositório Git:

```bash
git add .
git commit -m "Atualização do sistema"
git push origin main
```

O Render automaticamente:
1. Executa o build conforme `render.yaml`
2. Roda o comando de migração: `python migrate_production.py`
3. Inicia a aplicação

### 2. Script de Migração (`migrate_production.py`)

O script executa as seguintes etapas:

#### Verificação e Criação de Estrutura
- ✅ Testa conexão com banco de dados
- ✅ Cria tabelas se não existirem
- ✅ Adiciona colunas faltantes automaticamente

#### Migração de Dados Essenciais
- ✅ **Usuários**: Cria admin_master e admin se não existirem
- ✅ **Atividades**: Migra atividades básicas (Vôlei, Futebol, etc.)
- ✅ **Alunos**: Migra dados do arquivo JSON local (se existir)

## Migração Manual

### Opção 1: Endpoint Web
Acesse diretamente no navegador:
```
https://seu-app.onrender.com/migrate
```

Retorna JSON com status da migração:
```json
{
  "status": "success",
  "message": "Migração executada com sucesso!",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Opção 2: Script Local
Execute localmente (conectando ao banco de produção):
```bash
python migrate_production.py
```

## Sincronização de Dados Específicos

### Alunos
1. **Exportar do localhost**:
   - Os dados ficam salvos em `dados_alunos.json`
   - Backup automático a cada operação

2. **Importar para produção**:
   - Upload do arquivo JSON
   - Execução da migração
   - Verificação de duplicatas por ID único

### Atividades e Turmas
- Migração automática das atividades padrão
- Criação manual de novas atividades via interface
- Sincronização via backup/restore de planilhas

## Comandos Úteis

### Verificar Status do Banco
```bash
# Testar conexão
python testar_postgresql.py

# Debug direto no banco
python test_debug_direto.py
```

### Backup e Restore
```bash
# Gerar backup de alunos
curl http://localhost:5000/baixar_cadastros

# Gerar todas as planilhas
curl http://localhost:5000/gerar_todas_planilhas
```

## Resolução de Problemas

### Erro: "Coluna não existe"
**Causa**: Estrutura do banco desatualizada
**Solução**: Execute a migração que adiciona colunas automaticamente

### Erro: "Usuário já existe"
**Causa**: Tentativa de criar usuários duplicados
**Solução**: A migração verifica existência antes de criar

### Erro: "Conexão recusada"
**Causa**: Problemas de conectividade com banco
**Solução**: 
1. Verifique variáveis de ambiente
2. Confirme status do banco no Render
3. Teste conexão local primeiro

## Variáveis de Ambiente Necessárias

### Produção (Render)
```
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=sua_chave_secreta
FLASK_ENV=production
```

### Desenvolvimento (.env)
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_NAME=academia_amigo_povo
SECRET_KEY=chave_desenvolvimento
```

## Monitoramento

### Health Check
```bash
curl https://seu-app.onrender.com/health
```

### Logs de Migração
- Logs detalhados durante execução
- Status de cada etapa (✅ sucesso, ⚠️ aviso, ❌ erro)
- Contadores de registros migrados

## Boas Práticas

1. **Sempre teste localmente** antes de fazer deploy
2. **Mantenha backups** dos dados importantes
3. **Monitore logs** durante migrações
4. **Use o endpoint /migrate** para migrações manuais em produção
5. **Verifique health check** após deploy

## Fluxo Recomendado

### Para Novos Deploys
1. Teste todas as funcionalidades localmente
2. Commit e push das alterações
3. Aguarde deploy automático no Render
4. Verifique health check
5. Teste funcionalidades críticas em produção

### Para Sincronização de Dados
1. Exporte dados do ambiente local
2. Faça backup dos dados atuais
3. Execute migração via endpoint /migrate
4. Verifique integridade dos dados
5. Teste funcionalidades principais

---

**Última atualização**: Janeiro 2024
**Versão do sistema**: 2.0
**Responsável**: Sistema de Migração Automática
# 🚀 CONFIGURAÇÃO DE PRODUÇÃO NO RENDER

## 📋 Status Atual

✅ **Deploy realizado com sucesso**
❌ **Serviço inativo** - Necessário configurar variáveis de ambiente

## 🔧 PASSOS OBRIGATÓRIOS PARA ATIVAR O SERVIÇO

### 1. Acessar o Painel do Render

1. Acesse: https://render.com/
2. Faça login na sua conta
3. Vá para o dashboard
4. Localize o serviço: **associacao-amigo-do-povo**

### 2. Configurar o Banco PostgreSQL

1. No dashboard, clique em **associacao-amigo-do-povo-db** (PostgreSQL)
2. Na aba **Info**, copie as seguintes informações:
   - **Hostname** (exemplo: dpg-xxxxxxxxx-a.oregon-postgres.render.com)
   - **Port** (geralmente: 5432)
   - **Database** (exemplo: associacao_amigo_do_povo_xxxx)
   - **Username** (exemplo: associacao_amigo_do_povo_user)
   - **Password** (senha gerada automaticamente)
   - **External Database URL** (URL completa)

### 3. Configurar Variáveis de Ambiente no Serviço Web

1. Clique no serviço web: **associacao-amigo-do-povo**
2. Vá para a aba **Environment**
3. Clique em **Add Environment Variable**
4. Adicione as seguintes variáveis:

```bash
# Configurações do PostgreSQL (usar valores do passo 2)
DB_HOST=dpg-xxxxxxxxx-a.oregon-postgres.render.com
DB_PORT=5432
DB_USER=associacao_amigo_do_povo_user
DB_PASSWORD=[senha_do_banco]
DB_NAME=associacao_amigo_do_povo_xxxx

# URL completa (usar valor do passo 2)
DATABASE_URL=postgresql://user:password@host:5432/database

# Configurações da aplicação
SECRET_KEY=associacao_amigo_do_povo_2024_secure_key_production
FLASK_ENV=production
FLASK_DEBUG=False

# Configurações de upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### 4. Salvar e Aguardar Deploy

1. Clique em **Save Changes**
2. O Render fará redeploy automático
3. Aguarde 3-5 minutos
4. Verifique os logs na aba **Logs**

### 5. Verificar se o Serviço Está Ativo

Após o deploy, teste:

```bash
curl -I https://associacao-amigo-do-povo.onrender.com/health
```

**Resposta esperada:**
```
HTTP/1.1 200 OK
```

## 🔍 Troubleshooting

### Se o serviço ainda estiver inativo:

1. **Verificar logs:**
   - Aba **Logs** no painel do Render
   - Procurar por erros de conexão ou dependências

2. **Verificar build:**
   - Aba **Events** para ver se o build foi bem-sucedido

3. **Testar conexão do banco:**
   - Usar as credenciais em um cliente PostgreSQL

### Logs esperados após configuração correta:

```
✅ Conexão com banco de dados estabelecida
Carregando variáveis de ambiente de produção (.env.production)
Tabelas do banco de dados criadas/verificadas com sucesso!
📦 Carregados XXX alunos do banco PostgreSQL
🎯 Atividades carregadas do banco: XX atividades
📅 Turmas carregadas do banco PostgreSQL: X turmas
✅ Sistema Academia inicializado com sucesso
```

## 📞 Próximos Passos

Após ativar o serviço:

1. ✅ Testar login: `/`
2. ✅ Testar cadastro de alunos: `/novo_aluno`
3. ✅ Testar upload de planilhas: `/backup_planilhas`
4. ✅ Testar relatórios: `/relatorios`

---

**⚠️ IMPORTANTE:** Sem as variáveis de ambiente configuradas, o serviço não consegue conectar ao banco PostgreSQL e permanece inativo.
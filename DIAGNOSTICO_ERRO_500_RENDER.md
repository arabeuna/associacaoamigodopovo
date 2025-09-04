# 🚨 DIAGNÓSTICO ERRO 500 NO RENDER

## 📊 Status Atual
❌ **Erro 500 no endpoint `/processar_planilha`** <mcreference link="https://render.com/docs/troubleshooting-deploys" index="1">1</mcreference>
✅ **PWA funcionando** (mas banner não aparece)
✅ **Service Worker registrado**

## 🔍 PASSOS PARA DIAGNÓSTICO

### 1. **Verificar Logs do Render** <mcreference link="https://render.com/docs/troubleshooting-deploys" index="1">1</mcreference>

1. Acesse: https://render.com/
2. Vá para o dashboard do serviço **associacao-amigo-do-povo**
3. Clique na aba **Logs**
4. Procure por:
   - `error` (palavra-chave)
   - `ModuleNotFoundError`
   - `pandas`
   - `500`
   - `/processar_planilha`

### 2. **Verificar Instalação do Pandas** <mcreference link="https://community.render.com/t/deployment-failure-of-app/12406" index="3">3</mcreference>

Erros comuns relacionados ao pandas:
```
ERROR: No matching distribution found for pandas==1.5.3
ModuleNotFoundError: No module named 'pandas'
```

**Soluções:**
- Verificar se `pandas==1.5.3` está no `requirements.txt`
- Confirmar se o build command está correto: `pip install -r requirements.txt`
- Verificar compatibilidade da versão do Python

### 3. **Verificar Variáveis de Ambiente**

Confirmar se estão configuradas:
```bash
DB_HOST=...
DB_PORT=5432
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
DATABASE_URL=...
SECRET_KEY=...
FLASK_ENV=production
FLASK_DEBUG=False
```

### 4. **Verificar Build e Start Commands** <mcreference link="https://render.com/docs/troubleshooting-deploys" index="1">1</mcreference>

**Build Command esperado:**
```bash
pip install -r requirements.txt
```

**Start Command esperado:**
```bash
gunicorn app:app
```

## 🛠️ POSSÍVEIS CAUSAS DO ERRO 500

### 1. **Pandas não instalado** <mcreference link="https://community.render.com/t/deployment-failure-of-app/12406" index="3">3</mcreference>
- Versão incompatível com Python do Render
- Falha na instalação durante o build
- Dependências do pandas não satisfeitas

### 2. **Erro de importação no app.py**
```python
# Linha que pode estar causando erro:
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
```

### 3. **Problema de conexão com banco**
- Variáveis de ambiente incorretas
- Banco PostgreSQL inativo
- Credenciais inválidas

### 4. **Erro de encoding/charset**
- Problemas com arquivos CSV/Excel
- Encoding não suportado no Linux

## 🔧 SOLUÇÕES RECOMENDADAS

### **Solução 1: Atualizar requirements.txt**
```txt
Flask==2.3.3
gunicorn==21.2.0
Werkzeug==2.3.7
psycopg2-binary==2.9.7
SQLAlchemy==2.0.21
numpy==1.24.3
pandas==1.5.3
openpyxl==3.1.2
python-dotenv==1.0.0
```

### **Solução 2: Forçar Redeploy**
1. No dashboard do Render
2. Aba **Settings**
3. Clicar em **Manual Deploy**
4. Selecionar **Deploy latest commit**

### **Solução 3: Verificar Python Version**
Adicionar arquivo `.python-version`:
```
3.9.18
```

### **Solução 4: Debug Mode Temporário**
Para diagnóstico, temporariamente:
```bash
FLASK_DEBUG=True
```
⚠️ **IMPORTANTE:** Voltar para `False` após diagnóstico!

## 🧪 TESTE APÓS CORREÇÃO

### 1. **Verificar se app inicia**
- Logs devem mostrar: "Sistema Academia inicializado com sucesso"
- Sem erros de ModuleNotFoundError

### 2. **Testar endpoint específico**
```bash
curl -X POST https://associacaoamigodopovo.onrender.com/processar_planilha
```
Esperado: Erro 405 (Method Not Allowed) em vez de 500

### 3. **Testar upload de arquivo**
- Acessar página de backup/planilhas
- Tentar upload de arquivo CSV pequeno
- Verificar se não há erro 500

## 📋 CHECKLIST DE VERIFICAÇÃO

- [ ] Logs verificados no dashboard Render
- [ ] `pandas==1.5.3` confirmado no requirements.txt
- [ ] Variáveis de ambiente configuradas
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `gunicorn app:app`
- [ ] Python version compatível (3.9+)
- [ ] Banco PostgreSQL ativo
- [ ] Redeploy manual executado
- [ ] Teste de endpoint realizado

## 🆘 SE O PROBLEMA PERSISTIR

1. **Contatar Suporte Render:**
   - Dashboard > Contact Support
   - Incluir logs específicos do erro

2. **Implementar Fallback:**
   - Desabilitar temporariamente processamento Excel
   - Manter apenas CSV básico

3. **Rollback:**
   - Voltar para versão anterior que funcionava
   - Implementar correções gradualmente

---

**Próximo passo:** Verificar logs do Render para identificar a causa exata do erro 500.
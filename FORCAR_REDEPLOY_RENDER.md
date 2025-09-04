# 🔄 FORÇAR REDEPLOY NO RENDER

## 🚨 PROBLEMA IDENTIFICADO
❌ **Alterações não aplicadas em produção**
- Correções do PWA não refletidas
- Arquivo `pwa.js` não atualizado no servidor
- Cache do navegador pode estar interferindo

## 🛠️ SOLUÇÕES PARA FORÇAR ATUALIZAÇÃO

### **Método 1: Manual Deploy (RECOMENDADO)**

1. **Acessar Dashboard Render:**
   - URL: https://render.com/
   - Login na conta
   - Localizar serviço: **associacao-amigo-do-povo**

2. **Forçar Deploy Manual:**
   - Clicar no serviço web
   - Ir para aba **Settings**
   - Rolar até "Manual Deploy"
   - Clicar em **Deploy latest commit**
   - Aguardar processo (2-5 minutos)

3. **Verificar Logs:**
   - Ir para aba **Logs**
   - Procurar por:
     ```
     Build successful
     Deploy live
     ```

### **Método 2: Trigger Deploy via Git**

1. **Fazer pequena alteração:**
   ```bash
   # Adicionar linha vazia em qualquer arquivo
   echo "" >> deploy_trigger.txt
   ```

2. **Commit e Push:**
   ```bash
   git add .
   git commit -m "Force redeploy - PWA corrections"
   git push origin main
   ```

3. **Aguardar Auto-Deploy:**
   - Render detectará mudança automaticamente
   - Deploy iniciará em 1-2 minutos

### **Método 3: Limpar Cache do Render**

1. **No Dashboard:**
   - Aba **Settings**
   - Seção "Danger Zone"
   - **Clear build cache** (se disponível)

2. **Redeploy após limpar cache:**
   - Manual Deploy novamente

## 🔍 VERIFICAR SE ATUALIZOU

### **1. Verificar Timestamp dos Arquivos**
```bash
# Acessar no navegador:
https://associacaoamigodopovo.onrender.com/static/js/pwa.js

# Procurar por:
"PWA: Botão personalizado não encontrado - permitindo banner nativo"
```

### **2. Verificar Console do Navegador**
```javascript
// Deve aparecer:
"PWA: Botão personalizado encontrado - usando controle manual"
// OU
"PWA: Botão personalizado não encontrado - permitindo banner nativo"
```

### **3. Forçar Refresh no Navegador**
```bash
# Windows/Linux:
Ctrl + F5

# Mac:
Cmd + Shift + R

# Ou abrir DevTools e:
# Right-click no refresh → "Empty Cache and Hard Reload"
```

## 🧪 TESTAR APÓS REDEPLOY

### **Teste 1: PWA Banner**
1. Abrir site em navegador compatível (Chrome/Edge)
2. Aguardar alguns segundos
3. Verificar se banner de instalação aparece
4. Ou verificar se botão personalizado funciona

### **Teste 2: Endpoint /processar_planilha**
```bash
# Testar com curl ou Postman:
curl -X POST https://associacaoamigodopovo.onrender.com/processar_planilha

# Esperado: 405 Method Not Allowed (não 500)
```

### **Teste 3: Console Limpo**
1. Abrir DevTools (F12)
2. Ir para aba Console
3. Recarregar página
4. Verificar se não há erros 500

## 📋 CHECKLIST DE VERIFICAÇÃO

- [ ] **Deploy manual executado no Render**
- [ ] **Logs mostram "Deploy live"**
- [ ] **Arquivo pwa.js atualizado** (verificar URL direta)
- [ ] **Cache do navegador limpo** (Ctrl+F5)
- [ ] **Console sem erros 500**
- [ ] **PWA banner funcionando**
- [ ] **Endpoint retorna 405 (não 500)**

## ⚠️ SE AINDA NÃO FUNCIONAR

### **Verificar Problemas Comuns:**

1. **Git não sincronizado:**
   ```bash
   git status
   git push origin main
   ```

2. **Branch incorreta:**
   - Verificar se Render está monitorando branch correta
   - Settings → Build & Deploy → Branch

3. **Build falhou:**
   - Verificar logs de build
   - Procurar por erros de sintaxe

4. **Cache persistente:**
   - Testar em aba anônima/incógnita
   - Testar em navegador diferente

### **Última Opção: Recriar Serviço**

Se nada funcionar:
1. Criar novo serviço no Render
2. Conectar ao mesmo repositório
3. Configurar variáveis de ambiente
4. Testar deploy limpo

---

## 🎯 RESULTADO ESPERADO

✅ **PWA:** Banner nativo aparece ou botão personalizado funciona  
✅ **Console:** Sem erros 500 no /processar_planilha  
✅ **Logs:** "PWA: Botão personalizado não encontrado - permitindo banner nativo"  
✅ **Funcionalidade:** Upload de planilhas sem erro interno  

**Tempo estimado:** 5-10 minutos para deploy + teste
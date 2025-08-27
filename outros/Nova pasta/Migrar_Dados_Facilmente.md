# 📋 GUIA RÁPIDO: COMO MIGRAR SEUS DADOS EXISTENTES

## 🎯 **OBJETIVO**
Transferir todos os dados das suas planilhas Excel atuais para o novo sistema Google Sheets sem perder nenhuma informação.

---

## 📊 **PASSO 1: PREPARAR DADOS DE CADASTROS**

### 1.1 Abrir Planilha Atual
1. Abra o arquivo `Cadastros_Unificados_GOOGLE_v2.xlsx`
2. Identifique qual aba contém os dados principais dos alunos
3. Anote quais colunas têm as seguintes informações:
   - Nome completo
   - CPF  
   - RG
   - Telefone
   - Data de nascimento
   - E-mail
   - Endereço
   - Situação de pagamento
   - Valor da mensalidade

### 1.2 Mapeamento de Colunas
**Crie uma tabela como esta para organizar:**

| Dado na Planilha Atual | Coluna Antiga | Nova Coluna no Sistema | Posição Nova |
|------------------------|---------------|------------------------|--------------|
| Nome do aluno          | A             | Nome Completo          | B            |
| Telefone               | C             | Telefone               | E            |
| CPF                    | B             | CPF                    | C            |
| *(continue...)*        |               |                        |              |

### 1.3 Transferência dos Dados
1. **Selecione todos os dados** da planilha atual (Ctrl+A)
2. **Copie** (Ctrl+C)
3. Abra a nova planilha **👥 Academia Amigo do Povo - CADASTROS**
4. **Cole na linha 2** (deixe linha 1 para cabeçalhos)
5. **Reorganize as colunas** conforme o mapeamento

### 1.4 Preencher Dados Obrigatórios
Para alunos que não têm algumas informações, preencha:
- **Status**: "Ativo" (se ainda frequenta) ou "Inativo"
- **Situação Pagamento**: "Pago", "Pendente" ou "Vencido"
- **Valor Mensalidade**: Valor atual do plano
- **Data Vencimento**: Próxima data de pagamento
- **Plano**: "Mensal" ou "Premium"
- **Data Cadastro**: Se não souber, coloque data aproximada

---

## ✅ **PASSO 2: MIGRAR DADOS DE PRESENÇA**

### 2.1 Abrir Ficha de Presença Atual
1. Abra `FICHA_DE_PRESENCA_REMODELADA_CONSOLIDADA.xlsx`
2. Identifique como estão organizados os dados de presença

### 2.2 Formatos Possíveis de Presença

**Se sua planilha atual tem formato de CALENDÁRIO:**
```
Nome          | 01/01 | 02/01 | 03/01 | 04/01 |
João Silva    |   X   |       |   X   |   X   |
Maria Santos  |   X   |   X   |       |   X   |
```

**Converter para formato de LISTA:**
```
Nome          | Data      | Horário | Check-in Por |
João Silva    | 01/01/25  | 08:30   | Recepção     |
João Silva    | 03/01/25  | 08:45   | Recepção     |
João Silva    | 04/01/25  | 08:30   | Recepção     |
Maria Santos  | 01/01/25  | 09:15   | Recepção     |
```

### 2.3 Processo de Conversão

**Método Manual (Rápido para poucos dados):**
1. Para cada "X" na planilha atual
2. Criar uma linha na nova planilha com:
   - Nome do aluno
   - Data da presença  
   - Horário aproximado (se não souber, coloque 08:00)
   - "Recepção" na coluna Check-in Por

**Método Semi-Automático:**
1. Copie a lista de nomes da planilha atual
2. Para cada data que tem presenças:
   - Cole os nomes que estiveram presentes
   - Preencha a data ao lado
   - Arraste para baixo para repetir a data

### 2.4 Dados Mínimos Necessários
Se não tiver todos os dados, o mínimo necessário é:
- **Nome do aluno** (deve ser idêntico ao cadastro)
- **Data da presença** (formato DD/MM/AAAA)
- **Horário**: Pode usar sempre "08:00" se não souber
- **Check-in Por**: Sempre "Recepção"

---

## 🔧 **PASSO 3: VALIDAR E LIMPAR DADOS**

### 3.1 Verificar Nomes Duplicados
1. Na planilha de cadastros, ordene por nome (Dados → Classificar)
2. Procure nomes muito similares:
   - "João Silva" e "João Silva Santos"
   - "Maria" e "Maria Oliveira"
3. **Escolha um nome padrão** para cada pessoa
4. **Delete as linhas duplicadas**

### 3.2 Padronizar Nomes entre Planilhas
1. Os nomes na planilha de PRESENÇA devem ser **IDÊNTICOS** aos da planilha de CADASTROS
2. Use a função "Localizar e Substituir" (Ctrl+H) para corrigir:
   - "João" → "João Silva Santos"
   - "Maria" → "Maria Oliveira Costa"

### 3.3 Verificar Dados Obrigatórios
**Na planilha de CADASTROS, certifique-se que todos têm:**
- ✅ Nome preenchido
- ✅ Status (Ativo/Inativo)
- ✅ Situação Pagamento
- ✅ Valor Mensalidade

**Na planilha de PRESENÇA:**
- ✅ Nome idêntico ao cadastro
- ✅ Data válida
- ✅ Sem células vazias nas colunas principais

---

## 📱 **PASSO 4: TESTAR O SISTEMA**

### 4.1 Verificar Dashboard
1. Abra a planilha **DASHBOARD**
2. Verifique se os números fazem sentido:
   - Total de alunos
   - Alunos ativos
   - Receita mensal
   - Presenças recentes

### 4.2 Teste de Funcionalidades
1. **Adicione um novo aluno** na planilha de cadastros
2. **Registre uma presença** na planilha de presença  
3. **Verifique se aparece no dashboard**

### 4.3 Resolver Problemas Comuns

**Dashboard mostra #REF! ou #N/A:**
- Verificar se os nomes das abas estão corretos
- Reconfigurar fórmulas IMPORTRANGE

**Números não batem:**
- Verificar se não há linhas vazias entre os dados
- Confirmar que status estão escritos exatamente como "Ativo"

**Presenças não aparecem:**
- Verificar se nomes são idênticos entre planilhas
- Confirmar formato de data (DD/MM/AAAA)

---

## 🎯 **PASSO 5: BACKUP DOS DADOS MIGRADOS**

### 5.1 Backup das Planilhas Originais
1. **IMPORTANTE:** Não delete as planilhas Excel originais
2. Renomeie-as para "BACKUP_[nome_original]"
3. Mantenha em local seguro

### 5.2 Backup do Novo Sistema
1. Baixe as 3 planilhas Google Sheets em formato Excel
2. Salve com nomes claros:
   - "Academia_Cadastros_BACKUP_[data]"
   - "Academia_Presenca_BACKUP_[data]"
   - "Academia_Dashboard_BACKUP_[data]"

---

## ⚠️ **DICAS IMPORTANTES**

### ✅ **DO's (Faça)**
- ✅ **Teste com poucos dados primeiro** antes de migrar tudo
- ✅ **Mantenha nomes padronizados** entre todas as planilhas
- ✅ **Faça backup** antes de qualquer alteração grande
- ✅ **Valide os dados** após cada etapa
- ✅ **Peça ajuda** se alguma fórmula não funcionar

### ❌ **DON'Ts (Não faça)**
- ❌ **Não delete** as planilhas originais
- ❌ **Não misture formatos** de data (use sempre DD/MM/AAAA)
- ❌ **Não deixe células vazias** em colunas obrigatórias
- ❌ **Não mude nomes** das abas do sistema
- ❌ **Não copie fórmulas** por acidente (só valores)

---

## 🆘 **PRECISA DE AJUDA?**

### Problemas com Migração de Dados:
1. **Tire print** da sua planilha atual
2. **Descreva** qual dificuldade está enfrentando
3. **Teste** com apenas 3-5 linhas primeiro

### Problemas com Fórmulas:
1. **Verifique** se os IDs das planilhas estão corretos
2. **Reautorize** as conexões IMPORTRANGE
3. **Confirme** nomes das abas (Cadastros, Presencas, Dashboard)

### Não consegue abrir Excel:
1. **Use o Google Sheets** para abrir os arquivos .xlsx
2. **Importe diretamente** via Arquivo → Importar
3. **Copie e cole** os dados manualmente

---

## 🎉 **PRONTO!**

Seguindo este guia, você terá migrado com sucesso todos os seus dados para o novo sistema!

**Resultado esperado:**
- ✅ **Todos os alunos** no sistema novo
- ✅ **Histórico de presenças** preservado  
- ✅ **Dashboard funcionando** com dados reais
- ✅ **Sistema pronto** para uso diário

**Agora é só começar a usar as automações e aproveitar todas as funcionalidades do sistema turbinado!** 🚀

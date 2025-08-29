# Sistema de Logs de Atividades - Associação Amigo do Povo

## 📋 Visão Geral

O sistema de logs de atividades permite que o **Admin Master** acompanhe todas as ações realizadas pelos administradores e usuários do sistema. Este sistema registra automaticamente todas as atividades importantes, fornecendo transparência e controle total sobre o uso da plataforma.

## 🎯 Funcionalidades

### ✅ **Atividades Monitoradas**

#### **Login/Logout**
- ✅ Login no sistema
- ✅ Logout do sistema

#### **Gestão de Alunos**
- ✅ Cadastro de novos alunos
- ✅ Alteração de dados de alunos
- ✅ Exclusão de alunos

#### **Gestão de Presenças**
- ✅ Marcação de presenças
- ✅ Registro de faltas
- ✅ Edição de presenças

#### **Gestão de Atividades**
- ✅ Criação de novas atividades
- ✅ Edição de atividades
- ✅ Exclusão de atividades
- ✅ Vinculação de professores

#### **Gestão de Turmas**
- ✅ Criação de turmas
- ✅ Edição de turmas
- ✅ Exclusão de turmas

#### **Gestão de Colaboradores**
- ✅ Criação de contas de usuário
- ✅ Edição de permissões
- ✅ Exclusão de usuários

## 🔍 Filtros Disponíveis

### **Por Período**
- **Todos**: Exibe todas as atividades registradas
- **Hoje**: Apenas atividades do dia atual
- **Última Semana**: Atividades dos últimos 7 dias
- **Último Mês**: Atividades dos últimos 30 dias

### **Por Tipo de Usuário**
- **Admin Master**: Administrador principal (vermelho)
- **Admin**: Administrador (amarelo)
- **Usuário**: Professor/Colaborador (azul)

## 📊 Estatísticas Disponíveis

### **Dashboard de Logs**
- **Total de Atividades**: Número total de ações registradas
- **Usuários Ativos**: Quantidade de usuários que realizaram ações
- **Ações Mais Frequentes**: Gráfico de barras com as ações mais comuns

### **Informações Detalhadas**
- **Data e Hora**: Timestamp exato de cada ação
- **Usuário**: Quem realizou a ação
- **Tipo de Usuário**: Nível de acesso do usuário
- **Ação**: Tipo de atividade realizada
- **Detalhes**: Descrição específica da ação

## 🛠️ Implementação Técnica

### **Arquivo de Logs**
- **Localização**: `logs_atividades.json`
- **Formato**: JSON estruturado
- **Limite**: Máximo 1000 registros (mais recentes mantidos)

### **Estrutura do Log**
```json
{
  "timestamp": "2025-08-28T22:30:00",
  "data_hora": "28/08/2025 às 22:30:00",
  "usuario": "admin_master",
  "tipo_usuario": "admin_master",
  "acao": "Fez Login",
  "detalhes": "Usuário Admin Master fez login no sistema"
}
```

### **Funções Principais**

#### **`registrar_atividade(usuario, acao, detalhes, tipo_usuario)`**
- Registra uma nova atividade no sistema
- Parâmetros:
  - `usuario`: Login do usuário
  - `acao`: Tipo de ação realizada
  - `detalhes`: Descrição detalhada
  - `tipo_usuario`: Nível de acesso (admin_master/admin/usuario)

#### **`carregar_logs(filtro_periodo)`**
- Carrega logs com filtro por período
- Parâmetros:
  - `filtro_periodo`: "todos", "hoje", "semana", "mes"

## 🎨 Interface do Usuário

### **Página de Logs**
- **Acesso**: Apenas para Admin Master
- **URL**: `/logs_atividades`
- **Menu**: "Logs de Atividades" no menu principal

### **Elementos Visuais**
- **Filtros**: Botões para selecionar período
- **Estatísticas**: Cards com números importantes
- **Tabela**: Lista detalhada de todas as atividades
- **Cores**: Diferenciação por tipo de usuário

## 🔒 Segurança

### **Controle de Acesso**
- ✅ Apenas Admin Master pode visualizar logs
- ✅ Tentativas de acesso não autorizado são bloqueadas
- ✅ Mensagem de erro para usuários sem permissão

### **Proteção de Dados**
- ✅ Logs são armazenados localmente
- ✅ Limite de 1000 registros para evitar sobrecarga
- ✅ Backup automático dos logs

## 📱 Exemplos de Uso

### **Cenário 1: Monitoramento Diário**
1. Admin Master acessa `/logs_atividades`
2. Seleciona filtro "Hoje"
3. Visualiza todas as atividades do dia
4. Identifica padrões de uso

### **Cenário 2: Investigação de Problemas**
1. Admin Master acessa logs
2. Filtra por usuário específico
3. Analisa sequência de ações
4. Identifica causa do problema

### **Cenário 3: Relatório Semanal**
1. Admin Master acessa logs
2. Seleciona filtro "Última Semana"
3. Analisa estatísticas
4. Gera relatório de atividades

## 🚀 Benefícios

### **Para o Admin Master**
- ✅ **Transparência Total**: Visão completa de todas as ações
- ✅ **Controle de Qualidade**: Monitoramento de atividades
- ✅ **Segurança**: Detecção de atividades suspeitas
- ✅ **Relatórios**: Dados para tomada de decisões

### **Para a Instituição**
- ✅ **Auditoria**: Rastreamento completo de ações
- ✅ **Compliance**: Registro de todas as operações
- ✅ **Melhoria**: Identificação de pontos de melhoria
- ✅ **Confiança**: Sistema transparente e confiável

## 🔧 Manutenção

### **Limpeza de Logs**
- Sistema mantém automaticamente apenas os 1000 logs mais recentes
- Logs antigos são removidos automaticamente
- Não é necessária intervenção manual

### **Backup**
- Arquivo `logs_atividades.json` deve ser incluído no backup regular
- Recomenda-se backup diário dos logs

## 📈 Futuras Melhorias

### **Funcionalidades Planejadas**
- 🔄 Exportação de logs para Excel/PDF
- 🔄 Alertas automáticos para atividades suspeitas
- 🔄 Dashboard em tempo real
- 🔄 Filtros avançados por usuário/ação
- 🔄 Relatórios automáticos por email

### **Integrações**
- 🔄 Sistema de notificações
- 🔄 API para integração externa
- 🔄 Backup na nuvem
- 🔄 Análise preditiva de atividades

---

**Desenvolvido por Arabuenã**  
**Sistema de Gestão - Associação Amigo do Povo**

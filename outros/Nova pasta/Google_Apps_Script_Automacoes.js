/**
 * SISTEMA DE AUTOMAÇÕES - ACADEMIA AMIGO DO POVO
 * Google Apps Script para automatizar processos
 */

// ========================================
// CONFIGURAÇÕES - ALTERE CONFORME NECESSÁRIO
// ========================================

const CONFIG = {
  // IDs das planilhas (substitua pelos IDs reais)
  PLANILHA_CADASTROS: 'SEU_ID_PLANILHA_CADASTROS_AQUI',
  PLANILHA_PRESENCA: 'SEU_ID_PLANILHA_PRESENCA_AQUI',
  PLANILHA_DASHBOARD: 'SEU_ID_PLANILHA_DASHBOARD_AQUI',
  
  // E-mail para notificações
  EMAIL_ADMIN: 'admin@academiaamigodopovo.com',
  
  // WhatsApp Business API (opcional)
  WHATSAPP_TOKEN: 'SEU_TOKEN_WHATSAPP_AQUI',
  
  // Configurações gerais
  META_PRESENCAS_DIA: 30,
  DIAS_ALERTA_VENCIMENTO: 7,
  DIAS_ALERTA_INATIVIDADE: 15
};

// ========================================
// FUNÇÃO PRINCIPAL - EXECUTAR DIARIAMENTE
// ========================================

function executarAutomacoesDiarias() {
  console.log('🚀 Iniciando automações diárias...');
  
  try {
    // 1. Verificar vencimentos
    verificarVencimentos();
    
    // 2. Identificar alunos inativos
    verificarAlunosInativos();
    
    // 3. Enviar relatório diário
    enviarRelatorioDiario();
    
    // 4. Atualizar dashboard
    atualizarDashboard();
    
    console.log('✅ Automações concluídas com sucesso!');
    
  } catch (error) {
    console.error('❌ Erro nas automações:', error);
    enviarEmailErro(error);
  }
}

// ========================================
// VERIFICAR VENCIMENTOS
// ========================================

function verificarVencimentos() {
  console.log('📅 Verificando vencimentos...');
  
  const planilha = SpreadsheetApp.openById(CONFIG.PLANILHA_CADASTROS);
  const aba = planilha.getSheetByName('Cadastros');
  const dados = aba.getDataRange().getValues();
  
  const hoje = new Date();
  const alertaData = new Date(hoje.getTime() + (CONFIG.DIAS_ALERTA_VENCIMENTO * 24 * 60 * 60 * 1000));
  
  let vencimentosProximos = [];
  let vencimentosVencidos = [];
  
  // Percorrer dados (começar da linha 2 para pular cabeçalho)
  for (let i = 1; i < dados.length; i++) {
    const linha = dados[i];
    const nome = linha[1]; // Coluna B - Nome
    const status = linha[7]; // Coluna H - Status
    const situacaoPagamento = linha[8]; // Coluna I - Situação Pagamento
    const dataVencimento = new Date(linha[10]); // Coluna K - Data Vencimento
    const telefone = linha[4]; // Coluna E - Telefone
    const valor = linha[9]; // Coluna J - Valor
    
    // Verificar apenas alunos ativos
    if (status === 'Ativo') {
      // Vencimentos próximos
      if (dataVencimento <= alertaData && dataVencimento > hoje) {
        vencimentosProximos.push({
          nome: nome,
          dataVencimento: dataVencimento,
          telefone: telefone,
          valor: valor,
          linha: i + 1
        });
      }
      
      // Vencimentos já vencidos
      if (dataVencimento < hoje && situacaoPagamento !== 'Pago') {
        vencimentosVencidos.push({
          nome: nome,
          dataVencimento: dataVencimento,
          telefone: telefone,
          valor: valor,
          diasAtraso: Math.floor((hoje - dataVencimento) / (1000 * 60 * 60 * 24)),
          linha: i + 1
        });
        
        // Atualizar status para "Vencido" automaticamente
        aba.getRange(i + 1, 9).setValue('Vencido');
      }
    }
  }
  
  // Enviar notificações
  if (vencimentosProximos.length > 0) {
    enviarNotificacaoVencimentos(vencimentosProximos, 'proximos');
  }
  
  if (vencimentosVencidos.length > 0) {
    enviarNotificacaoVencimentos(vencimentosVencidos, 'vencidos');
  }
  
  console.log(`📊 Encontrados: ${vencimentosProximos.length} vencimentos próximos, ${vencimentosVencidos.length} vencidos`);
}

// ========================================
// VERIFICAR ALUNOS INATIVOS
// ========================================

function verificarAlunosInativos() {
  console.log('😴 Verificando alunos inativos...');
  
  const planilhaPresenca = SpreadsheetApp.openById(CONFIG.PLANILHA_PRESENCA);
  const abaPresenca = planilhaPresenca.getSheetByName('Presencas');
  const dadosPresenca = abaPresenca.getDataRange().getValues();
  
  const planilhaCadastros = SpreadsheetApp.openById(CONFIG.PLANILHA_CADASTROS);
  const abaCadastros = planilhaCadastros.getSheetByName('Cadastros');
  const dadosCadastros = abaCadastros.getDataRange().getValues();
  
  const hoje = new Date();
  const dataLimite = new Date(hoje.getTime() - (CONFIG.DIAS_ALERTA_INATIVIDADE * 24 * 60 * 60 * 1000));
  
  let alunosInativos = [];
  
  // Para cada aluno ativo, verificar última presença
  for (let i = 1; i < dadosCadastros.length; i++) {
    const aluno = dadosCadastros[i];
    const nome = aluno[1];
    const status = aluno[7];
    const telefone = aluno[4];
    
    if (status === 'Ativo') {
      // Buscar última presença do aluno
      let ultimaPresenca = null;
      
      for (let j = dadosPresenca.length - 1; j >= 1; j--) {
        if (dadosPresenca[j][0] === nome) {
          ultimaPresenca = new Date(dadosPresenca[j][1]);
          break;
        }
      }
      
      // Se não tem presença ou última presença é muito antiga
      if (!ultimaPresenca || ultimaPresenca < dataLimite) {
        const diasInativo = ultimaPresenca ? 
          Math.floor((hoje - ultimaPresenca) / (1000 * 60 * 60 * 24)) : 
          'Nunca veio';
          
        alunosInativos.push({
          nome: nome,
          ultimaPresenca: ultimaPresenca,
          diasInativo: diasInativo,
          telefone: telefone,
          linha: i + 1
        });
      }
    }
  }
  
  // Enviar notificação sobre alunos inativos
  if (alunosInativos.length > 0) {
    enviarNotificacaoInativos(alunosInativos);
  }
  
  console.log(`📊 Encontrados ${alunosInativos.length} alunos inativos`);
}

// ========================================
// ENVIAR NOTIFICAÇÕES
// ========================================

function enviarNotificacaoVencimentos(lista, tipo) {
  const assunto = tipo === 'proximos' ? 
    '⚠️ Vencimentos Próximos - Academia Amigo do Povo' : 
    '🚨 Pagamentos Vencidos - Academia Amigo do Povo';
    
  let corpo = `<h2>${assunto}</h2><br>`;
  corpo += `<p>Data: ${new Date().toLocaleDateString('pt-BR')}</p><br>`;
  corpo += '<table border="1" style="border-collapse: collapse; width: 100%;">';
  corpo += '<tr><th>Nome</th><th>Vencimento</th><th>Valor</th><th>Telefone</th>';
  
  if (tipo === 'vencidos') {
    corpo += '<th>Dias em Atraso</th>';
  }
  
  corpo += '</tr>';
  
  lista.forEach(item => {
    corpo += `<tr>
      <td>${item.nome}</td>
      <td>${item.dataVencimento.toLocaleDateString('pt-BR')}</td>
      <td>${item.valor}</td>
      <td>${item.telefone}</td>`;
      
    if (tipo === 'vencidos') {
      corpo += `<td>${item.diasAtraso} dias</td>`;
    }
    
    corpo += '</tr>';
  });
  
  corpo += '</table><br>';
  corpo += '<p><i>E-mail automático do sistema da Academia Amigo do Povo</i></p>';
  
  MailApp.sendEmail({
    to: CONFIG.EMAIL_ADMIN,
    subject: assunto,
    htmlBody: corpo
  });
}

function enviarNotificacaoInativos(lista) {
  const assunto = '😴 Alunos Inativos - Academia Amigo do Povo';
  
  let corpo = `<h2>${assunto}</h2><br>`;
  corpo += `<p>Data: ${new Date().toLocaleDateString('pt-BR')}</p><br>`;
  corpo += '<table border="1" style="border-collapse: collapse; width: 100%;">';
  corpo += '<tr><th>Nome</th><th>Última Presença</th><th>Dias Inativo</th><th>Telefone</th></tr>';
  
  lista.forEach(item => {
    corpo += `<tr>
      <td>${item.nome}</td>
      <td>${item.ultimaPresenca ? item.ultimaPresenca.toLocaleDateString('pt-BR') : 'Nunca'}</td>
      <td>${item.diasInativo}</td>
      <td>${item.telefone}</td>
    </tr>`;
  });
  
  corpo += '</table><br>';
  corpo += '<p><i>Sugestão: Entrar em contato para verificar satisfação</i></p>';
  
  MailApp.sendEmail({
    to: CONFIG.EMAIL_ADMIN,
    subject: assunto,
    htmlBody: corpo
  });
}

// ========================================
// RELATÓRIO DIÁRIO
// ========================================

function enviarRelatorioDiario() {
  console.log('📈 Gerando relatório diário...');
  
  const planilhaCadastros = SpreadsheetApp.openById(CONFIG.PLANILHA_CADASTROS);
  const abaCadastros = planilhaCadastros.getSheetByName('Cadastros');
  
  const planilhaPresenca = SpreadsheetApp.openById(CONFIG.PLANILHA_PRESENCA);
  const abaPresenca = planilhaPresenca.getSheetByName('Presencas');
  
  const hoje = new Date().toLocaleDateString('pt-BR');
  
  // Contar estatísticas
  const totalAlunos = abaCadastros.getLastRow() - 1;
  const alunosAtivos = contarStatus(abaCadastros, 'Ativo');
  const pagosHoje = contarPagamentos(abaCadastros, 'Pago');
  const pendentes = contarPagamentos(abaCadastros, 'Pendente');
  const vencidos = contarPagamentos(abaCadastros, 'Vencido');
  const presencasHoje = contarPresencasHoje(abaPresenca);
  
  const assunto = `📊 Relatório Diário - ${hoje} - Academia Amigo do Povo`;
  
  const corpo = `
    <h2>📊 Relatório Diário</h2>
    <p><strong>Data:</strong> ${hoje}</p><br>
    
    <h3>👥 Alunos</h3>
    <ul>
      <li><strong>Total de Alunos:</strong> ${totalAlunos}</li>
      <li><strong>Alunos Ativos:</strong> ${alunosAtivos}</li>
      <li><strong>Taxa de Atividade:</strong> ${((alunosAtivos/totalAlunos)*100).toFixed(1)}%</li>
    </ul>
    
    <h3>💰 Financeiro</h3>
    <ul>
      <li><strong>Pagamentos em Dia:</strong> ${pagosHoje}</li>
      <li><strong>Pagamentos Pendentes:</strong> ${pendentes}</li>
      <li><strong>Pagamentos Vencidos:</strong> ${vencidos}</li>
    </ul>
    
    <h3>✅ Presença</h3>
    <ul>
      <li><strong>Presenças Hoje:</strong> ${presencasHoje}</li>
      <li><strong>Meta Diária:</strong> ${CONFIG.META_PRESENCAS_DIA}</li>
      <li><strong>Status:</strong> ${presencasHoje >= CONFIG.META_PRESENCAS_DIA ? '✅ Meta Atingida' : '⚠️ Abaixo da Meta'}</li>
    </ul>
    
    <p><i>Relatório automático do sistema da Academia Amigo do Povo</i></p>
  `;
  
  MailApp.sendEmail({
    to: CONFIG.EMAIL_ADMIN,
    subject: assunto,
    htmlBody: corpo
  });
}

// ========================================
// FUNÇÕES AUXILIARES
// ========================================

function contarStatus(aba, status) {
  const dados = aba.getDataRange().getValues();
  let contador = 0;
  
  for (let i = 1; i < dados.length; i++) {
    if (dados[i][7] === status) { // Coluna H - Status
      contador++;
    }
  }
  
  return contador;
}

function contarPagamentos(aba, situacao) {
  const dados = aba.getDataRange().getValues();
  let contador = 0;
  
  for (let i = 1; i < dados.length; i++) {
    if (dados[i][8] === situacao) { // Coluna I - Situação Pagamento
      contador++;
    }
  }
  
  return contador;
}

function contarPresencasHoje(aba) {
  const dados = aba.getDataRange().getValues();
  const hoje = new Date().toDateString();
  let contador = 0;
  
  for (let i = 1; i < dados.length; i++) {
    const dataPresenca = new Date(dados[i][1]).toDateString(); // Coluna B - Data
    if (dataPresenca === hoje) {
      contador++;
    }
  }
  
  return contador;
}

function atualizarDashboard() {
  console.log('🔄 Atualizando dashboard...');
  
  const planilha = SpreadsheetApp.openById(CONFIG.PLANILHA_DASHBOARD);
  const aba = planilha.getSheetByName('Dashboard');
  
  // Atualizar data de atualização
  aba.getRange('B2').setValue(new Date());
  
  // Forçar recálculo das fórmulas
  SpreadsheetApp.flush();
}

function enviarEmailErro(erro) {
  MailApp.sendEmail({
    to: CONFIG.EMAIL_ADMIN,
    subject: '🚨 Erro no Sistema - Academia Amigo do Povo',
    body: `Erro detectado no sistema de automações:\n\n${erro.toString()}\n\nVerifique as configurações e planilhas.`
  });
}

// ========================================
// FUNÇÃO DE BACKUP AUTOMÁTICO
// ========================================

function criarBackupSemanal() {
  console.log('💾 Criando backup semanal...');
  
  try {
    const hoje = new Date();
    const dataFormatada = Utilities.formatDate(hoje, Session.getScriptTimeZone(), 'yyyy-MM-dd');
    
    // Criar cópia das planilhas principais
    const cadastros = SpreadsheetApp.openById(CONFIG.PLANILHA_CADASTROS);
    const presenca = SpreadsheetApp.openById(CONFIG.PLANILHA_PRESENCA);
    
    // Criar cópias na pasta raiz do Drive
    DriveApp.getFileById(CONFIG.PLANILHA_CADASTROS)
      .makeCopy(`BACKUP_Cadastros_${dataFormatada}`);
      
    DriveApp.getFileById(CONFIG.PLANILHA_PRESENCA)
      .makeCopy(`BACKUP_Presenca_${dataFormatada}`);
    
    console.log('✅ Backup criado com sucesso!');
    
  } catch (error) {
    console.error('❌ Erro ao criar backup:', error);
    enviarEmailErro(error);
  }
}

// ========================================
// CONFIGURAR TRIGGERS AUTOMÁTICOS
// ========================================

function configurarTriggers() {
  // Deletar triggers existentes
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => ScriptApp.deleteTrigger(trigger));
  
  // Trigger diário às 8h
  ScriptApp.newTrigger('executarAutomacoesDiarias')
    .timeBased()
    .everyDays(1)
    .atHour(8)
    .create();
  
  // Trigger semanal de backup (domingo às 2h)
  ScriptApp.newTrigger('criarBackupSemanal')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.SUNDAY)
    .atHour(2)
    .create();
  
  console.log('⏰ Triggers configurados com sucesso!');
}

// ========================================
// FUNÇÃO DE INSTALAÇÃO/CONFIGURAÇÃO
// ========================================

function instalarSistema() {
  console.log('🛠️ Instalando sistema de automações...');
  
  try {
    // Configurar triggers
    configurarTriggers();
    
    // Enviar e-mail de confirmação
    MailApp.sendEmail({
      to: CONFIG.EMAIL_ADMIN,
      subject: '✅ Sistema de Automações Instalado - Academia Amigo do Povo',
      body: `O sistema de automações foi instalado com sucesso!\n\nFuncionalidades ativas:\n\n- Verificação diária de vencimentos\n- Alerta de alunos inativos\n- Relatório diário por e-mail\n- Backup automático semanal\n\nO sistema executará automaticamente todos os dias às 8h.`
    });
    
    console.log('✅ Sistema instalado com sucesso!');
    
  } catch (error) {
    console.error('❌ Erro na instalação:', error);
  }
}

/**
 * INSTRUÇÕES DE USO:
 * 
 * 1. Substitua os IDs das planilhas na seção CONFIG
 * 2. Configure seu e-mail na variável EMAIL_ADMIN
 * 3. Execute a função 'instalarSistema()' uma vez
 * 4. O sistema funcionará automaticamente
 * 
 * TRIGGERS AUTOMÁTICOS:
 * - Verificações diárias às 8h
 * - Backup semanal aos domingos às 2h
 * 
 * PARA TESTAR:
 * - Execute manualmente 'executarAutomacoesDiarias()'
 */

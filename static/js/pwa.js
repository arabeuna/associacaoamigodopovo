// Registrar o Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/service-worker.js')
      .then((registration) => {
        console.log('Service Worker registrado com sucesso:', registration.scope);
      })
      .catch((error) => {
        console.log('Falha ao registrar o Service Worker:', error);
      });
  });
}

// Função para mostrar o prompt de instalação
let deferredPrompt;
let installButton;

// Aguarda o DOM estar carregado
document.addEventListener('DOMContentLoaded', () => {
  installButton = document.getElementById('install-button');
  console.log('PWA: DOM carregado, botão encontrado:', !!installButton);
});

window.addEventListener('beforeinstallprompt', (e) => {
  console.log('PWA: Evento beforeinstallprompt disparado');
  
  // Aguarda o DOM estar carregado se necessário
  if (!installButton) {
    installButton = document.getElementById('install-button');
  }
  
  // Verifica se existe botão personalizado
  if (installButton) {
    console.log('PWA: Botão personalizado encontrado - usando controle manual');
    // Previne o comportamento padrão apenas se temos botão personalizado
    e.preventDefault();
    // Armazena o evento para uso posterior
    deferredPrompt = e;
    
    // Mostra o botão de instalação
    installButton.style.display = 'block';
    
    // Remove listeners anteriores para evitar duplicação
    installButton.removeEventListener('click', handleInstallClick);
    installButton.addEventListener('click', handleInstallClick);
  } else {
    console.log('PWA: Botão personalizado não encontrado - permitindo banner nativo');
    // NÃO chama preventDefault() para permitir o banner nativo do navegador
    // O navegador mostrará seu próprio banner de instalação
  }
});

// Função separada para lidar com o clique de instalação
function handleInstallClick() {
  console.log('PWA: Botão de instalação clicado');
  if (deferredPrompt) {
    // Mostra o prompt de instalação
    deferredPrompt.prompt();
    
    // Espera o usuário responder ao prompt
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('PWA: Usuário aceitou a instalação');
      } else {
        console.log('PWA: Usuário recusou a instalação');
      }
      // Limpa a referência ao prompt
      deferredPrompt = null;
      // Esconde o botão de instalação
      if (installButton) {
        installButton.style.display = 'none';
      }
    });
  } else {
    console.warn('PWA: deferredPrompt não disponível');
  }
}

// Detecta quando o PWA foi instalado
window.addEventListener('appinstalled', (evt) => {
  console.log('Aplicativo instalado com sucesso!');
});
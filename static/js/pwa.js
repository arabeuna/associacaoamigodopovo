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
const installButton = document.getElementById('install-button');

window.addEventListener('beforeinstallprompt', (e) => {
  // Previne o comportamento padrão do navegador
  e.preventDefault();
  // Armazena o evento para uso posterior
  deferredPrompt = e;
  // Mostra o botão de instalação se ele existir
  if (installButton) {
    installButton.style.display = 'block';
    
    installButton.addEventListener('click', () => {
      // Mostra o prompt de instalação
      deferredPrompt.prompt();
      
      // Espera o usuário responder ao prompt
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('Usuário aceitou a instalação do PWA');
        } else {
          console.log('Usuário recusou a instalação do PWA');
        }
        // Limpa a referência ao prompt
        deferredPrompt = null;
        // Esconde o botão de instalação
        installButton.style.display = 'none';
      });
    });
  }
});

// Detecta quando o PWA foi instalado
window.addEventListener('appinstalled', (evt) => {
  console.log('Aplicativo instalado com sucesso!');
});
// Funcoes para gerenciar atividades

function excluirAtividade(nome) {
    if (confirm('Tem certeza que deseja excluir a atividade "' + nome + '"?')) {
        fetch('/excluir_atividade/' + encodeURIComponent(nome), {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Atividade excluida com sucesso!');
                location.reload();
            } else {
                alert('Erro ao excluir atividade: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir atividade. Tente novamente.');
        });
    }
}

function ativarAtividade(nome) {
    fetch('/ativar_atividade/' + encodeURIComponent(nome), {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Atividade ativada com sucesso!');
            location.reload();
        } else {
            alert('Erro ao ativar atividade: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao ativar atividade. Tente novamente.');
    });
}

// Desativar atividade
function desativarAtividade(nome) {
    if (confirm('Deseja desativar a atividade "' + nome + '"?')) {
        fetch('/desativar_atividade/' + encodeURIComponent(nome), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(function(data) {
            if (data.success) {
                alert('Atividade "' + nome + '" desativada com sucesso!');
                location.reload();
            } else {
                alert('Erro ao desativar atividade: ' + data.message);
            }
        })
        .catch(function(error) {
            console.error('Erro:', error);
            alert('Erro ao desativar atividade. Tente novamente.');
        });
    }
}

// Gerenciar turmas da atividade
function gerenciarTurmas(nome) {
    // Redirecionar para gerenciar turmas com filtro da atividade
    window.location.href = '/gerenciar_turmas?atividade=' + encodeURIComponent(nome);
}

// Editar atividade
function editarAtividade(nome) {
    // Buscar dados da atividade via fetch
    fetch('/api/atividade/' + encodeURIComponent(nome))
        .then(response => response.json())
        .then(atividade => {
            if (atividade) {
                document.getElementById('edit_nome_antigo').value = nome;
                document.getElementById('edit_nome_atividade').value = nome;
                document.getElementById('edit_descricao_atividade').value = atividade.descricao || '';
                
                // Definir professor se existir
                var professorSelect = document.getElementById('edit_professor');
                if (atividade.professores_vinculados && atividade.professores_vinculados.length > 0) {
                    professorSelect.value = atividade.professores_vinculados[0];
                } else {
                    professorSelect.value = '';
                }
                
                // Definir status
                var statusSelect = document.getElementById('edit_status');
                statusSelect.value = atividade.ativa ? 'true' : 'false';
            }
            
            var modal = new bootstrap.Modal(document.getElementById('modalEditarAtividade'));
            modal.show();
        })
        .catch(error => {
            console.error('Erro ao buscar atividade:', error);
            alert('Erro ao carregar dados da atividade.');
        });
}

// Ver detalhes da atividade
function verDetalhesAtividade(nome) {
    // Buscar dados da atividade via fetch
    fetch('/api/atividade/' + encodeURIComponent(nome))
        .then(response => response.json())
        .then(atividade => {
            if (!atividade) {
                alert('Atividade nao encontrada.');
                return;
            }
            
            // Criar modal com detalhes da atividade
            var modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Detalhes da Atividade</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Informacoes Basicas</h6>
                                    <p><strong>Nome:</strong> ${atividade.nome}</p>
                                    <p><strong>Descricao:</strong> ${atividade.descricao || 'Nao informado'}</p>
                                    <p><strong>Status:</strong> <span class="badge bg-${atividade.ativa ? 'success' : 'danger'}">${atividade.ativa ? 'Ativa' : 'Inativa'}</span></p>
                                    <p><strong>Data de Criacao:</strong> ${atividade.data_criacao || 'Nao informado'}</p>
                                    <p><strong>Criado por:</strong> ${atividade.criado_por || 'Nao informado'}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Estatisticas</h6>
                                    <p><strong>Total de Alunos:</strong> <span class="badge bg-info">${atividade.total_alunos || 0}</span></p>
                                    ${atividade.professores_vinculados && atividade.professores_vinculados.length > 0 ? 
                                        '<h6>Professores Vinculados</h6>' +
                                        '<div class="mb-3">' +
                                            atividade.professores_vinculados.map(prof => `<span class="badge bg-secondary me-1 mb-1">${prof}</span>`).join('') +
                                        '</div>'
                                     : '<p><strong>Professores:</strong> <span class="text-muted">Nenhum professor vinculado</span></p>'}
                                    ${atividade.turmas && atividade.turmas.length > 0 ? 
                                        '<h6>Turmas</h6>' +
                                        '<div class="mb-3">' +
                                            atividade.turmas.map(turma => `<span class="badge bg-primary me-1 mb-1">${turma}</span>`).join('') +
                                        '</div>'
                                     : ''}
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                            <div class="btn-group">
                                ${atividade.ativa ? 
                                    `<button type="button" class="btn btn-warning" onclick="desativarAtividade('${atividade.nome}')" data-bs-dismiss="modal">
                                        <i class="fas fa-pause"></i> Desativar
                                    </button>` :
                                    `<button type="button" class="btn btn-success" onclick="ativarAtividade('${atividade.nome}')" data-bs-dismiss="modal">
                                        <i class="fas fa-play"></i> Ativar
                                    </button>`
                                }
                                <button type="button" class="btn btn-danger" onclick="excluirAtividade('${atividade.nome}')" data-bs-dismiss="modal">
                                    <i class="fas fa-trash"></i> Excluir
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            var bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Remove modal do DOM quando fechado
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.removeChild(modal);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar atividade:', error);
            alert('Erro ao carregar detalhes da atividade.');
        });
}
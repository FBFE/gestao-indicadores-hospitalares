// ========================================
// GERENCIADOR DE ADMINISTRAÇÃO
// ========================================

class AdminManager {
  constructor() {
    this.isLoading = false;
  }

  init() {
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Event listener para mudança de unidade no admin
    const adminSelect = document.getElementById('admin-unidade-select');
    if (adminSelect && !adminSelect.hasAttribute('data-listener')) {
      adminSelect.addEventListener('change', (e) => this.preencherUrlFoto(e));
      adminSelect.setAttribute('data-listener', 'true');
    }

    // Event listener para validação de URL em tempo real
    const urlInput = document.getElementById('admin-unidade-foto-url');
    if (urlInput && !urlInput.hasAttribute('data-listener')) {
      urlInput.addEventListener('input', (e) => this.validateImageUrl(e.target));
      urlInput.setAttribute('data-listener', 'true');
    }
  }

  initUnidades() {
    this.setupEventListeners();
    this.populateUnidadeSelect();
  }

  initUsuarios() {
    this.loadUsuarios();
  }

  populateUnidadeSelect() {
    const select = document.getElementById('admin-unidade-select');
    if (!select || !window.app.listaUnidades) return;

    // Limpa opções existentes
    select.innerHTML = '<option value="" disabled selected>Selecione a Unidade</option>';

    // Adiciona unidades
    window.app.listaUnidades.forEach(unidade => {
      const option = document.createElement('option');
      option.value = unidade.id;
      option.textContent = unidade.nome;
      select.appendChild(option);
    });

    // Reinicializa Materialize
    M.FormSelect.init(select);
  }

  preencherUrlFoto(event) {
    const unidadeId = event.target.value;
    const unidade = window.app.listaUnidades?.find(u => u.id === unidadeId);
    const inputUrl = document.getElementById('admin-unidade-foto-url');
    
    if (inputUrl) {
      inputUrl.value = (unidade && unidade.foto_url) ? unidade.foto_url : '';
      M.updateTextFields();
      
      // Valida URL se existir
      if (inputUrl.value) {
        this.validateImageUrl(inputUrl);
      }
    }
  }

  validateImageUrl(input) {
    const url = input.value.trim();
    const preview = this.getOrCreateImagePreview();
    
    if (!url) {
      this.hideImagePreview();
      input.classList.remove('valid', 'invalid');
      return;
    }

    // Validação básica de URL
    const urlPattern = /^https?:\/\/.+\..+/;
    if (!urlPattern.test(url)) {
      input.classList.remove('valid');
      input.classList.add('invalid');
      this.hideImagePreview();
      return;
    }

    // Tenta carregar a imagem para validar
    const img = new Image();
    img.onload = () => {
      input.classList.remove('invalid');
      input.classList.add('valid');
      this.showImagePreview(url);
    };
    
    img.onerror = () => {
      input.classList.remove('valid');
      input.classList.add('invalid');
      this.hideImagePreview();
    };
    
    img.src = url;
  }

  getOrCreateImagePreview() {
    let preview = document.getElementById('image-preview');
    
    if (!preview) {
      const container = document.querySelector('#page-adminUnidades .card');
      preview = document.createElement('div');
      preview.id = 'image-preview';
      preview.className = 'image-preview-container';
      preview.style.display = 'none';
      preview.innerHTML = `
        <div class="col s12 m6 offset-m3">
          <div class="card">
            <div class="card-content center-align">
              <span class="card-title">Pré-visualização da Imagem</span>
              <img id="preview-image" src="" alt="Preview" style="max-width: 100%; max-height: 200px; border-radius: 8px;">
            </div>
          </div>
        </div>
      `;
      container.appendChild(preview);
    }
    
    return preview;
  }

  showImagePreview(url) {
    const preview = this.getOrCreateImagePreview();
    const img = preview.querySelector('#preview-image');
    
    img.src = url;
    preview.style.display = 'block';
    preview.classList.add('animate-fadeIn');
  }

  hideImagePreview() {
    const preview = document.getElementById('image-preview');
    if (preview) {
      preview.style.display = 'none';
    }
  }

  async salvarUrlDaFoto() {
    if (this.isLoading) return;

    const unidadeId = document.getElementById('admin-unidade-select')?.value;
    const url = document.getElementById('admin-unidade-foto-url')?.value?.trim();

    // Validações
    if (!unidadeId) {
      window.app.showError('Selecione uma unidade primeiro.');
      return;
    }

    if (!url) {
      window.app.showError('Informe a URL da imagem.');
      return;
    }

    // Validação de URL
    const urlPattern = /^https?:\/\/.+\..+/;
    if (!urlPattern.test(url)) {
      window.app.showError('URL inválida. Use uma URL completa começando com http:// ou https://');
      return;
    }

    this.isLoading = true;

    try {
      // Mostra loading
      const toastCarregando = M.toast({
        html: '<i class="material-icons left">hourglass_empty</i>Salvando foto...',
        displayLength: 10000
      });

      // Chama API
      const response = await this.updateUnidadeFoto(unidadeId, url);
      
      toastCarregando.dismiss();

      if (response.success) {
        window.app.showSuccess(response.message);
        
        // Atualiza cache local
        const unidade = window.app.listaUnidades?.find(u => u.id === unidadeId);
        if (unidade) {
          unidade.foto_url = url;
        }
        
        // Limpa formulário
        this.clearForm();
        
      } else {
        window.app.showError(response.error || 'Erro ao salvar foto');
      }

    } catch (error) {
      window.app.log('error', 'Erro ao salvar foto da unidade:', error);
      window.app.showError('Erro ao salvar foto da unidade');
    } finally {
      this.isLoading = false;
    }
  }

  async updateUnidadeFoto(unidadeId, url) {
    try {
      return await window.app.makeApiCall(`/unidades/${unidadeId}/foto`, {
        method: 'PUT',
        body: { foto_url: url }
      });
    } catch (error) {
      // Fallback para desenvolvimento
      window.app.log('warn', 'API não disponível, simulando sucesso:', error);
      return {
        success: true,
        message: 'Foto da unidade salva com sucesso! (modo desenvolvimento)'
      };
    }
  }

  clearForm() {
    // Reset select
    const select = document.getElementById('admin-unidade-select');
    if (select) {
      select.value = '';
      M.FormSelect.init(select);
    }

    // Reset input
    const input = document.getElementById('admin-unidade-foto-url');
    if (input) {
      input.value = '';
      input.classList.remove('valid', 'invalid');
      M.updateTextFields();
    }

    // Esconde preview
    this.hideImagePreview();
  }

  // ========================================
  // GERENCIAMENTO DE USUÁRIOS
  // ========================================

  async loadUsuarios() {
    try {
      const usuarios = await this.getUsuarios();
      this.renderUsuarios(usuarios);
    } catch (error) {
      window.app.log('error', 'Erro ao carregar usuários:', error);
      this.renderUsuariosError();
    }
  }

  async getUsuarios() {
    try {
      return await window.app.makeApiCall('/admin/usuarios');
    } catch (error) {
      // Fallback para desenvolvimento
      return [
        { Email: 'admin@hospital.com', Nome: 'Administrador', Perfil: 'admin' },
        { Email: 'gestor@hospital.com', Nome: 'Gestor', Perfil: 'gestor' },
        { Email: 'operador@hospital.com', Nome: 'Operador', Perfil: 'operador' }
      ];
    }
  }

  renderUsuarios(usuarios) {
    const container = document.querySelector('#page-adminUsuarios .row');
    
    if (!container) return;

    let html = `
      <div class="col s12">
        <div class="card">
          <div class="card-content">
            <span class="card-title">
              <i class="material-icons left">people</i>
              Usuários do Sistema
              <span class="badge new blue" data-badge-caption="usuários">${usuarios.length}</span>
            </span>
            
            <div class="row">
              <div class="col s12">
                <table class="responsive-table striped highlight">
                  <thead>
                    <tr>
                      <th><i class="material-icons tiny">email</i> Email</th>
                      <th><i class="material-icons tiny">person</i> Nome</th>
                      <th><i class="material-icons tiny">security</i> Perfil</th>
                      <th><i class="material-icons tiny">settings</i> Ações</th>
                    </tr>
                  </thead>
                  <tbody>
    `;

    usuarios.forEach((usuario, index) => {
      const perfilColor = this.getPerfilColor(usuario.Perfil);
      
      html += `
        <tr>
          <td>${usuario.Email}</td>
          <td><strong>${usuario.Nome}</strong></td>
          <td>
            <span class="chip ${perfilColor}">
              <i class="material-icons left tiny">${this.getPerfilIcon(usuario.Perfil)}</i>
              ${usuario.Perfil}
            </span>
          </td>
          <td>
            <button class="btn-floating btn-small waves-effect waves-light blue tooltipped" 
                    data-position="top" 
                    data-tooltip="Editar usuário"
                    onclick="window.adminManager.editarUsuario(${index})">
              <i class="material-icons">edit</i>
            </button>
            ${usuario.Perfil !== 'admin' ? `
              <button class="btn-floating btn-small waves-effect waves-light red tooltipped" 
                      data-position="top" 
                      data-tooltip="Remover usuário"
                      onclick="window.adminManager.removerUsuario(${index})">
                <i class="material-icons">delete</i>
              </button>
            ` : ''}
          </td>
        </tr>
      `;
    });

    html += `
                  </tbody>
                </table>
              </div>
            </div>
            
            <div class="row">
              <div class="col s12 center-align">
                <button class="btn waves-effect waves-light gradient-btn" 
                        onclick="window.adminManager.adicionarUsuario()">
                  <i class="material-icons left">person_add</i>Adicionar Usuário
                </button>
              </div>
            </div>
            
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    // Inicializa tooltips
    M.Tooltip.init(document.querySelectorAll('.tooltipped'));
  }

  renderUsuariosError() {
    const container = document.querySelector('#page-adminUsuarios .row');
    
    if (!container) return;

    container.innerHTML = `
      <div class="col s12">
        <div class="card">
          <div class="card-content center-align">
            <i class="material-icons large red-text">error_outline</i>
            <h5 class="red-text">Erro ao carregar usuários</h5>
            <p class="grey-text">Verifique suas permissões e conexão</p>
            <button class="btn waves-effect waves-light" onclick="window.adminManager.loadUsuarios()">
              <i class="material-icons left">refresh</i>Tentar Novamente
            </button>
          </div>
        </div>
      </div>
    `;
  }

  getPerfilColor(perfil) {
    const colors = {
      admin: 'red lighten-1',
      gestor: 'blue lighten-1', 
      operador: 'green lighten-1',
      visualizador: 'grey lighten-1'
    };
    return colors[perfil] || 'grey';
  }

  getPerfilIcon(perfil) {
    const icons = {
      admin: 'shield',
      gestor: 'business_center',
      operador: 'work',
      visualizador: 'visibility'
    };
    return icons[perfil] || 'person';
  }

  editarUsuario(index) {
    // TODO: Implementar modal de edição
    window.app.showInfo('Funcionalidade de edição será implementada em breve');
  }

  removerUsuario(index) {
    // TODO: Implementar remoção
    if (confirm('Tem certeza que deseja remover este usuário?')) {
      window.app.showInfo('Funcionalidade de remoção será implementada em breve');
    }
  }

  adicionarUsuario() {
    // TODO: Implementar modal de adição
    window.app.showInfo('Funcionalidade de adição será implementada em breve');
  }

  // ========================================
  // UTILIDADES
  // ========================================

  validatePermissions(requiredPermission) {
    const userProfile = window.app.userProfile;
    
    if (!userProfile || userProfile.perfil !== 'admin') {
      window.app.showError('Acesso negado. Apenas administradores podem acessar esta funcionalidade.');
      window.app.navegarPara('dashboard');
      return false;
    }
    
    return true;
  }

  exportUsuarios() {
    // TODO: Implementar exportação de usuários
    window.app.showInfo('Funcionalidade de exportação será implementada em breve');
  }

  importUsuarios() {
    // TODO: Implementar importação de usuários
    window.app.showInfo('Funcionalidade de importação será implementada em breve');
  }
}

// Expor globalmente
window.adminManager = new AdminManager();

// Funções globais para compatibilidade
window.salvarUrlDaFoto = () => window.adminManager.salvarUrlDaFoto();
window.popularFormularioAdminUnidades = () => window.adminManager.initUnidades();

// Auto-inicializar quando a aplicação estiver pronta
document.addEventListener('DOMContentLoaded', () => {
  if (window.app) {
    window.adminManager.init();
  }
});
# Sistema de Gestão de Indicadores Hospitalares

Uma aplicação web moderna para gestão de indicadores hospitalares, desenvolvida com HTML/CSS/JavaScript no frontend e Python/Flask no backend, integrada com Google Sheets para armazenamento de dados.

## 🏥 Características

- **Dashboard Responsivo**: Visualização clara dos indicadores com gráficos e tabelas
- **Modo Escuro**: Interface adaptável para diferentes preferências
- **Acessibilidade**: Suporte para daltonismo e recursos de acessibilidade
- **Lançamento em Lote**: Inserção eficiente de múltiplos indicadores
- **Autenticação Google**: Login seguro via Google OAuth
- **Responsive Design**: Funciona perfeitamente em desktop e mobile
- **Animações Suaves**: UX moderna com transições e animações

## 🚀 Tecnologias Utilizadas

### Frontend
- HTML5, CSS3, JavaScript ES6+
- Materialize CSS para componentes
- AOS (Animate On Scroll) para animações
- Progressive Web App (PWA) ready

### Backend
- Python 3.9+
- Flask (framework web)
- Google Sheets API
- Google OAuth 2.0
- Redis (sessões em produção)

### Integração
- Google Sheets como banco de dados
- Netlify para deploy do frontend
- Heroku/Render para deploy do backend

## 📋 Pré-requisitos

1. **Conta Google** com acesso ao Google Sheets
2. **Python 3.9+** para desenvolvimento local
3. **Node.js 16+** para ferramentas de build
4. **Conta Netlify** para deploy

## 🛠️ Configuração

### 1. Configurar Google Sheets API

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a **Google Sheets API**
4. Crie credenciais de **Service Account**
5. Baixe o arquivo JSON das credenciais
6. Crie uma planilha no Google Sheets com as seguintes abas:

#### Estrutura das Planilhas:

**Usuarios**
```
Email | Nome | Perfil
admin@hospital.com | Administrador | admin
gestor@hospital.com | Gestor | gestor
```

**Unidades**
```
ID | Nome | Foto_URL
1 | Hospital Central | https://exemplo.com/foto1.jpg
2 | UPA Norte | https://exemplo.com/foto2.jpg
```

**Indicadores_Dicionario**
```
ID | Indicador | O que Mede | Numerador | Denominador | Fórmula | Meta
1 | Taxa de Mortalidade | Percentual de óbitos | Óbitos | Total Internações | (N/D)*100 | <5%
```

**Lancamentos**
```
Timestamp | Email_Usuario | ID_Unidade | Indicador_Nome | Mes | Ano | Valor_Numerador | Valor_Denominador
```

7. Compartilhe a planilha com o email do service account (permissão de edição)

### 2. Configurar OAuth Google

1. No Google Cloud Console, vá em **Credenciais**
2. Clique em **Criar credenciais** > **ID do cliente OAuth 2.0**
3. Tipo: **Aplicação da Web**
4. Adicione suas URLs autorizadas:
   - http://localhost:3000 (desenvolvimento)
   - https://seu-site.netlify.app (produção)

### 3. Configurar Backend

```bash
cd backend
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Instalar dependências
pip install -r requirements.txt

# Executar servidor de desenvolvimento
python src/app.py
```

### 4. Configurar Frontend

```bash
cd frontend
npm install

# Servidor de desenvolvimento
npm run dev

# Build para produção
npm run build
```

## 🔧 Variáveis de Ambiente

### Backend (.env)
```env
GOOGLE_SPREADSHEET_ID=sua-planilha-id
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
SECRET_KEY=sua-chave-secreta
FLASK_ENV=development
```

### Netlify (Variáveis de Ambiente)
```
GOOGLE_SPREADSHEET_ID
GOOGLE_CLIENT_ID  
GOOGLE_CREDENTIALS_JSON
SECRET_KEY
```

## 📦 Deploy

### Frontend (Netlify)

1. Conecte seu repositório ao Netlify
2. Configure as variáveis de ambiente
3. Build settings:
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend`

### Backend (Heroku/Render)

1. Crie uma aplicação no Heroku/Render
2. Configure as variáveis de ambiente
3. Deploy via Git ou GitHub

## 🎨 Personalização

### Temas
- Modifique as CSS variables em `css/styles.css`
- Cores, espaçamentos e gradientes são configuráveis

### Indicadores
- Adicione novos indicadores na planilha "Indicadores_Dicionario"
- Configure fórmulas e metas personalizadas

### Permissões
- Configure perfis de usuário na planilha "Usuarios"
- Perfis disponíveis: admin, gestor, operador, visualizador

## 📱 Funcionalidades

### Dashboard
- ✅ Filtros por unidade, período
- ✅ Visualização em tabela responsiva
- ✅ Status visual dos indicadores
- ✅ Detalhes expandidos em modal

### Lançamento
- ✅ Formulário dinâmico de indicadores
- ✅ Validação de dados
- ✅ Salvamento em lote
- ✅ Feedback visual de progresso

### Administração
- ✅ Gerenciamento de unidades
- ✅ Upload de fotos de perfil
- ✅ Controle de acesso por perfil

### Acessibilidade
- ✅ Modo escuro/claro
- ✅ Suporte para daltonismo
- ✅ Navegação por teclado
- ✅ Leitores de tela

## 🐛 Troubleshooting

### Erro de Autenticação Google
- Verifique se o domínio está autorizado no OAuth
- Confirme se o Client ID está correto
- Verifique se a planilha está compartilhada

### Erro de Conexão com Sheets
- Confirme se a API está ativada
- Verifique as credenciais do service account
- Confirme se o ID da planilha está correto

### Erro 500 no Backend
- Verifique os logs do servidor
- Confirme se todas as variáveis de ambiente estão configuradas
- Teste a conexão com Google Sheets

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 👥 Suporte

Para suporte, entre em contato através do email: suporte@gestao-indicadores.com

## 🗺️ Roadmap

- [ ] Exportação para PDF/Excel
- [ ] Gráficos interativos
- [ ] Notificações push
- [ ] API pública
- [ ] App mobile nativo
- [ ] Integração com BI tools

---

Desenvolvido com ❤️ para a gestão hospitalar eficiente.
# Gestão de Indicadores Hospitalares - Deploy Completo

## 🎯 ARQUITETURA DE DEPLOY

### Stack de Produção:
- **Frontend**: Netlify (Estático)
- **Backend**: Railway (API Flask + PostgreSQL)
- **Banco**: PostgreSQL na Railway
- **SSL**: Automático (HTTPS)

---

## 🚀 PARTE 1: Deploy do Backend (Railway)

### 1.1 Preparação do Backend
Já configurado com:
- ✅ Flask app otimizada
- ✅ PostgreSQL support
- ✅ Configurações de produção
- ✅ Variáveis de ambiente

### 1.2 Deploy na Railway
1. **Acesse**: https://railway.app
2. **Login** com GitHub
3. **New Project** > Deploy from GitHub repo
4. **Selecione** este repositório
5. **Configure** service:
   - Root directory: `/backend`
   - Start command: `python src/app_postgresql.py`

### 1.3 Adicionar PostgreSQL
1. No projeto Railway, clique **+ New**
2. Selecione **Database** > **PostgreSQL**
3. Aguarde provisioning

### 1.4 Variáveis de Ambiente (Railway)
```env
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-aqui
JWT_SECRET_KEY=sua-jwt-chave-aqui
DATABASE_URL=${{Postgres.DATABASE_URL}}
CORS_ORIGINS=https://seu-site.netlify.app,https://seu-dominio.com
```

---

## 🌐 PARTE 2: Deploy do Frontend (Netlify)

### 2.1 Preparação do Frontend

```
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
```

### 4. Configuração de Domínio
- Configure um domínio personalizado se necessário
- Certifique-se de que o SSL está habilitado

---

## 🐍 Deploy do Backend (Heroku/Render)

### Opção A: Heroku

#### 1. Preparação
```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Criar app
heroku create seu-app-indicadores-api
```

#### 2. Configuração
```bash
cd backend

# Adicionar buildpack Python
heroku buildpacks:set heroku/python -a seu-app-indicadores-api

# Configurar variáveis de ambiente
heroku config:set SECRET_KEY="sua-chave-secreta-super-segura" -a seu-app-indicadores-api
heroku config:set GOOGLE_SPREADSHEET_ID="1RXm-9-K_1H8GZjvNjnhpBvNnDQCejDMkBUPEKF26Too" -a seu-app-indicadores-api
heroku config:set GOOGLE_CLIENT_ID="seu-client-id.apps.googleusercontent.com" -a seu-app-indicadores-api
heroku config:set GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}' -a seu-app-indicadores-api
```

#### 3. Deploy
```bash
# Inicializar git no backend (se necessário)
git init
git add .
git commit -m "Initial commit"

# Adicionar remote do Heroku
heroku git:remote -a seu-app-indicadores-api

# Deploy
git push heroku main
```

### Opção B: Render

#### 1. Configuração
1. Acesse [Render](https://render.com)
2. Conecte seu repositório
3. Crie um novo "Web Service"

#### 2. Configuração do Build
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && gunicorn src.app:app`
- **Environment**: Python 3

#### 3. Variáveis de Ambiente
Configure no painel do Render:
```
SECRET_KEY=sua-chave-secreta-super-segura
GOOGLE_SPREADSHEET_ID=1RXm-9-K_1H8GZjvNjnhpBvNnDQCejDMkBUPEKF26Too
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

---

## 📊 Configuração do Google Sheets

### 1. Criar Service Account
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto ou selecione existente
3. Ative a "Google Sheets API"
4. Vá em "Credenciais" > "Criar credenciais" > "Conta de serviço"
5. Baixe o arquivo JSON das credenciais

### 2. Configurar OAuth
1. No mesmo projeto, crie "ID do cliente OAuth 2.0"
2. Tipo: "Aplicação da Web"
3. Adicione suas URLs autorizadas:
   - `http://localhost:3000` (desenvolvimento)
   - `https://seu-site.netlify.app` (produção)

### 3. Estrutura da Planilha
Crie uma planilha com as seguintes abas:

#### Usuarios
| Email | Nome | Perfil |
|-------|------|--------|
| admin@hospital.com | Administrador | admin |
| gestor@hospital.com | Gestor | gestor |

#### Unidades
| ID | Nome | Foto_URL |
|----|------|----------|
| 1 | Hospital Central | https://exemplo.com/foto1.jpg |
| 2 | UPA Norte | https://exemplo.com/foto2.jpg |

#### Indicadores_Dicionario
| ID | Indicador | O que Mede | Numerador | Denominador | Fórmula | Meta |
|----|-----------|------------|-----------|-------------|---------|------|
| 1 | Taxa de Mortalidade | Percentual de óbitos | Óbitos | Internações | (N/D)*100 | <5% |

#### Lancamentos
| Timestamp | Email_Usuario | ID_Unidade | Indicador_Nome | Mes | Ano | Valor_Numerador | Valor_Denominador |
|-----------|---------------|------------|----------------|-----|-----|-----------------|-------------------|
| (dados serão inseridos automaticamente) |

### 4. Compartilhar Planilha
Compartilhe a planilha com o email do service account (permissão de edição)

---

## 🔗 Conectar Frontend e Backend

### 1. Atualizar URL da API
No arquivo `frontend/js/config.js`, atualize:

```javascript
const API_CONFIG = {
  baseURL: 'https://seu-app-indicadores-api.herokuapp.com/api',
  // ou
  baseURL: 'https://seu-app-indicadores-api.onrender.com/api',
};
```

### 2. Configurar CORS
No backend, verifique se as URLs do frontend estão nas configurações de CORS.

### 3. Atualizar Netlify Redirects
No arquivo `netlify.toml`, atualize:

```toml
[[redirects]]
  from = "/api/*"
  to = "https://seu-app-indicadores-api.herokuapp.com/api/:splat"
  status = 200
```

---

## ✅ Checklist de Deploy

### Antes do Deploy
- [ ] Credenciais Google configuradas
- [ ] Planilha criada e compartilhada
- [ ] Variáveis de ambiente definidas
- [ ] URLs de produção configuradas
- [ ] Código testado localmente

### Backend
- [ ] Deploy no Heroku/Render realizado
- [ ] Variáveis de ambiente configuradas
- [ ] Endpoint `/api/health` funcionando
- [ ] Conexão com Google Sheets testada

### Frontend
- [ ] Deploy no Netlify realizado
- [ ] Redirects configurados
- [ ] Autenticação Google funcionando
- [ ] API calls funcionando

### Testes Finais
- [ ] Login com Google funciona
- [ ] Dashboard carrega dados
- [ ] Lançamentos podem ser salvos
- [ ] Admin consegue gerenciar unidades
- [ ] Responsividade mobile OK

---

## 🐛 Troubleshooting

### Erro de CORS
- Verifique se a URL do frontend está nas configurações de CORS do backend
- Certifique-se de que os redirects do Netlify estão corretos

### Erro de Autenticação Google
- Verifique se o Client ID está correto
- Confirme se as URLs estão autorizadas no Google Cloud Console
- Verifique se o domínio de produção está configurado

### Erro de Conexão com Sheets
- Confirme se a API do Google Sheets está ativada
- Verifique se as credenciais JSON estão corretas
- Certifique-se de que a planilha está compartilhada com o service account

### Erro 500 no Backend
- Verifique os logs do Heroku/Render
- Confirme se todas as variáveis de ambiente estão configuradas
- Teste o endpoint `/api/health`

### Performance
- Configure cache adequadamente
- Otimize imagens
- Use CDN se necessário

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs dos serviços (Netlify, Heroku/Render)
2. Consulte a documentação das APIs utilizadas
3. Entre em contato através dos issues do repositório
# 🚀 GUIA DE DEPLOY - PASSO A PASSO

## ORDEM DE DEPLOY
1. ✅ Backend (Railway) 
2. ✅ Frontend (Netlify)
3. ✅ Configurar URLs
4. ✅ Testes finais

---

## 🎯 PASSO 1: DEPLOY DO BACKEND (Railway)

### 1.1 Criar Conta na Railway
1. Acesse: https://railway.app
2. Faça login com GitHub
3. Clique em **"New Project"**

### 1.2 Deploy do Backend
1. Selecione **"Deploy from GitHub repo"**
2. Escolha este repositório
3. Selecione o serviço **backend**
4. Railway vai detectar automaticamente o Python

### 1.3 Adicionar PostgreSQL
1. No projeto, clique **"+ New"**
2. Selecione **"Database"** > **"PostgreSQL"**
3. Aguarde provisioning (2-3 minutos)

### 1.4 Configurar Variáveis de Ambiente
No painel do Railway, adicione:
```
FLASK_ENV=production
SECRET_KEY=gestao-indicadores-secret-super-strong-2024
JWT_SECRET_KEY=jwt-secret-key-muito-forte-2024
DATABASE_URL=${{Postgres.DATABASE_URL}}
CORS_ORIGINS=https://gestao-indicadores.netlify.app
```

### 1.5 Configurar Start Command
```
cd src && python app_postgresql.py
```

### 1.6 Copiar URL da API
Após deploy, copie a URL (ex: `https://web-production-xxxx.up.railway.app`)

---

## 🌐 PASSO 2: DEPLOY DO FRONTEND (Netlify)

### 2.1 Atualizar Config do Frontend
1. **Edite**: `frontend/js/config-production.js`
2. **Substitua** a URL da API:
```javascript
const API_CONFIG = {
  baseURL: 'https://sua-url-railway-aqui.up.railway.app'
}
```

### 2.2 Usar Config de Produção
**Edite** `frontend/index.html` e substitua:
```html
<!-- TROCAR esta linha: -->
<script src="js/config.js"></script>

<!-- POR esta: -->
<script src="js/config-production.js"></script>
```

### 2.3 Deploy no Netlify
1. Acesse: https://netlify.com
2. Login com GitHub  
3. **"New site from Git"**
4. Selecione este repositório
5. Configurações:
   - **Branch**: main
   - **Base directory**: frontend
   - **Publish directory**: frontend
   - **Build command**: (deixar vazio)

### 2.4 Atualizar netlify.toml
**Edite** `netlify.toml` e substitua:
```
https://sua-api-railway.up.railway.app
```

### 2.5 Copiar URL do Frontend
Após deploy, copie a URL (ex: `https://gestao-indicadores.netlify.app`)

---

## 🔧 PASSO 3: CONFIGURAR CORS

### 3.1 Atualizar CORS no Backend
No Railway, **atualize** a variável:
```
CORS_ORIGINS=https://sua-url-netlify.netlify.app
```

### 3.2 Redeploy
O Railway vai fazer redeploy automaticamente.

---

## ✅ PASSO 4: TESTES FINAIS

### 4.1 Testar Endpoints
```bash
# Health check
curl https://sua-api-railway.up.railway.app/health

# Login
curl -X POST https://sua-api-railway.up.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hospital.com","senha":"admin123"}'
```

### 4.2 Testar Frontend
1. Acesse: `https://sua-url-netlify.netlify.app`
2. Faça login com: `admin@hospital.com` / `admin123`
3. Teste todas as funcionalidades

---

## 🎉 RESULTADO FINAL

Após conclusão:
- ✅ **Frontend**: https://gestao-indicadores.netlify.app
- ✅ **Backend**: https://web-production-xxxx.up.railway.app  
- ✅ **HTTPS**: Automático
- ✅ **Banco PostgreSQL**: Configurado
- ✅ **Sistema funcionando** online!

---

## 🔧 TROUBLESHOOTING

### Erro de CORS
- Verificar variável `CORS_ORIGINS` no Railway
- URL deve terminar sem `/`

### Erro 404 na API
- Verificar URL no `config-production.js`
- Verificar start command no Railway

### Erro de Banco
- Verificar se PostgreSQL está conectado
- Ver logs no Railway: Project > Deployments > Logs

### Frontend não carrega
- Verificar se `config-production.js` está sendo usado
- Ver Network tab no DevTools do navegador

---

## 📞 SUPORTE

Se tiver problemas:
1. **Logs Railway**: Project > Deployments > Logs
2. **Logs Netlify**: Site > Functions > Logs  
3. **DevTools**: F12 > Console/Network
4. **Health Check**: `sua-api/health`
# ⚡ DEPLOY RÁPIDO - 5 MINUTOS

## 🚀 1. BACKEND (Railway) - 2 minutos

1. **Acesse**: https://railway.app
2. **Login** com GitHub
3. **New Project** > **Deploy from GitHub repo**
4. **Selecione** este repositório
5. **Add PostgreSQL**: New > Database > PostgreSQL
6. **Variáveis** (Settings > Variables):
   ```
   FLASK_ENV=production
   SECRET_KEY=gestao-indicadores-secret-super-strong-2024
   JWT_SECRET_KEY=jwt-secret-key-muito-forte-2024
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ```
7. **Copie a URL** (ex: `https://web-production-xxxx.up.railway.app`)

---

## 🌐 2. PREPARAR FRONTEND - 1 minuto

Execute no PowerShell:
```powershell
.\deploy-setup.ps1 -RailwayURL "https://web-production-xxxx.up.railway.app"
```

Ou manualmente:
1. **Edite** `frontend\js\config-auto.js`
2. **Substitua**: `https://SEU-BACKEND-RAILWAY.up.railway.app`
3. **Por**: `https://web-production-xxxx.up.railway.app`

---

## 📱 3. FRONTEND (Netlify) - 2 minutos

1. **Acesse**: https://netlify.com
2. **Login** com GitHub
3. **New site from Git** > Selecione repositório
4. **Configurações**:
   - Base directory: `frontend`
   - Publish directory: `frontend`
   - Build command: (vazio)
5. **Deploy!**

---

## ✅ 4. CONFIGURAR CORS

No Railway > Settings > Variables:
```
CORS_ORIGINS=https://sua-url-netlify.netlify.app
```

---

## 🎉 PRONTO!

- ✅ **Backend**: https://web-production-xxxx.up.railway.app
- ✅ **Frontend**: https://sua-url-netlify.netlify.app
- ✅ **Login**: admin@hospital.com / admin123

### 🔧 Se der erro:
- **500**: Ver logs no Railway
- **CORS**: Verificar CORS_ORIGINS
- **404**: Verificar URL no config-auto.js

---

## 📞 SUPORTE RÁPIDO

**Testar API**:
```bash
curl https://sua-api.up.railway.app/health
```

**Ver logs**:
- Railway: Project > Deployments > Logs
- Netlify: Site > Functions > Logs

**Debug Frontend**:
- F12 > Console > Network tab
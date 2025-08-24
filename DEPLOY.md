# 🚀 LaOpen 网球管理系统部署指南

## 📋 快速部署到 Render.com (免费)

### 1️⃣ 准备工作
确保你的代码已推送到GitHub仓库。

### 2️⃣ 在Render.com部署

1. **注册账号**
   - 访问 [render.com](https://render.com)
   - 使用GitHub账号注册/登录

2. **创建Web服务**
   - 点击 "New +" → "Web Service"
   - 连接你的GitHub仓库
   - 选择LaOpen项目仓库

3. **配置服务**
   ```
   Name: laopen-tennis
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```

4. **设置环境变量**
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = `你的密钥` (Render可以自动生成)
   - `PORT` = (Render自动设置)

5. **部署**
   - 点击 "Create Web Service"
   - 等待构建完成（约2-5分钟）
   - 获得类似 `https://laopen-tennis.onrender.com` 的URL

### 3️⃣ 初始化数据
首次部署后需要创建管理员账号：
1. 访问你的网站URL
2. 点击"注册"创建第一个账号
3. 该账号将自动成为管理员

---

## 🔧 其他部署选项

### Railway.app (推荐，简单)
1. 访问 [railway.app](https://railway.app)
2. 连接GitHub仓库
3. 自动检测Python应用并部署
4. 获得 `.railway.app` 域名

### PythonAnywhere (免费tier)
1. 注册 [pythonanywhere.com](https://www.pythonanywhere.com)
2. 上传代码到Web应用目录
3. 配置WSGI文件
4. 获得 `.pythonanywhere.com` 域名

### Heroku (付费，但稳定)
1. 安装Heroku CLI
2. `heroku create laopen-tennis`
3. `git push heroku main`
4. `heroku config:set FLASK_ENV=production`

---

## 🛡️ 生产环境安全配置

### 必须修改的设置：
```python
# 在app.py中已配置从环境变量读取
SECRET_KEY = os.environ.get('SECRET_KEY')  # 使用强密钥
FLASK_ENV = 'production'                   # 关闭调试模式
```

### 推荐的环境变量：
```
SECRET_KEY=your-very-strong-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///instance/laopen.db
```

---

## 📊 数据库选择

### SQLite (默认，适合小规模)
- ✅ 零配置，文件数据库
- ✅ 适合<100并发用户
- ❌ 不支持多服务器

### PostgreSQL (推荐生产环境)
如需升级到PostgreSQL：
1. 在Render添加PostgreSQL服务
2. 更新`requirements.txt`添加`psycopg2-binary`
3. 设置`DATABASE_URL`环境变量

---

## 🔄 自动部署

### GitHub Actions (自动化)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Trigger Render Deploy
        run: curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

### Render Auto-Deploy
Render会自动检测GitHub推送并重新部署。

---

## 📱 域名配置

### 免费域名
- Render: `yourapp.onrender.com`
- Railway: `yourapp.railway.app`
- PythonAnywhere: `yourname.pythonanywhere.com`

### 自定义域名
1. 在Render控制台添加自定义域名
2. 配置DNS CNAME记录指向Render
3. Render自动提供SSL证书

---

## 🚨 故障排查

### 常见问题：
1. **500错误**：检查环境变量和数据库连接
2. **静态文件404**：确保static文件夹已上传
3. **数据库初始化失败**：检查instance目录权限

### 日志查看：
- Render: Dashboard → Logs
- Railway: Dashboard → Deployments
- Heroku: `heroku logs --tail`

---

## 📈 性能优化

### 生产环境建议：
1. 启用Gzip压缩
2. 配置CDN for静态文件
3. 使用缓存策略
4. 监控应用性能

### 扩展建议：
- 使用Redis做缓存
- 配置负载均衡
- 数据库连接池
- 异步任务队列

---

## 💰 成本预估

| 平台 | 免费tier | 付费起价 | 特点 |
|------|----------|----------|------|
| Render | 512MB RAM | $7/月 | 自动SSL |
| Railway | 500小时/月 | $5/月 | 简单易用 |
| PythonAnywhere | 100MB存储 | $5/月 | Python专用 |
| Heroku | - | $7/月 | 企业级 |

---

## ✅ 部署检查清单

- [ ] 代码推送到GitHub
- [ ] requirements.txt包含所有依赖
- [ ] 环境变量配置正确
- [ ] 数据库初始化成功
- [ ] 静态文件加载正常
- [ ] 用户注册登录正常
- [ ] 比赛管理功能正常
- [ ] 移动端界面适配正常
- [ ] SSL证书配置完成

🎉 部署完成后，你的网球管理系统就可以全世界访问了！

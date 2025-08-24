# LaOpen

一个炫酷的像素风格网站项目，具有完整的用户注册登录系统

## 🚀 功能特性

- ⚡ **炫酷像素风格界面**：深色背景配橙色发光效果
- 🔥 **用户注册登录系统**：支持昵称、手机号注册
- 💎 **响应式设计**：完美适配桌面端和移动端
- 🎮 **动态交互效果**：浮动粒子、触摸效果、发光动画
- 🛡️ **安全性保障**：密码加密存储、表单验证

## 📁 项目结构

```
LaOpen/
├── app.py              # Flask 应用工厂
├── auth.py             # 用户认证蓝图
├── main.py             # 主页面蓝图
├── models.py           # 数据库模型
├── forms.py            # 表单定义
├── requirements.txt    # Python 依赖包
├── init_sqlite.py      # SQLite数据库初始化脚本
├── start.sh           # 项目启动脚本
├── templates/         # HTML 模板目录
│   ├── index.html     # 首页模板
│   ├── register.html  # 注册页面
│   ├── login.html     # 登录页面
│   └── dashboard.html # 用户中心
└── static/           # 静态资源目录
    ├── css/          # 样式文件
    └── js/           # JavaScript 文件
```

## 🛠️ 安装和运行

### 1. 环境准备
确保已安装：
- Python 3.7+
- 无需额外数据库服务器！

### 2. 安装依赖
```bash
pip3 install -r requirements.txt
```

### 3. 数据库设置（可选）
```bash
# SQLite会自动创建，也可以手动初始化：
python3 init_sqlite.py
```

### 4. 启动应用
```bash
# 方法一：使用启动脚本
./start.sh

# 方法二：直接启动
python app.py
```

### 5. 访问网站
打开浏览器访问：`http://localhost:5000`

## 🎯 用户系统

### 注册功能
- **昵称**：2-20字符，唯一性验证
- **手机号**：11位手机号，格式验证
- **密码**：6-20字符，bcrypt加密存储

### 登录功能
- 手机号 + 密码登录
- 会话管理
- 登录状态保持

## 🎨 技术栈

- **后端**：Python3 + Flask + SQLAlchemy
- **数据库**：SQLite（零配置）
- **前端**：HTML5 + CSS3 + JavaScript
- **安全**：Flask-Login + bcrypt + WTForms
- **风格**：像素风 + 响应式设计

## 🔧 数据库配置

默认配置位于 `app.py`：
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///laopen.db'
```

SQLite优势：
- ✅ **零配置**：无需安装数据库服务器
- ✅ **单文件存储**：数据存储在 `laopen.db` 文件中
- ✅ **即插即用**：Python内置支持
- ✅ **完整SQL支持**：支持标准SQL语法

## 📱 响应式支持

- **桌面端** (>1024px)：完整功能和动画
- **平板端** (768-1024px)：适度缩减
- **手机端** (<768px)：优化布局和性能

## ⚠️ 注意事项

1. **数据库文件**：SQLite数据存储在 `laopen.db` 文件中
2. **备份重要**：定期备份 `laopen.db` 文件
3. **生产环境**：建议修改 SECRET_KEY
4. **性能考虑**：SQLite适合中小型项目，大型项目可考虑PostgreSQL

## 📚 开发文档

- **README.md** - 项目介绍和快速开始
- **DEVELOPER.md** - 完整的开发者技术指南

## 🎉 开始体验

项目启动后，访问首页即可看到注册和登录按钮，开始你的像素冒险之旅！

想了解更多技术细节？查看 [开发者指南](DEVELOPER.md) 📖

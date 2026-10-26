# 不要再熬夜了

一艘写给夜里的个人博客。首页是驾驶舱，文章是航线，实验室里有一位沿着 LangGraph 走路的档案员。

- 界面：React、TypeScript、Vite
- 档案员：LangGraph 规划 / 检索 / 成稿，LangChain 工具
- 接口：FastAPI

不配置模型钥匙也能用。档案员会沿同一条图检索文章并直接引用。设置 `OPENAI_API_KEY` 之后，成稿改由模型组织，检索这一步仍然先发生。

## 运行

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
./scripts/dev.sh
```

打开 <http://127.0.0.1:5173>。

只跑接口：

```bash
cd backend && ../backend/.venv/bin/uvicorn app.main:app --reload --port 8000
```

构建前端后，同一个接口会顺便托管页面：

```bash
cd frontend && npm run build
cd ../backend && ../backend/.venv/bin/uvicorn app.main:app --port 8000
```

## 页面

- `/` 驾驶舱：主张、状态、三篇精选、作品
- `/essays` 航线，`/essays/:slug` 文章
- `/works` 与 `/works/:slug` 能点开的案例
- `/about` 船的结构
- `/lab` 星图，以及会带回出处的档案员
- `/feed.xml` 订阅

## 管理舱

普通访问始终落在用户界面；前台导航**不放**管理入口。

要改界面内容，直接打开隐式地址：

- 登录：<http://127.0.0.1:5173/admin>（账号密码默认已预填）
- 工作台：登录后进入 `/admin/desk`

默认管理员：`changxy` / `changxy`（可用 `ADMIN_USER`、`ADMIN_PASSWORD`、`ADMIN_SECRET` 覆盖，见 `.env.example`）。

可管理：船名与主张、近况、关于、作品、文章增删改。保存后写入 `backend/content/`，前台刷新即可看到。

可选环境变量见 `.env.example`。

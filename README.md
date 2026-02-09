# 定向调查问卷系统（FastAPI + MySQL + Vue3）

本项目实现定向发放问卷、ID 不明文、中文导入导出（xlsx）与统计分析。

## 目录结构

- `backend/` 后端 FastAPI
- `frontend/` 前端 Vue3（填写端 + 管理后台）

## 后端启动

1. 进入后端目录并安装依赖

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 配置环境变量

```bash
cp .env.example .env
```

按需修改 `DATABASE_URL`、`ADMIN_USER`、`ADMIN_PASSWORD`、`ADMIN_TOKEN`、`PUBLIC_BASE_URL`。

3. 初始化数据库（utf8mb4）

```sql
-- 使用 backend/schema.sql 或手动执行
CREATE DATABASE questionnaire CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

默认地址：`http://localhost:5173`

## 使用流程

1. 访问 `http://localhost:5173/admin/login` 登录后台（默认 admin / admin123）。
2. 新建问卷，填写中文题目与选项，保存。
3. 进入“发放管理”上传 ID Excel（列名固定为 `ID`）。
4. 导出“ID-问卷链接”Excel，将链接分发给用户。
5. 用户访问 `http://localhost:5173/s/:token` 进行填写。
6. 后台查看提交记录与统计，导出答案（含真实 ID）。

## Excel 模板与示例数据

- Excel 模板：`backend/resources/ID导入模板.xlsx`
- 示例问卷脚本：`backend/sample_seed.py`

运行示例数据脚本：

```bash
cd backend
python sample_seed.py
```

## 重要约束说明

- ID 不出现在 URL 参数和前端页面，仅使用高熵 `public_token`。
- MySQL 连接使用 `utf8mb4`，确保中文不乱码。
- Excel 导入导出使用 `openpyxl`，支持中文表头与内容。


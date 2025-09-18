# ChatGLM智能对话系统项目

## 安装指南
### 1. 安装 Redis 数据库
```bash
更新软件包列表
sudo apt update
安装 Redis 服务器
sudo apt install redis-server
启动 Redis 服务
sudo service redis-server start
检查 Redis 运行状态
sudo systemctl status redis-server
```
### 2. 创建 Python 虚拟环境
```bash
创建名为 chatglm 的虚拟环境 (Python 3.10)
conda create -n chatglm python=3.10
激活虚拟环境
conda activate chatglm
```
### 3. 安装 Python 依赖库
```bash
升级 pip
pip install -U pip
安装项目依赖
pip install redis transfer flask bcrypt
```
> **注意**：`socket`, `threading` 和 `json` 是 Python 标准库，无需单独安装
## 运行指南
### 启动顺序
1. 确保 Redis 服务正在运行：
bash
sudo service redis-server status
2. 启动后端服务：
bash
cd 后端（仅数据库）/
python server.py
3. 启动前端应用：
bash
cd 前端/
python main.py
4. 访问前端终端显示的 URL (通常是 `http://127.0.0.1:5000`)
### 重要提示
- Redis 数据库必须保持运行状态
- 严格遵循启动顺序：先启动后端，再启动前端
- 首次运行时可能需要初始化数据库（根据具体实现）
## 系统功能
- 用户认证（登录/注册）
- 实时对话交互
- 聊天记录管理
- 敏感词过滤系统
- 情感词汇增强
- 管理员控制面板
## 故障排除
如果遇到连接问题：
1. 检查 Redis 服务状态：`sudo systemctl status redis-server`
2. 确认后端服务已正常运行
3. 检查防火墙设置是否阻止了端口访问
4. 查看日志文件获取详细错误信息

如需技术支持，请联系项目维护人员。

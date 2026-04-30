#!/bin/bash
# ==============================================
# ERP系统 Git一键安装脚本
# 适用于 Ubuntu 桌面版服务器
# 使用方式: sudo bash install_from_git.sh
# ==============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置参数
PROJECT_NAME="erp_thirteen"
PROJECT_DIR="/opt/$PROJECT_NAME"
BACKEND_DIR="$PROJECT_DIR/tp_education_system/backend"
FRONTEND_DIR="$PROJECT_DIR/tp_education_system/frontend"
VENV_DIR="$BACKEND_DIR/venv"
BACKEND_PORT=8000
GIT_REPO="https://github.com/your-repo/erp_thirteen.git"  # 替换为您的Git仓库地址

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}  ERP系统 Git一键安装脚本${NC}"
echo -e "${YELLOW}==============================================${NC}"

# 检查是否以root用户运行
if [ "$(id -u)" != "0" ]; then
    echo -e "${RED}错误：请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 安装系统依赖
echo -e "\n${GREEN}[1/8] 安装系统依赖...${NC}"
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx git nodejs npm

# 克隆代码仓库
echo -e "\n${GREEN}[2/8] 克隆代码仓库...${NC}"
rm -rf $PROJECT_DIR
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR
git clone $GIT_REPO .

# 检查是否克隆成功
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}错误：无法克隆仓库，请检查Git仓库地址是否正确${NC}"
    exit 1
fi

# 安装后端依赖
echo -e "\n${GREEN}[3/8] 安装后端依赖...${NC}"
cd $BACKEND_DIR
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip

# 安装requirements中的依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 安装必要的额外依赖
pip install fastapi uvicorn openpyxl python-multipart
deactivate

# 构建前端
echo -e "\n${GREEN}[4/8] 构建前端...${NC}"
cd $FRONTEND_DIR

# 安装前端依赖
npm install --legacy-peer-deps

# 构建生产版本
npm run build

# 检查构建是否成功
if [ ! -d "dist" ]; then
    echo -e "${RED}错误：前端构建失败${NC}"
    exit 1
fi

# 配置Nginx
echo -e "\n${GREEN}[5/8] 配置Nginx...${NC}"

# 删除旧配置
rm -f /etc/nginx/sites-enabled/erp.conf
rm -f /etc/nginx/sites-available/erp.conf

# 创建Nginx配置文件
cat > /etc/nginx/sites-available/erp.conf <<EOF
server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        root $FRONTEND_DIR/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:$BACKEND_PORT/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# 启用Nginx配置
ln -sf /etc/nginx/sites-available/erp.conf /etc/nginx/sites-enabled/

# 测试Nginx配置
if ! nginx -t; then
    echo -e "${RED}错误：Nginx配置错误${NC}"
    exit 1
fi

# 重启Nginx
systemctl reload nginx

# 创建systemd服务
echo -e "\n${GREEN}[6/8] 创建系统服务...${NC}"

# 删除旧服务
rm -f /etc/systemd/system/erp-backend.service

cat > /etc/systemd/system/erp-backend.service <<EOF
[Unit]
Description=ERP Backend Service
After=network.target nginx.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=$BACKEND_DIR
ExecStart=$VENV_DIR/bin/python -m uvicorn main:app --host 127.0.0.1 --port $BACKEND_PORT --workers 2
Restart=always
RestartSec=5
Environment=PYTHONPATH=$BACKEND_DIR

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
systemctl daemon-reload

# 设置文件权限
echo -e "\n${GREEN}[7/8] 设置文件权限...${NC}"
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR

# 配置防火墙
echo -e "\n${GREEN}[8/8] 配置防火墙...${NC}"
ufw allow 'Nginx Full' > /dev/null 2>&1 || true
ufw allow ssh > /dev/null 2>&1 || true
ufw --force enable > /dev/null 2>&1 || true

# 启动服务
echo -e "\n${GREEN}启动后端服务...${NC}"
systemctl enable erp-backend
systemctl restart erp-backend

# 等待服务启动
sleep 3

# 检查服务状态
echo -e "\n${GREEN}检查服务状态...${NC}"
if systemctl is-active --quiet erp-backend; then
    echo -e "${GREEN}后端服务启动成功${NC}"
else
    echo -e "${RED}错误：后端服务启动失败${NC}"
    echo "请检查日志: journalctl -u erp-backend -f"
    exit 1
fi

echo -e "\n${GREEN}==============================================${NC}"
echo -e "${GREEN}  安装完成！${NC}"
echo -e "${GREEN}==============================================${NC}"
echo -e "\n${YELLOW}访问地址:${NC} http://localhost"
echo -e "${YELLOW}后端API:${NC} http://localhost:$BACKEND_PORT/api"
echo -e "\n${YELLOW}服务管理命令:${NC}"
echo -e "  启动:    sudo systemctl start erp-backend"
echo -e "  停止:    sudo systemctl stop erp-backend"
echo -e "  重启:    sudo systemctl restart erp-backend"
echo -e "  状态:    sudo systemctl status erp-backend"
echo -e "  日志:    journalctl -u erp-backend -f"
echo -e "\n${YELLOW}更新命令:${NC}"
echo -e "  sudo bash install_from_git.sh  (重新安装并更新到最新版本)"
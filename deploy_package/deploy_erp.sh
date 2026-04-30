#!/bin/bash
# ==============================================
# ERP系统一键部署脚本
# 适用于 Ubuntu 桌面版服务器
# 使用方式: sudo bash deploy_erp.sh
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
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"
BACKEND_PORT=8000
DOMAIN="erp.local"

echo -e "${YELLOW}==============================================${NC}"
echo -e "${YELLOW}  ERP系统一键部署脚本${NC}"
echo -e "${YELLOW}==============================================${NC}"

# 检查是否以root用户运行
if [ "$(id -u)" != "0" ]; then
    echo -e "${RED}错误：请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 安装系统依赖
echo -e "\n${GREEN}[1/6] 安装系统依赖...${NC}"
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx git nodejs npm

# 创建项目目录
echo -e "\n${GREEN}[2/6] 创建项目目录...${NC}"
mkdir -p $PROJECT_DIR

# 复制项目文件到服务器
echo -e "\n${GREEN}[3/6] 复制项目文件...${NC}"
cp -r /host_machine/tp_education_system/* $PROJECT_DIR/

# 安装后端依赖
echo -e "\n${GREEN}[4/6] 安装后端依赖...${NC}"
cd $BACKEND_DIR
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi uvicorn openpyxl
deactivate

# 构建前端
echo -e "\n${GREEN}[5/6] 构建前端...${NC}"
cd $FRONTEND_DIR
npm install
npm run build

# 配置Nginx
echo -e "\n${GREEN}[6/6] 配置Nginx...${NC}"

# 创建Nginx配置文件
cat > /etc/nginx/sites-available/erp.conf <<EOF
server {
    listen 80;
    server_name $DOMAIN localhost;

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
    }
}
EOF

# 启用Nginx配置
ln -sf /etc/nginx/sites-available/erp.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 创建systemd服务
cat > /etc/systemd/system/erp-backend.service <<EOF
[Unit]
Description=ERP Backend Service
After=network.target

[Service]
User=www-data
WorkingDirectory=$BACKEND_DIR
ExecStart=$VENV_DIR/bin/python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
systemctl daemon-reload
systemctl enable erp-backend
systemctl start erp-backend

# 配置防火墙
echo -e "\n${GREEN}[7/7] 配置防火墙...${NC}"
ufw allow 'Nginx Full'
ufw allow ssh
ufw --force enable

echo -e "\n${GREEN}==============================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}==============================================${NC}"
echo -e "\n${YELLOW}访问地址:${NC} http://localhost"
echo -e "${YELLOW}后端API:${NC} http://localhost:$BACKEND_PORT/api"
echo -e "${YELLOW}服务管理:${NC}"
echo -e "  启动: sudo systemctl start erp-backend"
echo -e "  停止: sudo systemctl stop erp-backend"
echo -e "  状态: sudo systemctl status erp-backend"
echo -e "  日志: journalctl -u erp-backend -f"
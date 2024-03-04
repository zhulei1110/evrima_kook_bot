# evrima_kook_bot

## ubuntu 部署

### 1、安装 python3-venv
sudo apt-get update  
sudo apt-get install python3-venv

### 2、clone 仓库到服务器
git clone https://github.com/zhulei1991/evrima_kook_bot.git  
cd evrima_kook_bot

### 3、创建虚拟环境
python3 -m venv venv

### 4、激活虚拟环境
source venv/bin/activate

### 5、安装项目依赖包
pip install -r requirements.txt

### 6、退出虚拟环境
deactivate

## 创建系统服务

### 1、创建 evrima_kook_bot.service 文件
sudo vi /etc/systemd/system/evrima_kook_bot.service

#### 文件内容如下：
  
[Unit]  
Description=Evrima KOOK Bot  
After=network.target  
StartLimitIntervalSec=0  
  
[Service]  
Type=simple  
Restart=always  
RestartSec=1  
User=ziyu0209  
WorkingDirectory=/home/USER_NAME/evrima_kook_bot  
ExecStart=/usr/bin/python3 /home/USER_NAME/evrima_kook_bot/main.py  
Environment=PYTHONPATH=/home/USER_NAME/evrima_kook_bot/venv/lib/python3.10/site-packages  
  
[Install]  
WantedBy=multi-user.target  

#### 保存并退出

### 2、重新加载 systemd 守护进程
sudo systemctl daemon-reload  

### 3、设置开机自动启动
systemctl enable evrima_kook_bot.service  

### 4、启动服务，查看状态
systemctl start evrima_kook_bot.service  
systemctl status evrima_kook_bot.service  

### 5、查看日志  
journalctl -u evrima_kook_bot.service  
或者  
vi evrima_kook_bot/logs/evrima_kook_bot.log  

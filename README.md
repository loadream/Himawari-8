# Himawari-8
爬取向日葵8号的卫星图像合并

python脚本，可以爬取向日葵8号的卫星图像4d版，并合并成一张整图，分辨率为2200*2200

新建 /home/Earth 和 /home/Earth/himawari 目录

# 安装所需的 Python 库
sudo apt update

sudo apt install python3-pip

pip3 install requests Pillow schedule


可以使用 python3 himawari8.py 手动运行下载一次

也可以使用 */15 * * * * python3 /home/Earth/himawari.py >> /home/Earth/himawari.log 2>&1 之类的定时任务，设置每隔一段时间自动下载一张最新的

index.php 和 api.php 是一个简单的展示和输出最新的图像url的工具

简易的预览效果

https://earth.loadream.com/

https://earth.loadream.com/api.php

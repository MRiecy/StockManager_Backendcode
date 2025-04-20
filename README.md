# 创建 PyThon3.8 虚拟环境

conda create --name myprojectenv python=3.8
conda activate myprojectenv

# 安装 Django

pip install django

# 安装其他依赖

pip install xtquant pymongo djangorestframework django-cors-headers djangorestframework-simplejwt

# 启动 Django 项目

python manage.py runserver

from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Comparison'


# myapp/apps.py
from django.apps import AppConfig
import threading
from xtquant import xtdatacenter as xtdc
from xtquant import xtdata
import time

class MyAppConfig(AppConfig):
    name = 'Comparison'

    def ready(self):
        # 定义初始化 xtdatacenter 的函数
        def init_xtdatacenter():
            # 设置 token
            xtdc.set_token('6a9f346cbeb93be0165122d9a2da5872c7c25963')
            # 设置连接池地址
            addr_list = [
                '115.231.218.73:55310',
                '115.231.218.79:55310',
                '218.16.123.11:55310',
                '218.16.123.27:55310'
            ]
            xtdc.set_allow_optmize_address(addr_list)
            # 初始化（参数根据需要调整）
            xtdc.init(False)
            port = 58601
            xtdc.listen(port=port)
            print(f"服务启动,开放端口：{port}")
            print('-----连接上了------')
            print(xtdata.data_dir)
            servers = xtdata.get_quote_server_status()
            for k, v in servers.items():
                print(k, v)
            # 运行 xtdata.run()，可能是阻塞调用
            xtdata.run()

        # 通过线程启动初始化过程，防止阻塞主进程
        thread = threading.Thread(target=init_xtdatacenter, daemon=True)
        thread.start()

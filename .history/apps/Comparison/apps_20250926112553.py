from django.apps import AppConfig
import threading
from xtquant import xtdatacenter as xtdc
from xtquant import xtdata
import time
from django.conf import settings

class ComparisonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Comparison'

    def ready(self):
        # 定义初始化 xtdatacenter 的函数
        def init_xtdatacenter():
            # 设置 token - 使用统一配置
            xtdc.set_token(settings.XT_CONFIG['TOKEN'])
            # 设置连接池地址 - 使用统一配置
            xtdc.set_allow_optmize_address(settings.XT_CONFIG['ADDR_LIST'])
            # 初始化（参数根据需要调整）
            xtdc.init(False)
            port = settings.XT_CONFIG['PORT']
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

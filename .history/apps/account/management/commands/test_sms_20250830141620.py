"""
测试短信服务的Django管理命令
使用方法: python manage.py test_sms <phone_number>
"""
from django.core.management.base import BaseCommand, CommandError
from account.sms_service import send_verification_code, get_sms_provider_info, get_sms_balance


class Command(BaseCommand):
    help = '测试短信服务是否正常工作'
    
    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help='要发送测试短信的手机号')
        parser.add_argument(
            '--code',
            type=str,
            default='123456',
            help='要发送的验证码（默认: 123456）'
        )
        parser.add_argument(
            '--provider',
            type=str,
            choices=['aliyun', 'tencent', 'mock'],
            help='指定短信服务提供商'
        )
    
    def handle(self, *args, **options):
        phone = options['phone']
        code = options['code']
        provider = options.get('provider')
        
        self.stdout.write(f"🚀 开始测试短信服务...")
        self.stdout.write(f"📱 手机号: {phone}")
        self.stdout.write(f"🔢 验证码: {code}")
        
        # 显示当前短信服务配置
        self.stdout.write("\n📋 当前短信服务配置:")
        provider_info = get_sms_provider_info()
        for key, value in provider_info.items():
            self.stdout.write(f"  {key}: {value}")
        
        # 如果指定了提供商，显示相关信息
        if provider:
            self.stdout.write(f"\n🎯 指定使用: {provider}")
        
        # 测试发送短信
        self.stdout.write(f"\n📤 正在发送测试短信...")
        try:
            success, message = send_verification_code(phone, code)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ 短信发送成功: {message}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ 短信发送失败: {message}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"💥 发送过程中出现异常: {str(e)}")
            )
        
        # 显示余额信息
        self.stdout.write(f"\n💰 账户余额信息:")
        balance = get_sms_balance()
        if balance is not None:
            self.stdout.write(f"  余额: {balance}")
        else:
            self.stdout.write("  余额: 无法获取（该服务商可能不支持余额查询）")
        
        self.stdout.write(f"\n🎉 短信服务测试完成！")
        
        # 提供使用建议
        if provider_info['provider'] == 'mock':
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  当前使用模拟短信服务，生产环境请配置真实的短信服务！"
                )
            )
            self.stdout.write(
                "💡 配置方法：\n"
                "  1. 复制 env_example.txt 为 .env\n"
                "  2. 填入真实的短信服务配置\n"
                "  3. 设置 SMS_PROVIDER=aliyun 或 tencent"
            ) 
from django.db import models
from django.utils import timezone

# Create your models here.

class CacheIndex(models.Model):
    """缓存索引模型，用于管理Parquet文件的元数据"""
    symbol = models.CharField(max_length=20, verbose_name="股票代码")  # 股票代码，如 "600519.SH"
    period = models.CharField(max_length=10, verbose_name="周期")  # 周期，如 "1m", "5m", "1d"
    start_date = models.DateField(verbose_name="起始日期")  # 缓存数据的起始日期
    end_date = models.DateField(verbose_name="结束日期")  # 缓存数据的结束日期
    file_path = models.CharField(max_length=255, verbose_name="文件路径")  # Parquet文件的绝对路径
    last_access = models.DateTimeField(default=timezone.now, verbose_name="最后访问时间")  # 最后访问时间，用于LRU
    size_bytes = models.BigIntegerField(verbose_name="文件大小")  # 文件大小（字节）
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "缓存索引"
        verbose_name_plural = "缓存索引"
        # 确保同一个股票代码和周期的数据不重复
        unique_together = ['symbol', 'period', 'start_date', 'end_date']
        indexes = [
            models.Index(fields=['symbol', 'period']),
            models.Index(fields=['last_access']),  # 用于LRU查询
            models.Index(fields=['start_date', 'end_date']),  # 用于时间范围查询
        ]

    def __str__(self):
        return f"{self.symbol}_{self.period}_{self.start_date}_{self.end_date}"

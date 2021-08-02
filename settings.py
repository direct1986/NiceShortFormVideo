# -*- encoding: utf-8 -*-

"""
------------------------------------------
@File       : settings.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@CreatedOn  : 2021/6/6 22:55
------------------------------------------
"""
from os.path import dirname, join as path_join


class BaseConfig:
    # 该文件所在的目录的绝对路径
    base_dir = dirname(__file__)

    # ======================[ 数据库相关设置 ]======================
    # ORM格式的数据库地址
    # db_uri = f"sqlite:///{base_dir}/kuaidou.db"
    db_uri = f"mysql+pymysql://spider:Spider666123~@192.168.3.2/videos?charset=utf8"

    # 连接池大小
    pool_size = 5

    # 超过连接池的大小外最多创建的连接
    max_overflow = 10

    # 池中没有线程最多等待的时间，否则报错
    pool_timeout = -1

    # 多久后对线程池中的线程进行一次连接的回收(重置)
    pool_recycle = -1
    # ===========================[ end ]===========================

    # 日志配置
    log = {
        "log_dir": path_join(base_dir, "logs"),
        "filename": "belles_short_video.log"
    }

    # 视频文件保存位置
    videos_dir = path_join(base_dir, "videos")

    # 下载的视频地址
    urls = [
        "https://sp.nico.run/video.php",
        "http://www.kuaidoushe.com/video.php",
        "https://tvv.tw/xjj/kuaishou/video.php",
        "https://xjj.349457.xyz/video.php",
        "http://wmsp.cc/video.php",  # 这个反爬虫，设置(2, 4)秒的随机sleep可解除
        "http://dou.plus/get/get1.php",  # 这个也只能下载一些
        "http://dou.plus/get/get2.php",  # 这个也只能下载一些
    ]

    # 备选的下载地址，这些下载地址或多或少有一些限制
    urls2 = [
        "http://dou.plus/get/get1.php",  # 这个也只能下载一些
        "http://wmsp.cc/video.php"  # 这个反爬虫，设置(2, 4)秒的随机sleep可解除
    ]

    # # 线程相关设置
    parser_worker = 20  # 解析线程数
    check_worker = 10  # 验证线程数
    save_worker = 10  # 下载线程数

    parser_delay = 5  # 解析线程的延迟时间，防止反爬虫, 单位:秒

    # 下载视频的个数，由于可能在不同网站下载到相同的视频，又由于所下载的视频可能之前已经下载过，所以，实际保存的视频数 ≤ 下载的视频个数
    # tips: 每一个的视频下载是随机从urls中的一个去下载
    download_number = 10000


cfg = BaseConfig

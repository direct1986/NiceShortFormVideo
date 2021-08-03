# NiceShortFormVideo

下载好看的跳舞短视频，视频源于网络。多任务版

#### 使用说明

+ 电脑上安装 `Python3.6`及以上版本
+ `CD`到项目根目录内，运行`pip install -r requirements.txt`安装所需库
+ 本程序需要用到数据库，请在`settings.py`中配置自己的数据库`ORM`连接信息
  + 为了简便，可以使用在`uri`注释中写的`sqlite`数据库，该数据库轻便，无需安装数据库软件,`Python`内置`sqlite`包
+ 首次运行需运行`python init.py`进行初始化
+ 运行命令`python run.py`即可自动下载

#### *Tips*

+ 程序默认使用sqlite数据库，如需变更请在配置文件(`settings.py`)中修改
+ 其它相关设置，在`settings.py`中均有注释，简单易懂

---
The end.
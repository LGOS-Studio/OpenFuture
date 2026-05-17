 OpenFuture 开发者指南

# OpenFuture 模拟操作系统

本项目构建了一个名为 **OpenFuture** 的 Python 模拟操作系统。系统文件保存在 `/rootfs` 目录下，包含 `boot`、`system`、`vendor` 三个必要分区。

## 目录结构

+   `rootfs/boot` - 引导分区
+   `rootfs/system` - 系统分区
+   `rootfs/vendor` - 供应商分区
+   `openfuture/` - Python 模块实现
+   `run.py` - 运行示例
+   `README.html` - 本文档

## 快速开始

```
python run.py
```

这个脚本会初始化 rootfs，添加示例驱动与服务，并输出当前引导信息与分区状态。

## 交互式操作

运行 `python run.py` 将进入一个交互式 shell，支持以下示例命令：

```
partitions
inspect boot
list_services
list_drivers
set_boot bootargs ["root=/dev/rootfs","console=tty0"]
install_driver mydriver {"version":"1.0","status":"enabled"}
install_module mymodule {"version":"0.1"}
deploy_service mysvc {"startup":"automatic"}
sync
exit
```

## 文件管理

新增一组文件操作命令，在交互式 shell 中可直接操作 `rootfs`：

+   `ls [path]` - 列出目录内容
+   `md | mkdir <path>` - 创建目录
+   `chmod <mode> <path>` - 修改文件/目录模式（如 755）
+   `files` - 启动交互式文件资源管理器（支持 `ls`/ `cd`/ `cat`/ `rm`/ `mkdir` 等）

示例：

```
python run.py
OpenFuture> ls rootfs
OpenFuture> md rootfs/newdir
OpenFuture> chmod 755 rootfs/newdir
OpenFuture> files
files:/$ ls
files:/$ mkdir test
files:/$ cat README.html
```

## 核心 API

主要类：

+   `openfuture.OpenFutureOS`
+   `openfuture.BootManager`
+   `openfuture.SystemPartition`
+   `openfuture.VendorPartition`
+   `openfuture.FileSystemEmulator`
+   `openfuture.OpenFutureInterface`

### 示例用法

```
from openfuture import OpenFutureOS

os_sim = OpenFutureOS()
os_sim.initialize()
os_sim.set_boot_option("bootargs", ["root=/dev/rootfs", "console=tty0"])
os_sim.install_vendor_module("openfuture-audio", {"version": "0.1", "status": "enabled"})
os_sim.load_system_service("metrics", {"startup": "automatic", "description": "Collect runtime metrics."})
print(os_sim.boot_sequence())
print(os_sim.summary())
```

## 可修改接口

你可以通过以下接口定制系统：

+   `os_sim.set_boot_option(key, value)` - 配置引导选项
+   `os_sim.install_vendor_module(name, data)` - 安装供应商模块
+   `os_sim.load_system_service(name, spec)` - 部署系统服务
+   `os_sim.system.set_property(key, value)` - 修改系统属性
+   `os_sim.vendor.install_driver(name, spec)` - 安装硬件驱动
+   `os_sim.interface.register_hook(event, callback)` - 注册开发者回调

## 分区浏览

可以读取分区元数据，查看实时状态：

```
print(os_sim.inspect_partition("boot"))
print(os_sim.system.list_services())
print(os_sim.vendor.list_drivers())
```

## 开发建议

你可以基于现有模块继续扩展：

+   为 `rootfs/boot` 增加引导脚本
+   为 `rootfs/system` 添加更多系统属性与配置文件
+   为 `rootfs/vendor` 添加实际驱动描述和硬件模型
+   在 `openfuture/interface.py` 中扩展插件事件

OpenFuture 模拟操作系统 由 Python 实现，适合用于概念验证和开发实验。

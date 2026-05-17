from .core import OpenFutureOS


def main() -> None:
    os_sim = OpenFutureOS()
    os_sim.initialize()
    print("[OpenFuture] 初始化完成。默认系统已经准备就绪。")
    print(os_sim.boot_sequence())
    print("[OpenFuture] 当前分区状态：")
    print(os_sim.summary())


if __name__ == "__main__":
    main()

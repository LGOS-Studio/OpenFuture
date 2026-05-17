from openfuture import OpenFutureOS
from openfuture.cli import OpenFutureShell


def main() -> None:
    os_sim = OpenFutureOS()
    os_sim.initialize()

    # 启动交互式 shell，让用户以命令形式操作伪操作系统
    shell = OpenFutureShell(os_sim)
    shell.start()


if __name__ == "__main__":
    main()

# encoding:utf-8

import signal
import sys

from channel import channel_factory
from config import load_config
from plugins import *
from channel.wechatnt.linkMysql import link_db


def sigterm_handler_wrap(_signo):
    old_handler = signal.getsignal(_signo)

    def func(_signo, _stack_frame):
        """
        处理信号并保存用户数据。
        Args:
            _signo (int): 接收到的信号编号。
            _stack_frame (object): 当前堆栈帧。
        Returns:
            None.
        """
        logger.info("signal {} received, exiting...".format(_signo))
        conf().save_user_datas()
        if callable(old_handler):  # check old_handler
            return old_handler(_signo, _stack_frame)
        sys.exit(0)

    signal.signal(_signo, func)

def run():
    try:
        # load config
        load_config()
        # ctrl + c
        sigterm_handler_wrap(signal.SIGINT)
        # kill signal
        sigterm_handler_wrap(signal.SIGTERM)

        # create channel
        channel_name = conf().get("channel_type", "ntchat")
        if conf().get("wechat_link_db"):
            config={
                'user': conf().get("db_user"),
                'password': conf().get("db_password"),
                'host': conf().get("db_host"),
                'port': conf().get("db_port"),
                'database': conf().get("db_name"),
            }
            link_db(config)


        if "--cmd" in sys.argv:
            channel_name = "terminal"
        logger.debug("********************app.py的run（）")
        channel = channel_factory.create_channel(channel_name)
        # if channel_name in ["ntchat", "wework", "weworktop"]:
        #     PluginManager().load_plugins()
        # startup channel
        channel.startup()
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)


if __name__ == "__main__":
    run()

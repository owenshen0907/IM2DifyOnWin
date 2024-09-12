import mysql.connector
from mysql.connector import errorcode

from common.log import logger


# 连接到MySQL服务器
def link_db(config):
    connect_config = {
        'user': config['user'],
        'password': config['password'],
        'host': config['host'],
        'port': config['port']
    }
    conn = mysql.connector.connect(**connect_config)
    cursor = conn.cursor()
    dbname = config['database']
    # 检查并创建数据库
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname}")
        logger.debug(f"Database '{dbname}' created successfully or already exists.")
    except mysql.connector.Error as err:
        logger.debug(f"Failed creating database: {err}")
        cursor.close()
        conn.close()
        exit(1)

    #选择数据库
    cursor.execute(f"USE {dbname}")

    # 定义表结构的SQL语句
    private_chat_table = """
    CREATE TABLE IF NOT EXISTS private_chat (
        msgid VARCHAR(100)  PRIMARY KEY,
        host_wx_id VARCHAR(50) NOT NULL,
        host_wx_name VARCHAR(100),
        sender_id VARCHAR(50) NOT NULL,
        sender_name VARCHAR(100),
        sender_remark VARCHAR(100),
        msg_type VARCHAR(20),
        msg_content TEXT,
        img_path VARCHAR(255),
        attachment_path VARCHAR(255),
        link_url VARCHAR(1000),
        record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        replay2msgid VARCHAR(255),
        ext_field1 VARCHAR(255),
        ext_field2 VARCHAR(255)
    );
    """

    group_chat_table = """
    CREATE TABLE IF NOT EXISTS group_chat (
        msgid VARCHAR(100) PRIMARY KEY,
        host_wx_id VARCHAR(50) NOT NULL,
        host_wx_name VARCHAR(100),
        group_id VARCHAR(50) NOT NULL,
        group_name VARCHAR(100),
        group_alias VARCHAR(100),
        sender_id VARCHAR(50) NOT NULL,
        sender_name VARCHAR(100),
        sender_group_name VARCHAR(100),
        msg_type VARCHAR(20),
        msg_content TEXT,
        img_path VARCHAR(255),
        attachment_path VARCHAR(255),
        link_url VARCHAR(1000),
        record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        replay2msgid VARCHAR(255),
        ext_field1 VARCHAR(255),
        ext_field2 VARCHAR(255)
    );
    """

    #创建表
    try:
        cursor.execute(private_chat_table)
        cursor.execute(group_chat_table)
        logger.debug("Tables are created successfully or already exist.")
    except mysql.connector.Error as err:
        logger.debug(err)
    finally:
        cursor.close()
        conn.close()
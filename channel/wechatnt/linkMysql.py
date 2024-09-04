import mysql.connector
from mysql.connector import errorcode

# 数据库连接配置
config = {
    'user': 'root',
    'password': 'root',
    'host': 'IP-ADDRESS',
    # 'database': 'chat_record'
}


# 连接到MySQL服务器
conn = mysql.connector.connect(**config)
cursor = conn.cursor()
dbname = "chat_record0904"
# 检查并创建数据库
try:
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname}")
    print(f"Database '{dbname}' created successfully or already exists.")
except mysql.connector.Error as err:
    print(f"Failed creating database: {err}")
    cursor.close()
    conn.close()
    exit(1)

# 选择数据库
cursor.execute(f"USE {dbname}")

# 定义表结构的SQL语句
private_chat_table = """
CREATE TABLE IF NOT EXISTS private_chat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    host_wx_id VARCHAR(50) NOT NULL,
    host_wx_name VARCHAR(100),
    sender_id VARCHAR(50) NOT NULL,
    sender_name VARCHAR(100),
    sender_remark VARCHAR(100),
    msg_type VARCHAR(20),
    msg_content TEXT,
    img_path VARCHAR(255),
    attachment_path VARCHAR(255),
    link_url VARCHAR(255),
    record_time DATETIME NOT NULL,
    ext_field1 VARCHAR(255),
    ext_field2 VARCHAR(255)
);
"""

group_chat_table = """
CREATE TABLE IF NOT EXISTS group_chat (
    id INT AUTO_INCREMENT PRIMARY KEY,
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
    link_url VARCHAR(255),
    record_time DATETIME NOT NULL,
    ext_field1 VARCHAR(255),
    ext_field2 VARCHAR(255)
);
"""

# 创建表
try:
    cursor.execute(private_chat_table)
    cursor.execute(group_chat_table)
    print("Tables are created successfully or already exist.")
except mysql.connector.Error as err:
    print(err)
finally:
    cursor.close()
    conn.close()
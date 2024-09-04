import mysql.connector
from mysql.connector import errorcode

# 数据库连接配置
config = {
    'user': 'root',
    'password': 'root',
    'host': 'IP-ADDRESS',
    'database': 'chat_record'
}

# 创建数据库连接（持久连接）
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

def insert_into_private_chat(data):
    try:
        add_private_chat = (
            "INSERT INTO private_chat "
            "(host_wx_id, host_wx_name, sender_id, sender_name, sender_remark, msg_type, msg_content, img_path, attachment_path, link_url, record_time, ext_field1, ext_field2) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(add_private_chat, data)
        conn.commit()
        print("Data inserted into private_chat successfully.")
    except mysql.connector.Error as err:
        print(f"Failed to insert data into private_chat: {err}")

def insert_into_group_chat(data):
    try:
        add_group_chat = (
            "INSERT INTO group_chat "
            "(group_id, group_name, group_alias, sender_id, sender_name, sender_group_name, msg_type, msg_content, img_path, attachment_path, link_url, record_time, ext_field1, ext_field2) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        cursor.execute(add_group_chat, data)
        conn.commit()
        print("Data inserted into group_chat successfully.")
    except mysql.connector.Error as err:
        print(f"Failed to insert data into group_chat: {err}")

# 示例数据插入
private_chat_data = (
    'wxid_host123', 'Host Name', 'wxid_sender456', 'Sender Name', 'Remark', 'text',
    'Hello, this is a private message.', '/path/to/image.jpg', '/path/to/attachment.pdf', 'http://example.com',
    '2024-09-04 10:00:00', 'Extension 1', 'Extension 2'
)

group_chat_data = (
    'group123', 'Group Name', 'Group Alias', 'wxid_sender789', 'Sender Name', 'Sender Group Name', 'text',
    'Hello, this is a group message.', '/path/to/group_image.jpg', '/path/to/group_attachment.pdf', 'http://example.com/group',
    '2024-09-04 10:05:00', 'Extension 1', 'Extension 2'
)

# 执行插入操作
insert_into_private_chat(private_chat_data)
insert_into_group_chat(group_chat_data)

# 所有操作完成后关闭连接
cursor.close()
conn.close()
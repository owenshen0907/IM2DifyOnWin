import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
from common.log import logger


# 操作数据库
def operateMysql (config,chatinfo):
    # 创建数据库连接（持久连接）
    connect_config = {
        'user': config['user'],
        'password': config['password'],
        'host': config['host'],
        'port': config['port']
    }
    conn = mysql.connector.connect(**connect_config)
    cursor = conn.cursor()
    # 选择数据库
    cursor.execute(f"USE {config['database']}")

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
    # print(chatinfo)
    record_time = datetime.utcfromtimestamp(chatinfo['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    private_chat_data = (
        chatinfo['to_id'],chatinfo['to_nick'],chatinfo['from_id'], chatinfo['from_nick'], '发生人的备注', chatinfo['msg_type'],
        chatinfo['msg'], '/path/to/image.jpg', '/path/to/attachment.pdf', 'http://example.com',
        record_time, 'Extension 1', 'Extension 2'
    )

    group_chat_data = (
        chatinfo['group_id'], chatinfo['group_name'], 'Group Alias', chatinfo['from_id'], chatinfo['from_nick'], '发生人的备注', chatinfo['msg_type'],
        chatinfo['msg'], '/path/to/group_image.jpg', '/path/to/group_attachment.pdf',
        'http://example.com/group',record_time, chatinfo['to_id'], chatinfo['to_nick']
    )

    # 执行插入操作
    try:
        if chatinfo['isgroup']:
            insert_into_group_chat(group_chat_data)
            # logger.debug(f"已插入群聊信息:{group_chat_data}")
        else:
            insert_into_private_chat(private_chat_data)
            # logger.debug(f"已插入私聊信息:{private_chat_data}")
    except Exception as e:
        logger.error(e)

    # 所有操作完成后关闭连接
    cursor.close()
    conn.close()




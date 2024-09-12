import mysql.connector
# from lxml.xmlerror import log_handler
from mysql.connector import errorcode
from datetime import datetime, timedelta
from common.log import logger
from lxml import etree
from config import load_config, conf


def get_dbconfig():
    load_config()
    connect_config = {
        'user': conf().get("db_user"),
        'password': conf().get("db_password"),
        'host': conf().get("db_host"),
        'port': conf().get("db_port"),
        'database': conf().get("db_name"),
    }
    return connect_config
# 操作数据库
def operateMysql (chatinfo):
    # 创建数据库连接（持久连接）
    connect_config = get_dbconfig()
    conn = mysql.connector.connect(**connect_config)
    cursor = conn.cursor()
    # 选择数据库
    # cursor.execute(f"USE {connect_config['database']}")

    def insert_into_private_chat(data):
        try:
            add_private_chat = (
                "INSERT INTO private_chat "
                "(msgid,host_wx_id, host_wx_name, sender_id, sender_name, sender_remark, msg_type, msg_content, img_path, attachment_path, link_url, record_time,replay2msgid, ext_field1, ext_field2) "
                "VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
            )
            cursor.execute(add_private_chat, data)
            conn.commit()
            logger.info("Data inserted into private_chat successfully.")
        except mysql.connector.Error as err:
            logger.info(f"Failed to insert data into private_chat: {err}")

    def insert_into_group_chat(data):
        try:
            add_group_chat = (
                "INSERT INTO group_chat "
                "(msgid,host_wx_id, host_wx_name,group_id, group_name, group_alias, sender_id, sender_name, sender_group_name, msg_type, msg_content, img_path, attachment_path, link_url, record_time,replay2msgid, ext_field1, ext_field2) "
                "VALUES (%s,%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
            )
            cursor.execute(add_group_chat, data)
            conn.commit()
            logger.info("Data inserted into group_chat successfully.")
        except mysql.connector.Error as err:
            logger.info(f"Failed to insert data into group_chat: {err}")

    # 示例数据插入
    # 转换时间戳为时间
    # record_time = datetime.utcfromtimestamp(chatinfo['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    # print(record_time)
    # 如果是图片则将content值为空，同时将图片路径填充到图片路径字段
    img_path = ''
    file_path= ''
    link_url = ''
    content = chatinfo['msg']
    replay2msgid = ''
    ##图片
    if chatinfo['msg_type'] == 'IMAGE':
        img_path = chatinfo['msg']
        content=''
    ##附件或者语言或者视频
    if chatinfo['msg_type'] == 'FILE' or chatinfo['msg_type'] == 'VOICE'or chatinfo['msg_type'] == 'VIDEO':
        file_path = chatinfo['msg']
        content=''
    ##公众号文章
    if chatinfo['msg_type'] == 'SHARING':
        link_url = chatinfo['msg']
        content=''
    ##视频号文章分享
    if chatinfo['msg_type'] == 'WECHAT_VIDEO':
        urlload = etree.fromstring(content)
        media_urls = []
        for media in urlload.xpath('//media'):
            media_url = media.findtext('url')
            if media_url:
                media_urls.append(media_url)
            # thumb_url = media.findtext('thumbUrl')
            # if thumb_url:
            #     media_urls.append(thumb_url)
        urls_str = '\n'.join(media_urls)
        print(urls_str)
        link_url = urls_str
        content=''
    ##引用消息
    if chatinfo['msg_type'] == 'QUOTE':
        try:
            replay2msgid = chatinfo['source_content']
            replay2msgid = replay2msgid.replace('\n', '').replace('\t', '')
            quoteload = etree.fromstring(replay2msgid)
            # 提取 svrid
            svrid = quoteload.xpath('//refermsg/svrid/text()')
            replay2msgid = svrid[0] if svrid else None
        except Exception as e:
            logger.error(e)


    private_chat_data = (
        chatinfo['msgid'],chatinfo['to_id'],chatinfo['to_nick'],chatinfo['from_id'], chatinfo['from_nick'], '发生人的备注', chatinfo['msg_type'],
        content, img_path, file_path, link_url,chatinfo['timestamp'],replay2msgid, 'Extension 1', 'Extension 2'
    )

    group_chat_data = (
        chatinfo['msgid'],chatinfo['to_id'], chatinfo['to_nick'],chatinfo['group_id'], chatinfo['group_name'], 'Group Alias', chatinfo['from_id'], chatinfo['from_nick'], '发生人的备注', chatinfo['msg_type'],
        content, img_path, file_path, link_url,chatinfo['timestamp'],replay2msgid, 'Extension 1', 'Extension 2'
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

def sqlQuery(from_id,record_time,other_user_id,isgroup,ctype):
    config = get_dbconfig()
    # 转换时间戳为时间
    record_time = datetime.fromtimestamp(record_time).strftime('%Y-%m-%d %H:%M:%S')
    # group_chat_log_sql = f"SELECT sender_id, sender_name, msg_type, msg_content, img_path, attachment_path, link_url, record_time, replay2msgid FROM group_chat WHERE group_id ='{other_user_id}' and sender_id='{from_id}' ORDER BY record_time DESC LIMIT 30"
    # private_chat_log_sql = f"SELECT sender_id, sender_name, msg_type, msg_content, img_path, attachment_path, link_url,record_time, replay2msgid FROM private_chat WHERE sender_id ='{from_id}'  ORDER BY record_time DESC LIMIT 30"
    group_quote_sql = f"SELECT msg_content, img_path, attachment_path, link_url, replay2msgid from group_chat WHERE sender_id ='{from_id}' and record_time='{record_time}'and msg_type='{ctype}' and group_id='{other_user_id}'"
    logger.info(f"查询语句: {group_quote_sql}")
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        # if isgroup == "isnotgroup":
        #     sql = private_chat_log_sql
        # else:
        #     sql = group_chat_log_sql
        # chatlog=cursor.execute(sql).fetchall()
        # logger.debug(f"聊天历史记录查询成功: {chatlog}")
        if isgroup == "isgroup":
            cursor.execute(group_quote_sql)
            quotechat=cursor.fetchall()
            logger.debug(f"引用消息查询成功: {quotechat}")
            return quotechat
    except mysql.connector.Error as err:
        logger.error(f"查询失败: {err}")
    finally:
        cursor.close()
        conn.close()




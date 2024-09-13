import mysql.connector
# from lxml.xmlerror import log_handler
from mysql.connector import errorcode
from datetime import datetime, timedelta
from common.log import logger
from lxml import etree
from config import load_config, conf
import shutil
import os
def get_config():
    load_config()
    connect_config = {
        'user': conf().get("db_user"),
        'password': conf().get("db_password"),
        'host': conf().get("db_host"),
        'port': conf().get("db_port"),
        'database': conf().get("db_name"),
    }
    file_web_config = {
        "file_host_path": conf().get("file_host_path"),
        "file_web_host":conf().get("file_web_host"),
        "file_web_port":conf().get("file_web_port"),
    }
    return connect_config, file_web_config
# 操作数据库
def operateMysql (chatinfo):
    # 创建数据库连接（持久连接）
    connect_config,file_web_config = get_config()
    conn = mysql.connector.connect(**connect_config)
    cursor = conn.cursor()
    # 选择数据库
    # cursor.execute(f"USE {connect_config['database']}")

    def insert_into_private_chat(data):
        try:
            add_private_chat = (
                "INSERT INTO private_chat "
                "(msgid,receiver_id,host_wx_id, host_wx_name, sender_id, sender_name, sender_remark, msg_type, msg_content, img_path, attachment_path, link_url, record_time,replay2msgid, ext_field1, ext_field2) "
                "VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)"
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
        chatinfo['msgid'],chatinfo['to_wxid'],chatinfo['to_id'],chatinfo['to_nick'],chatinfo['from_id'], chatinfo['from_nick'], '发生人的备注', chatinfo['msg_type'],
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

def sqlQuery(from_id,record_time,to_id,group_id,isgroup,ctype):
    db_config,file_web_config = get_config()
    # 转换时间戳为时间
    record_time = datetime.fromtimestamp(record_time).strftime('%Y-%m-%d %H:%M:%S')
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        #生成生成history内容，查询近50条文本对话的记录
        historySql = ''
        if isgroup == "isgroup":
            historySql = f"SELECT sender_id, msg_content from group_chat WHERE group_id ='{group_id}' AND msg_content <> '' ORDER BY record_time ASC LIMIT 20"
        else:
            historySql = f"SELECT sender_id , msg_content ,receiver_id from private_chat WHERE msg_content <>''AND  (sender_id='{from_id}' AND receiver_id='{to_id}') or  (sender_id='{to_id}'AND receiver_id='{from_id}')  ORDER BY record_time ASC LIMIT 20"
        cursor.execute(historySql)
        historychat = cursor.fetchall()
        logger.debug(f"读取到历史记录: {historychat}")
        historyQuery = historyInfo(historychat,isgroup)

        #如果是引用消息，则在查询时只根据引用的消息进行推理
        if ctype == "QUOTE":
            # 引用消息时，当前消息内容，和被引用消息的msgid查询
            group_quote_sql = f"SELECT msg_content, replay2msgid from group_chat WHERE sender_id ='{from_id}' and record_time='{record_time}'and msg_type='{ctype}' and group_id='{group_id}'"
            logger.info(f"查询语句: {group_quote_sql}")
            if isgroup == "isgroup":#群聊
                cursor.execute(group_quote_sql)
                quotechat = cursor.fetchall()
                msg_content, replay2msgid = quotechat[0]
                logger.debug(f"当前消息的内容: {msg_content},引用消息的msgid:{replay2msgid}")
                #查询被引用消息的内容
                group_quote_sourceinfo_sql = f"SELECT msg_type, msg_content, img_path, attachment_path, link_url from group_chat WHERE msgid ='{replay2msgid}'"
                cursor.execute(group_quote_sourceinfo_sql)
                groupsourcechat = cursor.fetchall()
                sourcemsg_type, sourcemsg_content, img_path, attachment_path, link_url = groupsourcechat[0]
                logger.debug(f"读取到被引用消息的源内容: {sourcemsg_content},img_path:{img_path},attachment_path:{attachment_path},link_url:{link_url}")
                #消息处理
                quote_content = quoteMsgExe(sourcemsg_type, msg_content, img_path, attachment_path,link_url,file_web_config)
                return quote_content,sourcemsg_type ,historyQuery
        return None,None , historyQuery
    except mysql.connector.Error as err:
        logger.error(f"查询失败: {err}")
    finally:
        cursor.close()
        conn.close()

def quoteMsgExe(ctype,msg_content, img_path, attachment_path, link,file_web_config):
    if ctype == "TEXT":#如果被引用的是文本消息则直接返回msg_content
        return ctype,msg_content
    if ctype == "IMAGE":#如果被引用的是图片消息,则将图片负责到网站目录下，并返回图片的访问网址
        if img_path:
            shutil.copy(img_path, file_web_config['file_host_path'])
            img_name = os.path.basename(img_path)
            img_web_path = file_web_config['file_web_path']+img_name
        return ctype,img_web_path
    if ctype == "SHARE":#如果被引用的是分享消息，则返回分享的链接地址
        return ctype,link
    if ctype == "VOICE" or ctype == "FILE":#如果被引用的是语音消息或文件消息，则返回文件的访问地址
        return ctype,attachment_path


def historyInfo(hostorychat,isgroup):
    if isgroup == "isgroup":
        result = "|".join([f"{name}：{message}" for name, message in hostorychat])
        logger.debug(f"历史记录: {result}")
        return result.replace(' ','').replace('\n','')
    else:
        result = "\n".join([f"{name}：{message}" for name, message, _ in hostorychat])
        logger.debug(f"历史记录: {result}")
        return result.replace(' ','').replace('\n','')


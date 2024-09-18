import mysql.connector
# from lxml.xmlerror import log_handler
from mysql.connector import errorcode
from datetime import datetime, timedelta
from common.log import logger
from lxml import etree
from config import load_config, conf
import shutil
import os
import re
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
    intent_config = {
        "img_intent": conf().get("img_intent"),
        "generate_img_intent": conf().get("generate_img_intent"),
        "web_search_intent": conf().get("web_search_intent"),
    }
    return connect_config, file_web_config,intent_config
# 操作数据库
def operateMysql (chatinfo):
    # 创建数据库连接（持久连接）
    connect_config,file_web_config,_ = get_config()
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

def sqlQuery(query,from_id,record_time,to_id,group_id,isgroup,ctype):
    db_config,file_web_config,intent_config = get_config()
    query = infoClean(query)
    quote_content = ''
    quote_type = ''
    # 转换时间戳为时间
    record_time = datetime.fromtimestamp(record_time).strftime('%Y-%m-%d %H:%M:%S')
    dt_record_time = datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
    history_start_time = (dt_record_time - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        #生成生成history内容，查询近50条文本对话的记录
        historySql = ''
        if isgroup == "isgroup":
            historySql = f"SELECT sender_id, msg_content from group_chat WHERE group_id ='{group_id}' AND msg_content <> '' AND record_time <> '{record_time}' AND record_time >= '{history_start_time}' ORDER BY record_time ASC LIMIT 20"
            imgHistorySql = f"SELECT img_path FROM ( SELECT * FROM group_chat ORDER BY record_time DESC LIMIT 10) AS last10 WHERE group_id = '{group_id}' AND msg_type = 'IMAGE' LIMIT 1"
        else:
            historySql = f"SELECT sender_id , msg_content ,receiver_id from private_chat WHERE msg_content <>''AND record_time <> '{record_time}' AND record_time >= '{history_start_time}' AND  (sender_id='{from_id}' AND receiver_id='{to_id}') or  (sender_id='{to_id}'AND receiver_id='{from_id}')  ORDER BY record_time ASC LIMIT 20"
            imgHistorySql = f"SELECT img_path FROM ( SELECT * FROM private_chat WHERE (sender_id='{from_id}' AND receiver_id='{to_id}') or  (sender_id='{to_id}'AND receiver_id='{from_id}')  ORDER BY record_time DESC LIMIT 10) AS last10 WHERE msg_type = 'IMAGE' LIMIT 1"
        logger.debug(f"查询近一小时的聊天记录sql语句: {historySql}")
        logger.debug(f"查询近一小时的图片记录sql语句: {imgHistorySql}")
        cursor.execute(historySql)
        historychat = cursor.fetchall()
        # logger.debug(f"读取到历史记录: {historychat}")
        # 拼接历史记录
        historyQuery = historyInfo(historychat,isgroup)
        # 判断非引用消息时，判断否触发特定功能：图片分析，文生图，联网搜索。并将相关类型传递给引用消息的类型，在dify中根据引用消息的类型，走不同功能分支
        # 当来聊天内容少于等于20字的时候，通过关键词判断是否触发特定功能。超过50字则直接交给模型判断。
        if count_chinese_characters(query) <= 50:
            quote_type = intent_recognition(query, intent_config)
        if quote_type == 'IMAGE' or quote_type == 'TEXT':
            #意图判断需要分析图片或者没有识别。，都将历史记录的10条对话记录内容的最新一张图片放到quote_content里。
            # 未找到图片，则重置引用消息类型为TEXT。
            # 在意图识别不是分析图片的情况下，如果近10条记录有图片，也先放进去，待大模型再次判断，是否是图片分析，是的话，则可以直接取到图片
            # 后面可以基于此机制，把视频，文件，等可能需要大模型处理的内容都预先放进来，待大模型判断需要分析相关内容的时候，就都可以直接取用
            cursor.execute(imgHistorySql)
            imgPath = cursor.fetchall()
            logger.debug(f"读取图片的历史记录: {imgPath}")
            if imgPath:
                logger.debug(f"读取到历史记录: {imgPath}")
                quote_content = getImgUrl(imgPath[0][0], file_web_config["file_host_path"],
                                          file_web_config["file_web_host"])
                logger.debug("10条历史记录中有图片,将图片放到了引用消息，待意图识别时使用")
            else:
                #如果历史记录未查到图片
                quote_type = 'TEXT'
        if quote_type == 'GENIMG':
            pass
        if quote_type == 'Web_Search':
            pass

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
                return query, quote_content,sourcemsg_type ,historyQuery
        return query, quote_content,quote_type, historyQuery
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
        result = infoClean(result)
        logger.debug(f"历史记录: {result}")
        # return result.replace('\n', '')
        return result
    else:
        result = "\n".join([f"{name}：{message}" for name, message, _ in hostorychat])
        result = infoClean(result)
        logger.debug(f"历史记录: {result}")
        # return result.replace('\n', '')
        return result
def getImgUrl(img_path,targetPath,web_host):
    shutil.copy(img_path, targetPath)
    img_name = os.path.basename(img_path)
    img_url = web_host + img_name
    return img_url

def infoClean(info):
    s = info.replace('\\', '\\\\')
    # 然后，将已正确转义的转回单反斜杠（如 \n，\t 等）
    s = re.sub(r'\\\\(n|t|r|b|f|\"|\'|\\)', r'\\\1', s)
    s = s.replace('\n', '').replace('"', '\\"')
    return s

def intent_recognition(text,intent_config):
    # 意图识别
    # 通过配置文件设置的图像，联网搜索，文生图等的关键词列表。判断用户请求是否直接调用以上功能。
    # 后续文件分析，视频生成，url分析等。全部都在此方法下面进行处理
    isImgIntent = False
    isGenImgIntent = False
    isWebSearchIntent = False
    # print(intent_config)
    imgKeywords = intent_config['img_intent']
    generateImgKeywords = intent_config['generate_img_intent']
    webSearchKeywords = intent_config['web_search_intent']
    for keyword in imgKeywords:
        # print(f"img意图：{keyword}")
        if keyword in text:
            isImgIntent = True
    for keyword in generateImgKeywords:
        # print(f"genimg意图：{keyword}")
        if keyword in text:
            isGenImgIntent = True

    for keyword in webSearchKeywords:
        # print(f"websearch意图：{keyword}")
        if keyword in text:
            isWebSearchIntent = True

    if isImgIntent and not isGenImgIntent and not isWebSearchIntent:
        return "IMAGE"
    elif not isImgIntent and isGenImgIntent and not isWebSearchIntent:
        return "GENIMG"
    elif not isImgIntent and not isGenImgIntent and isWebSearchIntent:
        return "Web_Search"
    else:
        return "TEXT"

def count_chinese_characters(s):
    #输入文本的汉字数量
    count = 0
    for char in s:
        if '\u4e00' <= char <= '\u9fff':
            count += 1
    return count
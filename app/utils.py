from app import config
import requests
import json
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import re
import os

# 获取日志器对象
logger = logging.getLogger('app')
# 获取环境变量
debug = os.getenv('DEBUG')


def extract_data(title, content, type=''):
    if "告警恢复" in title:
        # 告警恢复数据获取
        # [告警恢复] [告警类型 Transacation告警][cat URL-All-count],[告警已恢复][恢复时间]2023-06-15 18:20
        alert_type = title.split('[')[2].split(']')[0].split(' ')[1].strip()
        alert_project = title.split('[')[3].split(']')[0].split(' ')[0].strip()
        monitor_item = title.split('[')[3].split(']')[0].split(' ')[1].strip()
        alert_content = content.split('[')[1].split(']')[0].strip()
        alert_time = content.split(']')[2].strip()
        alert_interval = ''
        alert_url = ''
    else:
        # 告警数据获取
        alert_type = title.split('[')[1].split(']')[0].strip()
        alert_project = title.split('[')[2].split(']')[0].split(':')[1].strip()
        monitor_item = title.split('[')[3].split(']')[0].split(':')[1].strip()
        alert_content = content.split('[')[3].split(']')[0].strip() + ', ' + \
                        (': '.join(content.split('[')[2].split(']')[0].split(':')[:])).strip()
        alert_time = (':'.join(content.split('[')[4].split(']')[0].split(':')[1:])).strip()
        alert_interval = content.split('[')[6].split(']')[1]
        alert_url = ''

        if type == 'Mail':
            pattern = r"<a href='(.*?)'>"
            match = re.search(pattern, content)
            if match:
                http_address = match.group(1)
                if debug and debug.lower() == 'true' or config.DEBUG:
                    alert_url = http_address.replace("cat-web-server", config.test_url_address)
                else:
                    alert_url = http_address.replace("cat-web-server", config.prod_url_address)

            else:
                logger.error("HTTP 地址未找到")

    return alert_type, alert_project, monitor_item, alert_content, alert_time, alert_interval, alert_url


def format_alert_message(alert_type, alert_project, monitor_item, alert_content, alert_time, alert_interval,
                         alert_url=''):
    if not alert_url:
        if "告警已恢复" in alert_content:
            msg = '''
# Cat监控告警恢复信息
> <font color="info">告警类型</font>：%s
> <font color="info">告警项目</font>：%s
> <font color="info">监控项目</font>：%s
> <font color="info">告警内容</font>：%s
> <font color="info">恢复时间</font>：%s''' % (alert_type, alert_project, monitor_item, alert_content, alert_time)
        else:
            msg = '''
# Cat监控告警信息
> <font color="warning">告警类型</font>：%s
> <font color="warning">告警项目</font>：%s
> <font color="warning">监控项目</font>：%s
> <font color="warning">告警内容</font>：%s
> <font color="warning">告警时间</font>：%s
> <font color="warning">告警间隔时间</font>：%s''' % (alert_type, alert_project, monitor_item, alert_content, alert_time, alert_interval)
    else:
        msg = '''
# Cat监控告警信息
> <font color="warning">告警类型</font>：%s
> <font color="warning">告警项目</font>：%s
> <font color="warning">监控项目</font>：%s
> <font color="warning">告警内容</font>：%s
> <font color="warning">告警时间</font>：%s
> <font color="warning">告警URL</font>：%s
> <font color="warning">告警间隔时间</font>：%s''' % (alert_type, alert_project, monitor_item, alert_content, alert_time, alert_url, alert_interval)
    return msg


def alert_service(msg):
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": msg,
        }
    }
    # 请求企业微信机器人接口
    if debug and debug.lower() == 'true' or config.DEBUG:
        response = requests.post(config.test_webhook, data=json.dumps(payload))
    else:
        response = requests.post(config.prod_webhook, data=json.dumps(payload))

    return response.status_code


def send_email(sender, recipient, subject, body):
    # 将 Markdown 文本转换为 HTML
    tmp_html_body = markdown.markdown(body)
    # 将换行符替换为 <br> 标签
    html_body = tmp_html_body.replace('\n', '<br>')

    # 创建一个带附件的邮件实例
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    # 添加邮件正文（HTML 格式）
    msg.attach(MIMEText(html_body, 'html'))
    # logger.info(msg)
    logger.info(html_body)

    # 连接到邮件服务器并发送邮件
    with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
        server.starttls()
        server.login(config.smtp_username, config.smtp_password)
        server.send_message(msg)
        logger.info("邮件发送完成")
    return 200

from .config import webhook
import requests
import json
import logging

# rest_ful 接口风格
from rest_framework.views import APIView
from rest_framework.response import Response

# 获取日志器对象
logger = logging.getLogger('app')


def alert_service(msg):
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": msg,
        }
    }
    # 请求企业微信机器人接口
    response = requests.post(webhook, data=json.dumps(payload))

    return response.status_code


# Create your views here.
class Alert(APIView):

    def post(self, request):
        logger.info(request.data)

        try:
            # 提取数据
            title = request.data['title']
            content = request.data['content']

            # 抽离数据
            alert_type = title.split('[')[1].split(']')[0].strip()
            alert_project = title.split('[')[2].split(']')[0].split(':')[1].strip()
            monitor_item = title.split('[')[3].split(']')[0].split(':')[1].strip()
            alert_content = content.split('[')[3].split(']')[0].strip() + ', ' + \
                            (': '.join(content.split('[')[2].split(']')[0].split(':')[:])).strip()
            alert_time = (':'.join(content.split('[')[4].split(']')[0].split(':')[1:])).strip()
            alert_interval = content.split('[')[6].split(']')[1]

            # 组装数据
            msg = '''
                # Cat监控告警信息
                > <font color="warning">告警类型</font>：%s
                > <font color="warning">告警项目</font>：%s
                > <font color="warning">监控项目</font>：%s
                > <font color="warning">告警内容</font>：%s
                > <font color="warning">告警时间</font>：%s
                > <font color="warning">告警间隔时间</font>：%s
            ''' % (alert_type, alert_project, monitor_item, alert_content, alert_time, alert_interval)
            logger.info(str(msg))
            status = alert_service(msg)
            return Response(status)
        except Exception as e:
            logger.error("发生了异常: %s", str(e))
            return Response(500)


class Mail(APIView):

    def post(self, request):
        print(request.data)
        return Response({'status': '200'})

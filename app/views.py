from app import utils
import logging
from django.http import JsonResponse

# rest_ful 接口风格
from rest_framework.views import APIView
from rest_framework.response import Response

# 获取日志器对象
logger = logging.getLogger('app')


# Create your views here.
class Alert(APIView):

    def post(self, request):
        logger.info(request.data)

        try:
            # 提取数据
            title = request.data['title']
            content = request.data['content']

            # 抽离数据
            alert_type, alert_project, monitor_item, alert_content, alert_time, alert_interval, _ = utils.extract_data(
                title,
                content
            )

            # 组装数据
            msg = utils.format_alert_message(
                alert_type,
                alert_project,
                monitor_item,
                alert_content,
                alert_time,
                alert_interval
            )
            logger.info(msg)

            status = utils.alert_service(msg)
            logger.info("告警发送完成")
            return Response({'status': status})
        except Exception as e:
            logger.error("发生了异常: %s", str(e))
            logger.info("告警发送异常")
            return Response({'status': '500'})


class Mail(APIView):

    def post(self, request):
        logger.info(request.data)
        try:
            # 提取数据
            tmp_data = request.data['value']
            title = tmp_data.split(',')[0].strip()
            content = tmp_data.split(',')[1].strip()

            # 抽离数据
            alert_type, alert_project, monitor_item, alert_content, alert_time, alert_interval, alert_url = utils.extract_data(
                title,
                content,
                'Mail'
            )

            # 组装数据
            msg = utils.format_alert_message(
                alert_type,
                alert_project,
                monitor_item,
                alert_content,
                alert_time,
                alert_interval,
                alert_url
            )
            # logger.info(msg)

            sender = request.data['re']
            recipient = request.data['to']
            subject = 'Cat监控告警信息'
            body = str(msg)

            status = utils.send_email(sender, recipient, subject, body)
            return Response({'status': status})
        except Exception as e:
            logger.error("发生了异常: %s", str(e))
            logger.info("邮件发送异常")
            return Response({'status': '500'})


def handler404(request, exception):
    return JsonResponse({'error': 'API endpoint not found.'}, status=404)
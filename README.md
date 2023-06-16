# alert
> 企业微信告警和邮件告警服务

## 1. 服务镜像打包

```shell
$ git clone https://github.com/evescn/alert.git

$ cd alert

# 打包 Docker 镜像
$ docker build -t harbor.xxx.com/devops/alert:v1.0 -f Dockerfile .
$ docker push harbor.xxx.com/devops/alert:v1.0
```

## 2. 服务部署

### a | `/data/alert/config/config.py` 配置文件

> 服务启动需要使用，项目配置文件

```python
DEBUG = False
# DEBUG = True

# 企业微信机器人配置
## 生产地址
prod_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx"
prod_url_address = "cat.evescn.com"
## 测试地址
test_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxx"
test_url_address = "10.0.0.111:8080"

# 邮件配置
## 部署需要确定当前云是否支持 smtp_port 端口，比如：阿里云不支持25端口，163邮件服务使用25端口
smtp_server = "smtp.qq.com"  # 邮件服务器地址
smtp_port = 587  # 邮件服务器端口
smtp_username = "xxxxx@qq.com"  # 邮件服务器用户名
smtp_password = "xxxxxxxxxxxx"  # 邮件服务器密码
```

### b | Docker 启动

```shell
$ docker run -d \
  --name alert \
  --hostname alert \
  --privileged \
  --restart=always \
  ## 配置文件中默认为 DEBUG=False 修改此处或者配置文件中二选一即可
  # 测试环境：DEBUG=True 企业微信走测试环境
  # 生产环境：DEBUG=False 企业微信走生产环境
  -e DEBUG=True \ 
  -p 8000:8000 \
  -v /data/alert/config/config.py:/alert/app/config.py \
  -v /data/alert/log:/alert/log \
  harbor.xxx.com/devops/alert:v1.0
```

### c | docker-compose 启动

```yaml
version: '3.1'

services:
  alert:
    image: harbor.xxx.com/devops/alert:v1.0
    container_name: alert
    hostname: alert
    privileged: true
    user: root
    restart: always
    ports:
      - 8000:8000
    environment:
      - DEBUG=True
    volumes:
      - /data/alert/config/config.py:/alert/app/config.py
      - /data/alert/log:/alert/log

# docker-compose up -d
```

### d | Kubernetes 启动

```yaml
# k8s.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: alert
  namespace: devops
spec:
  replicas: 1
  selector:
    matchLabels:
      app: alert
  template:
    metadata:
      labels:
        app: alert
    spec:
      containers:
      - name: alert
        image: harbor.xxx.com/devops/alert:v1.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8080

---
# service
apiVersion: v1
kind: Service
metadata:
  name: alert
  namespace: devops
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 8000
    nodePort: 38000
  selector:
    app: alert
  type: NodePort

---
# ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: alert
  namespace: devops
spec:
  ingressClassName: nginx
  rules:
  - host: alert.evescn.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: alert
            port:
              number: 80

# kubectl apply -f k8s.yaml
```

## 3. 服务访问

> 服务提供的 api 接口

### 接口地址

```shell
http://ip:8000/api/alert
http://ip:8000/api/mail
```

# cat 服务部署

> 详细的部署，请查看 [官方文档](https://github.com/dianping/cat/wiki/readme_server)

## 初始化Mysql数据库

一套CAT集群需要部署一个数据库，数据库脚本 `script/CatApplication.sql`

## docker-compose

```yaml
version: '3.1'

services:
  cat-server:
    image: harbor.xxxxx.com/monitoring/cat:v1.0.0
    container_name: cat-server
    privileged: true
    user: root
    restart: always
    ports:
      - 2280:2280
      - 8080:8080
    environment:
      - MYSQL_URL=10.0.0.111
      - MYSQL_PORT=3306
      - MYSQL_USERNAME=xxxxx
      - MYSQL_PASSWD=xxxxxxxxx
      - MYSQL_SCHEMA=cat
      - SERVER_IP=10.0.0.111
      - PATH=/data/app/tomcat/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
      - JAVA_VERSION=1.8.0
      - JAVA_HOME=/usr/lib/jvm/java
      - CATALINA_HOME=/data/app/tomcat
      - TOMCAT_MAJOR_VERSION=8
      - TOMCAT_MINOR_VERSION=8.5.73
    volumes:
      - /etc/localtime:/etc/localtime
      - /data/cat-server/cat/:/data/appdatas/cat/
      - /data/cat-server/applogs/:/data/applogs/
    command: ["/bin/sh", "-c", "chmod +x /datasources.sh && /datasources.sh && catalina.sh run"]

```

> 详细的 Dockerfile 镜像打包文档没有，后续需要在研究
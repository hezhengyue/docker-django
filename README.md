# 国内下载镜像
docker pull registry.cn-chengdu.aliyuncs.com/zhengyue/python:3.12-slim
docker tag registry.cn-chengdu.aliyuncs.com/zhengyue/python:3.12-slim python:3.12-slim
docker pull registry.cn-chengdu.aliyuncs.com/zhengyue/nginx:1.26.3-alpine3.20
docker tag registry.cn-chengdu.aliyuncs.com/zhengyue/nginx:1.26.3-alpine3.20 nginx:1.26.3-alpine3.20
docker pull registry.cn-chengdu.aliyuncs.com/zhengyue/postgres:15.17-alpine3.23
docker tag registry.cn-chengdu.aliyuncs.com/zhengyue/postgres:15.17-alpine3.23 postgres:15.17-alpine3.23
docker pull registry.cn-chengdu.aliyuncs.com/zhengyue/redis:7.2.13-alpine3.21
docker tag registry.cn-chengdu.aliyuncs.com/zhengyue/redis:7.2.13-alpine3.21 redis:7.2.13-alpine3.21

# 赋予执行权限
chmod +x start.sh

# 启动服务 + 初始化数据库 + 创建管理员
./start.sh init
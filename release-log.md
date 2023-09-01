# v2.0.1 发布日志 （待发布）

fixbug:
1. 修复开启摘要，导致长期记忆存储报错问题

# v2.0.2 发布日志

release:
1. python升级至3.10.12
2. 优化prompt让对话更加拟人
3. text_generation 支持上下文，适配短期记忆
4. text_generation 支持流式返回数据，提高性能

fixbug:
1. 修复音频文件堆积
2. 修复多人同时讨论，长期记忆检索问题
3. 增加解决docker网络问题文档
4. 修复直播获取弹幕，用户名带*号问题

remove：
1. 移除英文角色提示模版

known issues:
1. 语音识别，待解决

注意事项：
- 本次改动更改了数据库表设计，更新代码后请执行数据库迁移操作
```shell
python manage.py makemigrations 
```
```shell
python manage.py migrate 
```
- 本次改动新增了依赖，请执行更新依赖操作
```shell
pip3 install -r requirements.txt
```
# 引入必要的 Python 模块
import asyncio # 异步 I/O 标准库
import datetime # 处理日期和时间的模块
import json # JSON 编码和解码模块
import openai # OpenAI 的 Python API
import websockets # WebSocket 实现的模块
#定义异步函数 handle_dialogue，处理 WebSocket 的连接请求
async def handle_dialogue(websocket, path):
    async for message in websocket:
        # 从 WebSocket 接收消息,循环遍历
        request = json.loads(message)
        # 将接收到的消息转为 JSON 对象
        if len(message)<10:
            continue
        dialogues = request['dialogues']
        # 获取对话内容
        openai.api_key = "*****************************************"
        """
        调用OpenAI API，完成对话
        参数解释:
        messages : 与chatgpt对话的数组，具体格式为{"dialogues":[{"role":"user","content":"什么是python"}]}，我是选择从前端编辑好再传入
        model : 这里使用3.5模型，目前来说较为常用的，要使用别的，如果是003模型，请去看官方文档，传递的参数就不是这个了，是prompt
        temperature : chatgpt回答的开放程度，数值是0-2之间，越大，越天马行空，自行调整，太大了回的比较扯淡
        stream :流式输出，如果传入的数据是True,就是启用流式输出，这种方式，返回很快，适合于部署，用户体验比较好，基本在0.5-3秒之间；
                如果传入False，或者干脆不传，直接删掉，就是一整句返回，这种方式，简单的问题3秒左右，稍微难一点，比如“什么是python",测试了几次差不多要10秒，也跟服务器位置有关
        """
        response = openai.ChatCompletion.create(
            messages=dialogues,
            model="gpt-3.5-turbo",
            temperature=0.7,
            stream=True
        )
        # 发送对话结果给前端
        for chunk in response:
            response_json = json.loads(str(chunk))
            choices = response_json['choices'][0]
            # 处理删除返回数据中，第一行的角色数据
            if choices.get("delta").get("role"):
                # print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                continue;
            # 如果对话未结束，则将回复消息发送给前端
            if choices['finish_reason'] != 'stop':
                message = json.dumps({'text': choices['delta']})
                print(message)
                try:
                    # 设置发送超时为 5 秒钟
                    await asyncio.wait_for(websocket.send(message), timeout=0.5)
                except asyncio.TimeoutError:
                    # 如果发送超时，则打印提示信息
                    print("WebSocket 发送超时")
"""
 使用websockets模块创建一个WebSocket服务器，并将其绑定到本地主机和端口8765
第一个参数为异步函数 handle_dialogue
第二个参数是ip地址，比如本地环回地址“127.0.0.1”，如果要部署到阿里云、腾讯云之类的，改成“0.0.0.0”
第三个参数是缓冲区大小
"""
start_server = websockets.serve(handle_dialogue, 'localhost', 8765,max_size=100)
# 获取一个事件循环并运行WebSocket服务器，直到服务器关闭或出现错误
asyncio.get_event_loop().run_until_complete(start_server)
# 运行事件循环，直到程序结束或被强制退出
asyncio.get_event_loop().run_forever()

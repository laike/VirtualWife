import queue
import threading
import traceback
from ..utils.chat_message_utils import format_user_chat_text
from ..process import process_core
from ..output import realtime_message_queue

# 创建一个线程安全的队列
insight_message_queue = queue.SimpleQueue()


class InsightMessage():

    type: str
    user_name: str
    content: str
    expand: str

    def __init__(self, type: str, user_name: str, content: str, expand: str = None) -> None:
        self.type = type
        self.user_name = user_name
        self.content = content
        self.expand = expand

    def to_dict(self):
        return {
            "type": self.type,
            "user_name": self.user_name,
            "content": self.content,
            "expand": self.expand
        }


def put_message(message: InsightMessage):
    global insight_message_queue
    insight_message_queue.put(message)


def send_message():
    while True:
        try:
            message = insight_message_queue.get()
            if (message != None and message != ''):
                if (message.type == "chat"):
                    content = format_user_chat_text(text=message.content)
                    realtime_message_queue.put_message(realtime_message_queue.RealtimeMessage(
                        type=message.type,
                        user_name=message.user_name,
                        content=content
                    ))
                    process_core.chat(
                        you_name=message.user_name, query=message.content)
        except Exception as e:
            traceback.print_exc()


class InsightMessageQueryJobTask():

    @staticmethod
    def start():
        # 创建后台线程
        background_thread = threading.Thread(target=send_message)
        # 将后台线程设置为守护线程，以便在主线程结束时自动退出
        background_thread.daemon = True
        # 启动后台线程
        background_thread.start()
        print("=> InsightMessageQueryJobTask start")

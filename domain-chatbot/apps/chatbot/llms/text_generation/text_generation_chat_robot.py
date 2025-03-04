import html
import sys
from typing import Any
from dotenv import load_dotenv
from langchain import LLMChain, PromptTemplate
import requests
import os
import logging
import json
try:
    import websockets
except ImportError:
    print("Websockets package not found. Make sure it's installed.")


class TextGeneration():

    max_new_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    max_retries: int = 3

    text_generation_api_url: str
    text_generation_web_socket_url: str
    chat_api_url: str

    def __init__(self):
        self.text_generation_api_url = os.getenv("TEXT_GENERATION_API_URL")
        self.chat_api_url = self.text_generation_api_url + '/api/v1/generate'
        self.text_generation_web_socket_url = os.getenv(
            "TEXT_GENERATION_WEB_SOCKET_URL")
        print("=> init TextGeneration")
        print('text_generation_api_url:', self.text_generation_api_url)
        print('text_generation_web_socket_url:',
              self.text_generation_web_socket_url)
        print('chat_api_url:', self.chat_api_url)
        print('max_new_tokens:', self.max_new_tokens)
        print('temperature:', self.temperature)
        print('top_p:', self.top_p)

    def chat(self, prompt: str, role_name: str, you_name: str, query: str, short_history: list[dict[str, str]], long_history: str) -> str:
        body = self.build_body(prompt=prompt, role_name=role_name, you_name=you_name,
                               query=query, short_history=short_history, long_history=long_history)
        for _ in range(self.max_retries + 1):
            response = requests.post(self.chat_api_url, json=body)
            if response.status_code == 200:
                result = response.json()['results'][0]['text'].strip()
                print("=> result:"+result)
                if result != '':
                    return result
                else:
                    print("Received empty response. Retrying...")
            else:
                print(f"text_generation error response is ",
                      response, json.dumps(body))

    async def handle_realtime_data(self, role_name: str, you_name: str, realtime_callback=None, data: str = ""):
        if realtime_callback:
            await realtime_callback(role_name, you_name, data)

    async def chatStream(self,
                         prompt: str,
                         role_name: str,
                         you_name: str,
                         query: str,
                         history: list[dict[str, str]],
                         realtime_callback=None,
                         conversation_end_callback=None
                         ):
        async for response in self.stream(prompt=prompt, role_name=role_name, you_name=you_name, query=query, history=history, realtime_callback=realtime_callback, conversation_end_callback=conversation_end_callback):
            sys.stdout.flush()

    async def stream(self,
                     prompt: str,
                     role_name: str,
                     you_name: str,
                     query: str,
                     history: list[dict[str, str]],
                     realtime_callback=None,
                     conversation_end_callback=None
                     ):
        body = self.build_body(prompt=prompt, role_name=role_name, you_name=you_name,
                               query=query, short_history=history, long_history="")

        async with websockets.connect(self.text_generation_web_socket_url, ping_interval=None) as websocket:
            await websocket.send(json.dumps(body))
            answer = ''
            while True:
                incoming_data = await websocket.recv()
                incoming_data = json.loads(incoming_data)
                match incoming_data['event']:
                    case 'text_stream':
                        text = incoming_data['text']
                        if text == '' or text == None:
                            continue
                        answer = answer + text
                        realtime_callback(role_name, you_name, text)
                        yield text
                    case 'stream_end':
                        conversation_end_callback(
                            role_name, answer, you_name, query)
                        return

    def build_body(self, prompt: str, role_name: str, you_name: str, query: str, short_history: list[dict[str, str]], long_history: str) -> dict[str, Any]:
        input_prompt = you_name+"说"+query+"[/INST]"
        prompt = prompt + input_prompt
        logging.info(f"prompt:{prompt}")
        # 构建短期记忆数据
        internal = []
        visible = []
        for item in short_history:
            internal.append(item["human"])
            visible.append(item["ai"])
        history = {'internal': internal, 'visible': visible}
        body = {
            'prompt': prompt,
            'history': history,
            '_continue': False,
            'max_new_tokens': self.max_new_tokens,
            'preset': 'None',
            'do_sample': True,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': 20,
            'typical_p': 1,
            'epsilon_cutoff': 0,
            'eta_cutoff': 0,
            'tfs': 1,
            'top_a': 0,
            'repetition_penalty': 1.15,
            'repetition_penalty_range': 0,
            'encoder_repetition_penalty': 1,
            'no_repeat_ngram_size': 0,
            'min_length': 0,
            'num_beams': 1,
            'penalty_alpha': 0,
            'length_penalty': 1,
            'early_stopping': False,
            'mirostat_mode': 0,
            'mirostat_tau': 5,
            'mirostat_eta': 0.1,
            'seed': -1,
            'add_bos_token': True,
            'truncation_length': 2048,
            'ban_eos_token': False,
            'skip_special_tokens': True
            # 'stopping_strings': []
        }
        return body

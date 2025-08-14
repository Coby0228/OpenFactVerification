import time
import openai
from openai import OpenAI
from .base import BaseClient


class LocalOpenAIClient(BaseClient):
    """Support Local host LLM chatbot with OpenAI API.
    see https://github.com/lm-sys/FastChat/blob/main/docs/openai_api.md for example usage.
    """

    def __init__(
        self,
        model: str = "",
        api_config: dict = None,
        max_requests_per_minute=200,
        request_window=60,
    ):
        super().__init__(model, api_config, max_requests_per_minute, request_window)

        openai.api_key = api_config["LOCAL_API_KEY"]
        openai.base_url = api_config["LOCAL_API_URL"]

    def _call(self, messages: str, **kwargs):
        seed = kwargs.get("seed", 42)  # default seed is 42
        assert type(seed) is int, "Seed must be an integer."

        response = openai.chat.completions.create(
            response_format={"type": "json_object"},
            seed=seed,
            model=self.model,
            messages=messages,
        )
        r = response.choices[0].message.content
        return r

    def get_request_length(self, messages):
        # TODO: check if we should return the len(menages) instead
        return 1

    def construct_message_list(
        self,
        prompt_list: list[str],
        system_role: str = "You are a helpful assistant designed to output JSON.",
    ):
        messages_list = list()
        for prompt in prompt_list:
            messages = [
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt},
            ]
            messages_list.append(messages)
        return messages_list

if __name__ == '__main__':
    print("--- Running LocalOpenAIClient Test ---")
    
    # 假設您的 Ollama 服務正在本地運行
    # 您可以從環境變數或設定檔載入這些設定
    test_api_config = {
        "LOCAL_API_URL": "https://ollama.nlpnchu.org/v1",
        "LOCAL_API_KEY": "amallobalpln" 
    }

    # 請將 'qwen:latest' 換成您已下載的 Ollama 模型名稱
    test_model = "qwen3:30b" 

    try:
        # 1. 初始化客戶端
        print(f"Initializing client with model: {test_model}")
        client = LocalOpenAIClient(model=test_model, api_config=test_api_config)
        
        # 2. 準備測試訊息
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "說個笑話/no_think"}
        ]
        print(f"Sending message to the model...")

        # 3. 呼叫模型並取得回應
        response = client._call(test_messages)

        # 4. 印出結果
        print("\n--- Model Response ---")
        print(response)
        print("\n--- Test Successful ---")

    except Exception as e:
        print(f"\n--- Test Failed ---")
        print(f"An error occurred: {e}")
        print("Please ensure that your Ollama service is running and the model '{test_model}' is available.")

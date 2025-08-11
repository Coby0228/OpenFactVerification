import sys
import time
import json
from tqdm import tqdm

sys.path.append("..")
from factcheck import FactCheck  # noqa: E402

# ANSI escape codes for colors
green = "\033[92m"
red = "\033[91m"
reset = "\033[0m"
THRESHOLD = 0.8  # 設定真實性分數的閾值


def minimal_test(lang="en"):
    # Initialize the FactCheck class
    prompt = "chatgpt_prompt"
    if lang == "zh":
        prompt = "chatgpt_prompt_zh"
    factcheck = FactCheck(prompt=prompt)

    def atom_test(instance):
        response = instance["response"]
        res = factcheck.check_text(response)
        try:
            for k, v in instance["attributes"].items():
                actual_value = None
                if k == "factuality":
                    # 從 'summary' 物件中獲取 'factuality'
                    factuality_score = res['summary'][k]
                    actual_value = factuality_score >= THRESHOLD
                else:
                    actual_value = res[k]
                
                print(f"Comparing '{k}': actual={actual_value}, expected={v}")
                assert actual_value == v
            return True
        except Exception as e:  # 捕捉更明確的錯誤
            print(f"Test failed for response: '{response}'. Error: {e}")
            return False

    with open(f"script/minimal_test_{lang}.json", encoding="utf-8") as f:
        test_data = json.load(f)
    num_tests = len(test_data)

    with tqdm(total=num_tests, position=0) as pbar:
        success_count = 0
        fail_count = 0
        for i, test_piece in enumerate(test_data):
            result = atom_test(test_piece)

            if result is True:
                success_count += 1
                pbar.set_postfix_str("█", refresh=False)
                pbar.colour = "green"
            else:
                fail_count += 1
                pbar.set_postfix_str("█", refresh=False)
                pbar.colour = "red"

            pbar.set_description(f"| Success: {success_count}, Failed: {fail_count}", refresh=True)
            pbar.update(1)
            time.sleep(0.1)  # Sleep for 0.1 seconds


def minimal_test_from_jsonl(filepath="script/data.jsonl", lang="en"):
    """
    從 jsonl 檔案執行最小測試。
    每一行應該是一個包含 'claim' 和 'label' 的 JSON 物件。
    """
    # 初始化 FactCheck 類別
    prompt = "chatgpt_prompt"
    if lang == "zh":
        prompt = "chatgpt_prompt_zh"
    factcheck = FactCheck(prompt=prompt)

    def atom_test(instance):
        response = instance["response"]
        res = factcheck.check_text(response)
        try:
            for k, v in instance["attributes"].items():
                actual_value = None
                if k == "factuality":
                    threshold = 0.8  # 設定真實性分數的閾值
                    factuality_score = res['summary'].get(k, 0.0) # 使用 .get 避免 KeyError
                    actual_value = factuality_score >= threshold
                else:
                    actual_value = res.get(k)
                
                print(f"Comparing '{k}': actual={actual_value}, expected={v}")
                assert actual_value == v
            return True
        except Exception as e:
            print(f"Test failed for response: '{response}'. Error: {e}")
            return False

    test_data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            test_data.append(json.loads(line))

    num_tests = len(test_data)
    with tqdm(total=num_tests, position=0) as pbar:
        success_count = 0
        fail_count = 0
        for i, test_piece in enumerate(test_data):
            # 將 jsonl 格式轉換為 atom_test 所需的格式
            instance_for_test = {
                "response": test_piece["claim"],
                "attributes": {
                    "factuality": test_piece["label"]
                }
            }
            result = atom_test(instance_for_test)

            if result is True:
                success_count += 1
                pbar.set_postfix_str("█", refresh=False)
                pbar.colour = "green"
            else:
                fail_count += 1
                pbar.set_postfix_str("█", refresh=False)
                pbar.colour = "red"

            pbar.set_description(f"| Success: {success_count}, Failed: {fail_count}", refresh=True)
            pbar.update(1)
            time.sleep(0.1)


if __name__ == "__main__":
    # minimal_test() 
    minimal_test_from_jsonl(filepath="script/data.jsonl")

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
DATASET = "sampled_data_100.jsonl"
# OLLAMA_MODEL = "qwen3:32b"  # 預設模型

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
    從 jsonl 檔案執行最小測試，並將結果（P、R、錯誤細節）儲存起來。
    """
    # 初始化 FactCheck 類別
    prompt = "chatgpt_prompt"
    factcheck = FactCheck(
        prompt=prompt,
        # default_model=OLLAMA_MODEL
    )

    test_data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            test_data.append(json.loads(line))

    num_tests = len(test_data)
    tp, fp, tn, fn = 0, 0, 0, 0
    error_details = []

    with tqdm(total=num_tests, position=0) as pbar:
        for i, test_piece in enumerate(test_data):
            claim = test_piece["claim"]
            ground_truth = test_piece["label"]

            res = factcheck.check_text(claim)
            factuality_score = res['summary'].get('factuality', 0.0)
            prediction = factuality_score >= THRESHOLD

            if prediction == ground_truth:
                if prediction is True:
                    tp += 1
                else:
                    tn += 1
                pbar.colour = "green"
            else:
                if prediction is True: # ground_truth is False
                    fp += 1
                else: # prediction is False, ground_truth is True
                    fn += 1
                error_details.append({
                    "claim": claim,
                    "ground_truth": ground_truth,
                    "prediction": prediction,
                    "factuality_score": factuality_score
                })
                pbar.colour = "red"
            
            pbar.set_description(f"| TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}", refresh=True)
            pbar.update(1)
            time.sleep(0.1)

    # 計算 P, R, F1
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # 準備儲存結果
    results = {
        "metrics": {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "total_samples": num_tests
        },
        "error_details": error_details
    }

    # 將結果寫入檔案
    with open(f"{DATASET}_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\nTest finished. Results saved to {DATASET}_results.json")
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1-Score: {f1_score:.2f}")


if __name__ == "__main__":
    # minimal_test() 
    minimal_test_from_jsonl(filepath=f"script/{DATASET}", lang="en")

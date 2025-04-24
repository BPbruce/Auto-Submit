from openai import OpenAI
import json
import time
import re

client = OpenAI(
    api_key="sk-5a29f90dd2f64e35af69ae526ce5a95c",
    base_url="https://api.deepseek.com/v1",
    timeout=20  
)

def extract_json(content):
    """尝试从文本中提取JSON内容"""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        return {"Result": "解析失败", "error": "Invalid JSON format"}

def extract_tokens(text):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # 适用于信息提取
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个区块链数据分析助手。请按照以下步骤解析用户提供的文本：\n"
                        "1. 提取文本中所有涉及的加密货币代币（Token），包括其名称和代码（如 BTC、ETH）。\n"
                        "2. 确保输出为严格的 JSON 格式，格式如下：\n"
                        '{\n'
                        '    "Result": "成功",\n'
                        '    "Tokens": [\n'
                        '        {"Name": "代币名称", "Symbol": "代币代码"},\n'
                        '        {"Name": "代币名称", "Symbol": "代币代码"}\n'
                        '    ]\n'
                        '}\n'
                        "3. 若文本未涉及任何代币，请返回：\n"
                        '{\n'
                        '    "Result": "无代币信息",\n'
                        '    "Tokens": []\n'
                        '}\n'
                        "请严格确保输出为合法 JSON，不要有任何额外文本。"
                    )
                },
                {"role": "user", "content": text}
            ]
        )
        
        content = response.choices[0].message.content
        return extract_json(content)
    except Exception as e:
        return {"Result": "解析失败", "error": str(e)}

# 测试用例
if __name__ == "__main__":      
    test_news = """
币安发布公告宣布，币安将于 2025 年 03 月 28 日 11:00（东八区时间）停止交易并下架以下币种：
Aergo (AERGO)、AirSwap (AST)、BurgerCities (BURGER)、COMBO (COMBO) 及 Linear Finance (LINA)。
"""
    
    start_time = time.time()
    token_result = extract_tokens(test_news)
    
    try:
        valid_json = json.dumps(token_result, ensure_ascii=False, indent=4)
        print(valid_json)
    except Exception as e:
        print('{"Result": "格式错误", "error": "Invalid JSON format"}')
    
    print(f"耗时：{time.time()-start_time:.2f}秒")

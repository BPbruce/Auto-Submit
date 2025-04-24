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
        # 使用正则表达式匹配JSON结构
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        return {"Result": "解析失败", "error": "Invalid JSON format"}

def semantic_analysis(text):
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",  # 改为深度思考模型
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个区块链项目分析师。\n"
                         "帮我把代币名字全部抽取出来，单独列出来"
                    )
                },
                {"role": "user", "content": text}
            ]
        )
        
        # 获取最终回答内容
        content = response.choices[0].message.content
        # 获取思维链内容（可根据需要记录或展示）
        reasoning_content = response.choices[0].message.reasoning_content
        
        return extract_json(content)
    except Exception as e:
        return {"Result": "解析失败", "error": str(e)}

# 测试用例
if __name__ == "__main__":      
    test_news = """
币安发布公告宣布，币安将于 2025 年 03 月 28 日 11:00（东八区时间）停止交易并下架以下币种：Aergo (AERGO) 、AirSwap (AST) 、BurgerCities (BURGER) 、COMBO (COMBO) 及 Linear Finance (LINA)🌌
"""
    
    start_time = time.time()
    analysis_result = semantic_analysis(test_news)
    
    try:
        valid_json = json.dumps(analysis_result, ensure_ascii=False, indent=4)
        print(valid_json)
    except Exception as e:
        print('{"Result": "格式错误", "error": "Invalid JSON format"}')
    
    print(f"耗时：{time.time()-start_time:.2f}秒")
from datasets import load_dataset

# 加载数据集
ds = load_dataset("Conard/fortune-telling")

# 查看数据集结构
print(ds)
print(ds["train"][0])  # 查看第一条数据
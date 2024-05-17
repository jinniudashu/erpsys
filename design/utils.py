import pandas as pd

# 读取 Excel 文件
def read_excel(file_path: str, sheet_name: str,) -> pd.DataFrame:
    
    df = pd.read_excel(file_path, engine="openpyxl")
    # 显示 DataFrame 的前几行数据
    print(df.head())
    return df


import pandas as pd
from database.db_manager import engine

def get_eda_statistics():
    # 读取 dataset 表的前 1000 行进行分析
    df = pd.read_sql("SELECT * FROM dataset LIMIT 1000", engine)
    summary = {
        "columns": df.columns.tolist(),
        "stats": df.describe(include='all').to_dict(),
        "null_counts": df.isnull().sum().to_dict()
    }
    return str(summary)
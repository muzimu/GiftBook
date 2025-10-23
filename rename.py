import os
import glob
from pathlib import Path
import re

def rename_jpg_files(directory="image"):
    """
    将指定目录下的所有jpg图片重命名为lzj-1.jpg, lzj-2.jpg等格式
    按照原文件名排序
    """
    # 获取目录下所有的jpg文件（包括.JPG等大小写变体）
    jpg_files = glob.glob(os.path.join(directory, "*.jpg"))
    
    def sort_key(filename):
        # 提取文件名中的所有数字，组成列表（用于排序）
        numbers = re.findall(r'\d+', filename)
        return [int(num) for num in numbers], filename  # 先按数字排序，再按文件名排序
    
    # 按文件名排序
    jpg_files = sorted(jpg_files, key=sort_key)
    
    print(f"找到 {len(jpg_files)} 个jpg文件")
    
    # 重命名文件
    for i, old_path in enumerate(jpg_files, 1):
        # 获取文件扩展名（保持原大小写）
        ext = os.path.splitext(old_path)[1].lower()  # 统一转为小写
        
        # 构建新文件名
        new_filename = f"lzj-{i}{ext}"
        new_path = os.path.join(directory, new_filename)
        
        # 重命名文件
        try:
            os.rename(old_path, new_path)
            print(f"重命名: {os.path.basename(old_path)} -> {new_filename}")
        except OSError as e:
            print(f"错误: 无法重命名 {old_path} -> {new_filename}: {e}")
    
    print("重命名完成！")

rename_jpg_files()
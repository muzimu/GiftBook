import re
import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
from main import recognize  # 导入您原有的识别函数
from pathlib import Path

# 确保必要目录存在
os.makedirs('output', exist_ok=True)
os.makedirs('image', exist_ok=True)  # 确保image文件夹存在

def append_gifts_to_csv(gifts_df, csv_file='output/template.csv'):
    """将纠正后的礼金信息追加写入CSV文件"""
    import csv
    
    # 转换DataFrame为字典列表
    gifts = gifts_df.to_dict('records')
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        # 定义CSV字段名，与现有文件保持一致
        fieldnames = [
            '时间', '分类', '二级分类', '类型', '金额', 
            '账户1', '账户2', '备注', '账单标记', 
            '手续费', '优惠券', '标签', '账单图片'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # 如果文件为空，写入表头
        if os.path.getsize(csv_file) == 0:
            writer.writeheader()
        
        # 遍历并写入CSV
        for gift in gifts:
            row = {
                '时间': datetime.now().strftime("%Y/%m/%d"),
                '分类': '礼金',
                '二级分类': '',
                '类型': '收入',
                '金额': gift['value'],
                '账户1': '',
                '账户2': '',
                '备注': f'{gift["name"]} {gift["remark"]}',
                '账单标记': '',
                '手续费': '',
                '优惠券': '',
                '标签': '',
                '账单图片': gift['img']
            }
            writer.writerow(row)
    
    return True

def get_image_files():
    """获取image文件夹下的所有图片文件"""
    import os
    from pathlib import Path
    import re  # 确保导入了re模块
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    image_files = []
    
    for file in os.listdir('image'):
        file_path = os.path.join('image', file)
        if os.path.isfile(file_path) and Path(file).suffix.lower() in image_extensions:
            image_files.append(file)
    
    # 提取文件名中的数字作为排序依据（如无数字则按原字符串排序）
    def sort_key(filename):
        # 提取文件名中的所有数字，组成列表（用于排序）
        numbers = re.findall(r'\d+', filename)
        # 将生成器改为列表，解决比较问题
        return [int(num) for num in numbers], filename  # 先按数字排序，再按文件名排序
    
    image_files_sorted = sorted(image_files, key=sort_key)
    return image_files_sorted

def main():
    st.title("礼金识别与管理系统")
    st.write("系统将自动读取/image文件夹中的图片，您可以选择图片进行处理和修正。")
    
    # 获取并显示image文件夹中的图片
    image_files = get_image_files()
    
    if not image_files:
        st.warning("在/image文件夹中未找到任何图片文件，请先添加图片到该文件夹")
        return
    
    # 侧边栏显示图片选择
    st.sidebar.subheader("选择要处理的图片")
    selected_image = st.sidebar.selectbox(
        "图片列表",
        image_files
    )
    
    # 显示选中的图片
    if selected_image:
        image_path = os.path.join('image', selected_image)
        st.subheader(f"当前图片: {selected_image}")
        st.image(image_path, width='stretch')
        
        # 处理图片
        if st.button("开始识别"):
            with st.spinner("正在识别图片中的礼金信息..."):
                try:
                    # 调用AI识别函数
                    img_url = f"http://t44p80tuo.hd-bkt.clouddn.com/GiftBook/{selected_image}"
                    gifts = recognize(image_path, img_url)
                    
                    # 转换为DataFrame以便编辑
                    gifts_df = pd.DataFrame(gifts)
                    
                    # 保存到session_state以便后续处理
                    st.session_state['current_image'] = selected_image
                    st.session_state['gifts_df'] = gifts_df
                    
                    st.success("识别完成，请检查并修正信息")
                    
                except Exception as e:
                    st.error(f"识别过程中出现错误: {str(e)}")
    
    # 批量处理选项
    st.sidebar.subheader("批量处理")
    if st.sidebar.button("处理所有未处理图片"):
        # 这里可以添加逻辑判断哪些图片已经处理过
        with st.spinner(f"正在批量处理{len(image_files)}张图片..."):
            # 简单实现：处理所有图片
            for img_file in image_files:
                try:
                    img_path = os.path.join('image', img_file)
                    img_url = f"http://t44p80tuo.hd-bkt.clouddn.com/GiftBook/{img_file}"
                    # if 
                    gifts = recognize(img_path, img_url)
                    
                    # 直接保存到CSV，不进行人工审核
                    # 实际应用中可能需要先存储到临时区域等待审核
                    gifts_df = pd.DataFrame(gifts)
                    append_gifts_to_csv(gifts_df)
                    
                    st.sidebar.success(f"已处理: {img_file}")
                except Exception as e:
                    st.sidebar.error(f"处理{img_file}出错: {str(e)}")
            
            st.success("所有图片处理完成")
    
    # 如果已经有识别结果，显示编辑表格
    if 'gifts_df' in st.session_state:
        st.subheader(f"《{st.session_state['current_image']}》识别结果（可直接点击单元格编辑）")
        
        # 使用data_editor让用户可以编辑
        edited_df = st.data_editor(
            st.session_state['gifts_df'],
            column_config={
                "name": "姓名",
                "value": "金额",
                "remark": "备注",
                "img": "图片链接"
            },
            use_container_width=True,
            num_rows="fixed"
        )
        
        # 保存修改后的结果
        st.session_state['edited_df'] = edited_df
        
        # 导出到CSV
        if st.button("确认并导出到CSV"):
            with st.spinner("正在导出数据..."):
                try:
                    result = append_gifts_to_csv(st.session_state['edited_df'])
                    if result:
                        st.success("数据已成功导出到CSV文件")
                        
                        # 提供下载链接
                        with open('output/template.csv', 'rb') as f:
                            st.download_button(
                                label="下载CSV文件",
                                data=f,
                                file_name='gift_records.csv',
                                mime='text/csv'
                            )
                except Exception as e:
                    st.error(f"导出过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()
    
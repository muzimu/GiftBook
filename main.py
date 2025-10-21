import re
import main as st
import pandas as pd
import os
import json
from datetime import datetime
from recognize import recognize
from pathlib import Path
import piexif  # 用于读取EXIF信息
from PIL import Image

# 确保必要目录存在
os.makedirs('output', exist_ok=True)
os.makedirs('image', exist_ok=True)
os.makedirs('processed_data', exist_ok=True)  # 用于保存处理记录

# 加载处理状态记录
def load_processed_status():
    """加载已处理图片的状态记录"""
    if os.path.exists('processed_status.json'):
        with open('processed_status.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 保存处理状态记录
def save_processed_status(status):
    """保存已处理图片的状态记录"""
    with open('processed_status.json', 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

# 加载单张图片的处理数据
def load_image_data(image_name):
    """加载单张图片的处理数据"""
    file_path = f'processed_data/{image_name}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return pd.DataFrame(data)
    return None

# 保存单张图片的处理数据
def save_image_data(image_name, df):
    """保存单张图片的处理数据"""
    file_path = f'processed_data/{image_name}.json'
    data = df.to_dict('records')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_gifts_to_csv(gifts_df, csv_file='output/template.csv'):
    """将纠正后的礼金信息追加写入CSV文件"""
    import csv
    
    gifts = gifts_df.to_dict('records')
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        fieldnames = [
            '时间', '分类', '二级分类', '类型', '金额', 
            '账户1', '账户2', '备注', '账单标记', 
            '手续费', '优惠券', '标签', '账单图片'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if os.path.getsize(csv_file) == 0:
            writer.writeheader()
        
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
    """获取image文件夹下的所有图片文件并按数字排序"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    image_files = []
    
    for file in os.listdir('image'):
        file_path = os.path.join('image', file)
        if os.path.isfile(file_path) and Path(file).suffix.lower() in image_extensions:
            image_files.append(file)
    
    def sort_key(filename):
        numbers = re.findall(r'\d+', filename)
        return [int(num) for num in numbers], filename
    
    return sorted(image_files, key=sort_key)

def fix_image_rotation(image_path):
    """根据EXIF信息自动纠正图片旋转角度"""
    with Image.open(image_path) as img:
        try:
            # 读取EXIF数据
            exif_data = img.getexif()
            
            if exif_data is not None:
                # 寻找方向标记（EXIF标签274对应方向）
                orientation_tag = 274
                if orientation_tag in exif_data:
                    orientation = exif_data[orientation_tag]
                    
                    # 根据方向标记旋转图片
                    if orientation == 1:
                        # 正常方向，无需旋转
                        return img.copy()
                    elif orientation == 2:
                        # 水平翻转
                        return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    elif orientation == 3:
                        # 旋转180度
                        return img.rotate(180, expand=True)
                    elif orientation == 4:
                        # 垂直翻转
                        return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                    elif orientation == 5:
                        # 水平翻转后旋转90度
                        return img.rotate(-90, expand=True).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    elif orientation == 6:
                        # 旋转270度（顺时针90度）
                        return img.rotate(-90, expand=True)
                    elif orientation == 7:
                        # 水平翻转后旋转270度
                        return img.rotate(90, expand=True).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                    elif orientation == 8:
                        # 旋转90度
                        return img.rotate(90, expand=True)
            
            # 无旋转信息或无法识别时，返回原图
            return img.copy()
            
        except (AttributeError, KeyError, IndexError):
            # 处理无EXIF信息的情况
            return img.copy()

def rotate_image_manually(img, rotation_angle=0):
    """手动旋转图片（用于用户调整）"""
    if rotation_angle == 90:
        return img.rotate(90, expand=True)
    elif rotation_angle == 180:
        return img.rotate(180, expand=True)
    elif rotation_angle == 270:
        return img.rotate(270, expand=True)
    else:
        return img.copy()

def main():
    st.title("礼金识别与管理系统")
    st.write("系统将自动读取/image文件夹中的图片，支持单张/批量处理及结果修正")
    
    # 加载处理状态
    processed_status = load_processed_status()
    image_files = get_image_files()
    
    if not image_files:
        st.warning("在/image文件夹中未找到任何图片文件，请先添加图片到该文件夹")
        return
    
    # 侧边栏显示图片选择和状态
    st.sidebar.subheader("图片处理状态")
    # 显示图片列表及处理状态
    for img in image_files:
        status = "✅ 已处理" if processed_status.get(img, False) else "❌ 未处理"
        st.sidebar.text(f"{img}: {status}")
    
    # 选择要处理的图片
    selected_image = st.sidebar.selectbox(
        "选择图片进行操作",
        image_files
    )
    
    # 检测图片切换并重置状态
    if 'last_selected_image' not in st.session_state:
        st.session_state['last_selected_image'] = selected_image
        st.session_state['manual_rotation'] = 0  # 手动旋转角度
    elif st.session_state['last_selected_image'] != selected_image:
        # 清除上一张图片的结果状态
        for key in ['gifts_df', 'edited_df', 'current_image', 'manual_rotation']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state['last_selected_image'] = selected_image
        st.session_state['manual_rotation'] = 0
        st.rerun()
    
    # 显示选中的图片及旋转控制
    if selected_image:
        image_path = os.path.join('image', selected_image)
        st.subheader(f"当前图片: {selected_image}")
        
        # 先自动纠正EXIF旋转，再应用手动旋转
        auto_corrected_img = fix_image_rotation(image_path)
        final_img = rotate_image_manually(auto_corrected_img, st.session_state['manual_rotation'])
        
        # 手动旋转控制按钮
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("向左旋转 (90°)"):
                st.session_state['manual_rotation'] = (st.session_state['manual_rotation'] - 90) % 360
                st.rerun()
        with col2:
            if st.button("向右旋转 (90°)"):
                st.session_state['manual_rotation'] = (st.session_state['manual_rotation'] + 90) % 360
                st.rerun()
        with col3:
            if st.button("重置旋转"):
                st.session_state['manual_rotation'] = 0
                st.rerun()
        
        # 显示处理后的图片
        st.image(final_img, width='stretch')
        
        # 检查是否有已保存的数据
        saved_data = load_image_data(selected_image)
        if saved_data is not None:
            st.info("检测到该图片已有处理记录，可直接编辑")
            st.session_state['gifts_df'] = saved_data
            st.session_state['current_image'] = selected_image
        
        # 处理图片按钮（仅未处理或需要重新处理时显示）
        if st.button("开始识别" if not processed_status.get(selected_image, False) else "重新识别"):
            with st.spinner("正在识别图片中的礼金信息..."):
                try:
                    img_url = f"http://t44p80tuo.hd-bkt.clouddn.com/GiftBook/{selected_image}"
                    gifts = recognize(image_path, img_url)
                    gifts_df = pd.DataFrame(gifts)
                    
                    # 保存数据和状态
                    st.session_state['gifts_df'] = gifts_df
                    st.session_state['current_image'] = selected_image
                    save_image_data(selected_image, gifts_df)
                    processed_status[selected_image] = True
                    save_processed_status(processed_status)
                    
                    st.success("识别完成，请检查并修正信息")
                    
                except Exception as e:
                    st.error(f"识别过程中出现错误: {str(e)}")
    
    # 批量处理选项
    st.sidebar.subheader("批量处理")
    unprocessed = [img for img in image_files if not processed_status.get(img, False)]
    st.sidebar.text(f"待处理图片: {len(unprocessed)}张")
    
    if st.sidebar.button(f"批量处理{len(unprocessed)}张未处理图片") and unprocessed:
        with st.spinner(f"正在批量处理{len(unprocessed)}张图片..."):
            progress_bar = st.progress(0)
            for i, img_file in enumerate(unprocessed):
                try:
                    img_path = os.path.join('image', img_file)
                    img_url = f"http://t44p80tuo.hd-bkt.clouddn.com/GiftBook/{img_file}"
                    gifts = recognize(img_path, img_url)
                    gifts_df = pd.DataFrame(gifts)
                    
                    # 保存数据但不直接导出，等待后续修正
                    save_image_data(img_file, gifts_df)
                    processed_status[img_file] = True
                    save_processed_status(processed_status)
                    
                    st.sidebar.success(f"已处理: {img_file}")
                except Exception as e:
                    st.sidebar.error(f"处理{img_file}出错: {str(e)}")
                
                progress_bar.progress((i + 1) / len(unprocessed))
            
            st.success("批量处理完成，可在图片列表中选择进行修正")
    
    # 显示和编辑识别结果
    if 'gifts_df' in st.session_state:
        current_img = st.session_state['current_image']
        st.subheader(f"《{current_img}》识别结果（可直接点击单元格编辑）")
        
        edited_df = st.data_editor(
            st.session_state['gifts_df'],
            column_config={
                "name": "姓名",
                "value": "金额",
                "remark": "备注",
                "img": "图片链接"
            },
            width='stretch',
            num_rows="fixed"
        )
        
        # 保存修改
        if st.button("保存修改"):
            st.session_state['edited_df'] = edited_df
            save_image_data(current_img, edited_df)
            st.success("修改已保存")
        
        # 导出到CSV
        if st.button("导出到CSV"):
            with st.spinner("正在导出数据..."):
                try:
                    # 使用最新的修改后的数据
                    df_to_export = edited_df if 'edited_df' in st.session_state else st.session_state['gifts_df']
                    result = append_gifts_to_csv(df_to_export)
                    if result:
                        st.success("数据已成功导出到CSV文件")
                        
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

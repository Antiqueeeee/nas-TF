import shutil
import gradio as gr
import os
from datetime import datetime
from config import *
import PIL.Image

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

def save_files(file_infos):
    saved_files = list()
    msg = str()
    current_date = datetime.now().strftime("%Y/%m/%d")
    date_dir = os.path.join(STORAGE_PATH, current_date)
    if not os.path.exists(date_dir):
        os.makedirs(date_dir)
    try:
        # 检查file_infos是否为列表
        if not isinstance(file_infos, list):
            file_infos = [file_infos]
        
        for file in file_infos:
            file_path = os.path.join(date_dir, os.path.basename(file.name))
            shutil.copy(file.name, file_path)
            saved_files.append(file_path)
            msg += f"📦 文件上传成功 ：{os.path.basename(file.name)} \n"
    
    except Exception as e:
        msg += f"❌ 文件上传失败: {os.path.basename(file.name)}\n{str(e)}\n"
    return msg

def get_media_files(directory):
    """
    获取指定目录下的所有媒体文件
    支持图片和视频格式
    """
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    extensions = image_extensions + video_extensions
    media_files = list()
    # 遍历所有子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            full_path = os.path.join(root, file)
            if ext in extensions:
                media_files.append(full_path)
    return media_files

# 创建Gradio界面
with gr.Blocks(title=INDEX_TITLE) as demo:
    with gr.Tabs():
        # 第一个标签页：文件上传
        with gr.TabItem("文件上传", id="upload"):
            gr.Markdown(INDEX_MARKDOWN)
            with gr.Row():
                file_input = gr.File(label="上传文件", file_count="multiple")  # 支持多文件上传
                submit_button = gr.Button("上传")
            output_text = gr.Textbox(label="上传结果")

            # 当提交按钮被点击时，调用save_files函数，并更新输出文本框
            submit_button.click(save_files, inputs=file_input, outputs=output_text)
        with gr.TabItem("库存浏览", id="images"):
            # 创建图库展示
            gallery = gr.Gallery(
                label="存储的图片",
                show_label=False,
                columns=4,  # 每行显示4张图片
                height="auto"
            )
            
            # 添加刷新按钮
            refresh_button = gr.Button("刷新图片列表")
            
            # 绑定刷新事件
            def refresh_collections():
                return get_media_files(STORAGE_PATH)
            
            refresh_button.click(
                fn=refresh_collections, 
                outputs=gallery
            )
            
            # 初始加载图片
            demo.load(refresh_collections, outputs=gallery)

# 运行界面
demo.launch(server_name=SERVER_NAME, server_port=SERVER_PORT, share=True)

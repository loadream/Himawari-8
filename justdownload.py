#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime
import requests
from PIL import Image

# 保存路径
SAVE_DIR = "/home/Earth/himawari"   # 你可以改路径
os.makedirs(SAVE_DIR, exist_ok=True)

# 瓦片配置
TILE_COUNT = 4 # 瓦片数量改为 4x4
TILE_SIZE = 550

# ===============================
#  计算最新时间（UTC - 30min）
# ===============================
def get_latest_timestamp():
    utc_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
    ts = utc_time.strftime("%Y/%m/%d/%H%M")
    ts_list = list(ts)
    # 分钟向下取整（最后一位变 0），符合 10 分钟间隔数据
    ts_list[-1] = "000"
    return "".join(ts_list)


# ===============================
#  下载一张瓦片
# ===============================
def download_tile(ts, x, y):
    filename = f"tile_{x}_{y}.png"
    # 瓦片 URL 结构
    url = f"https://himawari.asia/img/D531106/4d/{TILE_SIZE}/{ts}_{x}_{y}.png"

    try:
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status() # 检查 HTTP 错误 (如 404)

            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return filename
    except requests.exceptions.HTTPError as http_err:
        print(f"下载失败 (HTTP 错误): {http_err} for URL {url}")
        return None
    except Exception as e:
        print(f"下载错误: {e} for URL {url}")
        return None

# ===============================
#  清理瓦片缓存
# ===============================
def clean_tile_cache():
    """删除当前工作目录中所有可能的瓦片文件。"""
    # 遍历所有可能的 16 个瓦片文件名
    for y in range(TILE_COUNT):
        for x in range(TILE_COUNT):
            file_name = f"tile_{x}_{y}.png"
            try:
                # 只删除当前目录下存在的瓦片文件
                if os.path.exists(file_name):
                    os.remove(file_name)
                    # print(f"已删除缓存瓦片: {file_name}")
            except OSError as e:
                print(f"删除瓦片缓存失败: {file_name} - {e}")

# ===============================
#  处理瓦片下载、拼接和保存
# ===============================
def process_and_clean_tiles(timestamp, output_file):
    
    tiles_data = [] # 存储 (file, x, y)
    success = True
    
    # 1. 下载瓦片 (4x4)
    for y in range(TILE_COUNT):
        for x in range(TILE_COUNT):
            print(f"正在下载瓦片: ({x}, {y})")
            file = download_tile(timestamp, x, y)
            
            if file:
                tiles_data.append((file, x, y))
            else:
                # 任何一个瓦片缺失都判定失败
                print(f"瓦片缺失: ({x}, {y})，放弃本次拼接")
                success = False
                break
        if not success:
            break

    # 2. 拼接和保存
    if success:
        # 创建最终图片
        final_img = Image.new("RGB", (TILE_SIZE * TILE_COUNT, TILE_SIZE * TILE_COUNT))
        
        for file, x, y in tiles_data:
            img = Image.open(file)
            final_img.paste(img, (x * TILE_SIZE, y * TILE_SIZE))
            
        final_img.save(output_file, "JPEG")
        print("保存成功：", output_file)

    # 3. 清理瓦片缓存
    clean_tile_cache()
    
    return success


# ===============================
#  删除 1 天前图片
# ===============================
def clean_old_files():
    """清理 SAVE_DIR 中超过 1 天的日期文件夹。"""
    now = datetime.datetime.utcnow()
    if not os.path.exists(SAVE_DIR):
        print(f"保存目录不存在: {SAVE_DIR}")
        return

    for folder in os.listdir(SAVE_DIR):
        full_path = os.path.join(SAVE_DIR, folder)
        if os.path.isdir(full_path):
            try:
                folder_time = datetime.datetime.strptime(folder, "%Y%m%d")
                if (now - folder_time).days >= 1:
                    # 删除旧文件夹
                    os.system(f"rm -rf {full_path}")
                    print(f"已删除旧文件夹: {full_path}")
            except ValueError:
                # 忽略不是日期格式的文件夹名
                pass
            except Exception as e:
                 print(f"清理旧文件时发生错误: {e}")


# ===============================
#  主函数
# ===============================
def main():
    timestamp = get_latest_timestamp()
    print("当前下载时间：", timestamp)

    # 目标保存位置
    date_folder = datetime.datetime.utcnow().strftime("%Y%m%d")
    save_path = os.path.join(SAVE_DIR, date_folder)
    os.makedirs(save_path, exist_ok=True)

    output_file = os.path.join(save_path, timestamp.replace("/", "") + ".jpg")

    # 执行下载、拼接、保存和瓦片清理，只调用一次
    process_and_clean_tiles(timestamp, output_file)
    
    # 清理旧的日期文件夹
    clean_old_files()


if __name__ == "__main__":
    main()

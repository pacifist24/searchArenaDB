import cv2
import numpy as np
import os
from PIL import Image
import json

# OpenCVで画像を読み込む
def read_image(path):

    # Pillowで画像ファイルを開く
    pil_img = Image.open(path)

    # PillowからNumPyへ変換
    img = np.array(pil_img)

    # カラー画像のときは、RGBからBGRへ変換する
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img

# テンプレート画像とキャラ画像(中央部)の一致率を計算する
# テンプレート画像が大きいほど、min_sizeとmax_sizeの差が大きいほど処理に時間がかかる
def calc_match_rate(template_image_path, min_size, max_size):
    # 検索元／先画像を読み込み
    template = read_image(template_image_path)

    files_dir = [f for f in os.listdir('images') if os.path.isdir(os.path.join('images', f))]
    result_list = []

    for character_name in files_dir:
        character_image_files = os.listdir('images/' + character_name)
        max_match_rate = 0
        best_size = 0

        for character_image_file in character_image_files:
            # キャラ画像から中央だけを選択して使う（端はLVや★等でごちゃごちゃするため）
            image = read_image('images/' + character_name + '/' + os.path.split(character_image_file)[1])[30:100, 30:100]

            # キャラ画像の大きさを変更しながら一致率を計算する
            for size in range(min_size, max_size):
                image_resize = cv2.resize(image, (size, size))
                # OpenCVで画像部分一致を検索する
                result = cv2.matchTemplate(image_resize, template, cv2.TM_CCORR_NORMED)

                # 最も類似度が高い位置と低い位置を取得する
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_match_rate < max_val:
                    max_match_rate = max_val
                    best_size = size

        result_dic = {"name": character_name, "match_rate": max_match_rate, "best_size": best_size}
        # print(result_dic)
        result_list.append(result_dic)

    # 一致率順に並び替えして返す
    result_list.sort(key=lambda val: val["match_rate"], reverse=True)
    return result_list


def search_arena_db(target_image_file, min_size_from,max_size_from,min_size_to,max_size_to):

    defence_characters = list(map(lambda x: x['name'],calc_match_rate(target_image_file,min_size_from,max_size_from)[0:5]))
    json_file = open('characters.json', encoding="utf-8")
    characters = json.load(json_file)

    order = characters['order']

    characters_position = {}
    for character in defence_characters:
        characters_position[character] = order.index(character)

    print("防衛編成")
    print(characters_position)

    print("ブラウザ操作中")
    from selenium import webdriver
    import time
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument('--headless')

    browser = webdriver.Chrome('chromedriver.exe',options=options)
    browser.get('https://www.pcrdfans.com/battle')
    header = browser.find_elements_by_class_name('ant-collapse-header')

    header[0].click() # 前衛開く
    header[1].click() # 中衛開く
    header[2].click() # 後衛開く
    time.sleep(1)

    characters = browser.find_elements_by_css_selector('div.ant-collapse-content-box>div')
    for key in characters_position.keys():
        characters[characters_position[key]].click() # 対象キャラクリック

    browser.find_element_by_class_name('battle_search_button').click() # 検索ボタンクリック
    time.sleep(2)
    search_results = browser.find_elements_by_class_name('battle_search_single_result_ctn')

    # ここでは簡単のため一番上に表示された編成を選択する
    if len(search_results) != 0:
        selected_result = search_results[0]
        print("検索結果解析中")
        selected_result.find_element_by_class_name('battle_search_result').screenshot('selected_result.png')
        print("攻め編成")
        print(list(map(lambda x: x['name'],calc_match_rate('selected_result.png',min_size_to,max_size_to)[0:5])))
    else:
        print("検索結果なし")

    browser.quit()


search_arena_db('test.png',33,36,25,35)

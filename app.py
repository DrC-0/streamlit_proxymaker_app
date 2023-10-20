import streamlit as st
import streamlit.components.v1 as components
import requests
import os
import shutil
import json
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, portrait

pics_folder_path = './pics'
dic_name = "carddic.json"
pdf_name = "proxy.pdf"

CARD_H = 84
CARD_W = 60

def main():
    ready()
    st.text("以下の形式のjsonファイルをアップロードしてください(インデントは関係なし)")
    exjson = [
    {"name":"アビスベル＝覇＝ロード","num":2},
    {"name":"鬼札アバクと鬼札王国","num":1},
    {"name":"アーテル・ゴルギーニ","num":4}
    ]
    st.json(exjson)
    uped_file = st.file_uploader("Upload json file",type="json")
    ipt = st.number_input("左および上の角からの距離",0,30,15)
    btn = st.button("Create PDF")
    if uped_file is not None and ipt is not None:
        deck_data = json.load(uped_file)
        if btn: pdfgene(deck_data=deck_data,margin=ipt)
    
def height(i,margin):
  n = i//3 + 1
  return 297 - margin - (n*CARD_H)
def width(i,margin):
  n = i%3
  return margin + (n*CARD_W)

def ready():
    if not os.path.exists(pics_folder_path):
        os.mkdir(pics_folder_path)
    else:
        shutil.rmtree(pics_folder_path)
        os.mkdir(pics_folder_path)
    if os.path.isfile(pdf_name):
        os.remove(pdf_name)

def pdfgene(deck_data,margin:int):
    
    url_list = []

    with open(dic_name) as f:
        card_data = json.load(f)

    for card_info in deck_data:
        card_name = card_info['name']
        for card_info2 in card_data:
            if card_name == card_info2['name']:
                version = card_info2['image_link'][0].split("/")[4].split(".")[0]
                num = card_info['num']
                url_list.append({"version": version, "num": num})
                break

    count = 0

    for v in url_list:
        page_url = 'https://dm.takaratomy.co.jp/wp-content/card/cardimage/'+v['version'] + '.jpg'
        r = requests.get(page_url)
        for n in range(v['num']):
            count += 1
            img_name = "{}.jpg".format(str(count).zfill(2) + '_' + v['version'] +'_' + str(n+1))
            image_path = pics_folder_path + '/' + img_name
            if r.status_code == 200:
                with open(image_path, "wb") as f:
                    f.write(r.content)
    print("download")

    page = canvas.Canvas(pdf_name, pagesize=portrait(A4))

    # 画像ファイルの挿入
    file_names = os.listdir(pics_folder_path)
    image_files = [os.path.join(pics_folder_path, file_name) for file_name in file_names if file_name.endswith(('.jpg', '.png', '.bmp'))]
    sorted_files = sorted(image_files)

    num_images = len(sorted_files)
    for i in range(0, num_images, 9):
        for j in range(9):
            if i+j < num_images:
                page.drawInlineImage(sorted_files[i+j], width(j,margin)*mm, height(j,margin)*mm,CARD_W*mm,CARD_H*mm)
        page.showPage()
    # PDFファイルとして保存
    page.save()
    print("pdfgene")
    with open(pdf_name,"rb") as f:
        st.download_button("Download",f,file_name=pdf_name)

if __name__ == "__main__":
    main()
from PIL import Image, ImageEnhance,ImageFilter
import os

path = './images'
pathOut = './images'

for file in os.listdir(path):
    img = Image.open(f"{path}/{file}")
    # edit = img.filter(ImageFilter.SHARPEN)
    edit = img.filter(ImageFilter.BLUR)
    clean_name = os.path.splitext(file)[0]
    edit.save(f"{pathOut}/{clean_name}_edited.jpg")
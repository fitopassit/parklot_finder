import time
import os
import requests


def grab_photo(url, file_name) -> str:
    img_data = requests.get(url).content
    with open(f"./photo/{file_name}.png", 'wb') as handler:
        handler.write(img_data)


def detect(url, file_name,parklotid) -> str:

    grab_photo(url, file_name)
  
    # os.system("label-studio")

    # os.system(f"C:/neural network/grab1/ python detect.py --weight 1.pt --conf 0.35 --img-size 640 --source ./photo/2022_10_23220325.png --view-img --no-trace")
    os.system(f'python detect_and_count_total.py --weight {parklotid}.pt --conf 0.35 --img-size 640 --source ./photo/{file_name}.png --no-trace')
 
def clear_directory(file_name):
    os.remove(f'./photo/{file_name}.png')
    os.remove(f'./runs/detect/exp/{file_name}.png')
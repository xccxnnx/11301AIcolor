from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import cv2
import numpy as np
from io import BytesIO
from django.http import HttpResponse

# 設定紅綠色盲的顏色範圍和替換顏色
color_ranges = {
    "red": {
        "lower1": np.array([0, 100, 100]),
        "upper1": np.array([10, 255, 255]),
        "lower2": np.array([160, 100, 100]),
        "upper2": np.array([180, 255, 255]),
        "replace_color": [0, 165, 255],  # 替換為亮橘色
    },
    "green": {
        "lower": np.array([35, 100, 100]),
        "upper": np.array([85, 255, 255]),
        "replace_color": [255, 0, 255],  # 替換為紫色
    },
}

def process_image(image):
    """處理圖像"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 處理紅色範圍
    mask_red1 = cv2.inRange(hsv, color_ranges["red"]["lower1"], color_ranges["red"]["upper1"])
    mask_red2 = cv2.inRange(hsv, color_ranges["red"]["lower2"], color_ranges["red"]["upper2"])
    mask_red = mask_red1 + mask_red2
    image[mask_red > 0] = color_ranges["red"]["replace_color"]
    
    # 處理綠色範圍
    mask_green = cv2.inRange(hsv, color_ranges["green"]["lower"], color_ranges["green"]["upper"])
    image[mask_green > 0] = color_ranges["green"]["replace_color"]
    
    return image

def index(request):
    return render(request, 'index.html')

def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        uploaded_file = request.FILES['image']
        
        # 使用 Django 文件系統儲存上傳的圖片
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        # 讀取並處理圖片
        image_path = fs.url(filename)
        image = cv2.imread(file_url[1:])  # 刪除 URL 開頭的 '/'
        
        if image is None:
            return HttpResponse('Unable to read image', status=400)

        processed_image = process_image(image)

        # 將處理後的圖片轉換為 JPEG 格式
        _, img_encoded = cv2.imencode('.jpg', processed_image)
        img_bytes = img_encoded.tobytes()

        return HttpResponse(img_bytes, content_type="image/jpeg")

    return HttpResponse("No image uploaded", status=400)

import easyocr
import os

reader = easyocr.Reader(['en'])
img_path = 'downloaded_images/doc_0_default.jpg'

if os.path.exists(img_path):
    result = reader.readtext(img_path, detail=0)
    print("OCR Result:")
    print(" ".join(result))
else:
    print("Image not found.")

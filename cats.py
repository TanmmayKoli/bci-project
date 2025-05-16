from PIL import ImageTk, Image
import random

cat_num  = random.randint(1,4)
img = f"cat_assets\{cat_num}.jpg"
with Image.open(img) as im:
    im.show()
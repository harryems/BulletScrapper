from PIL import Image
import csv

with open('colorsCode.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        print row
        name=row[1]
        code=row[2]
        print code
        im = Image.new("RGB", (50, 50), "#"+code)
        im.save(name+".jpg", "JPEG")
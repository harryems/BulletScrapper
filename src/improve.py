import csv
import glob
import os
import re
destinyDirectorie='C:/Users/carlos.espinosa/Documents/Workspace/scrapper/'

csvImproved = csv.writer(open('C:/Users/carlos.espinosa/Documents/Improved.csv', 'wb'))
# csvMediumres = csv.writer(open('C:/Users/carlos.espinosa/Documents/bulletProductMediumres.csv', 'wb'))

imagesDirectory='C:/Users/carlos.espinosa/Documents/Workspace/Downloader/images/'
index=0
with open('C:/Users/carlos.espinosa/Documents/csvOutput.csv') as csvfile:
    reader = csv.reader(csvfile)
    configurablesImages=[]
    for row in reader:
        sku=row[0]
        _type=row[2]
        CatalogSize=row[17]
        print sku
        
        if _type=='simple':
            simplesImages=[]
            for image in glob.glob(imagesDirectory+sku+"*"):
                simplesImages.append(os.path.basename(image))
                configurablesImages.append(os.path.basename(image))
            print simplesImages
            csvImproved.writerow([sku,_type,"","","","",";".join(simplesImages),"+"+simplesImages[0],simplesImages[0],simplesImages[0]])
        if _type=='configurable':
            h=''
            w=''
            l=''
            d=''
            sizes=re.findall('([-+]?\d*\.\d+|\d+)" (.{1})',CatalogSize)
            for size in sizes:
                if size[1]=='H':
                    h=size[0]
                if size[1]=='L':
                    l=size[0]
                if size[1]=='D':
                    d=size[0]
                if size[1]=='W':
                    w=size[0]                                                            
#                 print type(size)
#                 print size[0]
#                 print size[1]
                
            print configurablesImages
            if len(configurablesImages)>0:
                csvImproved.writerow([sku,_type,h,l,d,w,";".join(configurablesImages),"+"+configurablesImages[0],configurablesImages[0],configurablesImages[0]])
            configurablesImages=[]
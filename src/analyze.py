import glob
from bs4 import BeautifulSoup
import csv

destinyDirectorie='C:/Users/carlos.espinosa/Documents/Workspace/scrapper/'
csvHires = csv.writer(open('C:/Users/carlos.espinosa/Documents/bulletProductHires2.csv', 'wb'))
csvMediumres = csv.writer(open('C:/Users/carlos.espinosa/Documents/bulletProductMediumres2.csv', 'wb'))
csvOutput = csv.writer(open('C:/Users/carlos.espinosa/Documents/csvOutput2.csv', 'wb'))
index=0
total=len(glob.glob(destinyDirectorie+"*"))
for fileName in glob.glob(destinyDirectorie+"*"):
    print fileName
    index+=1
    print str(index) + " of "+str(total)
    soup = BeautifulSoup(open(fileName))
    breadcrumb=[]
    categories=soup.find('div',{'id':'breadcrumb'})
    if categories:
        for _a in categories.findAll('a'):
            breadcrumb.append(_a.text.replace('\\n','').strip())
    breadcrumb=breadcrumb[2:]
    masterCartonCasePack=soup.find('span',{'id':'masterCartonCasePack'}).text.replace('\\n','').strip() if soup.find('span',{'id':'masterCartonCasePack'}) else ''
    masterCartonWeight=soup.find('span',{'id':'masterCartonDimension-Weight'}).text.replace('\\n','').strip() if soup.find('span',{'id':'masterCartonDimension-Weight'}) else ''
    masterCartonHeight=soup.find('span',{'id':'masterCartonDimension-Height'}).text.replace('\\n','').strip() if soup.find('span',{'id':'masterCartonDimension-Height'}) else ''
    masterCartonWidth=soup.find('span',{'id':'masterCartonDimension-Width'}).text.replace('\\n','').strip() if soup.find('span',{'id':'masterCartonDimension-Width'}) else ''
    masterCartonDepth=soup.find('span',{'id':'masterCartonDimension-Depth'}).text.replace('\\n','').strip() if soup.find('span',{'id':'masterCartonDimension-Depth'}) else ''
    if not soup.find('input',{'id':'itemId'}):
        continue
    sku=soup.find('input',{'id':'itemId'})['value']
    
    productName=soup.find('div',{'class':'product-details-right'}).find('h1').text.replace('\\n','').strip()
#     print productName
    
    colors=[]
    for img in soup.find('ul',{'class':'bxslider'}).findAll('li'):
        code= img.find('a')['id'].replace('productImageLink_','').split('_')[0]
        colors.append(code)
        imgUrlmedium=img.find('a').find('img')['data-src']
        imgNameMedium=imgUrlmedium.split('/')[-2]+".jpg"
        imgUrlHires= imgUrlmedium.replace('medium','hires')
        imgNameHires=imgUrlHires.split('/')[-2]+".jpg"
    
        csvHires.writerow([imgUrlHires,imgNameHires])
        csvMediumres.writerow([imgUrlmedium,imgNameMedium])
    colors=list(set(colors))
    colorsCode=[]
    
    for color in colors:
        try:
            name=soup.find('span',{'id':'color_swatch_box_'+color+'_text'}).text
            colorHex=soup.find('a',{'id':'color_swatch_box_'+color}).find('span')['style']
            colorsCode.append(color)
            datason=[color.replace('\\n','').strip(),colorHex.replace('\\n','').strip(),productName,"simple",name.replace('\\n','').strip()]
            csvOutput.writerow(datason)
        except:
            continue
    dataFather=[sku,"",productName,"configurable","",",".join(colorsCode),"/".join(breadcrumb),masterCartonCasePack,masterCartonWeight,masterCartonHeight,masterCartonWidth,masterCartonDepth]
    csvOutput.writerow(dataFather)
    #print colorsCode 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import csv

driver = webdriver.Firefox()
destinyDirectorie='C:/Users/carlos.espinosa/Documents/Workspace/scrapper/'

# csvHires = csv.writer(open('C:/Users/carlos.espinosa/Documents/bulletProductHires.csv', 'wb'))
# csvMediumres = csv.writer(open('C:/Users/carlos.espinosa/Documents/bulletProductMediumres.csv', 'wb'))


index=0
with open('C:/Users/carlos.espinosa/Documents/bulletProductList.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        ItemNo= row[0]
        index+=1
        if index <=944:
            continue
        try:
            print index
            driver.get("http://www.pcna.com/Bullet/en-us")
            elem = driver.find_element_by_name("SearchPhraseTextBox")
            elem.clear()
            sku=ItemNo
            elem.send_keys(sku)
            send=driver.find_element_by_id("SearchSubmitButton")
            send.click()
            print driver.current_url
            soup = BeautifulSoup(driver.page_source)
            categories=soup.find('div',{'id':'breadcrumb'})
            if categories:
                print categories.text
            with open(destinyDirectorie+sku+".html", "w") as text_file:
                text_file.write(repr(soup.prettify())) 
            colors=[]
            for img in soup.find('ul',{'class':'bxslider'}).findAll('li'):
                code= img.find('a')['id'].replace('productImageLink_','').split('_')[0]
                colors.append(code)
                imgUrlmedium=img.find('a').find('img')['data-src']
                imgNameMedium=imgUrlmedium.split('/')[-2]+".jpg"
                imgUrlHires= imgUrlmedium.replace('medium','hires')
                imgNameHires=imgUrlHires.split('/')[-2]+".jpg"
            
#                 csvHires.writerow([imgUrlHires,imgNameHires])
#                 csvMediumres.writerow([imgUrlmedium,imgNameMedium])
            colors=list(set(colors))
            colorsCode=[]
            for color in colors:
                name=soup.find('span',{'id':'color_swatch_box_'+color+'_text'}).text
                colorsCode.append({'code':color,'name':name})
            print colorsCode
        except:
            next

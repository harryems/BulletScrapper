import MySQLdb
import urllib2
from bs4 import BeautifulSoup
import xmlrpclib
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from collections import defaultdict
from utilities.downloader import Downloader
from shutil import copyfile
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os.path import basename
import time
#import csv
import ftplib
import unicodecsv as csv
import re
import ntpath    
    
client = None
session = None
conn= None
hiresDriectory='C:/Users/carlos.espinosa/Documents/Workspace/data/scrapping/bullet/images/hires/' 
mediumDriectory='C:/Users/carlos.espinosa/Documents/Workspace/data/scrapping/bullet/images/mediumres/' 


#*******readed lists***********
currentSimpleList= []
currentConfigurableList = []
feedSimpleList=[]
feedConfigurableList=[]

#*******To do lists**********
configurablesToCreate=[]
configurablesToDisable=[]

simplesToCreate=[]
simplesToDisable=[]

def sendFile(_file,body):
    server = smtplib.SMTP('secure.emailsrvr.com')
    server.login('carlos.espinosa@eximagen.com.mx', "Temporal")

    
    
    
    
    msg = MIMEMultipart(
        From='carlos.espinosa@eximagen.com.mx',
        To=COMMASPACE.join(['carlos.espinosa@eximagen.com.mx','carlos.espinosa@outlook.com']),
        Date=formatdate(localtime=True),
        Subject='new products'
    )
    text=body
    
    msg.attach(MIMEText(text))

#     for f in files or []:
    with open(_file, "rb") as fil:
        msg.attach(MIMEApplication(
            fil.read(),
            Content_Disposition='attachment; filename="%s"' % basename(_file),
            Name=basename(_file)
        ))

#     smtp = smtplib.SMTP(server)
    server.sendmail('carlos.espinosa@eximagen.com.mx', 'carlos.espinosa@outlook.com', msg.as_string())
    server.close()    
    
      
    
def setupMagento():
    global connMagento
    connMagento=MySQLdb.connect(host= "localhost",user="root",passwd="",db="magento")

def setup():
    global client, session,  conn
    # your domain here
    conn = MySQLdb.connect(host= "localhost",user="root",passwd="",db="bulletproductfeed")
    client = xmlrpclib.ServerProxy("http://bullet.loc/index.php/api/xmlrpc?type=xmlrpc")
    # your credentials here
    session = client.login('soapPython', '@#$5M0k137')
def setupFTP():
    global ftpsession
    
    ftpsession = ftplib.FTP('localhost','workspace','@#$5M0k137')
    
def getProductTypes():
    global client, session
    products = client.call(session, 'product_type.list')
    print products
    for product in products:
        print product
def getCurrentProductsLists():
    global client, session,currentSimpleList,currentConfigurableList
    setup()
    params= {'status':{'eq':'1'}}
    products = client.call(session, 'catalog_product.list', [params,'2'])
    for product in products:
        if product['type']=='simple':
            currentSimpleList.append(product['sku'])
        if product['type']=='configurable':
            currentConfigurableList.append(product['sku'])
    print "current info set it"
def ftpUload(files,localPath,remotePath):
    global ftpsession
    setupFTP()
    ftpsession.cwd(remotePath)
    for filename in files:
        _file = open(localPath+filename,'rb')                  # file to send
        ftpsession.storbinary('STOR '+ntpath.basename(filename), _file)     # send the file
        _file.close()                                    # close file and FTP
    ftpsession.quit()    

def insertScrapProducts(data):
    global conn
    setup()
    sql="INSERT INTO scrap_process (configurable,simples) VALUES (%s,%s)"
    cursor = conn.cursor()
    cursor.executemany(sql,data)
    conn.commit()    

def disableProducts():
    global connMagento,conn
    
    setup()
    sql="select distinct sku from process where method in ('configurableToDisable','simpleToDisable' )"
    cursor = conn.cursor()
    cursor.execute(sql)
    products=[]
    for product in cursor.fetchall():
        products.append(product[0])
    conn.close()
    setupMagento()
    format_strings = ','.join(['%s'] * len(products))
    sql="select cpei.value_id from catalog_product_entity_int cpei inner join catalog_product_entity cpe on cpe.entity_id = cpei.entity_id where cpe.sku in (%s) AND cpei.attribute_id = 96" %format_strings 
    cursor = connMagento.cursor()
    cursor.execute(sql,tuple(products))
    ids=[]
    for _id in cursor.fetchall():
        ids.append(_id[0])
    sql="UPDATE catalog_product_entity_int SET value = '2' where  value_id=%s" 
    cursor.executemany(sql,[[v] for v in ids])
    connMagento.commit()          
    connMagento.close()
def scrapInit():
    global conn
#     driver = webdriver.Firefox()
    
    setup()
    sql="select sku,simples from process left join (SELECT model, group_concat(ItemCode SEPARATOR ',') as simples FROM bulletproductfeed.feed group by Model ) as view on process.sku=view.model where method in ('configurableToCreate','simpleToCreate') "
    cursor = conn.cursor()
    cursor.execute(sql)
    tmp=cursor.fetchall()
    print tmp
    totalProducts=[product[0] for product in tmp]
    print totalProducts
    data=[]
    for product in tmp:
        sku=product[0]
        print "sku " +sku
        print "simples"+str(product[1])
        if product[1]:
            
            colors=set(totalProducts) & set(product[1].split(","))
            data.append([sku,",".join(colors)])
        
    insertScrapProducts(data)
def element_exist_by_class_name(driver,class_name):
    try:
        driver.find_element_by_class_name(class_name)
    except NoSuchElementException:
        return True
    return False
def element_exist_by_id(driver,_id):
    try:
        driver.find_element_by_id(_id)
    except NoSuchElementException:
        return True
    return False

def scrapExec():
    global conn,hiresDriectory,mediumDriectory
    setup()

    timestr = time.strftime("%Y%m%d-%H%M%S")
    destinyDirectorie='C:/Users/carlos.espinosa/Documents/Workspace/data/scrapping/bullet/current/' 
    csvfile= 'C:/Users/carlos.espinosa/Documents/Workspace/data/scrapping/bullet/csv/'+timestr+'.csv'  
    csvOutput = csv.writer(open(csvfile, 'wb'))
    sql="select configurable,simples from scrap_process"
    cursor = conn.cursor()
    cursor.execute(sql)
    products=cursor.fetchall()
    notFound=[]
    simplesNotFound=[]    
    driver = webdriver.Firefox()
        #colors=list(totalProducts)-set(simplesToCreate)
        
    for sku,simples in products: 
        driver.get("http://www.pcna.com/Bullet/en-us")
        elem = driver.find_element_by_name("SearchPhraseTextBox")
        elem.clear()
        elem.send_keys(sku)
        send=driver.find_element_by_id("SearchSubmitButton")
        send.click()
#         print sku
        if element_exist_by_id(driver,'productId'):
            notFound.append(sku)
            continue

        sqlSimples="SELECT group_concat(ItemCode SEPARATOR ',') FROM bulletproductfeed.feed where model ='"+sku+"' group by model"
        cursor = conn.cursor()
        cursor.execute(sqlSimples)
        simpleList=cursor.fetchone()

        soup = BeautifulSoup(driver.page_source, "html.parser")
        with open(destinyDirectorie+sku+".html", "w") as text_file:
            text_file.write(repr(soup.prettify())) 
        breadcrumb=[]
        categories=soup.find('div',{'id':'breadcrumb'})
        if categories:
            for _a in categories.findAll('a'):
                breadcrumb.append(_a.text.replace('\\n','').strip())
        breadcrumb=breadcrumb[2:]
        masterCartonCasePack=float(soup.find('span',{'id':'masterCartonCasePack'}).text.replace('\\n','').strip())*2.54 if soup.find('span',{'id':'masterCartonCasePack'}) else ''
        masterCartonWeight=float(soup.find('span',{'id':'masterCartonDimension-Weight'}).text.replace('\\n','').strip())*2.54 if soup.find('span',{'id':'masterCartonDimension-Weight'}) else ''
        masterCartonHeight=float(soup.find('span',{'id':'masterCartonDimension-Height'}).text.replace('\\n','').strip())*2.54 if soup.find('span',{'id':'masterCartonDimension-Height'}) else ''
        masterCartonWidth=float(soup.find('span',{'id':'masterCartonDimension-Width'}).text.replace('\\n','').strip())*2.54 if soup.find('span',{'id':'masterCartonDimension-Width'}) else ''
        masterCartonDepth=float(soup.find('span',{'id':'masterCartonDimension-Depth'}).text.replace('\\n','').strip())*2.54 if soup.find('span',{'id':'masterCartonDimension-Depth'}) else ''
        productName=soup.find('div',{'class':'product-details-right'}).find('h1').text.replace('\\n','').strip().encode('ascii','ignore').strip() if soup.find('div',{'class':'product-details-right'}) else ''
        description=soup.find('p',{'id':'lessDescr'}).text.replace('\\n','') if soup.find('p',{'id':'lessDescr'}) else ''
        description=description.replace(" Less", "",).strip().encode('utf-8').strip()
        print sku
        colorsCodes=simples.split(',')
        images=defaultdict(list)
        for img in soup.find('ul',{'class':'bxslider'}).findAll('li'):
            code= img.find('a')['id'].replace('productImageLink_','').split('_')[0]
            if code in colorsCodes:
                image={}
                imgUrlmedium=img.find('a').find('img')['data-src']
                image['imgUrlmedium']=imgUrlmedium
                image['imgNameMedium']=imgUrlmedium.split('/')[-2]+".jpg"
                imgUrlHires=imgUrlmedium.replace('medium','hires')
                image['imgUrlHires']=imgUrlHires
                image['imgNameHires']=imgUrlHires.split('/')[-2]+".jpg"
                images[code].append(image)
#         print images
        imgList=defaultdict(list)
        for _sku in images:
            imgtmlList=[]
            for values in images[_sku]:
#                 print values['imgUrlmedium']
#                 print values['imgNameMedium']
#                 print values['imgUrlHires']
#                 print values['imgNameHires']
                downloadExec(values['imgUrlHires'],hiresDriectory+values['imgNameHires'])
                imgtmlList.append(values['imgNameHires'])
                copyfile(hiresDriectory+values['imgNameHires'],mediumDriectory+values['imgNameHires'])
            imgList[_sku]=imgtmlList
            ftpUload(imgtmlList,hiresDriectory,'/sites/BulletMagento/media/import/images/')
        imgs_list=[]
        _img=''
        for color in colorsCodes:
#             print color
            if not soup.find('span',{'id':'color_swatch_box_'+color+'_text'}):
                simplesNotFound.append(color)
                continue
            colorName=soup.find('span',{'id':'color_swatch_box_'+color+'_text'}).text.replace('\\n','').strip()
#             print "\t"+colorName
            colorHex=re.search('#(.*);',soup.find('a',{'id':'color_swatch_box_'+color}).find('span')['style']).group(1).replace('\\n','').strip()
            if len(imgList[color])>0:
                imgs_list=imgList[color]
                _img=imgList[color][0]
            datason=['base','0',color,colorHex,productName+" "+colorName,"","simple","",colorName,re.sub("|".join(["\s","-","/"]), "", colorName).strip()+"_"+colorHex,";".join(imgs_list),"+"+_img,_img,_img]
            csvOutput.writerow(datason)
        dataFather=['base','1',sku,"",productName,"color","configurable",description,"","",_img,"+"+_img,_img,_img,",".join(simpleList),"/".join(breadcrumb),masterCartonCasePack,masterCartonWeight,masterCartonHeight,masterCartonWidth,masterCartonDepth]
        csvOutput.writerow(dataFather)
    driver.close()
    ftpUload([csvfile],'','/sites/BulletMagento/var/import/')
    body=''
    sendFile(csvfile,body)


#                 for value in values:
#                     print value,values[value]
#
# #                 csvHires.writerow([imgUrlHires,imgNameHires])
# #                 csvMediumres.writerow([imgUrlmedium,imgNameMedium])
#     colors=list(set(colors))
#     colorsCode=[]
#     for color in colors:
#         name=soup.find('span',{'id':'color_swatch_box_'+color+'_text'}).text
#         colorsCode.append({'code':color,'name':name})
#     print colorsCode      
def downloadExec(url,fileName):
    var = Downloader()
    var.downloadFile(url, fileName)

def getFeedProductsLists():
    global feedSimpleList,feedConfigurableList,conn
    
    setup()
    sql="SELECT model, group_concat(ItemCode SEPARATOR ',') FROM bulletproductfeed.feed group by Model;"
    cursor = conn.cursor()
    cursor.execute(sql)
    products=cursor.fetchall()
    for product in products:
        feedConfigurableList.append(product[0])
        for simple in product[1].split(','):
            feedSimpleList.append(simple)
    conn.commit()
    conn.close()
    print "feed info set it"        
def getComparedProducts():
    global feedSimpleList,feedConfigurableList,currentSimpleList,currentConfigurableList,configurablesToCreate,configurablesToDisable,simplesToCreate,simplesToDisable
    for configurable in list(set(feedConfigurableList) - set(currentConfigurableList)):
        configurablesToCreate.append(configurable)
    for configurable in list(set(currentConfigurableList) - set(feedConfigurableList)):
        configurablesToDisable.append(configurable)
    for simple in list(set(feedSimpleList) - set(currentSimpleList)):
        simplesToCreate.append(simple)
    for simple in list(set(currentSimpleList) - set(feedSimpleList)):
        simplesToDisable.append(simple)
    print "product compared"

def setComparedProducts():
    global conn,configurablesToCreate,configurablesToDisable,simplesToCreate,simplesToDisable
    setup()
    print "start set process"
    x = conn.cursor()
    x.execute("TRUNCATE TABLE process")
    conn.commit()    
    for method in ['configurableToCreate','configurableToDisable','simpleToCreate','simpleToDisable']:
    
#         try:        
        sql="INSERT INTO process (sku,method) VALUES (%s,'"+method+"')"
        
        if method=='configurableToCreate':
            data=configurablesToCreate
        elif method=='configurableToDisable':
            data=configurablesToDisable
        elif method=='simpleToCreate':
            data=simplesToCreate      
        elif method=='simpleToDisable':
            data=simplesToDisable
        x.executemany(sql,[[v] for v in data])
        conn.commit()
    #     except:
    #         conn.rollback()
    #     
    conn.close()
    print "set to procees"
def updateInventory(sku,qty):
    global client, session
    params = [sku,qty]
    try: 
        response = client.call(session, 'product_stock.update', params)
        print response
    except:
        pass
def insertData(data):
    global conn
    setup()
    x = conn.cursor()
    x.execute("TRUNCATE TABLE feed")
    conn.commit()
#     try:
    x.executemany(
"""INSERT INTO feed (Model,ItemCode,ItemDesc,ExtDesc,ItemKeywords,Size,SizeGrid,WeightGR,LengthCM,HeightCM,WidthCM,DiameterCM,SizeCombined,CountryOfOrigin,QtyperCarton,DecoPackagingIndiv,DecoPackagingIndivType,DecoPackaging,GrossWeightKG,NettWeightKG,ExportLcm,ExportWcm,ExportHcm,ImpAllMethods,ImpMethodDefault,ImpAllPositions,ImpPositionDefault,ImpPositionSimpleDefault,ImpWidthDefaultMM,ImpHeightDefaultMM,ImpDiameterDefaultMM,ImpSizeDefaultMM,MaxColoursDefault,Brand,XNGroupCode,XNGroupDesc,XNCatnCode,XNCatDesc,ColorDesc,SimpleColor,PMSColorReference,BasicColor,PenInkColor,HSCode,Material,BatteryType,Features,BestSeller,TrendItem,ThematicItem,Compliances,ImageMain,ImageDecoY1,ImageDecoY2,ImageDecoY3,ImagePackage,ImageFront,ImageBack,ImageExtra1,ImageExtra2,ImageExtra3,ImageDetail1,ImageDetail2,ImageDetail3,ImagePrintLinesDefault,MarkSegment,MainCat,EOYCat,Gender,NewItems,Language)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
data)
    conn.commit()
#     except:
#         conn.rollback()
#     
    print "info inserted"
    conn.close()    

def readfeed():
    print "started read"
    url_str = 'http://www.pfconcept.com/portal/datafeed/productfeed_en_bullet_v2.xml'
    data=[]
    request = urllib2.Request(url_str, headers={"Accept" : "application/xml"})
    u = urllib2.urlopen(request)
    tree = ET.parse(u)    
    root = tree.getroot()
    for product in root.findall('productfeedRow'):
        Model=product.find('Model').text
        ItemCode=product.find('ItemCode').text
        ItemDesc=product.find('ItemDesc').text
        ExtDesc=product.find('ExtDesc').text
        ItemKeywords=product.find('ItemKeywords').text
        Size=product.find('Size').text
        SizeGrid=product.find('SizeGrid').text
        WeightGR=product.find('WeightGR').text
        LengthCM=product.find('LengthCM').text
        HeightCM=product.find('HeightCM').text
        WidthCM=product.find('WidthCM').text
        DiameterCM=product.find('DiameterCM').text
        SizeCombined=product.find('SizeCombined').text
        CountryOfOrigin=product.find('CountryOfOrigin').text
        QtyperCarton=product.find('QtyperCarton').text
        DecoPackagingIndiv=product.find('DecoPackagingIndiv').text
        DecoPackagingIndivType=product.find('DecoPackagingIndivType').text
        DecoPackaging=product.find('DecoPackaging').text
        GrossWeightKG=product.find('GrossWeightKG').text
        NettWeightKG=product.find('NettWeightKG').text
        ExportLcm=product.find('ExportLcm').text
        ExportWcm=product.find('ExportWcm').text
        ExportHcm=product.find('ExportHcm').text
        ImpAllMethods=product.find('ImpAllMethods').text
        ImpMethodDefault=product.find('ImpMethodDefault').text
        ImpAllPositions=product.find('ImpAllPositions').text
        ImpPositionDefault=product.find('ImpPositionDefault').text
        ImpPositionSimpleDefault=product.find('ImpPositionSimpleDefault').text
        ImpWidthDefaultMM=product.find('ImpWidthDefaultMM').text
        ImpHeightDefaultMM=product.find('ImpHeightDefaultMM').text
        ImpDiameterDefaultMM=product.find('ImpDiameterDefaultMM').text
        ImpSizeDefaultMM=product.find('ImpSizeDefaultMM').text
        MaxColoursDefault=product.find('MaxColoursDefault').text
        Brand=product.find('Brand').text
        XNGroupCode=product.find('XNGroupCode').text
        XNGroupDesc=product.find('XNGroupDesc').text
        XNCatnCode=product.find('XNCatnCode').text
        XNCatDesc=product.find('XNCatDesc').text
        ColorDesc=product.find('ColorDesc').text
        SimpleColor=product.find('SimpleColor').text
        PMSColorReference=product.find('PMSColorReference').text
        BasicColor=product.find('BasicColor').text
        PenInkColor=product.find('PenInkColor').text
        HSCode=product.find('HSCode').text
        Material=product.find('Material').text
        BatteryType=product.find('BatteryType').text
        Features=product.find('Features').text
        BestSeller=product.find('BestSeller').text
        TrendItem=product.find('TrendItem').text
        ThematicItem=product.find('ThematicItem').text
        Compliances=product.find('Compliances').text
        ImageMain=product.find('ImageMain').text
        ImageDecoY1=product.find('ImageDecoY1').text
        ImageDecoY2=product.find('ImageDecoY2').text
        ImageDecoY3=product.find('ImageDecoY3').text
        ImagePackage=product.find('ImagePackage').text
        ImageFront=product.find('ImageFront').text
        ImageBack=product.find('ImageBack').text
        ImageExtra1=product.find('ImageExtra1').text
        ImageExtra2=product.find('ImageExtra2').text
        ImageExtra3=product.find('ImageExtra3').text
        ImageDetail1=product.find('ImageDetail1').text
        ImageDetail2=product.find('ImageDetail2').text
        ImageDetail3=product.find('ImageDetail3').text
        ImagePrintLinesDefault=product.find('ImagePrintLinesDefault').text
        MarkSegment=product.find('MarkSegment').text
        MainCat=product.find('MainCat').text
        EOYCat=product.find('EOYCat').text
        Gender=product.find('Gender').text
        NewItems=product.find('NewItems').text
        Language=product.find('Language').text
        datassimple=[Model,ItemCode,ItemDesc,ExtDesc,ItemKeywords,Size,SizeGrid,WeightGR,LengthCM,HeightCM,WidthCM,DiameterCM,SizeCombined,CountryOfOrigin,QtyperCarton,DecoPackagingIndiv,DecoPackagingIndivType,DecoPackaging,GrossWeightKG,NettWeightKG,ExportLcm,ExportWcm,ExportHcm,ImpAllMethods,ImpMethodDefault,ImpAllPositions,ImpPositionDefault,ImpPositionSimpleDefault,ImpWidthDefaultMM,ImpHeightDefaultMM,ImpDiameterDefaultMM,ImpSizeDefaultMM,MaxColoursDefault,Brand,XNGroupCode,XNGroupDesc,XNCatnCode,XNCatDesc,ColorDesc,SimpleColor,PMSColorReference,BasicColor,PenInkColor,HSCode,Material,BatteryType,Features,BestSeller,TrendItem,ThematicItem,Compliances,ImageMain,ImageDecoY1,ImageDecoY2,ImageDecoY3,ImagePackage,ImageFront,ImageBack,ImageExtra1,ImageExtra2,ImageExtra3,ImageDetail1,ImageDetail2,ImageDetail3,ImagePrintLinesDefault,MarkSegment,MainCat,EOYCat,Gender,NewItems,Language]
        datassimple=[(x.encode('utf-8') if x!=None else '') for x in datassimple]
        data.append(datassimple)
    insertData(data)

if __name__ == '__main__':
#     readfeed()
#     getCurrentProductsLists()
#     getFeedProductsLists()  
#     getComparedProducts()
#     setComparedProducts()
#     disableProducts()
#     scrapInit()
    scrapExec()
    
import xlrd
import urllib2
from fractions import Fraction
import os
import MySQLdb
import re

__author__ = 'Cespinosa'


class Catalogs(object):
    def __init__(self):
        pass

    def downloadFile(self,url, downloadPath):
        try:
            if os.path.exists(downloadPath) and os.path.getsize(downloadPath) > 0:
                return
            directory = os.path.dirname(downloadPath)
            if not os.path.exists(directory):
                os.makedirs(directory)
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                                          urllib2.HTTPHandler(debuglevel=0),
                                          urllib2.HTTPSHandler(debuglevel=0))
            opener.addheaders = [
                ('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0'),
                ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
                ('Connection', 'keep-alive')]
            resp = opener.open(url, timeout=60)
            contentLength = resp.info()['Content-Length']
            totalSize = float(contentLength)
            currentSize = 0
            dl_file = open(downloadPath, 'wb')
            CHUNK_SIZE = 32 * 1024
            while True:
                data = resp.read(CHUNK_SIZE)
                if not data:
                    break
                currentSize += len(data)
                dl_file.write(data)
            if currentSize >= totalSize:
                dl_file.close()
        except Exception, x:
            print 'Error downloading: '
            print x            
    
    
    def setup(self):
        global  conn
        # your domain here
        conn = MySQLdb.connect(host= "localhost",user="root",passwd="",db="bulletproductfeed")
    
    
    def insertScrapProducts(self,data):
        global conn
        self.setup()
        sql="INSERT INTO catalogus (itemno,itemstatus,itemname,material,patentinfo,catalogdescription,materialdescpatent,colorlist,catalogsize,imprinttextall,packagingandweight,packagingdetails,disclaimers,batteries,catalogruncharges,priceqtycol1,priceqtycol2,priceqtycol3,priceqtycol4,priceqtycol5,priceuscol1,priceuscol2,priceuscol3,priceuscol4,priceuscol5,pricecode,height,width,length,diameter,weight) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"    
        cursor = conn.cursor()
        cursor.executemany(sql,data)
        conn.commit()    
    
    def insertDecorations(self,data):
        global conn
        self.setup()
        sql="INSERT INTO decorationus (itemno,itemname,imprintmethod1,imprintlocation1,imprintwidth1,imprintheight1,imprintaddinfo1,imprintlogoplacement1,imprintdiameter1,imprintmethod2,imprintlocation2,imprintwidth2,imprintheight2,imprintaddinfo2,imprintlogoplacement2,imprintdiameter2,imprintmethod3,imprintlocation3,imprintwidth3,imprintheight3,imprintaddinfo3,imprintlogoplacement3,imprintdiameter3,imprintmethod4,imprintlocation4,imprintwidth4,imprintheight4,imprintaddinfo4,imprintlogoplacement4,imprintdiameter4,imprintmethod5,imprintlocation5,imprintwidth5,imprintheight5,imprintaddinfo5,imprintlogoplacement5,imprintdiameter5,imprintmethod6,imprintlocation6,imprintwidth6,imprintheight6,imprintaddinfo6,imprintlogoplacement6,imprintdiameter) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"    
        cursor = conn.cursor()
        cursor.executemany(sql,data)
        conn.commit()    
     
    def getSizes(self,sizes):                                                                                       
        weight=''
        Height=''
        Width=''
        Length=''
        Diameter=''
        splitSizes=sizes.split(',')
        if len(splitSizes)>1:
            weight= float(re.search('(\d+(?:\.\d+)?)',splitSizes[1]).group(1))*28.34
        for size in splitSizes[0].split('x'):
            size=size.strip()
            if len(size)<=0:
                continue
            size= "0"+size if size[0]=="." else size
            if "L" in size:
                Length= float(re.search('(\d+(?:\.\d+)?)',size).group(1))*2.54
            elif "H" in size:
                Height= float(re.search('(\d+(?:\.\d+)?)',size).group(1))*2.54
            elif "D" in size:
                Diameter= float(re.search('(\d+(?:\.\d+)?)',size).group(1))*2.54
            elif "W" in size:
                Width= float(re.search('(\d+(?:\.\d+)?)',size).group(1))*2.54
        return [Height, Width, Length ,Diameter,weight]  
    
    
    def getCatalog(self):
        url="http://media.pcna.com/msfiles/PCNAFileSharing/Bullet_CatalogUS.xlsx"
        nameFile="Bullet_CatalogUS.xlsx"
        
        header=['itemno','item status','itemname','material','patentinfo','catalogdescription','materialdescpatent','colorlist','catalogsize','imprinttextall','packagingandweight','packagingdetails','disclaimers','batteries','catalogruncharges','priceqtycol1','priceqtycol2','priceqtycol3','priceqtycol4','priceqtycol5','priceuscol1','priceuscol2','priceuscol3','priceuscol4','priceuscol5','price code']
        self.downloadFile(url,nameFile)
        book = xlrd.open_workbook(nameFile)
        sheet = book.sheet_by_name("Sheet1")
        datalist=[]
        for r in range(1, sheet.nrows):
            
            
            datarow=[]
            for index in range(0,26):
                datarow.insert(index,sheet.cell(r,index).value.encode("utf-8") if not (type(sheet.cell(r,index).value)== int or type(sheet.cell(r,index).value) == float) else sheet.cell(r,index).value)
            
            sizes=self.getSizes(sheet.cell(r,8).value)
            datarow.extend(sizes)                          
            datalist.append(datarow)
        self.insertScrapProducts(datalist)
    def getDecoration(self):
        global ImprintMethod1,ImprintLocation1,ImprintWidth1,ImprintHeight1,ImprintAddInfo1, ImprintLogoPlacement1, ImprintDiameter1,ImprintMethod2,ImprintLocation2,ImprintWidth2,ImprintHeight2,ImprintAddInfo2, ImprintLogoPlacement2, ImprintDiameter2,ImprintMethod3,ImprintLocation3,ImprintWidth3,ImprintHeight3,ImprintAddInfo3, ImprintLogoPlacement3, ImprintDiameter3,ImprintMethod4,ImprintLocation4,ImprintWidth4,ImprintHeight4,ImprintAddInfo4, ImprintLogoPlacement4, ImprintDiameter4,ImprintMethod5,ImprintLocation5,ImprintWidth5,ImprintHeight5,ImprintAddInfo5, ImprintLogoPlacement5, ImprintDiameter5,ImprintMethod6,ImprintLocation6,ImprintWidth6,ImprintHeight6,ImprintAddInfo6, ImprintLogoPlacement6, ImprintDiameter6
        url='http://media.pcna.com/msfiles/PCNAFileSharing/Bullet_DecorationUS.xlsx'
        nameFile="Bullet_DecorationUS.xlsx"
        self.downloadFile(url,nameFile)
        book = xlrd.open_workbook(nameFile)
        sheet = book.sheet_by_name("CP-ITEMS")
        datalist=[]
        for r in range(1, sheet.nrows):
            sku=sheet.cell(r,0).value
            ImprintMethod1=sheet.cell(r,2).value
            ImprintLocation1=sheet.cell(r,3).value
            ImprintWidth1=sheet.cell(r,4).value
            ImprintHeight1=sheet.cell(r,5).value
            ImprintAddInfo1=sheet.cell(r,6).value
            ImprintLogoPlacement1=sheet.cell(r,7).value
            ImprintDiameter1=sheet.cell(r,8).value
            ImprintMethod2=sheet.cell(r,9).value
            ImprintLocation2=sheet.cell(r,10).value
            ImprintWidth2=sheet.cell(r,11).value
            ImprintHeight2=sheet.cell(r,12).value
            ImprintAddInfo2=sheet.cell(r,13).value
            ImprintLogoPlacement2=sheet.cell(r,14).value
            ImprintDiameter2=sheet.cell(r,15).value
            ImprintMethod3=sheet.cell(r,16).value
            ImprintLocation3=sheet.cell(r,17).value
            ImprintWidth3=sheet.cell(r,18).value
            ImprintHeight3=sheet.cell(r,19).value
            ImprintAddInfo3=sheet.cell(r,20).value
            ImprintLogoPlacement3=sheet.cell(r,21).value
            ImprintDiameter3=sheet.cell(r,22).value
            ImprintMethod4=sheet.cell(r,23).value
            ImprintLocation4=sheet.cell(r,24).value
            ImprintWidth4=sheet.cell(r,25).value
            ImprintHeight4=sheet.cell(r,26).value
            ImprintAddInfo4=sheet.cell(r,27).value
            ImprintLogoPlacement4=sheet.cell(r,28).value
            ImprintDiameter4=sheet.cell(r,29).value
            ImprintMethod5=sheet.cell(r,30).value
            ImprintLocation5=sheet.cell(r,31).value
            ImprintWidth5=sheet.cell(r,32).value
            ImprintHeight5=sheet.cell(r,33).value
            ImprintAddInfo5=sheet.cell(r,34).value
            ImprintLogoPlacement5=sheet.cell(r,35).value
            ImprintDiameter5=sheet.cell(r,36).value
            ImprintMethod6=sheet.cell(r,37).value
            ImprintLocation6=sheet.cell(r,38).value
            ImprintWidth6=sheet.cell(r,39).value
            ImprintHeight6=sheet.cell(r,40).value
            ImprintAddInfo6=sheet.cell(r,41).value
            ImprintLogoPlacement6=sheet.cell(r,42).value
            ImprintDiameter6=sheet.cell(r,43).value
            for index in range(1,7):
                if globals()['ImprintWidth%s' % index]:
                    globals()['ImprintWidth%s' % index]= float(sum(Fraction(s) for s in globals()['ImprintWidth%s' % index].split("-")))*2.54
                if globals()['ImprintHeight%s' % index]:
                    if '"' in globals()['ImprintHeight%s' % index]:
                        addinfotmp=globals()['ImprintHeight%s' % index].split('"')
                        if len(addinfotmp)>1:
                            globals()['ImprintHeight%s' % index]= str(float(sum(Fraction(s) for s in addinfotmp[0].split("-")))*2.54) +" ".join(addinfotmp[1:])               
                    else:
                        globals()['ImprintHeight%s' % index]= float(sum(Fraction(s) for s in globals()['ImprintHeight%s' % index].split("-")))*2.54
          
                if globals()['ImprintDiameter%s' % index]:
                    if '"' in globals()['ImprintDiameter%s' % index]:
                        addinfotmp=globals()['ImprintDiameter%s' % index].split('"')
                        if len(addinfotmp)>1:
                            globals()['ImprintDiameter%s' % index]= str(float(sum(Fraction(s) for s in addinfotmp[0].split("-")))*2.54)+" ".join(addinfotmp[1:])                
                    else:
                        if " " in globals()['ImprintDiameter%s' % index].strip():
                            globals()['ImprintDiameter%s' % index]=globals()['ImprintDiameter%s' % index].split(" ")[0]
                        globals()['ImprintDiameter%s' % index]= float(sum(Fraction(s) for s in globals()['ImprintDiameter%s' % index].strip().split("-")))*2.54
                          
                if globals()['ImprintAddInfo%s' % index]:
                    addinfotmp=globals()['ImprintAddInfo%s' % index].replace('default imprint area','').split('"')
                    if len(addinfotmp)>1:
                        addinfotmp[0]=addinfotmp[0].replace('Dia','')
                        globals()['ImprintAddInfo%s' % index]= str(float(sum(Fraction(s) for s in addinfotmp[0].split("-")))*2.54)+" ".join(addinfotmp[1:])               
            datarow=[sku,"",ImprintMethod1,ImprintLocation1,ImprintWidth1,ImprintHeight1,ImprintAddInfo1,ImprintLogoPlacement1,ImprintDiameter1,ImprintMethod2,ImprintLocation2,ImprintWidth2,ImprintHeight2,ImprintAddInfo2,ImprintLogoPlacement2,ImprintDiameter2,ImprintMethod3,ImprintLocation3,ImprintWidth3,ImprintHeight3,ImprintAddInfo3,ImprintLogoPlacement3,ImprintDiameter3,ImprintMethod4,ImprintLocation4,ImprintWidth4,ImprintHeight4,ImprintAddInfo4,ImprintLogoPlacement4,ImprintDiameter4,ImprintMethod5,ImprintLocation5,ImprintWidth5,ImprintHeight5,ImprintAddInfo5,ImprintLogoPlacement5,ImprintDiameter5,ImprintMethod6,ImprintLocation6,ImprintWidth6,ImprintHeight6,ImprintAddInfo6,ImprintLogoPlacement6,ImprintDiameter6]
            datalist.append(datarow)
        self.insertDecorations(datalist)


if __name__ == '__main__':
    program=Catalogs()
    program.getDecoration()

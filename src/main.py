import csv

csvfilewriter=open('C:/Users/carlos.espinosa/Documents/bulletProductListColors.csv', 'wb')
writerCat = csv.writer(csvfilewriter)

with open('C:/Users/carlos.espinosa/Documents/bulletProductList.csv') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        ItemNo= row[0]
        ItemStatus= row[1]
        ItemName= row[2]
        Material= row[3]
        PatentInfo= row[4]
        CatalogDescription= row[5]
        MaterialDescPatent= row[6]
        ColorList= row[7]
        CatalogSize= row[8]
        ImprintTextAll= row[9]
        PackagingAndWeight= row[10]
        PackagingDetails= row[11]
        Disclaimers= row[12]
        Batteries= row[13]
        CatalogRuncharges= row[14]
        PriceQtyCol1= row[15]
        PriceQtyCol2= row[16]
        PriceQtyCol3= row[17]
        PriceQtyCol4= row[18]
        PriceQtyCol5= row[19]
        PriceUSCol1= row[20]
        PriceUSCol2= row[21]
        PriceUSCol3= row[22]
        PriceUSCol4= row[23]
        PriceUSCol5= row[24]
        for color in ColorList.split(","):
            data=[ItemNo,ItemStatus,ItemName,color.strip(),Material,PatentInfo,CatalogDescription,MaterialDescPatent,ColorList,CatalogSize,ImprintTextAll,PackagingAndWeight,PackagingDetails,Disclaimers,Batteries,CatalogRuncharges,PriceQtyCol1,PriceQtyCol2,PriceQtyCol3,PriceQtyCol4,PriceQtyCol5,PriceUSCol1,PriceUSCol2,PriceUSCol3,PriceUSCol4,PriceUSCol5]
            writerCat.writerow(data)


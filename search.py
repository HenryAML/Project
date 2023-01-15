import urllib.request, urllib.parse, urllib.error
import json
import sqlite3
import sys

conn = sqlite3.connect('product.sqlite')
cur = conn.cursor()
barcode = input("Enter Barcode: ")

def create_db():

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS Product(
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        barcode INTEGER UNIQUE,
        productname TEXT,
        ingredients TEXT
    );
    CREATE TABLE IF NOT EXISTS Price(
        product_id INTEGER,
        price INTEGER,
        storename TEXT
    );
    ''')

def check_db(barcode):

    check_data_one=cur.execute('''SELECT Price.price, Price.storename,
    Product.productname, Product.ingredients
    FROM Price JOIN Product ON Price.product_id=Product.id WHERE
    barcode=?''', (barcode,))
    results_one=cur.fetchall()
    check_data_two=cur.execute('''SELECT productname, ingredients FROM Product
                              WHERE barcode=?''',(barcode,))
    result_two=cur.fetchall()
    if len(results_one) <= 0 and len(result_two) <= 0:
        print("Getting the data from APIs.... \n")
        pass
    else:
        print("Getting the data from database.... \n")
        if len(results_one)>0:
            print("PRODUCT: " + results_one[0][2] + "\n\n"+"INGREDIENTS: " + results_one[0][3] + "\n")
            for result in results_one:
                print("PRICE: " + str(result[0]) + "\n" + "STORENAME: " + result[1] + "\n")
            sys.exit()
        elif len(result_two)>0:
            print("\n"+"PRODUCT: " + result_two[0][0] + "\n\n" + "INGREDIENTS: " + result_two[0][1] + "\n")
            sys.exit()
        sys.exit()

def insert_ingredients():

    serviceurl = "https://world.openfoodfacts.org/api/v0/product/"+barcode+".json"
    uh = urllib.request.urlopen(serviceurl)
    data = uh.read()
    js = json.loads(data)

    try:
        try:
          product_name = js["product"]["product_name_en"]
        except:
          product_name = js["product"]["product_name"]
    except:
        print("Product name not found!!!")

    try:
        try:
          ingredients = js["product"]["ingredients_text_en"]
        except:
          ingredients = js["product"]["ingredients_text"]
    except:
        print("Ingredients not found!!!")
        sys.exit()

    if len(ingredients)<=0 or len(product_name)<=0:
        print("Product name and Ingredients are not found!!!")
        sys.exit()

    barcode_js = js["code"]
    cur.execute('''INSERT OR IGNORE INTO Product (barcode, productname, ingredients)
                   VALUES (?, ? , ?)''' , (barcode_js, product_name, ingredients))
    conn.commit()

def insert_prices(barcode):

    priceurl = "https://api.barcodelookup.com/v3/products?barcode=" + barcode + "&formatted=y&key=eiuwj9hwq3y1qypagmwa7wm2rxepp4"
    try:
        ph = urllib.request.urlopen(priceurl)
        pricedata = ph.read()
        ps = json.loads(pricedata)

        data = ps["products"][0]["stores"]
        length = len(data)
        if length<=0:
            print("No prices and store names are found!!!")
            sys.exit()
        count = 0

        while(count < length):
            price = ps["products"][0]["stores"][count]["price"]
            storename = ps["products"][0]["stores"][count]["name"]
            cur.execute('''SELECT id FROM Product WHERE barcode = ? ''', (barcode, ))
            product_id = cur.fetchone()[0]
            cur.execute('''INSERT OR IGNORE INTO Price (product_id, price , storename)
                           VALUES (?, ?, ?)''' , (product_id, price, storename))
            count = count + 1
        conn.commit()
    except:
        print("Prices and Store Names are not found!!!")

def print_msg(barcode):

    try:
        check_data=cur.execute('''SELECT Price.price, Price.storename,
        Product.productname, Product.ingredients
        FROM Price JOIN Product ON Price.product_id=Product.id WHERE
        barcode=?''', (barcode,))
        results=cur.fetchall()

        print("PRODUCT: " + results[0][2] + "\n\n" + "INGREDIENTS: " + results[0][3] + "\n")
        for result in results:
            print("PRICE: " + str(result[0]) + "\n" + "STORENAME: " + result[1] + "\n")
    except:
        check_data=cur.execute('''SELECT productname, ingredients FROM Product
                                  WHERE barcode=?''',(barcode,))
        result=cur.fetchone()
        print("\n"+"PRODUCT: " + result[0] + "\n\n" + "INGREDIENTS: " + result[1] + "\n")

def main():

    create_db()
    if barcode.isdigit():
        check_db(barcode)
        insert_ingredients()
        insert_prices(barcode)
        print_msg(barcode)
    else:
        print("Please type the correct barcode!!!")

main()

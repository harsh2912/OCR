
import os



import cv2
from detail_extraction import Extractor
import xlsxwriter

from utils import *

from img_processing import get_ocr_response

img = cv2.imread('../Images/IMG20200814045215.jpg')[:,:,::-1]

response = get_ocr_response(img)

page = response.full_text_annotation.pages[0]

xtractor = Extractor(page)

num_blocks , bill_ship_separate, ship_invoice_separate = num_blocks_nd_flags(page)


block_numbers = get_block_numbers(page,num_blocks,bill_ship_separate,ship_invoice_separate)

if len(block_numbers) == 4:
    target_bill_block, ship_gstin_block, bill_gstin_block, table_start = block_numbers
    
    dictionary = xtractor.single_block_logic(target_bill_block,bill_gstin_block,ship_gstin_block)
    
    
elif len(block_numbers) == 5:
    
    block1, block2 ,ship_gstin_block, bill_gstin_block, table_start = block_numbers
    
    dictionary = xtractor.two_blocks_logic(block1,block2,bill_ship_separate,bill_gstin_block,ship_gstin_block)
    
else:
    
    target_bill_block, target_invoice_block, target_ship_block , ship_gstin_block, bill_gstin_block, table_start = block_numbers
    
    dictionary = xtractor.three_blocks_logic(target_bill_block,target_ship_block,target_invoice_block,bill_gstin_block,ship_gstin_block)
    
entries = xtractor.get_rows(table_start)


workbook = xlsxwriter.Workbook('Expenses01.xlsx')
worksheet = workbook.add_worksheet()

worksheet.write(0,0,'BILL TO')
worksheet.write(2,0,"CUSTOMER NAME")
worksheet.write(3,0,"CUSTOMER ADDRESS")
worksheet.write(4,0,"CUSTOMER CODE")
worksheet.write(5,0,"GSTIN NUMBER")
worksheet.write(6,0,"PAN NUMBER")
worksheet.write(7,0,"ORDER NUMBER")


worksheet.write(10,0,'SHIP TO')
worksheet.write(12,0,"CUSTOMER CODE")
worksheet.write(13,0,"CUSTOMER NAME")
worksheet.write(14,0,"CUSTOMER ADDRESS")
worksheet.write(15,0,"GSTIN NUMBER")
worksheet.write(16,0,"PAN NUMBER")
worksheet.write(17,0,"ORDER NUMBER")


worksheet.write(20,0,'INVOICE DETAILS')
worksheet.write(22,0,"INVOICE NUMBER")
worksheet.write(23,0,"INVOICE DATE")
worksheet.write(24,0,"LR DATE")
worksheet.write(25,0,"LR NUMBER")

bill_customer_details = [key for key in dictionary.keys() if 'bill_customer' in key]
bill_gstin = [key for key in dictionary.keys() if 'bill' in key and key not in bill_customer_details]

ship_customer_details = [key for key in dictionary.keys() if 'ship_customer' in key]
ship_gstin = [key for key in dictionary.keys() if 'ship' in key and key not in ship_customer_details]

invoice_details = [key for key in dictionary.keys() if 'invoice' in key or 'LR' in key]

for i,val in enumerate(bill_customer_details + bill_gstin):
    worksheet.write(i+2,1,dictionary[val])
    
for i,val in enumerate(ship_customer_details + ship_gstin):
    worksheet.write(i+12,1,dictionary[val])
#     print(dictionary)

for i,val in enumerate(invoice_details):
    worksheet.write(i+22,1,dictionary[val])
    
worksheet.write(28,5,'ORDERS')
worksheet.write(30,0,'SL No.')
worksheet.write(30,1,'BRAND CODE')
worksheet.write(30,2,'STYLE CODE')
worksheet.write(30,3,'PRODUCT CODE')
worksheet.write(30,4,'QTY')
worksheet.write(30,5,'UNIT PRICE')
worksheet.write(30,6,'DISCOUNT')
worksheet.write(30,7,'SGST/UTGST')
worksheet.write(30,8,'CGST')
worksheet.write(30,9,'INVOICE VALUES')

for index,row in enumerate(entries):
    for i,val in enumerate(row):
        worksheet.write(31+index,i,get_word(val))

workbook.close()
    
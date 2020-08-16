from utils import get_word

keys = [
        'bill_customer_name','bill_customer_add','bill_customer_code',
        'ship_customer_name','ship_customer_add','ship_customer_code',
        'invoice_number', 'invoice_date', 'LR_date' , 'LR_num',
        'bill_gstin_num', 'bill_pan_num', 'bill_order_num',
        'ship_gstin_num', 'ship_pan_num', 'ship_order_num'
    ]

class Extractor:
    
    def __init__(self,page):
        self.page = page
        
    def get_customer_details(self,block_number):
        all_words = []
        for para in self.page.blocks[block_number].paragraphs:
            for word in para.words:
                all_words.append(word)
        cond = True
        j = 0
        while cond:
            text = get_word(all_words[j])
        #     print(text==':')
            if text == 'CODE' and get_word(all_words[j+1]) == ':':
                j += 2
                customer_code = ''
                customer_name = ''
                customer_add = ''
                while get_word(all_words[j] )!= 'CUSTOMER':
                    customer_code += get_word(all_words[j]) + ' '
                    j += 1
                j += 3
                while get_word(all_words[j] )!= 'CUSTOMER':
                    customer_name += get_word(all_words[j]) + ' '
                    j += 1
                j += 3
                while j<len(all_words):
                    customer_add += get_word(all_words[j]) + ' '
                    j += 1
                    if j == len(all_words):
                        cond = False
            j += 1
        return customer_name.strip(),customer_add.strip(),customer_code.strip()


    def get_invoice_details(self,block_number):
        all_words = []
        for para in self.page.blocks[block_number].paragraphs:
            for word in para.words:
                all_words.append(word)
        cond = True
        j = 0
        while cond:
            text = get_word(all_words[j])
        #     print(text==':')
            if text == 'INVOICE' and get_word(all_words[j+1]) == 'NO':
                invoice_number = get_word(all_words[j+3])
                invoice_date = get_word(all_words[j+8])
                LR_num = get_word(all_words[j+12])
                LR_date = get_word(all_words[j+16])
                cond = False
            j += 1
        return invoice_number.strip(), invoice_date.strip(), LR_date.strip() , LR_num.strip()




    def get_gstin(self,block_number):
        all_words = []
        for para in self.page.blocks[block_number].paragraphs:
            for word in para.words:
                all_words.append(word)
        j = 0
        gstin_num = ''
        pan_num = ''
        order_num = ''
        while j<len(all_words):
            text = get_word(all_words[j])
        #     print(text==':')
            if text == 'GSTIN' and get_word(all_words[j+1]) == ':':
                j += 2
                while get_word(all_words[j] )!= 'PAN':
                    gstin_num += get_word(all_words[j]) + ' '
                    j += 1
                j += 2
                while get_word(all_words[j] )!= 'ORDER':
                    pan_num += get_word(all_words[j]) + ' '
                    j += 1
                j += 4
                while j<len(all_words):
                    customer_add += get_word(all_words[j]) + ' '
                    j += 1
            j += 1
        return gstin_num.strip(), pan_num.strip(), order_num.strip()


    def three_blocks_logic(bill,ship,invoice,bill_gstin,ship_gstin,keys=keys):
        values = []
        values.extend(self.get_customer_details(bill))
        values.extend(self.get_customer_details(ship))
        values.extend(self.get_invoice_details(invoice))
        values.extend(self.get_gstin(bill_gstin))
        values.extend(self.get_gstin(ship_gstin))

        dictionary = dict((k,v) for k,v in zip(keys,values))

        return dictionary



    def two_blocks_logic(self,block1,block2,bill_ship_separate,bill_gstin,ship_gstin,key=keys):
        dictionary = dict()
        dictionary[key[10]], dictionary[key[11]], dictionary[key[12]] = self.get_gstin(bill_gstin)
        dictionary[key[13]], dictionary[key[14]], dictionary[key[15]] = self.get_gstin(ship_gstin)
        all_words = []
        if bill_ship_separate:
            dictionary[key[0]] ,dictionary[key[1]], dictionary[key[2]] = self.get_customer_details(block1)


            for para in self.page.blocks[block2].paragraphs:
                for word in para.words:
                    all_words.append(word)
            j = 0
            while 1:
                text = get_word(all_words[j])
                if text == 'INVOICE' and get_word(all_words[j+1]) == 'NO':
                    invoice_number = get_word(all_words[j+3])
                    dictionary[key[6]] = invoice_number
                    j += 4
                if text == 'CODE' and get_word(all_words[j+1]) == ':':
                    j += 2
                    customer_code = ''
                    customer_name = ''
                    customer_add = ''
                    while get_word(all_words[j] )!= 'DATE':
                        customer_code += get_word(all_words[j]) + ' '
                        j += 1
                    dictionary[key[5]] = customer_code
                    j += 4
                    invoice_date = get_word(all_words[j])
                    dictionary[key[7]] = invoice_date
                    j += 4
                    while get_word(all_words[j] )!= 'LR':
                        customer_name += get_word(all_words[j]) + ' '
                        j += 1
                    dictionary[key[3]] = customer_name
                    lr_num = get_word(all_words[j+3])
                    dictionary[key[9]] = lr_num
                    j += 7
                    while get_word(all_words[j]) != 'LR':
                        customer_add += get_word(all_words[j]) + ' '
                        j += 1
                    lr_date = get_word(all_words[j+3])
                    dictionary[key[8]] = lr_date
                    j += 4
                    if j<len(all_words):
                        while j<len(all_words):
                            customer_add += get_word(all_words[j]) + ' '
                            j+=1
                        dictionary[key[4]] = customer_add
                        break
                    else:
                        dictionary[key[4]] = customer_add
                        break

                j += 1
        else:
            dictionary[key[6]], dictionary[key[7]], dictionary[key[8]], dictionary[key[9]] = self.get_invoice_details(block2)

            bill_x_coord = self.page.blocks[block1].bounding_box.vertices[0].x

            for para in self.page.blocks[block1].paragraphs:
                for word in para.words:
                    all_words.append(word)
            j = 0

            while get_word(all_words[j]) != 'CUSTOMER' and get_word(all_words[j+1]) != 'CODE':
                j += 1
            j += 3
            bill_customer_code = ''
            while get_word(all_words[j])!= 'CUSTOMER' and get_word(all_words[j+1]) != 'CODE':
                bill_customer_code += get_word(all_words[j]) + ' '
                j += 1
            dictionary[key[2]] = bill_customer_code
            j += 3
            ship_customer_code = ''
            while get_word(all_words[j])!= 'CUSTOMER' and get_word(all_words[j+1]) != 'NAME':
                ship_customer_code += get_word(all_words[j]) + ' '
                j += 1
            dictionary[key[5]] = ship_customer_code
            j += 3
            bill_customer_name = ''
            while get_word(all_words[j])!= 'CUSTOMER' and get_word(all_words[j+1]) != 'NAME':
                bill_customer_name += get_word(all_words[j]) + ' '
                j += 1
            dictionary[key[0]] = bill_customer_name

            j += 3
            ship_customer_name = ''
            while get_word(all_words[j])!= 'CUSTOMER' and get_word(all_words[j+1]) != 'ADDRESS':
                ship_customer_name += get_word(all_words[j]) + ' '
                j += 1

            dictionary[key[3]] = ship_customer_name
            j += 3
            bill_customer_address = ''
            x_coords_bill_add = all_words[j].bounding_box.vertices[0].x
            while get_word(all_words[j])!= 'CUSTOMER' and get_word(all_words[j+1]) != 'ADDRESS':
                bill_customer_address += get_word(all_words[j]) + ' '
                j += 1
            j += 3
            ship_customer_address = ''
            x_coords_ship_add = all_words[j].bounding_box.vertices[0].x

            while all_words[j+1].bouning_box.vertices[0].x - all_words[j].bouning_box.vertices[0].x > 0:
                ship_customer_address += get_word(all_words[j]) + ' '
                j += 1
            j += 1
            while abs(all_words[j].bouning_box.vertices[0].x - x_coords_ship_add) > 50:
                bill_customer_address += get_word(all_words[j]) + ' '
                j += 1

            while j<len(all_words):
                ship_customer_address += get_word(all_words[j]) + ' '
                j+=1
            dictionary[key[1]] = bill_customer_address
            dictionary[key[4]] = ship_customer_address

        return dictionary


    def single_block_logic(self,block,bill_gstin,ship_gstin,key=keys):
        dictionary = dict()
        dictionary[key[10]], dictionary[key[11]], dictionary[key[12]] = self.get_gstin(bill_gstin)
        dictionary[key[13]], dictionary[key[14]], dictionary[key[15]] = self.get_gstin(ship_gstin)
        all_words = []
        for para in self.page.blocks[block].paragraphs:
            for word in para.words:
                all_words.append(word)
        j = 0
        while get_word(all_words[j])!= 'INVOICE' and get_word(all_words[j+1]) != 'NO.':
            j += 1
        j += 2
        invoice_num = get_word(all_words[j])
        j += 4
        bill_customer_code = ''
        while get_word(all_words[j])!= 'CUSTOMER' and get_word(all_words[j+1]) != 'CODE':
            bill_customer_code += get_word(all_words[j]) + ' '
            j += 1
        j += 3
        ship_customer_code = ''
        while get_word(all_words[j])!= 'DATE':
            ship_customer_name += get_word(all_words[j]) + ' '
            j += 1
        j += 4
        invoice_date = get_word(all_words[j]) 
        j += 4
        bill_customer_name = ''
        while get_word(all_words[j])!= 'CUSTOMER' and get_word(all_words[j+1]) != 'NAME':
            bill_customer_name += get_word(all_words[j]) + ' '
            j += 1
        j += 3
        ship_cutomer_name = ''
        while get_word(all_words[j])!= 'LR':
            ship_customer_name += get_word(all_words[j]) + ' '
            j += 1
        j += 3
        lr_num = get_word(all_words[j])

        bill_customer_address = ''
        x_coords_bill_add = all_words[j].bounding_box.vertices[0].x
        while get_word(all_words[j])!= 'CUSTOMER' and get_word(all_words[j+1]) != 'ADDRESS':
            bill_customer_address += get_word(all_words[j]) + ' '
            j += 1
        j += 3
        ship_customer_address = ''
        x_coords_ship_add = all_words[j].bounding_box.vertices[0].x

        while get_word(all_words[j])!= 'LR' and get_word(all_words[j+1]) != 'DATE':
            ship_customer_address += get_word(all_words[j]) + ' '
            j += 1
        j += 3

        lr_date = get_word(all_words[j])

        for word in all_words[j+1:]:
            if abs(word.bounding_box.vertices[0].x - x_coords_ship_add) > 80:
                bill_customer_address += get_word(word) + ' '
            else:
                ship_customer_address += get_word(word) + ' '
                x_coords_ship_add = word.bounding_box.vertices[2].x

        dictionary[key[0]], dictionary[key[1]], dictionary[key[2]] = bill_customer_name, bill_customer_address, bill_customer_code
        dictionary[key[3]], dictionary[key[4]], dictionary[key[5]] = ship_customer_name, ship_customer_address, ship_customer_code
        dictionary[key[6]], dictionary[key[7]], dictionary[key[8]], dictionary[key[2]] = invoice_num, invoice_date, lr_date,lr_num

        return dictionary


    def get_rows(self,table_start):
        block_table_start = self.page.blocks[table_start]
        blocks = self.page.blocks[table_start+1:]
        all_words = []
        for block in blocks:
            for para in block.paragraphs:
                for word in para.words:
                    all_words.append(word)
        x = block_table_start.bounding_box.vertices[0].x
        j = 0
        block_numbers = []
        while j<len(blocks):
            if abs(blocks[j].bounding_box.vertices[0].x - x) <= 50:
                block_numbers.append(j)
            j += 1

        rows = []
        for i,block_number in enumerate(block_numbers):
            y = blocks[block_number].bounding_box.vertices[2].y
            row = []
            for word in all_words:
                if abs(y - word.bounding_box.vertices[2].y) < 50:
                    row.append(word)
            rows.append(sorted(row,key=lambda x: x.bounding_box.vertices[0].x))
        return rows

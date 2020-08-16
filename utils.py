
def get_word(word):
    text = ''
    for symbol in word.symbols:
        text += symbol.text
    return text


def num_blocks_nd_flags(page):
    all_words = []
#     import pdb; pdb.set_trace()
    for block in page.blocks:
        for para in  block.paragraphs:
            for word in para.words:
                all_words.append(word)
    i = 0
    num_blocks = 1
    bill_ship_separate = False
    ship_invoice_separate = False
    while i< len(all_words):
        text = get_word(all_words[i])
        if text == 'BILL' and get_word(all_words[i+1]) == 'TO' and get_word(all_words[i+3]) != 'CONSIGNEE':
            num_blocks += 1
            bill_ship_separate = True

        if text == 'CONSIGNEE' and get_word(all_words[i+5]) != 'INVOICE':
            num_blocks += 1
            ship_invoice_separate = True
            break

        i += 1
    return num_blocks , bill_ship_separate, ship_invoice_separate


def find_idx(blocks,words):
    for i,block in enumerate(blocks):
        for para in block.paragraphs:
            for j,word in enumerate(para.words):
                text = get_word(word)
                if len(words)==2 and len(para.words)>2:
                    if text == words[0] and get_word(para.words[j+1]) == words[1]:
                        return i
                    
                elif len(words) == 3 and len(para.words)>3:
                    if text == words[0] and get_word(para.words[j+1]) == words[1] and get_word(para.words[j+2]) == words[2]:
                        return i
                else:
                    if text == words[0]:
                        return i
                    
                    
    
def find_gstin_block(blocks,target_bill_block):
    for i,block in enumerate(blocks):
        for para in block.paragraphs:
            for j,word in enumerate(para.words):
                text = get_word(word)
                if text == 'GSTIN':
                    bill_x = blocks[target_bill_block].bounding_box.vertices[0].x
                    if blocks[i].bounding_box.vertices[0].x - bill_x <= 100:
                        bill_gstin_block = i
                    else:
                        ship_gstin_block = i
    return bill_gstin_block , ship_gstin_block


def get_block_numbers(page,num_blocks,bill_ship_separate,ship_invoice_separate):
    if num_blocks == 3:
        
        target_bill_block = find_idx(page.blocks,['Receiver'])
        target_ship_block = find_idx(page.blocks[target_bill_block:],['CONSIGNEE']) + target_bill_block
        target_invoice_block = find_idx(page.blocks[target_ship_block:],['INVOICE','NO']) + target_ship_block
        
        bill_gstin_block ,ship_gstin_block = find_gstin_block(page.blocks[target_invoice_block:],target_bill_block)
        bill_gstin_block += target_invoice_block
        ship_gstin_block += target_invoice_block
        
        table_start = find_idx(page.blocks[ship_gstin_block:],['SL','.','No.']) + ship_gstin_block
        
        return target_bill_block, target_invoice_block, target_ship_block , ship_gstin_block, bill_gstin_block, table_start
    
    elif num_blocks == 2:
        if bill_ship_separate:
            target_bill_block = find_idx(page.blocks,['Receiver'])
            target_ship_block = find_idx(page.blocks[target_bill_block:],['CONSIGNEE']) + target_bill_block
            
            bill_gstin_block ,ship_gstin_block = find_gstin_block(page.blocks[target_ship_block:],target_bill_block)
            bill_gstin_block += target_ship_block
            ship_gstin_block += target_ship_block
            
            table_start = find_idx(page.blocks[ship_gstin_block:],['SL','.','No.']) + ship_gstin_block
            
            return target_bill_block, target_ship_block , ship_gstin_block, bill_gstin_block, table_start
        
        if ship_invoice_separate:
            target_bill_block = find_idx(page.blocks,['Receiver'])
            
            target_invoice_block = find_idx(page.blocks[target_bill_block:],['INVOICE','NO']) + target_bill_block
        
            bill_gstin_block ,ship_gstin_block = find_gstin_block(page.blocks[target_invoice_block:],target_bill_block)
            bill_gstin_block += target_invoice_block
            ship_gstin_block += target_invoice_block
        
            
            table_start = find_idx(page.blocks[ship_gstin_block:],['SL','.','No.']) + ship_gstin_block
            
            return target_bill_block, target_invoice_block , ship_gstin_block, bill_gstin_block, table_start
    else:
        
        target_bill_block = find_idx(page.blocks,['Receiver'])
        bill_gstin_block ,ship_gstin_block = find_gstin_block(page.blocks[target_bill_block:],target_bill_block)
        bill_gstin_block += target_invoice_block
        ship_gstin_block += target_invoice_block
        
            
        table_start = find_idx(page.blocks[ship_gstin_block:],['SL','.','No.']) + ship_gstin_block
        
        return target_bill_block, ship_gstin_block, bill_gstin_block, table_start

        
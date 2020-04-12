#!/usr/bin/env python3

import argparse  # parsing sys.argv line args
import os
import sys
import os.path
import Block
from Block import printBlock
from BlockPack import pack_block,unpack, pack_inital_block #functions I created to pack and unpack a block
from Blockchain import Blockchain
import datetime




os.environ['BCHOC_FILE_PATH'] = 'data.bin' #THIS IS HERE FOR TESTING, NEEDS TO BE COMMENTED OUT WHEN SUBMITTING

#try: 
#    print("BCHOC FILE PATH:", os.environ['BCHOC_FILE_PATH']) 
#except KeyError:  
#    print("Environment variable does not exist") 



###############################################################
#checks if the inital block exists, if not it creates inital block and returns false
def check_if_initial_block(file_path , bc):
    if os.path.exists(os.environ['BCHOC_FILE_PATH']):
        return True
    else:
        initial_block = Block.create_initial_block() # create initial block
        block_bytes= pack_inital_block(initial_block) #pack the inital block into bytes
        with open(os.environ['BCHOC_FILE_PATH'],'wb') as fp:   #open a file to store block
            fp.write(block_bytes)#write the initial block to binary file
            fp.write(initial_block.data) # write the block data to file (make sure the string is in bytes)
        print('Blockchain file not found. Created INITIAL block.')
        bc.blocks.append(initial_block)
        return False

###############################################################



#def add_initial_block(bc):
#    initial_block = Block.create_initial_block() # create initial block
#    block_bytes= pack_inital_block(initial_block) #pack the inital block into bytes
#    with open(os.environ['BCHOC_FILE_PATH'],'wb') as fp:   #open a file to store block
#        fp.write(block_bytes)#write the initial block to binary file
#        fp.write(initial_block.data) # write the block data to file (make sure the string is in bytes)
#    print('Blockchain file not found. Created INITIAL block.')
#    bc.blocks.append(initial_block)
        

###################################################################

bc = Blockchain()   #initialize the blockchain

arguments = sys.argv[1:]  # grab everything in list except executable name


parser = argparse.ArgumentParser()  # parser object

#=======================================================================================================================================================



if sys.argv[1] == "init":
 
    if len(sys.argv) > 2: #make sure we aren't adding extra arguments
        sys.exit('Invalid Parameters')
    if os.path.exists(os.environ['BCHOC_FILE_PATH']) == False:# if file doesn't exist
        initial_block = Block.create_initial_block() # create initial block
        block_bytes= pack_inital_block(initial_block) #pack the inital block into bytes
        with open(os.environ['BCHOC_FILE_PATH'],'wb') as fp:   #open a file to store block
            fp.write(block_bytes)#write the initial block to binary file
            fp.write(initial_block.data) # write the block data to file (make sure the string is in bytes)
        print('Blockchain file not found. Created INITIAL block.')
        
    else:#no blockchain file , need to create one with initial block
         with open(os.environ['BCHOC_FILE_PATH'],'rb') as fp:
           block_bytes = fp.read(68) #read 68 bytes of struct header
           initial_block = unpack(block_bytes)  #unpack the bytes and return a block object
           printBlock(initial_block)
         print('Blockchain file found with INITIAL block.')
       


#=======================================================================================================================================================
elif sys.argv[1] == 'verify':
    # verify code here
    print("Parse the blockchain and validate all entries.")
    done = False
    with open('data.bin','rb') as fp:
        while True:
            data_bytes = fp.read(68) # read the file to get bytes
            if not data_bytes:
                break
            block = unpack(data_bytes) # unpack the bytes
            block.data = fp.read(block.dataLength) # read the amount of blocks of data we have
            bc.fill_list(block)
    bc.verify()
            






#=======================================================================================================================================================



elif sys.argv[1] == 'add':
    parser.add_argument('add', help="Add a new evidence item to the blockchain and associate it with the given case identifier. For users convenience, more than one item_id may be given at a time, which will create a blockchain entry for each item without the need to enter the case_id multiple times. The state of a newly added item is CHECKEDIN. The given evidence ID must be unique(i.e., not already used in the blockchain) to be accepted.")
    parser.add_argument('-c', help="Specifies the case identifier that the evidence is associated with. Must be a valid UUID. When used with log only blocks with the given case_id are returned.")
    # makes a list of the remaining numbers
    parser.add_argument('-i', nargs=argparse.REMAINDER, help="Specifies the evidence item’s identifier. When used with log only blocks with the given item_id are returned. The item_ID must be unique within the blockchain. This means you cannot re-add an evidence item once the remove action has been performed on it.")
    args = parser.parse_args(arguments)
    
    #--------------------------------------------------------------------
    check_if_initial_block(os.environ['BCHOC_FILE_PATH'], bc)
    #--------------------------------------------------------------------

    for j in range(0,len(args.i)):
        bc.add(args.c,args.i[j])
    with open(os.environ['BCHOC_FILE_PATH'],'ab') as fp:
         for i in range (1,len(bc.blocks)):
            block_bytes= pack_block(bc.blocks[i])
            fp.write(block_bytes)
            fp.write(bc.blocks[i].data.encode('utf-8'))

#=======================================================================================================================================================


elif sys.argv[1] == 'checkin':
    parser.add_argument(
        'checkin', help="Add a new checkin entry to the chain of custody for the given evidence item. Checkin actions may only be performed on evidence items that have already been added to the blockchain.")
    parser.add_argument('-i', help="Specifies the evidence item’s identifier. When used with log only blocks with the given item_id are returned. The item ID must be unique within the blockchain. This means you cannot re-add an evidence item once the remove action has been performed on it.")
    args = parser.parse_args(arguments)
    print(args.i)  # args.i holds the value of the itme ID

#=======================================================================================================================================================

elif sys.argv[1] == 'checkout':
    parser.add_argument(
        'checkout', help="Add a new checkout entry to the chain of custody for the given evidence item. Checkout actions may only be performed on evidence items that have already been added to the blockchain.")
    parser.add_argument('-i', help="Specifies the evidence item’s identifier. When used with log only blocks with the given item_id are returned. The item ID must be unique within the blockchain. This means you cannot re-add an evidence item once the remove action has been performed on it.")
    args = parser.parse_args(arguments)
    print(args.i)  # args.i holds the value of the itme ID

#=======================================================================================================================================================

elif sys.argv[1] == 'log':
    parser.add_argument('log', help="Display the blockchain entries giving the oldest first (unless -r is given).")
    parser.add_argument('-r', '--reverse',
                        help="Reverses the order of the block entries to show the most recent entries first.")  # optional arg NEED TO FIX THIS ONE it is expect something after -r
    parser.add_argument('-n',
                        help="When used with log, shows num_entries number of block entries.")  # optional arg
    parser.add_argument('-c', help="Specifies the case identifier that the evidence is associated with. Must be a valid UUID. When used with log only blocks with the given case_id are returned.")  # optional arg
    parser.add_argument('-i', help="Specifies the evidence item’s identifier. When used with log only blocks with the given item_id are returned. The item ID must be unique within the blockchain. This means you cannot re-add an evidence item once the remove action has been performed on it.")  # optional arg
    args = parser.parse_args(arguments)
    if args.reverse:
        print("you want the chain reversed")
    if args.n:
        print("you want the number of entries")
    if args.c:
        print("you want the only the blocks that contain this case ID")
    if args.i:
        print("you only want the blocks that contain this item ID")

#=======================================================================================================================================================

elif sys.argv[1] == 'remove':
    parser.add_argument('remove', help="Prevents any further action from being taken on the evidence item specified. The specified item must have a state of CHECKEDIN for the action to succeed.")
    parser.add_argument('-i', help="Specifies the evidence item’s identifier. When used with log only blocks with the given item_id are returned. The item ID must be unique within the blockchain. This means you cannot re-add an evidence item once the remove action has been performed on it.")
    parser.add_argument(
        '-y', '--why', help="Reason for the removal of the evidence item. Must be one of: DISPOSED, DESTROYED, or RELEASED. If the reason given is RELEASED, -o must also be given.")
    parser.add_argument(
        '-o', help="Information about the lawful owner to whom the evidence was released. At this time, text is free-form and does not have any requirements.")
    print('remove')


#=======================================================================================================================================================



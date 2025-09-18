import userdb
import admin_recorddb
import chatdb
import messagedb
import emworddb
import senworddb

def dispatch(command):
    if(command==None):
        return 0
    db_type=command[0]
    del(command[0])
    if(db_type=='userdb'):
        return dispatch_userdb(command)
    elif(db_type=='admin_recorddb'):
        return dispatch_admin_recordb(command)
    elif(db_type=='chatdb'):
        return dispatch_chatdb(command)
    elif(db_type=='messagedb'):
        return dispatch_messagedb(command)
    elif(db_type=='emworddb'):
        return dispatch_emworddb(command)
    elif(db_type=='senworddb'):
        return dispatch_senworddb(command)
    else:
        return 0

def dispatch_userdb(command):
    if(command==None):
        return 0
    fun_type=command[0]
    if(fun_type=='add_user'):
        if(len(command)<4):
            return 0
        return userdb.add_user(command[1],command[2],command[3])
    elif(fun_type=='get_user_fields'):
        if(len(command)<3):
            return 0
        return userdb.get_user_fields(command[1],command[2])
    elif(fun_type=='clear_all_users'):
        return userdb.clear_all_users()
    elif(fun_type=='get_all_users'):
        return userdb.get_all_users()
    elif(fun_type=='delete_user_by_id'):
        if(len(command)<2):
            return 0
        return userdb.delete_user_by_id(command[1])
    elif(fun_type=='update_user_field'):
        if(len(command)<4):
            return 0
        return userdb.update_user_field(command[1],command[2],command[3])
    elif(fun_type=='check_user_exists'):
        if(len(command)<2):
            return 0
        return userdb.check_user_exists(command[1])
    else:
        return 0
    
def dispatch_admin_recordb(command):
    if(command==None):
        return False
    fun_type=command[0]
    if(fun_type=='clear_all_admin_record'):
        return admin_recorddb.clear_all_admin_record()
    elif(fun_type=='add_admin_record'):
        if(len(command)<4):
            return False
        return admin_recorddb.add_admin_record(command[1],command[2],command[3])
    elif(fun_type=='delete_admin_record_by_id'):
        if(len(command)<2):
            return False
        return admin_recorddb.delete_admin_record_by_id(command[1])
    elif(fun_type=='find_admin_record_by_field'):
        if(len(command)<3):
            return False
        return admin_recorddb.find_admin_record_by_field(command[1],command[2])
    else:
        return False
    
def dispatch_chatdb(command):
    if(command==None):
        return False
    fun_type=command[0]
    if(fun_type=='clear_all_chat'):
        return chatdb.clear_all_chat()
    elif(fun_type=='get_all_chats'):
        return chatdb.get_all_chats()
    elif(fun_type=='add_chat'):
        if(len(command)<3):
            return False
        return chatdb.add_chat(command[1],command[2])
    elif(fun_type=='delete_chat'):
        if(len(command)<2):
            return False
        return chatdb.delete_chat(command[1])
    elif(fun_type=='get_chat_fields'):
        if(len(command)<3):
            return False
        return chatdb.get_chat_fields(command[1],command[2])
    elif(fun_type=='update_chat_field'):
        if(len(command)<4):
            return False
        return chatdb.update_chat_field(command[1],command[2],command[3])
    elif(fun_type=='find_chat_by_field'):
        if(len(command)<2):
            return 0
        return chatdb.find_chat_by_field(command[1])
    else:
        return False

def dispatch_messagedb(command):
    if(command==None):
        return False
    fun_type=command[0]
    if(fun_type=='clear_all_message'):
        return messagedb.clear_all_message()
    elif(fun_type=='add_message'):
        if(len(command)<4):
            return False
        return messagedb.add_message(command[1],command[2],command[3])
    elif(fun_type=='delete_message'):
        if(len(command)<2):
            return False
        return messagedb.delete_message(command[1])
    elif(fun_type=='get_message_fields'):
        if(len(command)<3):
            return False
        return messagedb.get_message_fields(command[1],command[2])
    elif(fun_type=='update_message_field'):
        if(len(command)<4):
            return False
        return messagedb.update_message_field(command[1],command[2],command[3])
    elif(fun_type=='find_message_by_field'):
        if(len(command)<2):
            return False
        return messagedb.find_message_by_field(command[1])
    elif(fun_type=='delete_message_by_chat_id'):
        if(len(command)<2):
            return False
        return messagedb.delete_message_by_chat_id(command[1])
    else:
        return False

def dispatch_emworddb(command):
    if(command==None):
        return False
    fun_type=command[0]
    if(fun_type=='clear_all_emword'):
        return emworddb.clear_all_emword()
    elif(fun_type=='add_emword'):
        if(len(command)<4):
            return False
        return emworddb.add_emword(command[1],command[2],command[3])
    elif(fun_type=='delete_emword'):
        if(len(command)<2):
            return False
        return emworddb.delete_emword(command[1])
    elif(fun_type=='get_all_senword'):
        return emworddb.get_all_senword()
    elif(fun_type=='check_emword_by_field'):
        return emworddb.check_emword_by_field(command[1])
    elif(fun_type=='update_emword_field'):
        return emworddb.update_emword_field(command[1],command[2],command[3])
    else:
        return False

def dispatch_senworddb(command):
    if(command==None):
        return False
    fun_type=command[0]
    if(fun_type=='clear_all_senword'):
        return senworddb.clear_all_senword()
    elif(fun_type=='add_senword'):
        if(len(command)<2):
            return False
        return senworddb.add_senword(command[1])
    elif(fun_type=='delete_senword'):
        if(len(command)<2):
            return False
        return senworddb.delete_senword(command[1])
    elif(fun_type=='get_senword_by_id'):
        if(len(command)<2):
            return False
        return senworddb.get_senword_by_id(command[1])
    elif(fun_type=='get_all_senword'):
        return senworddb.get_all_senword()
    else:
        return False

def test(type):
    if(type==1):
        command=['userdb','check_user_exists',113]
        print(dispatch(command))
    else:
        print('ERROR')

if __name__ == "__main__":
    test(1)
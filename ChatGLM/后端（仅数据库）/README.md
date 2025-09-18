# 数据库代码说明
## 1.redisdb.py
redis数据库连接文件，各数据库函数通过调用该文件函数对redis数据库进行连接

## 2.db_dispatch.py
数据库调度文件，给外部留出的接口，接收外部的命令数组command，依据数组内容调度各个数据库
### 2.1 dispatch（command）
总调度函数，接收command命令，根据第一条命令（command[0]）去调度不同表的调度函数
### 2.2 dispatch_userdb(command)
用户表调度函数
### 2.3 dispatch_admin_recordb(command)
管理员记录表调度函数
### 2.4 dispatch_chatdb(command)
对话表调度函数
### 2.5 dispatch_messagedb(command)
消息表调度函数
### 2.6 dispatch_emworddb(command)
情感词表调度函数
### 2.7 dispatch_senworddb(command)
敏感词表调度函数

## 3.userdb.py
用户表文件
### 3.1 add_user
添加用户信息
### 3.2 get_user_fields
获得用户某个字段（'all'为全部字段）的内容
### 3.3 clear_all_users
清空用户表
### 3.4 delete_user_by_id
根据id删除用户
### 3.5 update_user_field
更新用户某字段内容

## 4.admin_record.py
管理员记录表文件
### 4.1 clear_all_admin_record
清空表
### 4.2 add_admin_record
添加管理员操作记录
### 4.3 delete_admin_record_by_id
根据id删除记录
### 4.4 find_admin_record_by_field
根据某字段的值查找记录

## 5.chatdb.py
对话记录表文件
### 5.1 clear_all_chat
清空表
### 5.2 add_chat
添加记录
### 5.3 delete_chat
删除记录
### 5.4 get_chat_fields
获得对话某字段的内容
### 5.5 update_chat_field
更新某字段的值
### 5.6 find_chat_by_field
根据某字段的值查找对话

## 6.messagedb.py
消息记录表文件
### 6.1 clear_all_message
清空表
### 6.2 add_message
添加消息
### 6.3 delete_message
删除消息
### 6.4 get_message_fields
获得某字段的值
### 6.5 update_message_field
更新某字段的值
### 6.6 find_message_by_field
根据某字段的值查找消息
### 6.7 delete_message_by_chat_id
根据chat_id删除对应对话的所有消息

## 7.emworddb.py
情感词表文件
### 7.1 clear_all_emword
清空表
### 7.2 add_emword
添加情感词
### 7.3 delete_emword
删除情感词
### 7.4 get_all_senword
获得所有情感词

## 8.senworddb.py
敏感词表文件
### 8.1 clear_all_senword
清空表
### 8.2 add_senword
添加敏感词
### 8.3 delete_senword
删除敏感词
### 8.4 get_senword_by_id
根据id获得敏感词
### 8.5 get_all_senword
获得所有敏感词
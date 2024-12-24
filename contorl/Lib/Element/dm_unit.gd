extends HBoxContainer

var sended := false 

var dm_info : Dictionary:
	set(dm):
		dm_info = dm
		if dm.get("author","").is_empty():
			push_warning("Author info empty")
			queue_free()
			return
		elif dm.get("content","").is_empty():
			push_warning("Content info empty")
			queue_free()
			return
		elif dm.get("price",-1) == -1:
			push_warning("No price info")
			queue_free()
			return
		type = dm["type"]
		author = dm["author"]
		master_lv = dm["price"]
		chat_info = dm["content"]

var master_lv : int:
	set(i):
		master_lv = 2 * (10 ** int(4-author[0])%4) + (5 ** author[1]) # 舰队等级加权+徽章等级加权
		master_lv += i # 花费金瓜子数(元*1000)
		$GiftBox/Price/GiftPrice.value = i
		$GiftBox/Weight.value = master_lv
var answer_chat : String = "你好！"
var o_content : String:
	set(t):
		o_content = t
		$Chat.text = t
var retell : String = ""

"""
author = [
	message.privilege_type,
	message.medal_level,
	message.medal_name,
	message.author_name,
]
"""
var author : Array:
	set(a):
		author = a
		$AuthorBox/Privilege.text = Global.GuardLevel[a[0]]
		$AuthorBox/Medal.text = a[2]
		$AuthorBox/Level.text = "lv" + str(a[1])
		$ID.text = a[3]

var type : int = 0
var chat_info : Array:
	set(a):
		chat_info = a
		match type:
			0: # 弹幕类 [content,author_type]
				o_content = chat_info[0]
				$GiftBox/Gift.text = Global.AuthorType[chat_info[1]]
				var title : String
				match int(chat_info[1]):
					0 : title = author[3]
					1 : title = Global.GuardLevel[author[0]] + author[3]
					2 : title = Global.AuthorType[chat_info[1]]
					3 : title = Global.AuthorType[chat_info[1]]
				answer_chat = title + "说：" + chat_info[0]
				retell = o_content
			1: # SC类 [content]
				o_content = chat_info[0]
				$GiftBox/Gift.text = "SuperChat"
				var title : String = author[3] + "给你打了" + str(dm_info["price"]/1000) + "元，说："
				answer_chat = title + chat_info[0]
				_on_send_pressed()
			2: # 礼物类 [giftname,num]
				$GiftBox/Gift.text = chat_info[0]
				o_content = str(chat_info[1]) + "*" + chat_info[0]
				answer_chat = author[3] + "送了你礼物" + str(chat_info[1]) + "*" + chat_info[0]
				_on_send_pressed()
			3: # 上舰类 [type,num,unit]
				$GiftBox/Gift.text = "上舰!" + Global.GuardLevel[a[0]]
				o_content = str(chat_info[1]) + chat_info[2] + Global.GuardLevel[a[0]]
				answer_chat = author[3] + "给你充值了" + str(dm_info["price"]/1000) + \
							"元！成为了你的" + Global.GuardLevel[a[0]]
				_on_send_pressed()

signal send_dm
func _on_send_pressed() -> void:
	sended = true
	$Send.disabled = true
	emit_signal("send_dm",answer_chat,true,retell)

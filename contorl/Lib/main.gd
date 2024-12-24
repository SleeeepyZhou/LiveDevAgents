extends MarginContainer

const DM_UNIT = preload("res://Lib/Element/DM_unit.tscn")
@onready var DMBox : VBoxContainer = $Split/DMBox/Box/Box/Box

const CHAT_UNIT = preload("res://Lib/Element/Chat_unit.tscn")
const MIAO_UNIT = preload("res://Lib/Element/Dev_unit.tscn")
@onready var ChatBox: VBoxContainer = $Split/ChatBox/Box/Chat/Box/Box/Box

@onready var captions = $Captions
@onready var prompt : LineEdit = $Split/ChatBox/Box/Send/Box/Prompt
@onready var auto : CheckBox = $Split/ChatBox/Box/Send/Box/Auto
@onready var ask : CheckBox = $Split/ChatBox/Box/Send/Box/Ask

const WSurl = "ws://127.0.0.1:8848/dm/control"

const ASKurl = "http://127.0.0.1:8123/ask"
const HISTORYurl = "http://127.0.0.1:8123/history"
const SAYurl = "http://127.0.0.1:8123/say"

func _ready() -> void:
	Global.api_url = ASKurl
	socket.connect_to_url(WSurl)
	history_path = OS.get_executable_path().get_base_dir() + "/"
	var temp = Time.get_datetime_string_from_system().split(":")
	history_path += "".join(temp) + ".txt"

func _process(_delta: float) -> void:
	DM_ji()
	read_sendlist()

# 错误提示
func new_tip(text : String):
	var tip = Label.new()
	tip.text = text
	tip.add_theme_color_override("font_color", Color.RED)
	tip.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	tip.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	tip.add_theme_font_size_override("font_size", 20)
	return tip

## 弹幕机
var socket = WebSocketPeer.new()
var is_connect := true:
	set(b):
		is_connect = b
		if !is_connect:
			DMBox.add_child(new_tip("DMwebError. Plz reconnect..."))

# 手动控制
func _on_connect_pressed():
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_CLOSED:
		socket = WebSocketPeer.new()
		socket.connect_to_url(WSurl)
		is_connect = true
func _on_refreshDM_timeout():
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_OPEN:
		socket.send_text("")
	elif state == WebSocketPeer.STATE_CLOSED:
		_on_connect_pressed()

# 弹幕管理
var has_newdm := false
func DM_manage(DMlist : Array):
	if DMlist.is_empty():
		return
	has_newdm = true
	var to_box : Array
	to_box = DMlist
	
	#var repeat
	#for DM in DMlist:
		#if DM.get("type", -1) == 0:
			#pass
	
	for DM in to_box:
		var dm_unit = DM_UNIT.instantiate()
		DMBox.add_child(dm_unit)
		dm_unit.send_dm.connect(send)
		dm_unit.dm_info = DM

# 自动轮询弹幕
func DM_ji():
	socket.poll()
	if is_connect:
		var state = socket.get_ready_state()
		if state == WebSocketPeer.STATE_OPEN:
			while socket.get_available_packet_count():
				var temp_data = socket.get_packet().get_string_from_utf8()
				var tempdm = null
				if temp_data.begins_with("["):
					tempdm = JSON.parse_string(temp_data)
				if tempdm:
					DM_manage(tempdm)
				elif temp_data != "[]":
					DMBox.add_child(new_tip(temp_data))
		elif state == WebSocketPeer.STATE_CLOSED:
			is_connect = false


## 回复
func programer(prompt : String):
	var http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.timeout = 10
	var head : PackedStringArray = ["Content-Type: application/json"]
	var data = JSON.stringify({"command": prompt})
	http_request.request("http://127.0.0.1:5000/execute", head, HTTPClient.METHOD_POST, data)
	var r = await http_request.request_completed
	if r[1] == 200:
		r = r[-1].get_string_from_utf8()
		print(r)
	http_request.queue_free()

# 手动回复
func _on_send_pressed() -> void:
	var temp = prompt.text
	prompt.text = ""
	send(temp, ask.button_pressed)
func _on_prompt_submitted(_new_text):
	var temp = prompt.text
	prompt.text = ""
	send(temp, ask.button_pressed)

# 自动回复
func auto_send():
	var dm_list : Array[Vector2] = []
	var total_weight : float = 0
	for i in range(clampi(DMBox.get_child_count(),0,maxlist)):
		var dm = DMBox.get_child(-(i+1))
		if !(dm is HBoxContainer) or dm.sended:
			continue
		var weight : float = Vector2(2 * dm.master_lv,len(dm.o_content)).length()
		total_weight += weight
		var tempv = Vector2(-(i+1), weight)
		dm_list.append(tempv)
	if dm_list.is_empty():
		has_newdm = false
	else:
		var r = randf() * total_weight
		var tempf : float = 0
		var target : int
		for dm_v in dm_list:
			tempf += dm_v.y
			if tempf > r:
				@warning_ignore("narrowing_conversion")
				target = dm_v.x
				break
		DMBox.get_child(target)._on_send_pressed()

# 加入队列
var asking := false # 回复线程
var send_list : Array = [] # 回复队列
func send(text : String, is_ask : bool, retell : String = ""):
	var new_task = [text, is_ask, retell]
	programer(retell)
	#send_list.append(new_task)

# 回复请求
func post(text : String, is_ask : bool, retell : String):
	asking = true
	var new_unit
	if is_ask:
		new_unit = CHAT_UNIT.instantiate()
	else:
		new_unit = MIAO_UNIT.instantiate()
	new_unit.chat = text
	ChatBox.add_child(new_unit)
	var res = await Global.post_api(text, is_ask, retell)
	if res[0]:
		if is_ask:
			new_unit = MIAO_UNIT.instantiate()
			new_unit.chat = res[1][1]
			ChatBox.add_child(new_unit)
		
		captions.captions = res[1][1]
		var http_request = HTTPRequest.new()
		add_child(http_request)
		http_request.timeout = 10
		var completed := false
		while !completed:
			http_request.request(SAYurl + "?task_id=" + res[1][2])
			var r = await http_request.request_completed
			var reply = r[-1].get_string_from_utf8()
			if reply == "true":
				completed = true
			else:
				await get_tree().create_timer(1).timeout
		captions.is_completed = true
		http_request.queue_free()
		
	else:
		print(res)
	asking = false

# 自动轮询回复
const maxlist = 50
func read_sendlist():
	if asking:
		return
	if !send_list.is_empty():
		var current_ask = send_list.pop_front()
		post(current_ask[0],current_ask[1],current_ask[2])
	elif auto.button_pressed and has_newdm:
		auto_send()

func _on_caption_toggled(toggled_on):
	captions.visible = toggled_on

# 历史管理
var history_path : String
var chat_num : int = 0
func _auto_save() -> void:
	if ChatBox.get_child_count() == chat_num:
		return
	else:
		chat_num = ChatBox.get_child_count() + 1
	var http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.timeout = 10
	http_request.request(HISTORYurl)
	var history = await http_request.request_completed
	if history[1] == 200:
		history = history[-1].get_string_from_utf8()
	http_request.queue_free()
	var save_path = FileAccess.open(history_path, FileAccess.WRITE)
	save_path.store_string(str(history))
	save_path.close()
	ChatBox.add_child(new_tip("Histroy Saved"))

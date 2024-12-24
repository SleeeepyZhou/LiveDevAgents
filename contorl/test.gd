extends Control

func _ready() -> void:
	var data = "84b8b441-73bc-4b45-a324-22a182cdacd2"
	var http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.timeout = 10
	http_request.request("http://127.0.0.1:8120/check" + "?task_id=" + data)
	var r = await http_request.request_completed
	if r[1] == 200:
		var reply = r[-1].get_string_from_utf8()
		print(reply)

func _on_button_pressed() -> void:
	var http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.timeout = 10
	var head : PackedStringArray = ["Content-Type: application/json"]
	var data = JSON.stringify({"command": $LineEdit.text})
	http_request.request("http://127.0.0.1:8120/meeting", head, HTTPClient.METHOD_POST, data)
	var r = await http_request.request_completed
	if r[1] == 200:
		r = r[-1].get_string_from_utf8()
		print(r)
	http_request.queue_free()

func _on_button_2_pressed() -> void:
	var http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.timeout = 10
	var head : PackedStringArray = ["Content-Type: application/json"]
	var data = JSON.stringify({"command": $LineEdit.text})
	http_request.request("http://127.0.0.1:8120/designer", head, HTTPClient.METHOD_POST, data)
	var r = await http_request.request_completed
	if r[1] == 200:
		r = r[-1].get_string_from_utf8()
		print(r)
	http_request.queue_free()
	pass
	
	
	
	#var http_request = HTTPRequest.new()
	#add_child(http_request)
	#http_request.timeout = 10
	#var head : PackedStringArray = ["Content-Type: application/json"]
	#var data = JSON.stringify({"command": $LineEdit.text})
	#http_request.request("http://127.0.0.1:5000/execute", head, HTTPClient.METHOD_POST, data)
	#var r = await http_request.request_completed
	#if r[1] == 200:
		##r = r[-1].get_string_from_utf8()
		#print(r)
	#http_request.queue_free()
	#

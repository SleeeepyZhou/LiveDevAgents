extends Window

var captions : String = "":
	set(t):
		is_running = true
		is_completed = false
		await get_tree().create_timer(0.35 * t.length()).timeout
		captions = ""
		$Captions/Label.text = ""
		for c in t:
			if is_completed:
				break
			captions += c
			$Captions/Label.text = captions
			await get_tree().create_timer(0.1).timeout
		captions = t
		$Captions/Label.text = t
		is_running = false

var is_running := false
var is_completed := false:
	set(b):
		if (b and is_running) or !b:
			is_completed = b
		elif !is_running:
			is_completed = false

func _on_close_requested():
	hide()
	$"../Split/DMBox/ButtonBox/Box/Box/Caption".button_pressed = false

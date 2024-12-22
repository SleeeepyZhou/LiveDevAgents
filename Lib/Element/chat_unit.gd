extends HBoxContainer

var chat : String:
	set(t):
		chat = t
		$TextEdit.text = t

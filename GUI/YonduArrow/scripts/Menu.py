from godot import exposed, export
from godot import *


@exposed
class Menu(Node):
	
	frame_counter = export(int, default=0)
	CYCLE = export(int, default=200)
	buttons = export(bool)		# (list[Button])
	
	def _ready(self):
		self.buttons = [self.get_node("ButtonStart"), self.get_node("ButtonExit")]

	def on_button_in(self, button):
		self.buttons[button].get_node("ButtonShape").color = Color(1, 1, 1, 0.6)
		self.buttons[button].get_node("ButtonText").modulate = Color(0, 240 / 255, 1, 1)
		self.buttons[button].get_node("ButtonText")
		
	def on_button_exit(self):
		self.get_tree().quit()
		
	def _process(self, delta):
		if self.frame_counter < self.CYCLE:
			prec = min(self.frame_counter, self.CYCLE - self.frame_counter) / self.CYCLE * 2
			for button in self.buttons:
				if not button.is_hovered():
					button.get_node("ButtonShape").color = Color(1, 1, 1, 0.6 * prec)
					button.get_node("ButtonText").modulate = Color(0, 240 / 255, 1, prec)
		self.frame_counter = (self.frame_counter + 1) % self.CYCLE

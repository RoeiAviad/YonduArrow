from godot import exposed, export
from godot import *
from scripts.ImageDetector import ImageDetector

@exposed
class GazeTune(Node2D):

	is_begin = export(bool, default=False)
	detector = export(bool)		# (ImageDetector)
	poses = export(bool)		# (list[tuple[int]])
	counter = export(int, default=0)
	
	def _ready(self):
		self.poses = [(60, 60), (1860, 60), (1860, 1020), (60, 1020)]
		self.detector = ImageDetector()

	def _process(self, delta):
		if not self.visible:
			if self.counter * delta >= 5:
				self.get_tree().change_scene("res://scenes/Main.tscn")
			self.counter += 1
			return
		if not self.is_begin or len(self.detector.corners) >= 4:
			return
		self.get_node("Dot").position = Vector2(*(self.poses[len(self.detector.corners)]))
		if Input.is_action_pressed("ui_accept") and delta * self.counter >= 0.5:
			self.counter = 0
			self.detector.detect_gaze()
			if len(self.detector.corners) == 4:
				self.visible = False
				for x, y in self.detector.corners:
					self.get_node("/root/Global").corners.append(x.item())
					self.get_node("/root/Global").corners.append(y.item())
		self.counter += 1
		
	def start(self):
		self.is_begin = True

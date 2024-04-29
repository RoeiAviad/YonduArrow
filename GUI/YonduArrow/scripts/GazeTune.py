from godot import exposed, export
from godot import *
from scripts.ImageDetector import ImageDetector

RADIUS = 60


@exposed
class GazeTune(Node2D):
	is_begin = export(bool, default=False)
	detector = export(bool)  # (ImageDetector)
	poses = export(bool)  # (list[tuple[int]])
	counter = export(int, default=0)

	def _ready(self):
		self._initialized = False
		size = self.get_viewport_rect().size
		self.poses = [
			(RADIUS, RADIUS),
			(size.x - RADIUS, RADIUS),
			(size.x - RADIUS, size.y - RADIUS),
			(RADIUS, size.y - RADIUS)
		]
		self.detector = ImageDetector(size)
		self.detector.process()
		self._initialized = True

	def _process(self, delta):
		if not getattr(self, "_initialized", False):
			return
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
			self.detector.process()
			self.detector.detect_gaze()
			if len(self.detector.corners) == 4:
				self.visible = False
		self.counter += 1

	def start(self):
		self.is_begin = True

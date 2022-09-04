from godot import exposed, export
from godot import *


@exposed
class Loading(Area2D):

	counter = export(int, default=0)
	CYCLE = 2

	def _process(self, delta):
		if self.counter <= self.CYCLE - 0.5:
			self.rotation_degrees = (360 / (self.CYCLE - 0.5)) * self.counter
		else:
			self.rotation_degrees = 0
		self.counter += delta
		self.counter = 0 if self.counter >= self.CYCLE else self.counter

from godot import exposed, export
from godot import *
from scripts.Hands import Hands

@exposed
class Fist(KinematicBody):
	
	rotate_counter = export(int, default=0)
	moving_func = export(int, default=0)
	speed = export(int, default=4)
	hands = export(bool)		# (Hands)
	frame_counter = export(int, default=0)
	detection = export(bool)	# (Tuple)
	
	def _ready(self):
		self.rotation_degrees += Vector3(-90, 0, 0)
		self.translation += Vector3(0, -0.1, 0.1)
		self.hands = Hands()
		self.detection = False, False
	
	def _physics_process(self, delta):
		temp_frames = round((1 / delta) / 6)
		if self.frame_counter % temp_frames == 0:
			self.detection = self.hands.detect()
		self.frame_counter = (self.frame_counter + 1) % temp_frames
		
		self.call_func()
		if self.detection[0] and self.detection[1]:
			self.up()
		else:
			self.down()
		
	def up(self):
		if self.rotate_counter < 90 / self.speed:
			self.rotation_degrees += Vector3(self.speed, 0, 0)
			self.translation += Vector3(0, self.speed / 900, -self.speed / 900)
			self.rotate_counter += 1
			self.moving_func = 1
		else:
			self.moving_func = 0
			
	def down(self):
		if self.rotate_counter > 0:
			self.rotation_degrees += Vector3(-self.speed, 0, 0)
			self.translation += Vector3(0, -self.speed / 900, self.speed / 900)
			self.rotate_counter -= 1
			self.moving_func = 2
		else:
			self.moving_func = 0
			
	def call_func(self):
		if self.moving_func == 1:
			self.up()
		elif self.moving_func == 2:
			self.down()

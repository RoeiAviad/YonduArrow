from godot import exposed, export
from godot import *
from scripts.ImageDetector import ImageDetector

@exposed
class Main(Node):
	
	detector = export(bool)		# (ImageDetector)
	frame_counter = export(int, default=0)
	detection = export(bool)	# (Tuple)
	fist = export(KinematicBody)
	arrow = export(KinematicBody)
	arrow_hand = export(bool, default=False)

	def _ready(self):
		self.detector = ImageDetector()
		self.detection = False, False
		self.fist = self.get_node("Fist")
		self.arrow = self.get_node("ArrowPivot")
		
	def _process(self, delta):
		self.process_fist(delta)
		self.process_arrow(delta)
			
	def process_fist(self, delta):
		temp_frames = round((1 / delta) / 6)
		if self.frame_counter % temp_frames == 0:
			self.detection = self.detector.detect_hand()
		self.frame_counter = (self.frame_counter + 1) % temp_frames
		
		if self.detection[0] and self.detection[1]:
			self.fist.up()
		else:
			self.fist.down()
			
	def process_arrow(self, delta):
		mouse = self.get_viewport().get_mouse_position()
		
		z_index = 8
		for i in range(1, 81):		# search for correct place
			if abs(self.get_node("CameraPivot/Camera").project_position(mouse, i / 10).y - 0.25) < 0.1:
				z_index = i / 10
				break
		pos = self.get_node("CameraPivot/Camera").project_position(mouse, z_index)
		
		if self.fist.is_up():		# return to hand
			pre = Vector3(0.09, 0.5, -0.5)
			enter = Vector3(0.09, 0.67, 0.76)
			exit = Vector3(0.09, 0.71, 0.888)
			if self.arrow.translation.distance_to(enter) > 0.01 and not self.arrow_hand:
				speed = 4 if self.arrow.translation.distance_to(enter) > 0.5 else 8
				self.arrow.look_at(pre, pre)
				self.arrow.translation += (enter - self.arrow.translation) * delta * speed
			elif self.arrow.translation.distance_to(exit) > 0.01:
				self.arrow_hand = True
				self.arrow.look_at(pre, pre)
				self.arrow.translation += (exit - self.arrow.translation) * delta * 4
		elif self.arrow.translation.distance_to(pos) > 0.01:	# move
			self.arrow_move(pos, 2, delta)
			self.arrow_hand = False
		else:		# nothing or gravity
			self.arrow_hand = False

	def arrow_move(self, pos, speed, delta):
		self.arrow.look_at(pos, pos)
		self.arrow.translation += (pos - self.arrow.translation) * delta * speed

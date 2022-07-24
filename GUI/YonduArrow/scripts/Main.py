from godot import exposed, export
from godot import *
from scripts.Hands import Hands

@exposed
class Main(Node):
	
	hands = export(bool)		# (Hands)
	frame_counter = export(int, default=0)
	detection = export(bool)	# (Tuple)
	fist = export(KinematicBody)
	arrow = export(KinematicBody)

	def _ready(self):
		self.hands = Hands()
		self.detection = False, False
		self.fist = self.get_node("Fist")
		self.arrow = self.get_node("ArrowPivot")
		
	def _process(self, delta):
		self.process_fist(delta)
		self.process_arrow(delta)
			
	def process_fist(self, delta):
		temp_frames = round((1 / delta) / 6)
		if self.frame_counter % temp_frames == 0:
			self.detection = self.hands.detect()
		self.frame_counter = (self.frame_counter + 1) % temp_frames
		
		if self.detection[0] and self.detection[1]:
			self.fist.up()
		else:
			self.fist.down()
			
	def process_arrow(self, delta):
		mouse = self.get_viewport().get_mouse_position()
		
		z_index = 8
		for i in range(1, 81):
			if abs(self.get_node("CameraPivot/Camera").project_position(mouse, i / 10).y) < 0.1:
				z_index = i / 10
				break
		pos = self.get_node("CameraPivot/Camera").project_position(mouse, z_index)
		
		self.arrow.look_at(pos, pos)
		self.arrow.translation += (pos - self.arrow.translation) * delta * 2

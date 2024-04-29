from godot import exposed, export
from godot import *
from scripts.ImageDetector import ImageDetector

ARROW_Y = 0.175
FIST_Y = 0.4


@exposed
class Main(Node):
	detector = export(bool)  # (ImageDetector)
	frame_counter = export(int, default=0)
	detection = export(bool)  # (Tuple)
	fist = export(KinematicBody)
	arrow = export(KinematicBody)
	arrow_hand = export(bool, default=False)

	def _ready(self):
		self.detector = ImageDetector(self.get_viewport().size)
		self.detection = False, False
		self.fist = self.get_node("Fist")
		self.arrow = self.get_node("ArrowPivot")

	def _process(self, delta):
		self.detector.process()
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

	def translate_position(self, pos):
		if not isinstance(pos, Vector2):
			pos = Vector2(*pos)
		# translate 2D pos into 3D pos
		z_index = 8
		for i in range(1, 81):
			if abs(self.get_node("CameraPivot/Camera").project_position(pos, i / 10).y - ARROW_Y) < 0.1:
				z_index = i / 10
				break
		return self.get_node("CameraPivot/Camera").project_position(pos, z_index)

	def process_arrow(self, delta):
		# screen_pos = self.get_viewport().get_mouse_position()
		screen_pos = self.detector.detect_gaze()
		if self.fist.is_up():
			self.return_to_hand(delta)
			return
		self.arrow_hand = False
		if not screen_pos:
			return
		pos = self.translate_position(screen_pos)
		if self.arrow.translation.distance_to(pos) > 0.01:
			self.arrow_move(pos, 2, delta)

	def return_to_hand(self, delta):
		pre = Vector3(0.09, FIST_Y - 0.14, -0.5)
		enter = Vector3(0.09, FIST_Y + 0.03, 0.76)
		exit = Vector3(0.09, FIST_Y + 0.07, 0.888)
		if self.arrow.translation.distance_to(enter) > 0.01 and not self.arrow_hand:
			speed = 4 if self.arrow.translation.distance_to(enter) > 0.5 else 8
			self.arrow_move(enter, speed, delta, pre)
		elif self.arrow.translation.distance_to(exit) > 0.01:
			self.arrow_hand = True
			self.arrow_move(exit, 4, delta, pre)

	def arrow_move(self, pos, speed, delta, look=None):
		look = look or pos
		self.arrow.look_at(look, look)
		self.arrow.translation += (pos - self.arrow.translation) * delta * speed

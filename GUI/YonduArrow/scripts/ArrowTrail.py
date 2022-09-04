from godot import exposed, export
from godot import *


@exposed
class ArrowTrail(Node):

	counter = export(int, default=0)
	arrow = export(Position3D)
	line = export(ImmediateGeometry)
	
	def _ready(self):
		self.arrow = self.get_node("../ArrowPivot")
		self.line = self.get_node("Line")

	def _process(self, delta):
		self.get_node("Point_%d" % self.counter).translation = self.arrow.translation
		# self.counter = (self.counter + 1) % self.get_child_count()
		
		self.line.begin(Mesh.PRIMITIVE_LINES)
		self.line.add_vertex(self.arrow.translation)
		self.line.end()

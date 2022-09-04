from godot import exposed, export
from godot import *


@exposed
class Global(Node):

	corners = export(Array, default=Array())

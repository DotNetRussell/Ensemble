from enum import Enum

class MessageType(Enum):
	INFORMATION = 0
	WARNING = 1
	NOTIFICATION = 2

class StreamEvent(Enum):
	Agent = 0
	Director = 1
	Command = 2
	Job = 3
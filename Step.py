from dataclasses import dataclass

@dataclass
class DataSet:
	mass: float
	leg_length: float
	time: list[float]
	vgrf: list[float]
	vacc: list[float]
	vvel: list[float]
	vdisp: list[float]
	gct: float
	theta: float
	kleg: float
	kvert: float

# __init__に渡す情報。1周期で切り取ったデータ。右足か左足か。
class Step:
	def __init__(self):
		self.side
		self.is_valid = True
		self.data = DataSet()


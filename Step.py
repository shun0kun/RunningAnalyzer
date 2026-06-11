from dataclasses import dataclass
from DataSet import StepData

class Step:
	def __init__(self, data: StepData):
		self.is_valid = True
		self.data = data
		self.side
	
	def _compute_vdisp(time: list[float], vvel: list[float]) -> list[float]:
		vdisp = [0.0] * len(time)
		# 計算
		return vdisp
	
	def _compute_theta() -> float:
		return
	
	def _compute_leg_stiffness() -> float:
		return
	
	def _compute_vertical_stiffness() -> float:
		return


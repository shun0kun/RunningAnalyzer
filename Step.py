from .DataSet import StepData
from . import utils
import numpy as np
from .constants import G, LEFT, RIGHT

class Step:
	def __init__(self, data: StepData):
		self.is_valid = True
		self.data = data
		self.data.toe_off_index = self.data.vgrf.index(0.0)
		self.data.vgrf_max = max(self.data.vgrf)
		if self.data.vgrf_max < self.data.mass * G:
			self.invalidate()
			return
		self.data.vdisp = self._compute_vdisp(self.data.time, self.data.vvel)
		self.data.time_norm, self.data.vgrf_norm = utils.time_normalize(self.data.time[:self.data.toe_off_index], self.data.vgrf[:self.data.toe_off_index])
		_, self.data.vacc_norm = utils.time_normalize(self.data.time[:self.data.toe_off_index], self.data.vacc[:self.data.toe_off_index])
		_, self.data.vvel_norm = utils.time_normalize(self.data.time[:self.data.toe_off_index], self.data.vvel[:self.data.toe_off_index])
		_, self.data.fvel_norm = utils.time_normalize(self.data.time[:self.data.toe_off_index], self.data.fvel[:self.data.toe_off_index])
		_, self.data.vdisp_norm = utils.time_normalize(self.data.time[:self.data.toe_off_index], self.data.vdisp[:self.data.toe_off_index])
		self.data.bottom_index = self.data.vdisp.index(min(self.data.vdisp[:self.data.toe_off_index]))
		self.data.gct = self.data.time[self.data.toe_off_index] - self.data.time[0]
		self.data.theta = self._compute_theta(self.data.time, self.data.fvel, self.data.toe_off_index, self.data.leg_length)
		if self.data.theta is None:
			self.invalidate()
			return
		self.data.leg_compressed = self._compute_leg_compressed(self.data.leg_length, self.data.theta, abs(self.data.vdisp[self.data.bottom_index]))
		self.data.kleg = self._compute_leg_stiffness(self.data.vgrf[self.data.bottom_index], self.data.leg_compressed)
		self.data.kvert = self._compute_vertical_stiffness(self.data.vgrf[self.data.bottom_index], abs(self.data.vdisp[self.data.bottom_index]))

	@staticmethod	
	def _compute_vdisp(time: list[float], vvel: list[float]) -> list[float]:
		return utils.cumulative_integrate_trapezoidal(time, vvel, 0.0)

	# 算出精度が少々心配。速度定数か平均にするのも検討しておく。fvelの値がしっかりしてれば大丈夫かも。速度計じゃなくて速度の方を使っていれば。
	@staticmethod
	def _compute_theta(time: list[float], fvel: list[float], toe_off_index: int, leg_length: float) -> float | None:
		sin_val = utils.integrate_trapezoidal(time[:toe_off_index+1], fvel[:toe_off_index+1], 0.0) / (2 * leg_length)
		if abs(sin_val) > 1.0:
			return None
		theta = np.arcsin(sin_val)
		return theta

	@staticmethod	
	def _compute_leg_compressed(leg_length: float, theta: float, delta_y: float) -> float:
		return delta_y + leg_length * (1 - np.cos(theta))

	@staticmethod	
	def _compute_leg_stiffness(vgrf_bottom: float, leg_compressed: float) -> float | None:
		if leg_compressed is None or leg_compressed == 0.0:
			return None
		return vgrf_bottom / leg_compressed

	@staticmethod	
	def _compute_vertical_stiffness(vgrf_bottom: float, delta_y: float) -> float | None:
		if delta_y == 0.0:
			return None
		return vgrf_bottom / delta_y

	def validate(self) -> None:
		self.is_valid = True

	def invalidate(self) -> None:
		self.is_valid = False
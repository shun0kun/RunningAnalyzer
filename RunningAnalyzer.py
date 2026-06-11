import numpy
from force_plate_data import ForcePlateData
from .Step import Step
import utils
from dataclasses import dataclass
import numpy as np
from .DataSet import RunningData
from .constants import G, LEFT, RIGHT

class RunningAnalyzer:
	def __init__(self, filepath: str, massdata: int | float | str, leg_length: int | float):
		self.fp = ForcePlateData(filepath)
		self.data = RunningData()
		self.data.mass = self._resolve_mass(massdata)
		self.data.leg_length = float(leg_length)
		self.data.time = self.fp.get("時刻")
		self.data.vgrf = self._preprocess_vgrf(self.fp.read("合成-Fz"))
		self.data.vgrf_left = self.fp.get("左-Fz")
		self.data.vgrf_right = self.fp.get("右-Fz")
		self.data.vacc = self._compute_vertical_acceleration(self.data.mass, self.data.time, self.data.vgrf)
		self.data.vvel = self._compute_vertical_velocity(self.data.time, self.data.vacc, self.data.vgrf)
		self.data.fvel_left = self.fp.get("左-速度計")
		self.data.fvel_right = self.fp.get("右-速度計")
		self.steps = self._extract_steps(self.data)

	@staticmethod
	def _resolve_mass(massdata: int | float | str) -> float:
		if isinstance(massdata, (int, float)):
			return float(massdata)
		fp = ForcePlateData(massdata)
		mass = np.mean(fp.read("合成-Fz")) / G
		return float(mass)
	
	@staticmethod
	def _preprocess_vgrf(vgrf_raw: list[float]) -> list[float]:
		# lowpass filterはここに入れる
		vgrf_proc = utils.threshold(vgrf_raw, 40.0)
		return vgrf_proc

	@staticmethod
	def _compute_vertical_acceleration(mass: float, time: list[float], vgrf: list[float]) -> list[float]:
		return [(f - mass * G) / mass for f in vgrf]

	@staticmethod
	def _compute_vertical_velocity(time: list[float], vacc: list[float], vgrf: list[float]) -> list[float]:
		swing_mid_indices = []
		is_contact = vgrf[0] > 0
		for i in range(len(time)):
			if is_contact and vgrf[i] == 0:
				is_contact = False
				left = i
			elif not is_contact and vgrf[i] > 0:
				is_contact = True
				right = i - 1
				swing_mid_indices.append((left + right) // 2)
		
		vvel = [0.0] * len(time)
		if len(swing_mid_indices) == 0:
			return vvel
		vvel[:swing_mid_indices[0]+1] = utils.cumulative_integrate_trapezoidal(time[:swing_mid_indices[0]+1][::-1], vacc[:swing_mid_indices[0]+1][::-1], 0.0)[::-1]
		for mid, next_mid in zip(swing_mid_indices, swing_mid_indices[1:]):
			vvel[mid:next_mid] = utils.cumulative_integrate_trapezoidal(time[mid:next_mid], vacc[mid:next_mid], 0.0)
		vvel[swing_mid_indices[-1]:] = utils.cumulative_integrate_trapezoidal(time[swing_mid_indices[-1]:], vacc[swing_mid_indices[-1]:], 0.0)
		return vvel

	@staticmethod
	def _extract_steps(data: RunningData) -> list[Step]:
		steps = []
		is_contact = data.vgrf[0] > 0.0
		left = None
		for i in range(len(data.vgrf)):
			if is_contact and data.vgrf[i] == 0.0:
				is_contact = False
			elif not is_contact and data.vgrf[i] > 0.0:
				is_contact = True
				right = i - 1
				if left is not None:
					steps.append(Step(data.extract_step(left, right)))
				left = i
		return steps

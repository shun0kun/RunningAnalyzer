import numpy
from force_plate_data import ForcePlateData
from .Step import Step
import utils
from dataclasses import dataclass
import numpy as np
from .DataSet import RunningData

G = 9.81

class RunningAnalyzer:
	def __init__(self, filepath: str, massdata: int | float | str, leg_length: int | float):
		self.fp = ForcePlateData(filepath)
		self.data = RunningData()
		self.data.mass = self._resolve_mass(massdata)
		self.data.leg_length = float(leg_length)
		self.data.time = self.fp.read("time")
		self.data.vgrf = self._preprocess_vgrf(self.fp.read("合成-Fz"))
		self.data.vacc = self._compute_vertical_acceleration(self.data.mass, self.data.time, self.data.vgrf)
		self.data.vvel = self._compute_vertical_velocity(self.data.time, self.data.vacc)
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
	def _compute_vertical_velocity(time: list[float], vacc: list[float]) -> list[float]:
		vvel = [0.0] * len(time)
		# 計算
		return vvel

	@staticmethod
	def _extract_steps(data: RunningData) -> list[Step]:
		steps = []
		is_contact = data.vgrf[0] > 0.0
		left = None
		for i in range(len(data.vgrf)):
			if not is_contact and data.vgrf[i] > 0.0:
				is_contact = True
				left = i - 1
			elif is_contact and data.vgrf[i] == 0.0:
				is_contact = False
				right = i
				if left is not None:
					steps.append(data.extract_step(left, right))
		return steps

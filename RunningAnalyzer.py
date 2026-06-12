from force_plate_data import ForcePlateData
from .Step import Step
from . import utils
from dataclasses import dataclass
from collections.abc import Iterable
import numpy as np
import matplotlib.pyplot as plt
from .DataSet import RunningData
from .constants import G, LEFT, RIGHT

class RunningAnalyzer:
	def __init__(self, filepath: str, massdata: int | float | str, leg_length: int | float):
		self.fp = ForcePlateData(filepath)

		self.data = RunningData()
		self.data.mass = self._resolve_mass(massdata)
		self.data.leg_length = float(leg_length)
		self.data.time = self.fp.get("時刻")
		self.data.vgrf = self._preprocess_vgrf(self.fp.get("合成-Fz"))
		self.data.vgrf_left = self.fp.get("左-Fz")
		self.data.vgrf_right = self.fp.get("右-Fz")
		self.data.vacc = self._compute_vertical_acceleration(self.data.mass, self.data.time, self.data.vgrf)
		self.data.vvel = self._compute_vertical_velocity(self.data.time, self.data.vacc, self.data.vgrf)
		self.data.fvel_left = self.fp.get("左-速度")
		self.data.fvel_right = self.fp.get("右-速度")

		self.steps = self._extract_steps(self.data)
		self.data.n_steps = len([step for step in self.steps if step.is_valid])

		# stance phaseにおけるもの
		self.data.time_mean = [i / 100.0 for i in range(101)]
		self.data.vacc_mean = [np.mean([step.data.vacc_norm[i] for step in self.steps if step.is_valid]) for i in range(len(self.data.time_mean))]
		self.data.vvel_mean = [np.mean([step.data.vvel_norm[i] for step in self.steps if step.is_valid]) for i in range(len(self.data.time_mean))]
		self.data.vdisp_mean = [np.mean([step.data.vdisp_norm[i] for step in self.steps if step.is_valid]) for i in range(len(self.data.time_mean))]
		self.data.vgrf_mean = [np.mean([step.data.vgrf_norm[i] for step in self.steps if step.is_valid]) for i in range(len(self.data.time_mean))]
		self.data.vgrf_left_mean = [np.mean([step.data.vgrf_left_norm[i] for step in self.steps if step.is_valid]) for i in range(len(self.data.time_mean))]
		self.data.vgrf_right_mean = [np.mean([step.data.vgrf_right_norm[i] for step in self.steps if step.is_valid]) for i in range(len(self.data.time_mean))]

		self.data.kleg_left_mean = np.mean([x.data.kleg for x in self.steps if x.is_valid and x.data.side == LEFT])
		self.data.kleg_right_mean = np.mean([x.data.kleg for x in self.steps if x.is_valid and x.data.side == RIGHT])
		self.data.kvert_left_mean = np.mean([x.data.kvert for x in self.steps if x.is_valid and x.data.side == LEFT])
		self.data.kvert_right_mean = np.mean([x.data.kvert for x in self.steps if x.is_valid and x.data.side == RIGHT])

	@staticmethod
	def _resolve_mass(massdata: int | float | str) -> float:
		if isinstance(massdata, (int, float)):
			return float(massdata)
		fp = ForcePlateData(massdata)
		mass = np.mean(fp.get("合成-Fz")) / G
		return float(mass)

	@staticmethod
	def _preprocess_vgrf(vgrf_raw: list[float]) -> list[float]:
		# lowpass filterはここに入れる
		vgrf_proc = utils.threshold(vgrf_raw, 40.0)
		return vgrf_proc

	@staticmethod
	def _compute_vertical_acceleration(mass: float, time: list[float], vgrf: list[float]) -> list[float]:
		return [(f - mass * G) / mass for f in vgrf]

	#真のmid pointが取れていない
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

	def _reanalyze(self) -> None:
		self.data.kleg_left_mean = np.mean([x.data.kleg for x in self.steps if x.is_valid and x.data.side == LEFT])
		self.data.kleg_right_mean = np.mean([x.data.kleg for x in self.steps if x.is_valid and x.data.side == RIGHT])
		self.data.kvert_left_mean = np.mean([x.data.kvert for x in self.steps if x.is_valid and x.data.side == LEFT])
		self.data.kvert_right_mean = np.mean([x.data.kvert for x in self.steps if x.is_valid and x.data.side == RIGHT])		

	def invalidate_steps(self, ids: int | Iterable[int]) -> None:
		if isinstance(ids, int):
			ids = [ids]
		for i in ids:
			self.steps[i].invalidate()
			self.data.n_steps -= 1
		self._reanalyze()

	def validate_steps(self, ids: int | Iterable[int]) -> None:
		if isinstance(ids, int):
			ids = [ids]
		for i in ids:
			self.steps[i].validate()
			self.data.n_steps += 1
		self._reanalyze()

	def select_steps(self, ids: int | Iterable[int]) -> None:
		self.invalidate_steps(range(len(self.steps)))
		self.validate_steps(ids)

	def export_check_steps_fig(self) -> None:
		plt.figure(figsize=(60,4.8))
		plt.plot(self.data.time, self.data.vgrf, color="black", alpha=1.0, linewidth=1.0)
		turn = 0
		for i, step in enumerate(self.steps):
			if step.is_valid:
				if step.data.side == RIGHT:
					plt.plot(step.data.global_time, step.data.vgrf, color="red", alpha=1.0, linewidth="1.0")
					plt.text(step.data.global_time[0], max(step.data.vgrf) + 30, str(i), fontsize=5, color="red")
				else:
					plt.plot(step.data.global_time, step.data.vgrf, color="blue", alpha=1.0, linewidth=1.0)
					plt.text(step.data.global_time[0], max(step.data.vgrf) + 30, str(i), fontsize=5, color="blue")
				turn += 1
			else:
				plt.text(step.data.global_time[0], max(step.data.vgrf) + 30, str(i), fontsize=5, color="black")
		plt.xlabel("Time [s]")
		plt.ylabel("vGRF [N]")
		plt.title("Valid Steps (Red=Valid R, Blue=Valid L, Black=Invalid)")
		plt.savefig("valid_steps.png", dpi=500)
		plt.close()

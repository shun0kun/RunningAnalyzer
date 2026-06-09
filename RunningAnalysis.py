from dataclasses import dataclass
import csv
import numpy as np
from .StancePhase import StancePhase
from collections.abc import Iterable

G = 9.81

class RunningAnalysis:
	def __init__(self, filepath: str, massdata: str | int | float, leg_length: float | int, u_left: float | int, u_right: float | int) -> None:
		self.filepath = filepath
		self.m = self._compute_mass(massdata)
		self.l = float(leg_length)
		self.t, self.fz, self.fz_right, self.fz_left = self._load_csv_data(filepath)
		self.pfz, self.pfz_right, self.pfz_left = self._preprocess_fz(self.fz), self._preprocess_fz(self.fz_right), self._preprocess_fz(self.fz_left)
		self.stance_right = self._extract_stance_phases(self.pfz_right, float(u_right))
		self.stance_left = self._extract_stance_phases(self.pfz_left, float(u_left))
		self.kvert_right = np.mean([x.kvert for x in self.stance_right if x.is_valid])
		self.kvert_left = np.mean([x.kvert for x in self.stance_left if x.is_valid])
		self.kleg_right = np.mean([x.kleg for x in self.stance_right if x.is_valid])
		self.kleg_left = np.mean([x.kleg for x in self.stance_left if x.is_valid])
		self.gct_right = np.mean([x.gct for x in self.stance_right if x.is_valid])
		self.gct_left = np.mean([x.gct for x in self.stance_left if x.is_valid])

	def _compute_mass(self, massdata: str | int | float) -> float:
		if isinstance(massdata, (int, float)):
			return float(massdata)
		else:
			with open(massdata) as f:
				fz = []
				reader = csv.reader(f)
				for i, row in enumerate(reader):
					if i < 13:
						continue
					fz.append(float(row[23]))
				mass = np.mean(fz[0:10000])
			return float(mass)

	def _load_csv_data(self, filepath: str) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
		t = []
		fz = []
		fz_right = []
		fz_left = []
		with open(filepath) as f:
			reader = csv.reader(f)
			for i, row in enumerate(reader):
				if i < 13:
					continue
				t.append(float(row[0]))
				fz.append(float(row[23]))
				fz_right.append(float(row[3]))
				fz_left.append(float(row[13]))
		return np.array(t), np.array(fz), np.array(fz_right), np.array(fz_left)

	def _preprocess_fz(self, fz: np.ndarray) -> list[np.ndarray]:
		THRESHOLD = 50.0
		# lowpassを今後ここに入れる
		pfz = np.where(fz > THRESHOLD, fz, 0.0)
		i = 0
		while i < len(self.t) and pfz[i] > 0:
			pfz[i] = 0.0
			i += 1
		i = len(self.t) - 1
		while i > 0 and pfz[i] > 0:
			pfz[i] = 0.0
			i -= 1
		return pfz

	def _extract_stance_phases(self, fz: np.ndarray, u: float) -> list[StancePhase]:
		stance_phases = []
		is_contact = False
		for i in range(len(self.t)):
			if not is_contact and fz[i] > 0.0:
				is_contact = True
				left = i - 1
			elif is_contact and fz[i] == 0.0:
				is_contact = False
				right = i
				stance_phases.append(StancePhase(self.m, self.l, u, self.t[left:right+1], fz[left:right+1]))
		return stance_phases
	
	def invalidate_stance_phases(self, side: str, ids: int | Iterable[int]) -> None:
		if isinstance(ids, int):
			ids = [ids]
		if side == "left":
			for i in ids:
				self.stance_left[i].is_valid = False
		elif side == "right":
			for i in ids:
				self.stance_right[i].is_valid = False
		self._reanalyze()
	
	def validate_stance_phases(self, side: str, ids: int | Iterable[int]) -> None:
		if isinstance(ids, int):
			ids = [ids]
		if side == "left":
			for i in ids:
				self.stance_left[i].is_valid = True
		elif side == "right":
			for i in ids:
				self.stance_right[i].is_valid = True
		self._reanalyze()

	def select_stance_phases(self, side: str, ids: int | Iterable[int]) -> None:
		if side == "left":
			self.invalidate_stance_phases(side, range(len(self.stance_left)))
		elif side == "right":
			self.invalidate_stance_phases(side, range(len(self.stance_right)))
		self.validate_stance_phases(side, ids)
		self._reanalyze()
	
	def _reanalyze(self) -> None:
		self.kvert_right = np.mean([x.kvert for x in self.stance_right if x.is_valid])
		self.kvert_left = np.mean([x.kvert for x in self.stance_left if x.is_valid])
		self.kleg_right = np.mean([x.kleg for x in self.stance_right if x.is_valid])
		self.kleg_left = np.mean([x.kleg for x in self.stance_left if x.is_valid])
		self.gct_right = np.mean([x.gct for x in self.stance_right if x.is_valid])
		self.gct_left = np.mean([x.gct for x in self.stance_left if x.is_valid])

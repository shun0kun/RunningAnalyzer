import numpy as np
from . import utils

G = 9.81

class StancePhase:
	def __init__(self, m: float, leg_len: float, u: float, t: np.ndarray, fz: np.ndarray) -> None:
		self.is_valid = True
		self.m = m
		self.l0 = leg_len
		self.t_global = t
		self.t_local = t - t[0]
		self.u = u
		self.fz = fz
		self.d_y = self._compute_vdisp()
		self.gct = t[-1] - t[0]
		self.theta = self._compute_theta()
		self.l_min = self._compute_l_min()
		self.t_norm, self.fz_norm = utils.time_normalize(self.t_local, self.fz)
		_, self.d_y_norm = utils.time_normalize(self.t_local, self.d_y)
		self.kvert = self._compute_kvert()
		self.kleg = self._compute_kleg()

	# 鉛直下向き正
	def _compute_vdisp(self) -> np.ndarray:
		a = (self.m * G - self.fz) / self.m
		i_bottom = self.fz.argmax()
		v = np.empty(len(self.t_local))
		v[:i_bottom+1] = utils.integrate_trapezoidal(self.t_local[:i_bottom+1], a[:i_bottom+1], 0, "backward")
		v[i_bottom:] = utils.integrate_trapezoidal(self.t_local[i_bottom:], a[i_bottom:], 0)
		d_y = utils.integrate_trapezoidal(self.t_local, v, 0)
		return d_y

	def _compute_theta(self) -> float:
		return np.arcsin((self.u * self.gct) / (2 * self.l0))

	def _compute_l_min(self) -> float:
		return self.l0 * np.cos(self.theta) - max(self.d_y)

	def _compute_kvert(self) -> float:
		return max(self.fz) / max(self.d_y)

	def _compute_kleg(self) -> float:
		return max(self.fz) / (self.l0 - self.l_min)

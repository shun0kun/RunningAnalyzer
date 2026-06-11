from dataclasses import dataclass
from .constants import LEFT, RIGHT


@dataclass
class StepData:
	mass: float | None = None
	leg_length: float | None = None
	time: list[float] | None = None
	global_time: list[float] | None = None
	vgrf: list[float] | None = None
	vgrf_left: list[float] | None = None	
	vgrf_right: list[float] | None = None
	vacc: list[float] | None = None
	vvel: list[float] | None = None
	fvel: list[float] | None = None
	vdisp: list[float] | None = None
	vgrf_norm: list[float] | None = None
	vacc_norm: list[float] | None = None
	vvel_norm: list[float] | None = None
	fvel_norm: list[float] | None = None
	vdisp_norm: list[float] | None = None
	vgrf_max: list[float] | None = None
	gct: float | None = None
	theta: float | None = None
	leg_compressed: float | None = None
	kleg: float | None = None
	kvert: float | None = None

	side: int | None = None
	toe_off_index: int | None = None
	bottom_index: int | None = None

@dataclass
class RunningData:
	mass: float | None = None
	leg_length: float | None = None
	time: list[float] | None = None
	vgrf: list[float] | None = None
	vgrf_left: list[float] | None = None
	vgrf_right: list[float] | None = None
	vacc: list[float] | None = None
	vvel: list[float] | None = None
	fvel_left: list[float] | None = None
	fvel_right: list[float] | None = None

	kleg_right_mean: float | None = None
	kleg_left_mean: float | None = None
	kvert_right_mean: float | None = None
	kvert_left_mean: float | None = None

	n_steps: int | None = None

	def extract_step(self, left: int, right: int) -> StepData:
		if left > right or left < 0 or right > len(self.time) - 1:
			raise ValueError("Invalid indexes")
		step = StepData()
		step.mass = self.mass
		step.leg_length = self.leg_length
		step.time = [t - self.time[left] for t in self.time[left:right+1]]
		step.global_time = self.time[left:right+1]
		step.vgrf = self.vgrf[left:right+1]
		step.vgrf_left = self.vgrf_left[left:right+1]
		step.vgrf_right = self.vgrf_right[left:right+1]
		step.vacc = self.vacc[left:right+1]
		step.vvel = self.vvel[left:right+1]
		step.side = self._determine_side(left, right)
		step.fvel = self.fvel_left[left:right+1] if step.side == LEFT else self.fvel_right[left:right+1]
		return step
	
	def _determine_side(self, left: int, right: int) -> int:
		left_ratio = sum(self.vgrf_left[left:right+1]) / sum(self.vgrf[left:right+1])
		right_ratio = sum(self.vgrf_right[left:right+1]) / sum(self.vgrf[left:right+1])
		if left_ratio > right_ratio:
			return LEFT
		return RIGHT


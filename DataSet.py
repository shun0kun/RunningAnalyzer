from dataclasses import dataclass

@dataclass
class StepData:
	mass: float | None = None
	leg_length: float | None = None
	time: list[float] | None = None
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
	gct: float | None = None
	theta: float | None = None
	leg_compressed: float | None = None
	kleg: float | None = None
	kvert: float | None = None

	side: int | None = None
	toe_off_index: int | None
	bottom_index: int | None

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
	fvel: list[float] | None = None

	def extract_step(self, left: int, right: int) -> StepData:
		if left > right or left < 0 or right > len(self.time) - 1:
			raise ValueError("Invalid indexes")
		step = StepData()
		step.mass = self.mass
		step.leg_length = self.leg_length
		step.time = self.time[left:right+1]
		step.vgrf = self.vgrf[left:right+1]
		step.vgrf_left = self.vgrf_left[left:right+1]
		step.vgrf_right = self.vgrf_right[left:right+1]
		step.vacc = self.vacc[left:right+1]
		step.vvel = self.vvel[left:right+1]
		step.fvel = self.fvel[left:right+1]
		return step



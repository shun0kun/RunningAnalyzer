import numpy as np

def lowpass():
	return

def lerp(a: float, b: float, t: float) -> float:
	return a + t * (b - a)

# intも許した方がいいかな。型ヒントの書き方。
def is_strictly_increasing(x: list[float]) -> bool:
	for i in range(len(x) - 1):
		if x[i] >= x[i + 1]:
			return False
	return True

def time_normalize(time: list[float], signal: list[float], n_points: int = 101) -> tuple[list[float], list[float]]:
	if len(time) != len(signal) or len(time) < 2 or n_points < 2 or not is_strictly_increasing(time):
		raise ValueError("time_normalize: Invalid value")
	phase_origin = []
	phase_target = []
	for i in range(len(time)):
		phase_origin.append((time[i] - time[0]) / (time[-1] - time[0]))
	for i in range(n_points):
		phase_target.append(i / (n_points - 1))
	time_norm = phase_target
	signal_norm = []
	i = 0
	j = 0
	while i < n_points:
		while j < len(phase_origin) - 1 and phase_origin[j + 1] < phase_target[i]:
			j += 1
		signal_norm.append(lerp(signal[j], signal[j + 1], (phase_target[i] - phase_origin[j]) / (phase_origin[j + 1] - phase_origin[j])))
		i += 1
	return time_norm, signal_norm

def integrate_trapezoidal(x: np.ndarray, f: np.ndarray, y0: float, direction: str = "forward") -> np.ndarray:
	y = np.empty(len(x))
	if direction == "backward":
		y[len(x) - 1] = y0
		for i in range(len(x) - 1, 0, -1):
			y[i - 1] = y[i] + lerp(f[i - 1], f[i], 0.5) * (x[i - 1] - x[i])
	else:
		y[0] = y0
		for i in range(len(x) - 1):
			y[i + 1] = y[i] + lerp(f[i], f[i + 1], 0.5) * (x[i + 1] - x[i])
	return y

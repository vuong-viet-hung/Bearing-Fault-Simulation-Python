from dataclasses import dataclass
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np


N_TIME_SAMPLES = 1000
N_SIMULATED_IMPULSES = 5

NATURAL_FREQUENCY = 10.0
DECAY_RATE = 5.0

AVERAGE_PERIOD = 1.0


@dataclass
class DecayComponentCreator: 
    natural_frequency: float
    decay_rate: float

    def __call__(self, t: np.ndarray) -> np.ndarray:
        decay_component = np.exp(-self.decay_rate * t) * np.cos(
            2 * np.pi * self.natural_frequency * t
        )
        decay_component[t < 0] = np.zeros(np.sum(t < 0))
        return decay_component


@dataclass
class FaultSignalCreator:
    impulse_amplitudes: np.ndarray
    create_decay_component: DecayComponentCreator
    average_period: float
    period_fluctuations: Optional[np.ndarray] = None

    def _create_fault_impulse(self, t: np.ndarray, idx: int) -> np.ndarray:
        fault_impulse = self.impulse_amplitudes[idx] * self.create_decay_component(
            t - idx * self.average_period - self.period_fluctuations[idx]
        )
        return fault_impulse

    def __call__(self, t: np.ndarray) -> np.ndarray:
        if self.period_fluctuations is None:
            self.period_fluctuations = np.zeros(len(t))
        fault_impulses = np.array(
            [
                self._create_fault_impulse(t, idx)
                for idx, _ in enumerate(self.impulse_amplitudes)
            ]
        )
        fault_signal = np.sum(fault_impulses, axis=0)
        return fault_signal


def main() -> None:
    impulse_amplitudes = np.ones(N_SIMULATED_IMPULSES)
    create_decay_component = DecayComponentCreator(NATURAL_FREQUENCY, DECAY_RATE)
    create_fault_signal = FaultSignalCreator(
        impulse_amplitudes,
        create_decay_component,
        AVERAGE_PERIOD,
    )

    signal_duration = AVERAGE_PERIOD * N_SIMULATED_IMPULSES
    t = np.linspace(0, signal_duration, N_TIME_SAMPLES)
    x = create_fault_signal(t)
    
    plt.plot(t, x)
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()

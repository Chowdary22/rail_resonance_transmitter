# 📊 TDD Report – Rail Resonance Transmitter

This report documents the Test-Driven Development (TDD) process for verifying key modules in the vibration monitoring system.

---

## ✅ Modules Tested

- `I2CDevice.read_data()`
- `UARTDevice.write()`
- `SPIDevice.read_data()`
- `start_thread()` (from `thread_handler.py`)

---

## 🔴 Red Phase

- Created tests before writing the method logic.
- One or more tests failed because the method wasn’t yet implemented.
- Output saved in `red_phase.txt`

---

## 🟢 Green Phase

- Implemented only enough code to pass the tests.
- All tests passed successfully.
- Output saved in `green_phase.txt`

---

## 🛠 Refactor Phase

- Improved internal method logic (e.g., try/except for robustness).
- Tests still passed, proving behavior is unchanged.
- Output saved in `refactor_phase.txt`

---

## 💡 Summary

- TDD applied successfully to simulate and verify real hardware behavior.
- Final code includes production-safe exception handling.
- The test suite can be reused in CI pipelines or for regression testing.


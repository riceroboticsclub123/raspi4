
## [0.5.6] - 2023-04-29

### Fixed

* Fixed race condition in homing sequence that was causing strange behaviour.  Fixes [#634](https://github.com/odriverobotics/ODrive/issues/634)]  
* When using a load encoder, CAN will report the correct position and velocity.
* When using a load encoder, homing will reset the correct linear position.  Fixes [#651](https://github.com/odriverobotics/ODrive/issues/651)
* Implemented CAN controller error message, which was previously defined but not actually implemented.
* Get Vbus Voltage message updated to match ODrive Pro's CANSimple implementation.
* `vel_setpoint` and `torque_setpoint` will be clamped to `vel_limit` and the active torque limit.  Fixes [#647](https://github.com/odriverobotics/ODrive/issues/647)

### Added

* Added public `controller.get_anticogging_value(uint32)` fibre function to index into the the cogging map.  Fixes [#690](https://github.com/odriverobotics/ODrive/issues/690)
* Added Get ADC Voltage message to CAN (0x1C).  Send the desired GPIO number in byte 1, and the ODrive will respond with the ADC voltage from that pin (if previously configured for analog)
* Added CAN heartbeat message flags for motor, controller, and encoder error.  If flag is true, fetch the corresponding error with the respective message.
* Added scoped enums, e.g. `CONTROL_MODE_POSITION_CONTROL` can be used as `ControlMode.POSITION_CONTROL`
* Added more cyclic messages to can.  Use the `rate_ms` values in `<odrv>.<axis>.config.can` to set the cycle rate of the message in milliseconds.  Set a rate to 0 to disable sending.  The following variables are avaialble:

Command ID | Rate Variable | Message Name
:-- | :-- | :--
 0x01 | `heartbeat_rate_ms` | Heartbeat
 0x09 | `encoder_rate_ms` | Get Encoder Estimates
 0x03 | `motor_error_rate_ms` | Get Motor Error
 0x04 | `encoder_error_rate_ms` | Get Encoder Error
 0x1D | `controller_error_rate_ms` | Get Controller Error
 0x05 | `sensorless_error_rate_ms` | Get Sensorless Error
 0x0A | `encoder_count_rate_ms` | Get Encoder Count
 0x14 | `iq_rate_ms` | Get Iq
 0x15 | `sensorless_rate_ms` | Get Sensorless Estimates
 0x17 | `bus_vi_rate_ms` | Get Bus Voltage Current

### Changed

* Improved can_generate_dbc.py file and resultant .dbc.  Now supports 8 ODrive axes (0..7) natively
* Add units and value tables to every signal in odrive-cansimple.dbc
* Autogenerate odrive-cansimple.dbc on compile

## [0.5.5] - 2022-08-11

* CANSimple messages which previously required the rtr bit to be set will now also respond if DLC = 0
* Ensure endstops update before being checked for errors, to prevent [#625](https://github.com/odriverobotics/ODrive/issues/625)
* Reset trajectory_done_ during homing to ensure a new trajectory is actually computed [#634](https://github.com/odriverobotics/ODrive/issues/634)
* Use `input_xxx` as a DC offset in tuning mode
* Sync `steps_` with input pos.
* Trigger reset of input_pos and pos_setpoint to estimate when changing control mode into position control

## [0.5.4] - 2021-10-12

### Fixed
* Some ASCII protocol commands (e.g. `w axis0.requested_state 4`) resulted in `not implemented` due to an issue with the CI compiler. A workaround was made to fix this.
* Fixed bad response of some ASCII procotol commands (e.g. `r axis0.error` returned `0d` instead of `0`).

### Added
* Added `<axis>.controller.config.vel_integrator_limit`
* Allow setting controller gains on CAN Simple

## [0.5.3] - 2021-09-03

### Fixed
* ASCII protocol commands with multiline responses (`i`, `h`) now return the expected response (in v0.5.2 the response was corrupted)
* odrivetool no longer shows the message `<Task pending coro=... running at ...>` when closing
* Homing used to erroneously complete with `is_homed == True` even if it failed for some reason
* When entering closed loop control in trapezoidal trajectory mode the axis no longer snaps to the 0 position
* Fix python DFU firmware version prerelease status resolution to use correct attribute
* Fixed firmware compiled-in version number

### Added
* `brake_resistor_current` added to interface for reading the commanded brake resistor current

### Changed
* Removed `odrivetool generate-code`. This feature was broken in 0.5.2. Use [`interface_generator.py`](https://github.com/odriverobotics/ODrive/blob/master/tools/fibre-tools/interface_generator.py) instead (see Tupfile.lua for examples).
* Firmware boots on devices with unset OTP.
* Changed CAN heartbeat message to include "trajectory done" flag

## [0.5.2] - 2021-05-21

### Fixed
* spinout error is no longer sticky and doesn't trigger on static torque loads due to I^2*R electrical power
* Step and direction mode resets position when entering closed loop just like `input_pos` does
* CAN baud rate setting is now correctly handled
* `odrivetool dfu` works properly when an ODrive is flashed with the `dfu` switch set to "dfu".
* `odrivetool dfu` now erases the entire flash memory before flashing firmware. This ensures that old configuration parameters are erased.
* ASCII and the Native Protocol do not run at the same time on a UART interface. See `odrv0.config.uart0_protocol` and the `STREAM_PROTOCOL_TYPE` enums for details.

### Added
* `sc` command to ascii protocol to run `odrv.clear_errors()`
* Added phase balance check to motor calibration and MOTOR_ERROR_UNBALANCED_PHASES to error enums
* Added polarity and phase offset calibration for hall effect encoders
* [Mechanical brake support](docs/mechanical-brakes.md)
* Added periodic sending of encoder position on CAN
* Support for UART1 on GPIO3 and GPIO4. UART0 (on GPIO1/2) and UART1 can currently not be enabled at the same time.
* Thermistors now have a 2nd order lowpass filter applied to reduce noise
* 2-norm current clamping is used for AC induction motors
* Added spinout detection to detect incorrect encoder offset and CONTROLLER_ERROR_SPINOUT_DETECTED to error enums.
* Added AARCH64 support to libfibre
* Tuning input mode added to provide sinusoidal position, velocity, or torque stimulus. See INPUT_MODE_TUNING and the controller class for details.
* Added torque mirroring to INPUT_MODE_MIRROR
* `mechanical_power_bandwidth`, `electrical_power_bandwidth`, `spinout_electrical_power_threshold`, `spinout_mechanical_power_threshold` added to `controller.config` for spinout detection.
* `mechanical_power` and `electrical_power` added to `controller`.
* Added autogenerated enums header file [ODriveEnums.h](../Arduino/ODriveArduino/ODriveEnums.h) for Arduino use. Created Jinja template and edited Makefile to autogenerate it. Reflected change in Dockerfile and added note in developer-guide markdown file for updating ODriveEnums.h alongside enums.py.
* Added GetPosition member function in ODriveArduino class to complement existing GetVelocity, SetVelocity, and SetPosition functions.

### Changed
* Step/dir performance improved! Dual axis step rates up to 250kHz have been tested
* Apply_config is called for encoders after a successful direction find
* Full calibration sequence now includes hall polarity calibration if a hall effect encoder is used
* Modified encoder offset calibration to work correctly when calib_scan_distance is not a multiple of 4pi
* Moved thermistors from being a top level object to belonging to Motor objects. Also changed errors: thermistor errors rolled into motor errors
* Use DMA for DRV8301 setup
* Make NVM configuration code more dynamic so that the layout doesn't have to be known at compile time.
* GPIO initialization logic was changed. GPIOs now need to be explicitly set to the mode corresponding to the feature that they are used by. See `<odrv>.config.gpioX_mode`.
* Previously, if two components used the same interrupt pin (e.g. step input for axis0 and axis1) then the one that was configured later would override the other one. Now this is no longer the case (the old component remains the owner of the pin).
* New control loop architecture:
  1. TIM8 update interrupt handler (CNT = 0) runs at a high priority and invokes the system level function `sample_cb()` to sample all timing critical inputs (currently only encoder state).
  2. TIM8 update interrupt handler (CNT = 0) raises an NVIC flag to kick off a lower priority interrupt.
  3. The control loop interrupt handler checks if all ADC measurements are ready and informs both motor objects about the current measurements.
  4. The control loop interrupt handler invokes the system level function `control_loop_cb()` which updates all components (encoders, estimators, torque controllers, etc). The data paths between the components are configured by the Axis threads based on the requested state. This replaces the previous architecture where the components were updated inside the Axis threads in `Axis::run_control_loop()`.
  5. Meanwhile the TIM1 and TIM8 updates for CNT = 3500 will have fired. The control loop interrupt handler thus reads the new ADC measurements and informs both motor objects that a DC calibration event has happened.
  6. Finally, the control loop interrupt invokes `pwm_update_cb` on both motors to make them update their PWM timing registers.
* Components that need low level control over PWM timings are implemented by inheriting from the `PhaseControlLaw` interface. Three components currently inherit this interface: `FieldOrientedController`, `ResistanceMeasurementControlLaw` and `InductanceMeasurementControlLaw`.
* The FOC algorithm is now found in foc.cpp and and is presumably capable of running at a different frequency than the main control tasks (not relevant for ODrive v3).
* ACIM estimator was consolidated into a separate component `<odrv>.acim_estimator`.
* The Automatic Output Enable (AOE) flag of TIM1/TIM8 is used to achieve glitch-free motor arming.
* Sensorless mode was merged into closed loop control mode. Use `<axis>.enable_sensorless_mode` to disable the use of an encoder.
* More informative profiling instrumentation was added.
* A system-level error property was introduced.
* Added `torque_mirror_ratio` and use it to feed-forward `controller_.torque_output` in `INPUT_MODE_MIRROR`
* Accumulate integer steps in step/dir to avoid float precision errors
* Circular setpoint mode must be enabled when the step/dir interface is used.
* Replaced inline enum in ODriveArduino class by including new autogenerated ODriveEnums.h header file.
* Changed the example ODriveArduinoTest.ino file to reflect the new GetPosition member function. Also removed the scope resolution operator to access the enums as it can now be accessed from the global namespace.
* `save_configuration()` reboots the board.

### API Migration Notes
* `axis.config.turns_per_step` changed to `axis.controller.config.steps_per_circular_range`
* `odrive.axis.fet_thermistor`, `odrive.axis.motor_thermistor` moved to `odrive.axis.motor` object
* `enable_uart` and `uart_baudrate` were renamed to `enable_uart0` and `uart0_baudrate`.
* `enable_i2c_instead_of_can` was replaced by the separate settings `enable_i2c0` and `enable_can0`.
* `<axis>.motor.gate_driver` was moved to `<axis>.gate_driver`.
* `<axis>.min_endstop.pullup` and `<axis>.max_endstop.pullup` were removed. Use `<odrv>.config.gpioX_mode = GPIO_MODE_DIGITAL / GPIO_MODE_DIGITAL_PULL_UP / GPIO_MODE_DIGITAL_PULL_DOWN` instead.
* `<axis>.config.can_node_id` was moved to `<axis>.config.can.node_id`
* `<axis>.config.can_node_id_extended` was moved to `<axis>.config.can.is_extended`
* `<axis>.config.can_heartbeat_rate_ms` was moved to `<axis>.config.can.heartbeat_rate_ms`
* `<odrv>.get_oscilloscope_val()` was moved to `<odrv>.oscilloscope.get_val()`.
* Several error flags from `<odrv>.<axis>.error` were removed. Some were moved to `<odrv>.error` and some are no longer relevant because implementation details changed.
* Several error flags from `<odrv>.<axis>.motor.error` were removed. Some were moved to `<odrv>.error` and some are no longer relevant because implementation details changed.
* `<axis>.lockin_state` was removed as the lockin implementation was replaced by a more general open loop control block (currently not exposed on the API).
* `AXIS_STATE_SENSORLESS_CONTROL` was removed. Use `AXIS_STATE_CLOSED_LOOP_CONTROL` instead with `<odrv>.enable_sensorless_mode = True`.
* `<axis>.config.startup_sensorless_control` was removed. Use `<axis>.config.startup_closed_loop_control` instead with `<odrv>.enable_sensorless_mode = True`.
* `<axis>.clear_errors()` was replaced by the system-wide function `<odrv>.clear_errors()`.
* `<axis>.armed_state` was replaced by `<axis>.is_armed`.
* Several properties in `<axis>.motor.current_control` were changed to read-only.
* `<axis>.motor.current_control.Ibus` was moved to `<axis>.motor.I_bus`.
* `<axis>.motor.current_control.max_allowed_current` was moved to `<axis>.motor.max_allowed_current`.
* `<axis>.motor.current_control.overcurrent_trip_level` was removed.
* `<axis>.motor.current_control.acim_rotor_flux` was moved to `<axis>.acim_estimator.rotor_flux`.
* `<axis>.motor.current_control.async_phase_vel` was moved to `<axis>.acim_estimator.stator_phase_vel`.
* `<axis>.motor.current_control.async_phase_offset` was moved to `<axis>.acim_estimator.phase`.
* `<axis>.motor.timing_log` was removed in favor of `<odrv>.task_times` and `<odrv>.<axis>.task_times`.
* `<axis>.motor.config.direction` was moved to `<axis>.encoder.config.direction`.
* `<axis>.motor.config.acim_slip_velocity` was moved to `<axis>.acim_estimator.config.slip_velocity`.
* Several properties were changed to readonly.
* `<axis>.encoder.config.offset` was renamed to ``<axis>.encoder.config.phase_offset`
* `<axis>.encoder.config.offset_float` was renamed to ``<axis>.encoder.config.phase_offset_float`
* `<odrv>.config.brake_resistance == 0.0` is no longer a valid way to disable the brake resistor. Use `<odrv>.config.enable_brake_resistor` instead. A reboot is necessary for this to take effect.
* `<odrv>.can.set_baud_rate()` was removed. The baudrate is now automatically updated when writing to `<odrv>.can.config.baud_rate`.

## [0.5.1] - 2020-09-27
### Added
* Added motor `torque_constant`: units of torque are now [Nm] instead of just motor current.
* Added `motor.config.torque_lim`: limit for motor torque in [Nm].
* [Motor thermistors support](docs/thermistors.md)
* Enable/disable of thermistor thermal limits according `setting axis.<thermistor>.enabled`.
* Introduced `odrive-interface.yaml` as a root source for the ODrive's API. `odrivetool` connects much faster as a side effect.
* Added torque_constant and torque_lim to motor config

### Changed
* **`input_pos`, `input_vel`, `pos_estimate_linear`, `pos_estimate_circular`, are now in units of [turns] or [turns/s] instead of [counts] or [counts/s]**
* **`pos_gain`, `vel_gain`, `vel_integrator_gain`, are now in units of [(turns/s) / turns], [Nm/(turns/s)], [Nm/(turns/s * s)] instead of [(counts/s) / counts], [A/(counts/s)], [A/((counts/s) * s)].** `pos_gain` is not affected. Old values of `vel_gain` and `vel_integrator_gain` should be multiplied by `torque_constant * encoder cpr` to convert from the old units to the new units. `torque_constant` is approximately equal to 8.27 / (motor KV).
* `axis.motor.thermal_current_lim` has been removed. Instead a new property is available `axis.motor.effective_current_lim` which contains the effective current limit including any thermal limits.
* `axis.motor.get_inverter_temp()`, `axis.motor.inverter_temp_limit_lower` and `axis.motor.inverter_temp_limit_upper` have been moved to seperate fet thermistor object under `axis.fet_thermistor`. `get_inverter_temp()` function has been renamed to `temp` and is now a read-only property.
* `axis.config.counts_per_step` is now `axis.config.turns_per_step`
* Outputs of `axis.sensorless_estimator` are now in turns/s instead of electrical rad/s
* Fixed bug of high current during lockin-ramp caused by `motor::update()` expecting a torque command instead of current
* Fixed bug where commanded velocity was extremely high just after sensorless ramp when using `input_mode` INPUT_MODE_VEL_RAMP caused by `vel_setpoint` and `axis.config.sensorless_ramp.vel` being in different units

### Fixed
* Fixed bug of high current during lockin-ramp caused by `motor::update()` expecting a torque command instead of current
* Fixed bug where commanded velocity was extremely high just after sensorless ramp when using `input_mode` INPUT_MODE_VEL_RAMP caused by `vel_setpoint` and `axis.config.sensorless_ramp.vel` being in different units

## [0.5.0] - 2020-08-03
### Added
* AC Induction Motor support.
  * Tracking of rotor flux through rotor time constant
  * Automatic d axis current for Maximum Torque Per Amp (MTPA)
* ASCII "w" commands now execute write hooks.
* Simplified control interface ("Input Filter" branch)
    * New input variables: `input_pos`, `input_vel`, and `input_current`
    * New setting `input_mode` to switch between different input behaviours
      * Passthrough
      * Velocity Ramp
      * 2nd Order Position Filter
      * Trapezoidal Trajectory Planner
    * Removed `set_xxx_setpoint()` functions and made `xxx_setpoint` variables read-only
* [Preliminary support for Absolute Encoders](docs/encoders.md)
* [Preliminary support for endstops and homing](docs/endstops.md)
* [CAN Communication with CANSimple stack](can-protocol.md)
* Gain scheduling for anti-hunt when close to 0 position error
* Velocity Limiting in Current Control mode according to `vel_limit` and `vel_gain`
* Regen current limiting according to `max_regen_current`, in Amps
* DC Bus hard current limiting according to `dc_max_negative_current` and `dc_max_positive_current`
* Brake resistor logic now attempts to clamp voltage according to `odrv.config.dc_bus_overvoltage_ramp_start` and `odrv.config.dc_bus_overvoltage_ramp_end`
* Unit Testing with Doctest has been started for select algorithms, see [Firmware/Tests/test_runner.cpp](Firmware/Tests/test_runner.cpp)
* Added support for Flylint VSCode Extension for static code analysis
* Using an STM32F405 .svd file allows CortexDebug to view registers during debugging
* Added scripts for building via docker.
* Added ability to change uart baudrate via fibre

### Changed
* Changed ratiometric `motor.config.current_lim_tolerance` to absolute `motor.config.current_lim_margin`
* Moved `controller.vel_ramp_enable` to INPUT_MODE_VEL_RAMP.
* Anticogging map is temporarily forced to 0.1 deg precision, but saves with the config
* Some Encoder settings have been made read-only
* Cleaned up VSCode C/C++ Configuration settings on Windows with recursive includePath
* Now compiling with C++17
* Fixed a firmware hang that could occur from unlikely but possible user input
* Added JSON caching to Fibre. This drastically reduces the time odrivetool needs to connect to an ODrive (except for the first time or after firmware updates).
* Fix IPython `RuntimeWarning` that would occur every time `odrivetool` was started.
* Reboot on `erase_configuration()`. This avoids unexpected behavior of a subsequent `save_configuration()` call, since the configuration is only erased from NVM, not from RAM.
* Change `motor.get_inverter_temp()` to use a property which was already being sampled at `motor.inverter_temp`
* Fixed a numerical issue in the trajectory planner that could cause sudden jumps of the position setpoint

## [0.4.12] - 2020-05-06
### Fixed
* Fixed a numerical issue in the trajectory planner that could cause sudden jumps of the position setpoint

## [0.4.11] - 2019-07-25
### Added
* Separate lockin configs for sensorless, index search, and general.
* Check current limit violation: added `ERROR_CURRENT_UNSTABLE`, `motor.config.current_lim_tolerance`.

### Changed
* Ascii command for reboot changed from `sb` to `sr`.

## [0.4.10] - 2019-04-24
### Fixed
* Index search would trigger in the wrong place.

## [0.4.9] - 2019-04-23
### Added
* A release target for ODrive v3.6
* Communication watchdog feature.
* `encoder.set_linear_count(count)` function.
* Configurable encoder offset calibration distance and speed:`calib_scan_distance` and `calib_scan_omega`
* Encoder offset calibration debug variable `calib_scan_response`
* Lock-in drive feature
* Script to enable using a hall signal as index edge.

### Changed
* Moved `traptraj.A_per_css` to `controller.inertia`
* Refactored velocity ramp mode into the new general input filtering structure
* Encoder index search now based on the new lock-in drive feature

### Fixed
* Encoder index interrupts now disabled when not searching

## [0.4.8] - 2019-02-25
### Added
* `dump_errors()` utility function in odrivetool to dump, decode and optionally clear errors.
* `f` command to ascii protocol to get encoder position and velocity feedback.
* `q` command to ascii protocol. It is like the old `p` command, but velocity and current mean limits, not feed-forward.
* `ss`, `se`, `sr` commands to ascii protocol, for save config, erase config and reboot.
* `move_incremental` function for relative trajectory moves.
* `encoder.config.ignore_illegal_hall_state` option.
* `encoder.config.enable_phase_interpolation` option. Setting to false may reduce jerky pulsations at low speed when using hall sensor feedback.
* Analog input. Used the same way as the PWM input mappings.
* Voltage limit soft clamping instead of ERROR_MODULATION_MAGNITUDE in gimbal motor closed loop.
* Thermal current limit with linear derating.

### Changed
* Unified lockin drive modes. Current for index searching and encoder offset calibration now moved to axis.lockin.current.

### Fixed
* Added required 1.5 cycle phase shift between ADC and PWM, lack thereof caused unstable current controller at high eRPM.

## [0.4.7] - 2018-11-28
### Added
* Overspeed fault
* Current sense saturation fault.
* Suppress startup transients by sampling encoder estimate into position setpoint when entering closed loop control.
* Make step dir gpio pins configurable.
* Configuration variable `encoder.config.zero_count_on_find_idx`, true by default. Set to false to leave the initial encoder count to be where the axis was at boot.
* Circular position setpoint mode: position setpoints wrapped [0, cpr). Useful for infinite incremental position control.
* Velocity setpoint ramping. Use velocity control mode, and set `controller.vel_ramp_enable` to true. This will ramp `controller.vel_setpoint` towards `controller.vel_ramp_target` at a ramp rate of `controller.config.vel_ramp_rate`.

### Changed
* Increased switching frequency from around 8kHz to 24kHz. Control loops still run at 8kHz.
* Renamed `axis.enable_step_dir` to `axis.step_dir_active`
* New process for working with STM32CubeMX.

### Fixed
* Would get ERROR_CONTROL_DEADLINE_MISSED along with every ERROR_PHASE_RESISTANCE_OUT_OF_RANGE.
* ODrive tool can now run interactive nested scripts with "%run -i script.py"

## [0.4.6] - 2018-10-07
### Fixed
* Broken printing of floats on ascii protocol

## [0.4.5] - 2018-10-06
### Added
* **Trapezoidal Trajectory Planner**
* Hook to execute protocol property written callback
* -Wdouble-promotion warning to compilation

### Changed
* Make python tools compatible with python 2.7 (so it can be used with ROS)
  * Threading API constructor can't take the daemon parameter, so all thread creation had to be expanded out.
  * `TimeoutError` isn't defined, but it makes for more readable code, so I defined it as an OSError subclass.
  * `ModuleNotFoundError` is replaced by the older ImportError.
  * Print function imported from future
* Using new hooks to calculate:
  * `motor.config.current_control_bandwidth`
    * This deprecates `motor.set_current_control_bandwidth()`
  * `encoder.config.bandwidth`
* Default value for `motor.resistance_calib_max_voltage` changed to 2.0

### Fixed
* An issue where the axis state machine would jump in and out of idle when there is an error
* There is a [bug](https://github.com/ARM-software/CMSIS_5/issues/267) in the arm fast math library, which gives spikes in the output of arm_cos_f32 for input values close to -pi/2. We fixed the bug locally, and hence are using "our_arm_cos_f32".

## [0.4.4] - 2018-09-18
### Fixed
* Serious reliability issue with USB communication where packets on Native and the CDC interface would collide with each other.

## [0.4.3] - 2018-08-30
### Added
* `min_endstop` and `max_endstop` objects can be configured on GPIO
* Axes can be homed if `min_endstop` is enabled
* Encoder position count "homed" to zero when index is found.

### Changed
* We now enforce encoder offset calibration must happen after index is found (if using index)
* Renaming of the velocity estimate `pll_vel` -> `vel_estimate`.
* Hardcoded maximum inductance now 2500 uH.

### Fixed
* Incorrect shifting of offset during index callback
* Once you got an axis error `ERROR_INVALID_STATE` you could never clear it
* Char to int conversion to read motornum on arduino example
* GPIO above #5 would not be used correctly in some cases

## [0.4.2] - 2018-08-04
### Added
* Hall sensor feedback
* Configurable RC PWM input
* Ability to read axis FET temperature
* Config settings for:
  * `motor.config.requested_current_range`
  * `motor.config.current_control_bandwidth` and `motor.set_current_control_bandwidth`. Latter required to invoke gain recalculation.
  * `encoder.config.bandwidth`
  * `sensorless_estimator.config.pm_flux_linkage`

## [0.4.1] - 2018-07-01
### Fixed
* Encoder errors would show up as Axis error `ERROR_MOTOR_FAILED` instead of `ERROR_ENCODER_FAILED`.
* Various pip install dependencies
* Ability for python tools threads to quit properly
* dfuse error prints now python3 compatible

## [0.4.0] - 2018-06-10
### Added
* Encoder can now go forever in velocity/torque mode due to using circular encoder space.
* Protocol supports function return values
* bake Git-derived firmware version into firmware binary. The firmware version is exposed through the `fw_version_[...]` properties.
* `make write_otp` command to burn the board version onto the ODrive's one-time programmable memory. If you have an ODrive v3.4 or older, you should run this once for a better firmware update user experience in the future. Run the command without any options for more details. Once set, the board version is exposed through the `hw_version_[...]` properties.
* infrastructure to publish the python tools to PyPi. See `tools/setup.py` for details.
* Automated test script `run_tests.py`
* System stats (e.g. stack usage) are exposed under `<odrv>.system_stats`

### Changed
* DFU script updates
  * Verify the flash after writing
  * Automatically download firmware from GitHub releases if no file is provided
  * Retain configuration during firmware updates
* Refactor python tools
  * The scripts `explore_odrive.py`, `liveplotter.py`, `drv_status.py` and `rate_test.py` have been merged into one single `odrivetool` script. Running this script without any arguments provides the shell that `explore_odrive.py` used to provide.
  * The command line options of `odrivetool` have changed compared to the original `explore_odrive.py`. See `odrivetool --help` for more details.
  * `odrivetool` (previously `explore_odrive.py`) now supports controlling multiple ODrives concurrently (`odrv0`, `odrv1`, ...)
  * No need to restart the `odrivetool` shell when devices get disconnected and reconnected
  * ODrive accesses from within python tools are now thread-safe. That means you can read from the same remote property from multiple threads concurrently.
  * The liveplotter (`odrivetool liveplotter`, formerly `liveplotter.py`) does no longer steal focus and closes as expected
  * Add commands `odrivetool backup-config` and `odrivetool restore-config`
  * (experimental: start liveplotter from `odrivetool` shell by typing `start_liveplotter(lambda: odrv0.motor0.encoder.encoder_state)`)
* Set thread priority of USB pump thread above protocol thread
* GPIO3 not sensitive to edges by default
* The device now appears as a composite device on USB. One subdevice is still a CDC device (virtual COM port), the other subdevice is a vendor specific class. This should resolve several issues that were caused by conflicting kernel drivers or OS services.
* Add WinUSB descriptors. This will tell Windows >= 8 to automatically load winusb.sys for the ODrive (only for the vendor specific subdevice). This makes it possible to use the ODrive from userspace via WinUSB with zero configuration. The Python tool currently still uses libusb so Zadig is still required.
* Add a configuration to enable the ASCII protocol on USB at runtime. This will only enable the ASCII protocol on the USB CDC subdevice, not the vendor specific subdevice so the python tools will still be able to talk to the ODrive.

### Fixed
* Enums now transported with correct underlying type on native protocol
* USB issue where the device would stop responding when the host script would quit abruptly or reset the device during operation

## [0.3.6] - 2018-03-26
### Added
* **Storing of configuration parameters to Non Volatile Memory**
* **USB Bootloader**
* `make erase_config` to erase the configuration with an STLink (the configuration can also be erased from within explore_odrive.py, using `odrv0.erase_configuration()`)
* Travis-CI builds firmware for all board versions and deploys the binaries when a tag is pushed to master
* General purpose ADC API. See function get_adc_voltage() in low_level.cpp for more detais.

### Changed
* Most of the code from `lowlevel.c` moved to `axis.cpp`, `encoder.cpp`, `controller.cpp`, `sensorless_estimator.cpp`, `motor.cpp` and the corresponding header files
* Refactoring of the developer-facing communication protocol interface. See e.g. `axis.hpp` or `controller.hpp` for examples on how to add your own fields and functions
* Change of the user-facing field paths. E.g. `my_odrive.motor0.pos_setpoint` is now at `my_odrive.axis0.controller.pos_setpoint`. Names are mostly unchanged.
* Rewrite of the top-level per-axis state-machine
* The build is now configured using the `tup.config` file instead of editing source files. Make sure you set your board version correctly. See [here](README.md#configuring-the-build) for details.
* The toplevel directory for tup is now `Firmware`. If you used tup before, go to `Firmware` and run `rm -rd ../.tup; rm -rd build/*; make`.
* Update CubeMX generated STM platform code to version 1.19.0
* Remove `UUID_0`, `UUID_1` and `UUID_2` from USB protocol. Use `serial_number` instead.
* Freertos memory pool (task stacks, etc) now uses Core Coupled Memory.

### Fixed
* malloc now fails if we run out of memory (before it would always succeed even if we are out of ram...)

## [0.3.5] - 2018-03-04
### Added
* Reporting error if your encoder CPR is incorrect
* Ability to start anticogging calibration over USB protocol
* Reporting of DRV status/control registers and fault codes
* DRV status read script
* Microsecond delay function
* Travis-CI
* Firmware update over USB

### Changed
* Build system is now tup instead of make. Please check the [Readme](README.md#installing-prerequisites) for installation instructions.

## [0.3.4] - 2018-02-13
### Fixed
* Broken way to check for python 2. Python 2 not supported yet.

## [0.3.3] - 2018-02-12
### Added
* Liveplotter script
* Automatic recovery of USB halt/stall condition

### Changed
* Modified python code to be Python 2 compatible

### Fixed
* USB CSC (USB serial) now reports a sensible baud rate

## [0.3.2] - 2018-02-02
### Added
* Gimbal motor mode
* Encoder index pulse support
* `resistance_calib_max_voltage` parameter

## [0.3.1] - 2018-01-18
### Added
* UUID Endpoint
* Reporting of correct ODrive version on USB descriptor
* Getting started instructions for VSCode

### Changed
* USB Product ID to 0x0D32, as it is the only Pid we were allocated on [pid.codes](http://pid.codes/1209/0D32/)
* Recommended method to debug firmware from VSCode now uses Cortex-Debug extension instead of native-debug.
* Refactor IDE instructions into separate files

### Fixed
* Bug where the remote function calls from Python to the ODrive were not working properly.

## [0.3] - 2017-12-18
### Added
* **New binary communication protocol**
  * This is a much richer and more efficient binary protocol than the old human-readable protocol.
  * The old protocol is still available (but will be depricated eventually). You must manually chose to fall back on this protocol if you wish to still use it.
* Support for C++
* Demo scripts for getting started with commanding ODrive from python
* Protection from user setting current_lim higher than is measurable
* Current sense shunt values for HW v3.4
* Check DRV chip fault line

### Changed
* Shunt resistance values for v3.3 and earlier to include extra resistance of PCB
* Default HW revision to v3.4
* Refactoring of control code:
  * Lifted top layer of low_level.c into Axis.cpp

## [0.2.2] - 2017-11-17
### Fixed
* Incorrect TIM14 interrupt mapping on board v3.2 caused hard-fault

### Changed
* GPIO communication mode now defaults to NONE

## [0.2.1] - 2017-11-14
### Fixed
* USB communication deadlock
* EXTI handler redefiniton in V3.2

### Changed
* Resistance/inductance measurement now saved dispite errors, to allow debugging

## [0.2.0] - 2017-11-12
### Added
* UART communication
* Setting to select UART or Step/dir on GIPIO 1,2
* Basic Anti-cogging

## [0.1.0] - 2017-08-26
### Added
* Step/Dir interface
* this Changelog
* motor control interrupt timing diagram
* uint16 exposed variable type
* null termination to USB string parsing

### Changed
* Fixed Resistance measurement bug
* Simplified motor control adc triggers
* Increased AUX bridge deadtime
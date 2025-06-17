-- Week 1: Overheating
INSERT INTO obd_injected_faults (user_id, timestamp, COOLANT_TEMPERATURE, ENGINE_RPM, injected_fault_type, is_synthetic)
SELECT
    generateUUIDv4(),
    toDateTime('2024-03-31 20:00:00') + INTERVAL intDiv(number, 24) DAY + INTERVAL (number % 24) HOUR,
    130,  -- high temp
    2500 + rand() % 500,
    'Overheating',
    1
FROM numbers(100);

-- Week 1: Vacuum Leak
INSERT INTO obd_injected_faults (user_id, timestamp, INTAKE_MANIFOLD_PRESSURE, LONG_TERM_FUEL_TRIM_BANK_1, injected_fault_type, is_synthetic)
SELECT
    generateUUIDv4(),
    toDateTime('2024-03-31 20:00:00') + INTERVAL intDiv(number, 24) DAY + INTERVAL (number % 24) HOUR,
    60,    -- high pressure
    25,    -- high fuel trim
    'Vacuum Leak',
    1
FROM numbers(100);

-- Week 3: Throttle Lag
INSERT INTO obd_injected_faults (user_id, timestamp, PEDAL_D, THROTTLE, injected_fault_type, is_synthetic)
SELECT
    generateUUIDv4(),
    toDateTime('2024-04-14 20:00:00') + INTERVAL intDiv(number, 24) DAY + INTERVAL (number % 24) HOUR,
    70,   -- pedal pressed
    10,   -- throttle not responding
    'Throttle Lag',
    1
FROM numbers(100);

-- Week 3: Low Voltage
INSERT INTO obd_injected_faults (user_id, timestamp, CONTROL_MODULE_VOLTAGE, injected_fault_type, is_synthetic)
SELECT
    generateUUIDv4(),
    toDateTime('2024-04-14 20:00:00') + INTERVAL intDiv(number, 24) DAY + INTERVAL (number % 24) HOUR,
    10.5,  -- low voltage
    'Low Voltage',
    1
FROM numbers(100);

-- Week 3: Misfire Simulation (RPM noise)
INSERT INTO obd_injected_faults (user_id, timestamp, ENGINE_RPM, injected_fault_type, is_synthetic)
SELECT
    generateUUIDv4(),
    toDateTime('2024-04-14 20:00:00') + INTERVAL intDiv(number, 24) DAY + INTERVAL (number % 24) HOUR,
    800 + intDiv(number, 10) * 200 + if(mod(number, 2) = 0, -300, 300),
    'Misfire',
    1
FROM numbers(100);

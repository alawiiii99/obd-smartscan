CREATE TABLE IF NOT EXISTS obd_anomalies (
    user_id UUID,
    timestamp DateTime,
    anomaly_score Float32,
    is_anomaly UInt8,
    pc1 Float32,
    pc2 Float32,
    fault_type LowCardinality(String) DEFAULT ''
) ENGINE = MergeTree
ORDER BY (user_id, timestamp);
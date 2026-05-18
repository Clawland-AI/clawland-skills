package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestAuditChainVerifyPassesForGeneratedLog(t *testing.T) {
	readings := []Reading{
		{
			Timestamp:       "2026-05-18T00:00:00Z",
			AssetID:         "truck-07",
			SensorID:        "logger-a",
			Location:        "depot",
			TemperatureC:    4.1,
			HumidityPercent: 62,
			PowerOK:         true,
		},
		{
			Timestamp:       "2026-05-18T01:00:00Z",
			AssetID:         "truck-07",
			SensorID:        "logger-a",
			Location:        "route-a12",
			TemperatureC:    9.2,
			HumidityPercent: 68,
			DoorOpen:        true,
			PowerOK:         true,
		},
	}

	auditPath := filepath.Join(t.TempDir(), "audit_log.jsonl")
	finalHash, err := writeAuditLog(auditPath, evaluate(readings, 2, 8, 85))
	if err != nil {
		t.Fatalf("write audit log: %v", err)
	}

	verifiedHash, err := verifyAuditLog(auditPath)
	if err != nil {
		t.Fatalf("verify generated audit log: %v", err)
	}
	if verifiedHash != finalHash {
		t.Fatalf("verified hash mismatch: got %s want %s", verifiedHash, finalHash)
	}
}

func TestAuditChainVerifyRejectsTamperedEvent(t *testing.T) {
	readings := []Reading{
		{
			Timestamp:       "2026-05-18T00:00:00Z",
			AssetID:         "truck-07",
			SensorID:        "logger-a",
			Location:        "depot",
			TemperatureC:    4.1,
			HumidityPercent: 62,
			PowerOK:         true,
		},
	}

	auditPath := filepath.Join(t.TempDir(), "audit_log.jsonl")
	if _, err := writeAuditLog(auditPath, evaluate(readings, 2, 8, 85)); err != nil {
		t.Fatalf("write audit log: %v", err)
	}

	content, err := os.ReadFile(auditPath)
	if err != nil {
		t.Fatalf("read audit log: %v", err)
	}
	tampered := strings.Replace(string(content), `"temperature_c":4.1`, `"temperature_c":9.1`, 1)
	if err := os.WriteFile(auditPath, []byte(tampered), 0644); err != nil {
		t.Fatalf("write tampered audit log: %v", err)
	}

	_, err = verifyAuditLog(auditPath)
	if err == nil {
		t.Fatal("expected tampered audit log to fail verification")
	}
	if !strings.Contains(err.Error(), "event_hash mismatch") {
		t.Fatalf("unexpected verification error: %v", err)
	}
}

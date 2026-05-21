package main

import (
	"bufio"
	"crypto/sha256"
	"encoding/csv"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

type Reading struct {
	Timestamp       string  `json:"timestamp"`
	AssetID         string  `json:"asset_id"`
	SensorID        string  `json:"sensor_id"`
	Location        string  `json:"location"`
	TemperatureC    float64 `json:"temperature_c"`
	HumidityPercent float64 `json:"humidity_percent"`
	DoorOpen        bool    `json:"door_open"`
	PowerOK         bool    `json:"power_ok"`
	GPS             string  `json:"gps,omitempty"`
	Notes           string  `json:"notes,omitempty"`
}

type EvaluatedReading struct {
	Reading
	Status     string   `json:"status"`
	Violations []string `json:"violations"`
}

type Summary struct {
	Total          int
	AssetID        string
	WindowStart    string
	WindowEnd      string
	MinTemp        float64
	MaxTemp        float64
	AvgTemp        float64
	MaxHumidity    float64
	Excursions     int
	DoorOpenEvents int
	PowerFailures  int
	FinalHash      string
}

type AuditRecord struct {
	Sequence     int              `json:"sequence"`
	PreviousHash string           `json:"previous_hash"`
	EventHash    string           `json:"event_hash"`
	Hash         string           `json:"hash"`
	Event        EvaluatedReading `json:"event"`
}

func main() {
	input := flag.String("input", "", "Path to JSONL readings")
	outDir := flag.String("out", "cold-chain-report", "Output directory")
	minTemp := flag.Float64("min-temp", 2.0, "Minimum allowed temperature in Celsius")
	maxTemp := flag.Float64("max-temp", 8.0, "Maximum allowed temperature in Celsius")
	maxHumidity := flag.Float64("max-humidity", 85.0, "Maximum allowed relative humidity")
	verifyAudit := flag.String("verify-audit", "", "Path to audit_log.jsonl to verify instead of generating a report")
	flag.Parse()

	if *verifyAudit != "" {
		finalHash, err := verifyAuditLog(*verifyAudit)
		if err != nil {
			exitf("verify audit chain: %v", err)
		}
		fmt.Printf("audit chain verified\n")
		fmt.Printf("final audit hash: %s\n", finalHash)
		return
	}

	if *input == "" {
		exitf("missing --input")
	}

	readings, err := loadReadings(*input)
	if err != nil {
		exitf("load readings: %v", err)
	}
	if len(readings) == 0 {
		exitf("no readings found")
	}

	evaluated := evaluate(readings, *minTemp, *maxTemp, *maxHumidity)

	if err := os.MkdirAll(*outDir, 0755); err != nil {
		exitf("create output dir: %v", err)
	}

	if err := writeCSV(filepath.Join(*outDir, "cold_chain_events.csv"), evaluated); err != nil {
		exitf("write csv: %v", err)
	}

	finalHash, err := writeAuditLog(filepath.Join(*outDir, "audit_log.jsonl"), evaluated)
	if err != nil {
		exitf("write audit log: %v", err)
	}

	summary := summarize(evaluated, finalHash)

	if err := writeMarkdown(filepath.Join(*outDir, "compliance_report.md"), summary, evaluated); err != nil {
		exitf("write markdown: %v", err)
	}

	if err := writePDF(filepath.Join(*outDir, "compliance_report.pdf"), summary, evaluated); err != nil {
		exitf("write pdf: %v", err)
	}

	fmt.Printf("cold-chain compliance package written to %s\n", *outDir)
	fmt.Printf("final audit hash: %s\n", finalHash)
}

func loadReadings(path string) ([]Reading, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var readings []Reading
	scanner := bufio.NewScanner(file)
	lineNumber := 0
	for scanner.Scan() {
		lineNumber++
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		var reading Reading
		if err := json.Unmarshal([]byte(line), &reading); err != nil {
			return nil, fmt.Errorf("line %d: %w", lineNumber, err)
		}
		if reading.Timestamp == "" || reading.AssetID == "" {
			return nil, fmt.Errorf("line %d: timestamp and asset_id are required", lineNumber)
		}
		readings = append(readings, reading)
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return readings, nil
}

func evaluate(readings []Reading, minTemp float64, maxTemp float64, maxHumidity float64) []EvaluatedReading {
	evaluated := make([]EvaluatedReading, 0, len(readings))
	for _, reading := range readings {
		var violations []string
		if reading.TemperatureC < minTemp {
			violations = append(violations, fmt.Sprintf("temperature below %.1f C", minTemp))
		}
		if reading.TemperatureC > maxTemp {
			violations = append(violations, fmt.Sprintf("temperature above %.1f C", maxTemp))
		}
		if reading.HumidityPercent > maxHumidity {
			violations = append(violations, fmt.Sprintf("humidity above %.1f%%", maxHumidity))
		}
		if reading.DoorOpen {
			violations = append(violations, "door open")
		}
		if !reading.PowerOK {
			violations = append(violations, "refrigeration power failure")
		}

		status := "compliant"
		if len(violations) > 0 {
			status = "excursion"
		}

		evaluated = append(evaluated, EvaluatedReading{
			Reading:    reading,
			Status:     status,
			Violations: violations,
		})
	}
	return evaluated
}

func writeCSV(path string, readings []EvaluatedReading) error {
	file, err := os.Create(path)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	header := []string{
		"timestamp",
		"asset_id",
		"sensor_id",
		"location",
		"temperature_c",
		"humidity_percent",
		"door_open",
		"power_ok",
		"gps",
		"status",
		"violations",
		"notes",
	}
	if err := writer.Write(header); err != nil {
		return err
	}

	for _, reading := range readings {
		row := []string{
			reading.Timestamp,
			reading.AssetID,
			reading.SensorID,
			reading.Location,
			strconv.FormatFloat(reading.TemperatureC, 'f', 2, 64),
			strconv.FormatFloat(reading.HumidityPercent, 'f', 2, 64),
			strconv.FormatBool(reading.DoorOpen),
			strconv.FormatBool(reading.PowerOK),
			reading.GPS,
			reading.Status,
			strings.Join(reading.Violations, "; "),
			reading.Notes,
		}
		if err := writer.Write(row); err != nil {
			return err
		}
	}
	return writer.Error()
}

func writeAuditLog(path string, readings []EvaluatedReading) (string, error) {
	file, err := os.Create(path)
	if err != nil {
		return "", err
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	previousHash := strings.Repeat("0", 64)
	for i, reading := range readings {
		eventJSON, err := json.Marshal(reading)
		if err != nil {
			return "", err
		}
		eventHash := sha256Hex(eventJSON)
		chainInput := []byte(previousHash + eventHash)
		recordHash := sha256Hex(chainInput)
		record := AuditRecord{
			Sequence:     i + 1,
			PreviousHash: previousHash,
			EventHash:    eventHash,
			Hash:         recordHash,
			Event:        reading,
		}
		if err := encoder.Encode(record); err != nil {
			return "", err
		}
		previousHash = recordHash
	}
	return previousHash, nil
}

func verifyAuditLog(path string) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	previousHash := strings.Repeat("0", 64)
	expectedSequence := 1
	for {
		var record AuditRecord
		if err := decoder.Decode(&record); err != nil {
			if err == io.EOF {
				break
			}
			return "", err
		}
		if record.Sequence != expectedSequence {
			return "", fmt.Errorf("sequence %d: expected sequence %d", record.Sequence, expectedSequence)
		}
		if record.PreviousHash != previousHash {
			return "", fmt.Errorf("sequence %d: previous_hash mismatch", record.Sequence)
		}

		eventJSON, err := json.Marshal(record.Event)
		if err != nil {
			return "", err
		}
		eventHash := sha256Hex(eventJSON)
		if record.EventHash != eventHash {
			return "", fmt.Errorf("sequence %d: event_hash mismatch", record.Sequence)
		}

		recordHash := sha256Hex([]byte(record.PreviousHash + record.EventHash))
		if record.Hash != recordHash {
			return "", fmt.Errorf("sequence %d: hash mismatch", record.Sequence)
		}

		previousHash = record.Hash
		expectedSequence++
	}
	if expectedSequence == 1 {
		return "", fmt.Errorf("audit log is empty")
	}
	return previousHash, nil
}

func sha256Hex(data []byte) string {
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:])
}

func summarize(readings []EvaluatedReading, finalHash string) Summary {
	summary := Summary{
		Total:       len(readings),
		AssetID:     readings[0].AssetID,
		WindowStart: readings[0].Timestamp,
		WindowEnd:   readings[len(readings)-1].Timestamp,
		MinTemp:     readings[0].TemperatureC,
		MaxTemp:     readings[0].TemperatureC,
		MaxHumidity: readings[0].HumidityPercent,
		FinalHash:   finalHash,
	}

	var tempSum float64
	for _, reading := range readings {
		if before(reading.Timestamp, summary.WindowStart) {
			summary.WindowStart = reading.Timestamp
		}
		if before(summary.WindowEnd, reading.Timestamp) {
			summary.WindowEnd = reading.Timestamp
		}
		if reading.TemperatureC < summary.MinTemp {
			summary.MinTemp = reading.TemperatureC
		}
		if reading.TemperatureC > summary.MaxTemp {
			summary.MaxTemp = reading.TemperatureC
		}
		if reading.HumidityPercent > summary.MaxHumidity {
			summary.MaxHumidity = reading.HumidityPercent
		}
		if reading.Status == "excursion" {
			summary.Excursions++
		}
		if reading.DoorOpen {
			summary.DoorOpenEvents++
		}
		if !reading.PowerOK {
			summary.PowerFailures++
		}
		tempSum += reading.TemperatureC
	}
	summary.AvgTemp = tempSum / float64(len(readings))
	return summary
}

func before(left string, right string) bool {
	leftTime, leftErr := time.Parse(time.RFC3339, left)
	rightTime, rightErr := time.Parse(time.RFC3339, right)
	if leftErr == nil && rightErr == nil {
		return leftTime.Before(rightTime)
	}
	return left < right
}

func writeMarkdown(path string, summary Summary, readings []EvaluatedReading) error {
	var builder strings.Builder
	builder.WriteString("# Cold Chain GSP/HACCP Compliance Report\n\n")
	builder.WriteString("## Executive Summary\n\n")
	builder.WriteString(fmt.Sprintf("- Asset ID: %s\n", summary.AssetID))
	builder.WriteString(fmt.Sprintf("- Reporting window: %s to %s\n", summary.WindowStart, summary.WindowEnd))
	builder.WriteString(fmt.Sprintf("- Total readings: %d\n", summary.Total))
	builder.WriteString(fmt.Sprintf("- Temperature min/avg/max: %.2f / %.2f / %.2f C\n", summary.MinTemp, summary.AvgTemp, summary.MaxTemp))
	builder.WriteString(fmt.Sprintf("- Max humidity: %.2f%%\n", summary.MaxHumidity))
	builder.WriteString(fmt.Sprintf("- Excursions: %d\n", summary.Excursions))
	builder.WriteString(fmt.Sprintf("- Door-open events: %d\n", summary.DoorOpenEvents))
	builder.WriteString(fmt.Sprintf("- Power failures: %d\n", summary.PowerFailures))
	builder.WriteString(fmt.Sprintf("- Final audit hash: `%s`\n\n", summary.FinalHash))

	builder.WriteString("## Excursions And Corrective Actions\n\n")
	builder.WriteString("| Time | Location | Reading | Violations | Corrective action |\n")
	builder.WriteString("|------|----------|---------|------------|-------------------|\n")
	for _, reading := range readings {
		if reading.Status != "excursion" {
			continue
		}
		builder.WriteString(fmt.Sprintf(
			"| %s | %s | %.2f C, %.2f%% RH | %s | Review and document product disposition |\n",
			reading.Timestamp,
			reading.Location,
			reading.TemperatureC,
			reading.HumidityPercent,
			strings.Join(reading.Violations, "; "),
		))
	}
	if summary.Excursions == 0 {
		builder.WriteString("| none | none | none | none | none |\n")
	}

	builder.WriteString("\n## Operator Sign-Off\n\n")
	builder.WriteString("- Name:\n- Signature:\n- Date:\n")

	return os.WriteFile(path, []byte(builder.String()), 0644)
}

func writePDF(path string, summary Summary, readings []EvaluatedReading) error {
	lines := []string{
		"Cold Chain GSP/HACCP Compliance Report",
		fmt.Sprintf("Asset ID: %s", summary.AssetID),
		fmt.Sprintf("Window: %s to %s", summary.WindowStart, summary.WindowEnd),
		fmt.Sprintf("Readings: %d", summary.Total),
		fmt.Sprintf("Temperature min/avg/max: %.2f / %.2f / %.2f C", summary.MinTemp, summary.AvgTemp, summary.MaxTemp),
		fmt.Sprintf("Max humidity: %.2f%%", summary.MaxHumidity),
		fmt.Sprintf("Excursions: %d", summary.Excursions),
		fmt.Sprintf("Door-open events: %d", summary.DoorOpenEvents),
		fmt.Sprintf("Power failures: %d", summary.PowerFailures),
		fmt.Sprintf("Final audit hash: %s", summary.FinalHash),
		"",
		"Excursion details:",
	}

	for _, reading := range readings {
		if reading.Status == "excursion" {
			lines = append(lines, fmt.Sprintf(
				"%s %s %.2f C %.2f%% RH - %s",
				reading.Timestamp,
				reading.Location,
				reading.TemperatureC,
				reading.HumidityPercent,
				strings.Join(reading.Violations, "; "),
			))
		}
	}
	if summary.Excursions == 0 {
		lines = append(lines, "No excursions recorded.")
	}
	lines = append(lines, "", "Operator sign-off: __________________________ Date: __________")

	content := pdfTextStream(lines)
	objects := []string{
		"<< /Type /Catalog /Pages 2 0 R >>",
		"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
		"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
		"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
		fmt.Sprintf("<< /Length %d >>\nstream\n%s\nendstream", len(content), content),
	}

	var builder strings.Builder
	builder.WriteString("%PDF-1.4\n")
	offsets := make([]int, 0, len(objects))
	for index, object := range objects {
		offsets = append(offsets, builder.Len())
		builder.WriteString(fmt.Sprintf("%d 0 obj\n%s\nendobj\n", index+1, object))
	}
	xrefOffset := builder.Len()
	builder.WriteString(fmt.Sprintf("xref\n0 %d\n", len(objects)+1))
	builder.WriteString("0000000000 65535 f \n")
	for _, offset := range offsets {
		builder.WriteString(fmt.Sprintf("%010d 00000 n \n", offset))
	}
	builder.WriteString(fmt.Sprintf("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n", len(objects)+1, xrefOffset))

	return os.WriteFile(path, []byte(builder.String()), 0644)
}

func pdfTextStream(lines []string) string {
	var builder strings.Builder
	builder.WriteString("BT\n/F1 10 Tf\n50 760 Td\n")
	for i, line := range lines {
		if i > 0 {
			builder.WriteString("0 -14 Td\n")
		}
		if i >= 48 {
			builder.WriteString("(More rows available in CSV and audit log.) Tj\n")
			break
		}
		builder.WriteString("(")
		builder.WriteString(escapePDF(line))
		builder.WriteString(") Tj\n")
	}
	builder.WriteString("ET")
	return builder.String()
}

func escapePDF(value string) string {
	value = strings.ReplaceAll(value, "\\", "\\\\")
	value = strings.ReplaceAll(value, "(", "\\(")
	value = strings.ReplaceAll(value, ")", "\\)")
	return value
}

func exitf(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(1)
}

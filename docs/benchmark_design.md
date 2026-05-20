# Benchmark Design

## Scope

LabInstrumentVQA should cover common electronic lab instruments:

- oscilloscopes,
- spectrum analyzers,
- vector network analyzers,
- logic analyzers,
- power supplies,
- multimeters.

Data can include direct screenshots, camera photos, synthetic renderings, and metadata-assisted variants.

## Task Taxonomy

| Task Type | Example |
| --- | --- |
| OCR and layout extraction | Extract visible settings: timebase, volts/div, span, RBW, marker readouts. |
| Trace grounding | Locate peaks, cursors, markers, trigger level, and graticule crossings. |
| Numeric extraction | Read frequency, power, voltage, period, phase, S11 minimum, bandwidth, or noise floor. |
| State recognition | Identify trigger status, overload, averaging, enabled channels, coupling, probe attenuation, calibration state. |
| Diagnosis | Detect clipping, aliasing, no signal, unstable trigger, saturated front end, poor calibration, or bad impedance match. |
| Action recommendation | Suggest concrete instrument adjustments based on the display. |
| Robustness | Test blur, glare, skew, compression, low resolution, and multiple vendors. |
| Metadata variants | Compare image-only performance with image plus SCPI, CSV, raw waveform, or IQ metadata. |

## Sample Fields

Current minimal VQA JSONL records use:

```json
{"id":"scope_001","image":"images/scope_001.svg","instrument":"oscilloscope","question":"What is the peak-to-peak voltage of channel 1?","answer":"2.0 Vpp"}
```

Required:

- `id`: stable sample identifier.
- `image`: image path relative to the JSONL file.
- `question`: VQA prompt.

Optional:

- `answer`: ground-truth answer.
- `instrument`: instrument type.
- `metadata`: structured metadata such as vendor, model, SCPI settings, trace files, task category, difficulty, or bounding boxes.

## Expected Failure Modes

- Confusing UI labels with measurement values.
- Reading small text incorrectly or ignoring it entirely.
- Estimating values without respecting volts/div, seconds/div, dBm/div, or span.
- Missing colored trace-to-channel associations.
- Hallucinating settings that are not visible.
- Failing on low-SNR traces, weak peaks, dense marker tables, or multi-panel layouts.
- Describing visible patterns without making the correct engineering diagnosis.
- Giving generic advice instead of instrument-specific next actions.

## Split Strategy

Useful evaluation splits:

- vendor-held-out,
- instrument-type-held-out,
- real-photo robustness,
- metadata-assisted,
- diagnosis-heavy expert split.

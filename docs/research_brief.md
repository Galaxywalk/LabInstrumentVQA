# Research Brief

## Goal

Build a benchmark and dataset for multimodal understanding of common electronic lab instruments, especially oscilloscope, spectrum analyzer, vector network analyzer, logic analyzer, power supply, and multimeter displays.

The central question:

> Can current multimodal LLMs reliably parse specialized lab-instrument user interfaces and reason from their visual measurements?

## Motivation

Recent multimodal benchmarks cover charts, GUI grounding, RF spectrograms, scientific plots, and electronics diagrams. They do not directly cover real lab-instrument screenshots or camera photos with vendor-specific settings, dense readouts, traces, markers, and measurement state.

This leaves room for a benchmark such as `LabInstrumentVQA` or `InstrumentUI-Bench`.

## Closest Related Work

| Work | Relevance | Main Gap |
| --- | --- | --- |
| RF-Analyzer | Spectrum-analyzer-like RF waterfall and spectrum images. | General VLMs hallucinate, miss weak or low-SNR signals, and struggle with precise protocol identification. |
| RF-GPT | RF-domain multimodal instruction tuning using spectrogram-like visual representations. | General VLMs lack RF grounding; synthetic training still leaves gaps for real over-the-air data and fine protocol details. |
| Seeing Radio | RF VQA over IQ traces, spectrograms, and time-frequency panels. | Base VLMs perform poorly without RF-specific fine-tuning; few-shot prompting is insufficient. |
| QCalEval | Scientific calibration plots, oscillations, 2D maps, histograms, fit reliability, and diagnosis. | Models can detect visual patterns but often fail to map them to domain conclusions. |
| ScreenSpot-Pro | Professional dense GUI grounding. | Strong GUI models still perform poorly on high-resolution, dense, specialized desktop interfaces. |
| ScreenParse | Dense screen parsing with UI element boxes, labels, OCR, and UI classes. | Generic UI supervision does not guarantee transfer to specialized out-of-domain instrument screens. |
| CRBench / ChartReasoner | Chart reasoning and value estimation. | MLLMs hallucinate and degrade when values must be visually estimated instead of read directly. |
| InterChart | Multi-panel chart understanding. | Models struggle with distributed information, irregular axes, range estimation, and domain-specific trends. |

Related but outside the strict 2025-2026 arXiv window:

- `EEE-Bench`: electronics/electrical-engineering benchmark with circuits, waveforms, plots, and technical visual reasoning. Reported performance is low, roughly 19.48-46.78%, with models often missing visual context.
- `ElectroVizQA`: electronics VQA over digital electronics diagrams. It shows strong MLLMs still make visual-perception and conceptual errors in engineering-specific visuals.

## Research Gap

Existing work does not directly test whether VLMs can understand the full visual and semantic structure of lab instruments. The missing capability combines:

1. Instrument-specific semantics: RBW, VBW, span, reference level, IFBW, S11, S21, trigger mode, coupling, probe attenuation, delta markers, Smith-chart markers, channel scale, persistence, averaging, and overload indicators.
2. Coordinate-to-measurement grounding: volts/div, seconds/div, dBm/div, frequency span, phase, impedance, bandwidth, rise time, peak power, noise floor, and marker deltas.
3. Dense professional UI parsing: tiny text, soft-key menus, status bars, colored traces, graticules, markers, nested panels, vendor-specific layouts, blur, glare, skew, and low resolution.
4. Domain diagnosis: clipping, aliasing, trigger instability, under-sampling, wrong RBW/span, saturated front end, insufficient averaging, poor impedance match, bad calibration, or failed measurement setup.
5. Actionable recommendations: lower reference level, increase span, reduce RBW, adjust trigger level, change coupling, recalibrate a VNA, or check probe attenuation.

## Paper Direction

The paper should position lab-instrument UI understanding as a distinct multimodal reasoning problem at the intersection of professional GUI grounding, chart reasoning, dense OCR, electrical/RF engineering semantics, calibrated visual measurement extraction, and experiment-diagnosis reasoning.

Central claim:

> Current multimodal LLMs are not reliably grounded in specialized electronic lab-instrument interfaces, and a dedicated benchmark is needed to measure and improve this capability.

# Multimodal Submission Integrity & Plagiarism Detection Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FAISS](https://img.shields.io/badge/vector--search-FAISS-green.svg)](https://github.com/facebookresearch/faiss)
[![SentenceTransformers](https://img.shields.io/badge/embeddings-all--MiniLM--L6--v2-orange.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Whisper ASR](https://img.shields.io/badge/ASR-Whisper--Tiny%2FBase-red.svg)](https://huggingface.co/openai/whisper-tiny)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An end-to-end prototype multimodal content verification and similarity detection pipeline designed to scale to large-scale university evaluations, hackathons, and case competitions (10,000+ submissions).

The engine analyzes submissions across multiple modalities—**PDF reports, DOCX executive summaries, and MP4 video pitches**—calculating a tri-factor integrity breakdown:
1. **Internal Peer-to-Peer Similarity %** (Unimodal text-to-text, cross-format PDF $\leftrightarrow$ DOCX, and cross-modal audio-to-text).
2. **External / Web Reference Match %** (Local reference knowledge base with source URLs and citation tracking).
3. **AI-Generated Content Likelihood %** (Supervised RoBERTa classifier + GPT-2 perplexity + sentence burstiness).

---

## Architecture Overview

```
                                  +------------------------------------+
                                  |   Candidate Multi-Modal Submissions|
                                  |      (.pdf, .docx, .mp4 files)     |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |    Multimodal Ingestion Layer      |
                                  |  - pypdf (Page-level text)         |
                                  |  - python-docx (Paragraph blocks)  |
                                  |  - Whisper ASR (Time-aligned audio)|
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | Text Normalization & Provenance    |
                                  |  - Header/footer artifact removal  |
                                  |  - Paragraph-aware token chunking  |
                                  |  - Page & Timestamp preservation   |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |  Corpus-Wide Boilerplate Filter    |
                                  |  - Document-frequency clustering   |
                                  |  - Isolates shared case prompts    |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | Dense Vector Indexing (FAISS)      |
                                  |  - all-MiniLM-L6-v2 embeddings     |
                                  |  - Strict self-doc_id exclusion    |
                                  +-----------------+------------------+
                                                    |
                    +-------------------------------+-------------------------------+
                    |                               |                               |
                    v                               v                               v
    +-------------------------------+   +-----------------------+   +-------------------------------+
    | Peer & Cross-Modal Detection  |   | External KB Matching  |   | Multi-Signal AI Estimator     |
    | - Sentence-level alignment    |   | - Public domain texts |   | - RoBERTa supervised detector |
    | - Cosine vs. Jaccard contrast |   | - Wikipedia source URL|   | - GPT-2 token perplexity      |
    | - Video timestamp citations   |   |   attribution         |   | - Sentence burstiness variance|
    +---------------+---------------+   +-----------+-----------+   +---------------+---------------+
                    |                               |                               |
                    +-------------------------------+-------------------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | Multi-Signal Risk Engine & Reports |
                                  |  - Configurable YAML risk logic    |
                                  |  - Structured .json (Audit Schema) |
                                  |  - Human-readable .md (<30s review)|
                                  |  - Pairwise similarity matrix      |
                                  +------------------------------------+
```

---

## Key Capabilities & Scenarios Handled

| Scenario | Challenge | Pipeline Solution | Outcome in Benchmark |
| :--- | :--- | :--- | :--- |
| **Scenario 1: Cross-Modal Duplication** | Candidate reads an exact paragraph from another student's PDF in their MP4 pitch. | Extracts audio via FFmpeg, generates time-aligned transcript via Whisper, indexes chunks, and matches PDF vector space. | Flags exact match with **video timestamp (`00:00:00 - 00:00:27`) and PDF page reference (Page 2)** with 1.00 cosine similarity. |
| **Scenario 2: Paraphrased Content** | Student rewrites content using synonyms to evade naive keyword matching. | Evaluates dense semantic embeddings alongside lexical string metrics (Jaccard, Levenshtein). | Flags **semantic similarity > 0.85** while **lexical Jaccard is low (<0.35)**, explicitly proving semantic evasion. |
| **Scenario 3: Corrupted / Empty Submissions** | Corrupted DOCX, zero-byte PDF, or silent MP4 video submitted. | Non-crashing exception handling, audio stream probing, volume detection, and corrupted file isolation. | Logs warning, flags file as **`⚠️ FLAGGED` (`SKIPPED_EMPTY`, `SKIPPED_SILENT`, `SKIPPED_CORRUPT`)**, and processes all remaining files. |
| **Scenario 4: Benign Common Formatting** | 5 documents share an identical 150-word problem prompt with original analytical answers. | Corpus-level document-frequency filter detects repeated chunks in $\ge 3$ documents and discounts them from plagiarism scoring. | **Zero false-positive alarms**; all 5 documents receive **`🟢 LOW RISK (0.0% Peer Similarity)`**. |
| **Scenario 5: Multi-Document Mixed Batch** | Mixed batch containing genuine, copied, external, and AI-generated text. | End-to-end evaluation with full pairwise matrix generation and structured individual reports. | Processes entire directory, outputs **`summary_matrix.csv`** and **`batch_summary_report.md`**. |

---

## Quickstart & Reproducibility Guide

### 1. Prerequisites
- **Python**: Python 3.9+ compatible (tested and verified under Python 3.10.8 via syntax/AST inspection avoiding PEP 604 union types and 3.10 pattern matching).
- **FFmpeg**: Automatically managed via bundled `imageio-ffmpeg` binary (or system FFmpeg if present).
- **Linux System Dependencies**: On Debian/Ubuntu environments, audio synthesis via `pyttsx3` requires `espeak` and `libespeak1` (`sudo apt-get install -y ffmpeg espeak libespeak1`).
- **Acoustic Testing Boundary**: Synthetic test videos (`submission_02`, `submission_19`) use clean TTS audio; real-world noisy, low-bitrate, or accented human speech was not evaluated in this benchmark.
- **Environment Note**: All benchmarks, unit tests, and pipeline executions were measured on **Windows 11 (13th Gen Intel(R) Core(TM) i5-13450HX, 10 physical cores / 16 logical processors, 15.69 GB RAM)**. Linux GitHub Actions CI (`.github/workflows/ci.yml`) validates the pipeline, unit tests, and evaluation on `ubuntu-latest`.

### 2. Cross-Platform Setup & Execution

#### Linux / macOS
```bash
# Clone the repository
git clone https://github.com/rishika-deshmukh/unstop-multimodal-integrity-engine.git
cd unstop-multimodal-integrity-engine

# Option A: One-command setup via script (creates venv, installs requirements, downloads NLTK data)
chmod +x setup.sh && ./setup.sh

# Option B: One-command setup via Makefile
make setup

# Run the complete pipeline
make run
# Or directly: ./venv/bin/python run_integrity_check.py --input_dir ./sample_submissions --output_dir ./reports

# Run empirical evaluation benchmark
make evaluate

# Run unit tests
make test
```

#### Windows (PowerShell or Command Prompt)
```powershell
# Clone the repository
git clone https://github.com/rishika-deshmukh/unstop-multimodal-integrity-engine.git
cd unstop-multimodal-integrity-engine

# Initialize virtual environment and install dependencies
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# Pre-cache open models (optional, offline ready)
.\venv\Scripts\python.exe scripts\download_models.py

# Run integrity check pipeline
.\venv\Scripts\python.exe run_integrity_check.py --input_dir ./sample_submissions --output_dir ./reports

# Run evaluation benchmark against ground truth
.\venv\Scripts\python.exe evaluate.py

# Run unit tests
.\venv\Scripts\python.exe -m pytest tests/ -v
```

*Tip for Windows: You can also simply double-click or run `.\run.bat` to execute automated setup, pipeline run, and evaluation in one step.*

---

## Output Format & Sample Report Snippet

Each submission generates a machine-readable `.json` audit report adhering strictly to the assessment brief schema, and a human-readable `.md` report designed for rapid (<30s) review.

### Sample JSON Audit Report (`reports/submission_02_video_pitch.mp4.json`)
```json
{
  "document_id": "submission_02_video_pitch.mp4",
  "total_integrity_risk": "HIGH",
  "scores": {
    "peer_similarity_percentage": 100.0,
    "external_similarity_percentage": 0.0,
    "ai_generated_probability": 15.1
  },
  "peer_matches": [],
  "multimodal_matches": [
    {
      "matched_file": "submission_01_fintech_report.pdf",
      "similarity_score": 1.0,
      "lexical_jaccard": 1.0,
      "lexical_levenshtein": 1.0,
      "is_paraphrase": false,
      "attribution_note": "Mutual overlap detected; direction undetermined (reviewer manual verification required).",
      "query_passage": "The core competitive advantage relies on vertical integration of credit underwriting models with real-time transactional payment gateways.",
      "matched_passage": "The core competitive advantage relies on vertical integration of credit underwriting models with real-time transactional payment gateways.",
      "location": {
        "query_page": null,
        "matched_page": 2,
        "query_timestamp": "00:00:00 - 00:00:27",
        "matched_timestamp": null
      }
    }
  ],
  "external_matches": [],
  "explanations": "Critical internal peer similarity detected (100.0% meets or exceeds 50.0% threshold)."
}
```

### Multimodal Location Schema (Bidirectional Citations)

The pipeline preserves exact page numbers and time-aligned audio timestamps across both matching directions:
- **Video Query $\rightarrow$ Text Target (e.g., `submission_02` $\rightarrow$ `submission_01`)**:
  - `query_timestamp`: The exact timestamp range in the video where the words were spoken (e.g., `"00:00:00 - 00:00:27"`).
  - `matched_page`: The page number in the source document where the duplicated text originates (e.g., `2`).
  - `query_page`: `null` (since the query document is a video).
  - `matched_timestamp`: `null` (since the target document is a PDF).
- **Text Query $\rightarrow$ Video Target (e.g., `submission_01` $\rightarrow$ `submission_02`)**:
  - `query_page`: The page number in the query PDF (e.g., `2`).
  - `matched_timestamp`: The timestamp range in the video where the audio was transcribed (e.g., `"00:00:00 - 00:00:27"`).
  - `query_timestamp`: `null`.
  - `matched_page`: `null`.

This bidirectional schema guarantees that regardless of which document is viewed first by an evaluator, the exact cross-modal citation is immediately verifiable in under 30 seconds.

### Sample Paraphrase Report Snippet (`reports/submission_04_logistics_rewritten.docx.md`)
> ### Overlap #1 — Target: `submission_03_logistics_strategy.docx` ⚠️ **[SYNONYM-BASED PARAPHRASE DETECTED]**
> | Semantic Cosine Sim | Lexical Jaccard Sim | Levenshtein Sim | Page References |
> | :---: | :---: | :---: | :---: |
> | **0.87** | **0.18** | **0.49** | Query: Pg 1 ↔ Match: Pg 1 |
> 
> **Reviewer Note:** High dense embedding similarity (>0.80) with low lexical Jaccard (<0.35) confirms semantic rewriting evasion.
> - **Query Passage:** *"Active refrigerated enclosures deploying computerized cooling mechanisms ensure temperature consistency during international flight segments..."*
> - **Matched Source:** *"Active refrigeration containers utilizing automated compressor cycles guarantee temperature stability during transcontinental flights..."*

---

## Task 5: 10,000 Document Production Scaling Brief

Processing 10,000 multi-modal submissions (est. 6,000 PDFs, 3,500 DOCXs, 500 MP4 video pitches) within a competitive post-deadline evaluation window introduces distinct computational, indexing, and storage challenges. Below is the concrete engineering blueprint backed by empirical hardware measurements.

### 1. Empirical Hardware Measurements (Benchmarked on x86_64 CPU)

From `benchmarks/results.json` run on this machine (10 physical cores, 16 logical cores, 15.69 GB RAM, Python 3.10.8):
- **MiniLM-L6-v2 Embedding Throughput (CPU)**: **219.83 chunks/second** (4.549 ms/chunk) [Measured].
- **Whisper Speech-to-Text (CPU)**: **0.112 RTF** (**8.92x faster than real-time**; 26.53s audio transcribed in 2.974s) [Measured].
- **FAISS Flat vs. HNSW (200,000 Vectors, Dimension 384)**:
  - `IndexFlatIP`: RAM footprint: **293.0 MB**, Query latency: **13.852 ms/query** (72.2 QPS) [Measured].
  - `IndexHNSWFlat` ($M=32, efSearch=64$): RAM footprint: **350.04 MB**, Query latency: **0.915 ms/query** (1092.9 QPS) [Measured].
  - **HNSW Speedup**: **15.1x faster query latency** with only +57.04 MB RAM overhead [Measured]!
- **Environment Notice**: Tested on Python 3.10.8; compatibility with 3.9 checked by inspection only.

### 2. Workload Sizing & Quantitative Bounds for 10,000 Documents
- **Average Document Length**: Design assumption: ~16 chunks per document [Estimate] (for comprehensive 10-page reports; the sample benchmark corpus averages 2.6 chunks/doc for concise executive summaries and short transcripts).
- **Corpus Chunk Volume**: $10,000 \text{ submissions} \times 16 \text{ chunks/doc} \approx \mathbf{160,000\text{ dense vectors}}$ [Estimate].
- **Vector Index RAM**: $160,000 \text{ vectors} \times 384 \text{ floats} \times 4 \text{ bytes} \approx 245 \text{ MB}$ raw ($< 360 \text{ MB}$ with HNSW graph) [Calculated]. Fits effortlessly in RAM on a single standard cloud node.
- **Embedding Generation Time**:
  - $160,000 \text{ chunks} / 219.83 \text{ chunks/sec} \approx 728 \text{ seconds}$ (~12.1 minutes on 1 CPU node) [Calculated from measured baseline].
  - Distributed across **4 standard CPU nodes** (`c6i.2xlarge`, 8 vCPUs each, running 8 parallel Celery worker processes per node = 32 total worker processes): $\mathbf{\approx 3.0\text{ minutes}}$ [Estimate based on horizontal scaling].
  - On a GPU node (`g4dn.xlarge` with TensorRT / PyTorch batching, estimated ~1,500 chunks/sec based on published T4 benchmarks): $\approx 107 \text{ seconds}$ (~1.8 minutes) [Estimate].

### 3. Whisper ASR Bottleneck Resolution (Dedicated GPU Queue)
- **The Workload**: 500 video pitches $\times$ 30s audio = 15,000 seconds of audio [Estimate].
  - On CPU (measured 8.92x speedup, RTF 0.112): sequential execution = $15,000 \times 0.112 \approx 1,680 \text{ seconds}$ (~28.0 minutes) [Calculated from measured RTF].
  - Distributed across 8 parallel Celery CPU worker processes: $1,680 / 8 \approx \mathbf{3.5\text{ minutes}}$ [Estimate based on worker parallelism].
- **Production Solution (Dedicated GPU Queue)**:
  - Route video files to a dedicated Celery GPU queue (`celery -Q gpu_whisper_workers`).
  - Using 2x `g4dn.xlarge` instances with NVIDIA T4 GPUs running `faster-whisper` (CTranslate2 INT8, estimated ~20x faster than real-time based on published benchmarks):
    $15,000 / (2 \times 20) \approx \mathbf{375\text{ seconds}}$ (**~6.2 minutes**) [Estimate].

### 4. Vector Search Latency: Flat vs. HNSW
- To match 160,000 query chunks against the 160,000 corpus vectors:
  - With `IndexFlatIP`: $160,000 \times 13.852 \text{ ms} \approx 2,216 \text{ seconds}$ (~36.9 minutes) [Calculated from measured 13.852 ms latency].
  - With `IndexHNSWFlat`: $160,000 \times 0.915 \text{ ms} \approx \mathbf{146\text{ seconds}}$ (**~2.4 minutes**) [Calculated from measured 0.915 ms latency].
  - Production recommendation: Deploy **`FAISS IndexHNSWFlat`** (or managed Qdrant with HNSW). Sub-millisecond search ensures real-time query resolution.

### 5. Multi-Stage Filtering: LSH / MinHash Pre-Filter
To eliminate redundant dense neural queries for verbatim submissions:
1. **MinHash Fingerprinting**: Compute 128-bit MinHash signatures during text normalization ($O(1)$ lookup time, < 1 ms) [Estimate].
2. Document pairs with Jaccard $\ge 0.90$ are flagged immediately as direct duplicates without querying the vector index, shedding **~30% of vector query load** [Design assumption based on competition submission distributions].
3. Dense HNSW vector search is reserved for subtle paraphrasing and cross-modal audio alignment.

### 6. Accurate Cloud Compute Cost Math (AWS Spot Pricing)
- Compute cluster for processing 10,000 submissions within a 15-minute SLA:
  - **4x `c6i.2xlarge` CPU instances** (8 vCPU, 16 GB RAM) @ \$0.102/hour spot:
    Run for 0.5 hours = $4 \times \$0.102 \times 0.5 = \mathbf{\$0.204}$ [Estimate]
  - **2x `g4dn.xlarge` GPU instances** (4 vCPU, 16 GB RAM, 1 NVIDIA T4 GPU) @ \$0.157/hour spot (dedicated Whisper queue):
    Run for 0.5 hours = $2 \times \$0.157 \times 0.5 = \mathbf{\$0.157}$ [Estimate]
  - **Object Storage & Message Broker** (Amazon S3 for raw files + Redis Streams on AWS ElastiCache): $\approx \mathbf{\$0.02}$ [Estimate]
- **Worker Allocation**: 4 CPU nodes hosting 8 Celery worker processes each (32 total worker processes) for document ingestion and text normalization; 2 GPU nodes hosting 2 dedicated Whisper ASR workers for video speech transcription.
- **Total Batch Execution Time**: **~10 to 15 minutes** [Estimate based on pipelined queue simulation].
- **Total Cloud Compute Cost Arithmetic**:
  $$\text{Total Cost} = \$0.204\ (\text{CPU}) + \$0.157\ (\text{GPU}) + \$0.020\ (\text{S3/Redis}) = \mathbf{\$0.381}\ (\approx \mathbf{\$0.38})$$
  *(Estimate based on published AWS EC2 spot pricing for us-east-1).*

---

## Repository Structure

```
unstop-multimodal-integrity-engine/
├── config.yaml                    # Centralized thresholds, model names, and risk criteria
├── requirements.txt               # Pinned dependencies (cross-platform)
├── Makefile                       # Cross-platform shortcuts (setup, run, evaluate, test)
├── run.bat                        # Windows execution runner script
├── run_integrity_check.py         # Main CLI pipeline entrypoint
├── evaluate.py                    # Empirical evaluation benchmark against ground truth
├── EVALUATION.md                  # Measured metrics, confusion matrix & failure analysis
├── README.md                      # Architecture brief & 10,000 doc scaling plan
├── LICENSE                        # MIT Open Source License
├── benchmarks/
│   └── results.json               # Raw empirical hardware benchmark results
├── scripts/
│   ├── benchmark.py               # Hardware benchmarking script (CPU, Whisper, FAISS)
│   └── download_models.py         # Offline model pre-caching utility
├── src/
│   ├── extractors/
│   │   ├── base_extractor.py      # Abstract interface & data classes (PageContent, AudioSegment)
│   │   ├── pdf_extractor.py       # pypdf text extraction with page tracking
│   │   ├── docx_extractor.py      # python-docx structural paragraph extraction
│   │   ├── video_extractor.py     # Transformers Whisper ASR with audio stream verification
│   │   └── dispatcher.py          # Modality-aware routing dispatcher
│   ├── normalizer/
│   │   ├── normalizer.py          # Header/footer cleaner & sentence tokenizer
│   │   └── chunker.py             # Paragraph-aware sliding-window chunker
│   ├── filters/
│   │   └── boilerplate_filter.py  # Corpus document-frequency template discounting (Scenario 4)
│   ├── indexer/
│   │   └── vector_indexer.py      # SentenceTransformers & FAISS index with self-doc_id exclusion
│   ├── detectors/
│   │   ├── peer_detector.py       # Coverage-based peer & cross-modal similarity scorer
│   │   ├── external_detector.py   # External knowledge base plagiarism matcher
│   │   ├── ai_detector.py         # RoBERTa + GPT-2 perplexity + burstiness estimator
│   │   └── risk_calculator.py     # Multi-signal risk decision mapping (LOW/MEDIUM/HIGH)
│   ├── reporter/
│   │   ├── json_reporter.py       # Brief-compliant JSON report generator
│   │   ├── markdown_reporter.py   # Rapid-review (<30s) Markdown audit generator
│   │   └── batch_summary.py       # Pairwise similarity matrix & summary report
│   └── utils/
│       ├── config_loader.py       # YAML configuration reader
│       ├── ffmpeg_setup.py        # Bundled FFmpeg path discovery & validation
│       └── text_metrics.py        # Jaccard, Levenshtein, and timestamp formatters
├── tests/
│   └── test_pipeline.py           # Pytest unit test suite covering all scenarios
├── external_kb/                   # Short synthetic reference texts
│   ├── sources_manifest.json
│   ├── fintech_market_entry.txt
│   ├── maritime_logistics.txt
│   ├── renewable_microgrids.txt
│   ├── e_commerce_retention.txt
│   └── circular_packaging.txt
├── sample_submissions/            # 24 synthetic and semi-synthetic multi-modal test files
│   ├── dataset_manifest.json      # Ground truth metadata and pairwise relationships
│   ├── submission_01_fintech_report.pdf
│   ├── submission_02_video_pitch.mp4
│   ├── ...
│   └── submission_24_renewable_energy.pdf
└── reports/                       # Generated audit reports & pairwise summary matrix
    ├── batch_summary_report.md
    ├── summary_matrix.csv
    ├── evaluation_results.json
    ├── evaluation_tables.md       # Pre-rendered Markdown tables for reports
    ├── failure_cases/             # Raw logs for documented failure cases
    │   ├── case1_boilerplate_leakage.txt
    │   ├── case2_native_whisper_dll_block.txt
    │   ├── case3_ai_detector_ood_calibration.txt
    │   └── case4_external_kb_leakage.txt
    ├── submission_01_fintech_report.pdf.json
    ├── submission_01_fintech_report.pdf.md
    └── ...
```

---

## Dataset Provenance & Public-Domain Attribution

| Submission / Resource | Source / Basis | License / Status | Attribution & Citation |
| :--- | :--- | :--- | :--- |
| `submission_22_wikipedia_urban_transit.pdf` | Wikipedia: *Bus rapid transit* | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | [Wikipedia Article](https://en.wikipedia.org/wiki/Bus_rapid_transit), Wikimedia Foundation |
| `submission_23_rfc_internet_protocol.docx` | IETF RFC 791: *Internet Protocol Specification* (1981) | Public Domain | [IETF Datatracker RFC 791](https://datatracker.ietf.org/doc/html/rfc791), DARPA |
| `submission_24_wikipedia_renewable_energy.pdf` | Wikipedia: *Photovoltaics* | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) | [Wikipedia Article](https://en.wikipedia.org/wiki/Photovoltaics), Wikimedia Foundation |
| `external_kb/*.txt` (5 files) | Short synthetic / adapted domain summaries | Prototype Test Assets | Authored for external plagiarism benchmark validation; thematic reference concepts (Circular Economy, Maritime Logistics, Microgrids, Quick-Commerce, Neobanks) |
| `submission_14_llm_generated_essay.docx` | Synthesized by Antigravity (Gemini) | Prototype Test Asset | Simulating ChatGPT response to EV bus charging brief |
| `submission_15_llm_generated_synthesis.pdf` | Synthesized by Antigravity (Gemini) | Prototype Test Asset | Simulating Claude response to EV bus charging brief |
| Submissions `01`–`13`, `16`–`21` | Script-Generated Synthetic Texts | MIT License | Programmatically generated by `scripts/generate_synthetic_dataset.py` |

---

## Assumptions

1. **Submission Metadata**: File names are unique within a competition cohort and act as immutable submission identifiers (`doc_id`).
2. **Audio Language**: Spoken pitches are delivered in English (Whisper `language='en'` enforced).
3. **Hardware Independence**: The prototype defaults to CPU execution to ensure deterministic reproducibility on standard commodity workstations without requiring local CUDA GPU configuration.
4. **AI Generation Policy**: AI-generation likelihood alone is treated as a probabilistic indicator and does not trigger an automatic `HIGH` risk escalation without corroborating peer or external similarity evidence.
5. **Boilerplate Scope**: Reusable institutional text (e.g. competition problem prompts, case background headers) is expected to recur across $\ge 3$ independent candidate submissions within opening document sections (chunk index $\le 3$).
6. **Cohort Size**: The evaluation dataset contains 24 submission files, intentionally expanding beyond the 10–15 files suggested in the assessment brief to rigorously validate degraded media handling (Scenario 3), 5-way institutional template sharing (Scenario 4), external knowledge base detection (Scenario 5), and cross-modal spoken paraphrasing.

---

## AI Coding Assistants Disclosure

In line with Section 10 of the brief, I used AI assistants on this project:

- Antigravity (Google Gemini): coding assistant for implementation, tests and synthetic dataset generation.
- Claude (Anthropic): assistant for planning, reviewing results, debugging guidance and drafting task instructions.

How I worked:
- I owned the project end to end: scoping it against the brief, deciding what to build, and directing the assistants task by task.
- I reviewed every result before accepting it and ran the pipeline, tests and evaluation myself.
- I made the design calls: embedding model (MiniLM) vs. heavier models, FAISS index choice, the two-tier similarity thresholds, the boilerplate rule, and treating AI detection as an advisory signal only.
- I caught and corrected weak or unsupported claims: unmeasured benchmarks were relabelled as estimates, mislabelled sample provenance was fixed, and detector calibration limits were documented.

I understand the architecture and code and am ready to explain any part of it.

---

## What I Learned / Limitations

What I learned
- Semantic embeddings catch paraphrases that word-matching misses. A synonym-swapped document scored about 0.87 cosine similarity but only 0.18 Jaccard.
- Chunk position and prevalence matter for boilerplate. A shared case prompt near the start of documents should be discounted, but the same text in the body of several documents is more likely collusion. My first rule had a loophole, and I tightened it.
- A perfect score on a small synthetic dataset proves little. Adding harder cases (partial copies, near-threshold negatives, spoken paraphrases) exposed real weaknesses.
- AI-text detectors are unreliable. An older detector scored a 1981 human-written technical standard as AI-generated, and the better detector missed one LLM-style sample (19.3%). So AI probability is an advisory signal that cannot trigger HIGH risk alone.
- Similar topic is not the same as copying. External matching initially produced a false positive because texts shared domain vocabulary, which is why lexical corroboration was added.

Limitations
- The dataset is small (24 files) and synthetic. Thresholds (0.80 high-confidence, 0.65-0.80 manual review) were calibrated on it and may not transfer to real submissions.
- Chunks targeting ~250 words can exceed MiniLM's 256 WordPiece token limit (250 words typically expand to 300–350 subword tokens), causing `sentence-transformers` to silently truncate trailing tokens beyond position 256.
- Short paragraphs under 15 words (e.g. isolated headings, short bullet points) are not indexed on their own to prevent false positives on generic fragments.
- Headers and footers are only partly removed via regex heuristics; recurring multi-line running headers or complex page banners may partly persist in indexed chunks.
- Widening the opening boilerplate region to `chunk_index <= 3` (to accommodate cover sheets and titles) means that copied text in chunks 2–3 will be excused as boilerplate if it recurs across $\ge 3$ submissions.
- 30-second non-overlapping transcription windows can clip words that straddle a window boundary. The ~56s test clip places the copied text starting at 30.00s, so speech straddling a window boundary was not evaluated.
- With filename-based heuristics removed, `submission_14` and `submission_15` no longer get the dual-AI prompt convergence reviewer note because `submission_15` scores 19.3% with `chatgpt-detector-roberta` (below the 50% threshold). AI probability is strictly an auxiliary signal.
- AI detection is weak on some LLM styles; zero-shot detectors struggle on structured long-form outputs.
- Document-level risk ratings (`HIGH`, `MEDIUM`, `LOW`, `FLAGGED`) were derived from component thresholds and evaluated via pairwise relationships, but were not evaluated against a separately labeled document-level benchmark.
- Spoken-paraphrase matches score about 0.67, so they are only caught at the lower review tier (0.65–0.80).
- Two students independently asking an LLM the same prompt can look like copying (sub_14 and sub_15 scored about 0.95), which is an inherent false-positive risk.
- Speech recognition was tested only on clean text-to-speech audio (about 4.8% word error rate). Accented, noisy or phone-recorded speech was not evaluated.
- Only some scaling figures were measured locally (FAISS Flat vs HNSW, MiniLM throughput, Whisper speed). The others are labelled as estimates.
- Tested on Windows 11 with Python 3.10.8. Linux is covered by a CI workflow, and Python 3.9 compatibility was checked by inspection only.
- The two "LLM-generated" samples were produced by an AI assistant (Gemini), not by ChatGPT or Claude.

Next steps if I continued
- Evaluate on real student-style submissions and noisy or accented audio.
- Tune thresholds on a larger labelled set with a proper train/validation split.
- Use a stronger or ensemble AI detector and add stylometric signals.
- Add MinHash/LSH pre-filtering and an HNSW index for scale.

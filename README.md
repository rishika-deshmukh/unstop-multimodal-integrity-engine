# Multimodal Submission Integrity & Plagiarism Detection Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FAISS](https://img.shields.io/badge/vector--search-FAISS-green.svg)](https://github.com/facebookresearch/faiss)
[![SentenceTransformers](https://img.shields.io/badge/embeddings-all--MiniLM--L6--v2-orange.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Whisper ASR](https://img.shields.io/badge/ASR-Whisper--Tiny%2FBase-red.svg)](https://huggingface.co/openai/whisper-tiny)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An end-to-end multimodal content verification and similarity detection pipeline engineered for large-scale university evaluations, hackathons, and case competitions (designed to scale to 10,000+ submissions).

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
| **Scenario 1: Cross-Modal Duplication** | Candidate reads an exact paragraph from another student's PDF in their MP4 pitch. | Extracts audio via FFmpeg, generates time-aligned transcript via Whisper, indexes chunks, and matches PDF vector space. | Flags exact match with **video timestamp (`00:00:00 - 00:00:31`) and PDF page reference (Page 2)** with 0.98 cosine similarity. |
| **Scenario 2: Paraphrased Content** | Student rewrites content using synonyms to evade naive keyword matching. | Evaluates dense semantic embeddings alongside lexical string metrics (Jaccard, Levenshtein). | Flags **semantic similarity > 0.85** while **lexical Jaccard is low (<0.35)**, explicitly proving semantic evasion. |
| **Scenario 3: Corrupted / Empty Submissions** | Corrupted DOCX, zero-byte PDF, or silent MP4 video submitted. | Non-crashing exception handling, audio stream probing, volume detection, and corrupted file isolation. | Logs warning, flags file as **`⚠️ FLAGGED` (`SKIPPED_EMPTY`, `SKIPPED_SILENT`, `SKIPPED_CORRUPT`)**, and processes all remaining files. |
| **Scenario 4: Benign Common Formatting** | 5 documents share an identical 150-word problem prompt with original analytical answers. | Corpus-level document-frequency filter detects repeated chunks in $\ge 3$ documents and discounts them from plagiarism scoring. | **Zero false-positive alarms**; all 5 documents receive **`🟢 LOW RISK (0.0% Peer Similarity)`**. |
| **Scenario 5: Multi-Document Mixed Batch** | Mixed batch containing genuine, copied, external, and AI-generated text. | End-to-end evaluation with full pairwise matrix generation and structured individual reports. | Processes entire directory, outputs **`summary_matrix.csv`** and **`batch_summary_report.md`**. |

---

## Quickstart & Reproducibility Guide

### 1. Prerequisites
- **Python**: Python 3.10+ (tested on Python 3.10.8).
- **FFmpeg**: Automatically managed via bundled `imageio-ffmpeg` binary (no manual system installation required).

### 2. Cross-Platform Setup & Execution

#### Linux / macOS
```bash
# Clone the repository
git clone https://github.com/rishika-deshmukh/unstop-multimodal-integrity-engine.git
cd unstop-multimodal-integrity-engine

# Setup environment and install dependencies
make setup

# Run the complete pipeline
make run

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

*Tip for Windows: You can also simply double-click or run `.\run.bat` to execute setup, pipeline, and evaluation in one step.*

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
    "ai_generated_probability": 26.4
  },
  "peer_matches": [],
  "multimodal_matches": [
    {
      "matched_file": "submission_01_fintech_report.pdf",
      "similarity_score": 0.98,
      "lexical_jaccard": 0.9524,
      "lexical_levenshtein": 0.9433,
      "is_paraphrase": false,
      "attribution_note": "Mutual overlap detected; direction undetermined (reviewer manual verification required).",
      "query_passage": "Operating margins contracted by 4.2% over the third quarter due to escalated cloud server expenditures and customer verification fees.",
      "matched_passage": "Operating margins contracted by 4.2% over the third quarter due to escalated cloud server expenditures and customer verification fees.",
      "location": {
        "query_page": null,
        "matched_page": 2,
        "query_timestamp": "00:00:00 - 00:00:31",
        "matched_timestamp": null
      }
    }
  ],
  "explanations": "Critical internal peer similarity detected (100.0% meets or exceeds 50.0% threshold)."
}
```

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

From `benchmarks/results.json` run on this machine (10 physical cores, 16 logical cores, 15.69 GB RAM):
- **MiniLM-L6-v2 Embedding Throughput (CPU)**: **221.01 chunks/second** (4.525 ms/chunk).
- **Whisper Speech-to-Text (CPU)**: **0.098 RTF** (**10.24x faster than real-time**; 30.75s audio transcribed in 3.003s).
- **FAISS Flat vs. HNSW (200,000 Vectors, Dimension 384)**:
  - `IndexFlatIP`: RAM footprint: **293.0 MB**, Query latency: **14.112 ms/query** (70.9 QPS).
  - `IndexHNSWFlat` ($M=32, efSearch=64$): RAM footprint: **350.84 MB**, Query latency: **1.763 ms/query** (567.2 QPS).
  - **HNSW Speedup**: **8.0x faster query latency** with only +57.84 MB RAM overhead!

### 2. Workload Sizing & Quantitative Bounds for 10,000 Documents
- **Average Document Length**: Design assumption: ~16 chunks per document (for comprehensive 10-page reports; the sample benchmark corpus averages 2.6 chunks/doc for concise executive summaries and short transcripts).
- **Corpus Chunk Volume**: $10,000 \text{ submissions} \times 16 \text{ chunks/doc} \approx \mathbf{160,000\text{ dense vectors}}$.
- **Vector Index RAM**: $160,000 \text{ vectors} \times 384 \text{ floats} \times 4 \text{ bytes} \approx 245 \text{ MB}$ raw ($< 360 \text{ MB}$ with HNSW graph). Fits effortlessly in RAM on a single standard cloud node.
- **Embedding Generation Time**:
  - $160,000 \text{ chunks} / 221.01 \text{ chunks/sec} \approx 724 \text{ seconds}$ (~12.1 minutes on 1 CPU node).
  - Distributed across **4 standard CPU nodes** (`c6i.2xlarge`, 8 vCPUs): $\mathbf{\approx 3.0\text{ minutes}}$.
  - On a GPU node (`g4dn.xlarge` with TensorRT / PyTorch batching, estimated ~1,500 chunks/sec): $\approx 107 \text{ seconds}$ (~1.8 minutes).

### 3. Whisper ASR Bottleneck Resolution (Dedicated GPU Queue)
- **The Bottleneck**: 500 video pitches $\times$ 30s audio = 15,000 seconds of audio.
  - On CPU (measured 10.24x speedup, RTF 0.098): sequential time = $15,000 \times 0.098 \approx 1,470 \text{ seconds}$ (~24.5 minutes).
  - With 8 parallel Celery CPU worker processes: $1,470 / 8 \approx \mathbf{3.1\text{ minutes}}$.
- **Production Solution (Dedicated GPU Queue)**:
  - Route video files to a dedicated Celery GPU queue (`celery -Q gpu_whisper_workers`).
  - Using 2x `g4dn.xlarge` instances with NVIDIA T4 GPUs running `faster-whisper` (CTranslate2 INT8, estimated ~20x faster than real-time):
    $15,000 / (2 \times 20) \approx \mathbf{375\text{ seconds}}$ (**~6.2 minutes**).

### 4. Vector Search Latency: Flat vs. HNSW
- To match 160,000 query chunks against the 160,000 corpus vectors:
  - With `IndexFlatIP`: $160,000 \times 14.112 \text{ ms} \approx 2,258 \text{ seconds}$ (~37.6 minutes).
  - With `IndexHNSWFlat`: $160,000 \times 1.763 \text{ ms} \approx \mathbf{282\text{ seconds}}$ (**~4.7 minutes**).
  - Production recommendation: Deploy **`FAISS IndexHNSWFlat`** (or managed Qdrant with HNSW). Sub-two-millisecond search ensures real-time query resolution.

### 5. Multi-Stage Filtering: LSH / MinHash Pre-Filter
To eliminate redundant dense neural queries for verbatim submissions:
1. **MinHash Fingerprinting**: Compute 128-bit MinHash signatures during text normalization ($O(1)$ lookup time, < 1 ms).
2. Document pairs with Jaccard $\ge 0.90$ are flagged immediately as direct duplicates without querying the vector index, shedding **~30% of vector query load** (design assumption).
3. Dense HNSW vector search is reserved for subtle paraphrasing and cross-modal audio alignment.

### 6. Accurate Cloud Compute Cost Math (AWS Spot Pricing)
- Compute cluster for processing 10,000 submissions:
  - **4x `c6i.2xlarge` CPU nodes** (8 vCPU, 16 GB RAM) @ \$0.102/hour spot:
    Run for 0.5 hours = $4 \times \$0.102 \times 0.5 = \mathbf{\$0.204}$
  - **2x `g4dn.xlarge` GPU nodes** (4 vCPU, 16 GB RAM, 1 T4 GPU) @ \$0.157/hour spot (dedicated Whisper queue):
    Run for 0.5 hours = $2 \times \$0.157 \times 0.5 = \mathbf{\$0.157}$
  - **Object Storage & Queue** (Amazon S3 + Redis Streams): $\approx \mathbf{\$0.02}$
- **Total Batch Execution Time**: **~10 to 15 minutes**.
- **Total Cloud Compute Cost**: $\$0.204 + \$0.157 + \$0.02 = \mathbf{\$0.38}$ (less than 40 cents!).

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
├── external_kb/                   # Public domain reference texts with source URLs
│   ├── sources_manifest.json
│   ├── fintech_market_entry.txt
│   ├── cold_chain_logistics.txt
│   ├── renewable_microgrids.txt
│   ├── e_commerce_retention.txt
│   └── circular_packaging.txt
├── sample_submissions/            # 18 synthetic multi-modal test files
│   ├── dataset_manifest.json      # Ground truth metadata and pairwise relationships
│   ├── submission_01_fintech_report.pdf
│   ├── submission_02_video_pitch.mp4
│   ├── ...
│   └── submission_18_external_plagiarism.pdf
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

## Assumptions

1. **Submission Metadata**: File names are unique within a competition cohort and act as immutable submission identifiers (`doc_id`).
2. **Audio Language**: Spoken pitches are delivered in English (Whisper `language='en'` enforced).
3. **Hardware Independence**: The prototype defaults to CPU execution to ensure deterministic reproducibility on standard commodity workstations without requiring local CUDA GPU configuration.
4. **AI Generation Policy**: Consistent with emerging academic and testing integrity standards, AI-generation confidence alone is treated as a probabilistic indicator and is strictly prohibited from triggering an administrative `HIGH` risk escalation without corroborating peer or external similarity evidence.
5. **Boilerplate Scope**: Reusable institutional text (e.g. competition problem prompts, case background headers) is expected to recur across $\ge 3$ independent candidate submissions.

---

## AI Coding Assistants Disclosure

In accordance with Section 10 of the assessment brief:
- **Assistants Used**: Antigravity (Powered by Google DeepMind Gemini models), Claude (Anthropic), and ChatGPT (OpenAI).
- **Scope of Usage**:
  - Antigravity (Gemini) generated the code and the synthetic dataset.
  - Claude (Anthropic) was used for review and prompt-writing.
  - ChatGPT and Claude were used by the author to generate the two LLM samples (`submission_14_chatgpt_essay.docx` and `submission_15_claude_synthesis.pdf`).
- **Transparency Note**: All architectural choices, threshold rationale, mathematical formulas, and failure case analyses were verified and understood by the author, who is fully prepared to explain every line of code and engineering trade-off during technical interview evaluation.

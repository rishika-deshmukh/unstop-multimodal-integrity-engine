"""
Empirical Hardware Benchmark Suite.
Measures real performance on the current evaluation machine:
(a) SentenceTransformers (all-MiniLM-L6-v2) embedding throughput on CPU (chunks/sec).
(b) Whisper-tiny real-time factor (RTF) and inference speedup on sample audio/video.
(c) FAISS IndexFlatIP vs. IndexHNSWFlat query latency and memory on 200,000 384-d vectors.
Saves all computed empirical results to benchmarks/results.json.
"""

import os
import sys
import time
import json
import psutil
from pathlib import Path
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentence_transformers import SentenceTransformer
import faiss
from src.extractors.video_extractor import VideoExtractor

def get_process_memory_mb() -> float:
    """Returns current process RAM usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def benchmark_embeddings(model_name: str = "all-MiniLM-L6-v2", n_chunks: int = 500) -> dict:
    print(f"\n[1/3] Benchmarking SentenceTransformer '{model_name}' on CPU ({n_chunks} chunks)...")
    model = SentenceTransformer(model_name, device="cpu")

    # Sample paragraph text ~120 words
    sample_text = (
        "The transition towards zero-emission commercial fleets requires systematic restructuring "
        "of utility charging interconnects, multi-megawatt depot substation capacity, and dynamic tariff "
        "arbitrage. Fleet telemetry demonstrates that nocturnal charging windows reduce peak coincident demand "
        "surcharges while extending battery life cycles through thermal regulation and balanced cell equalization."
    )
    texts = [f"{sample_text} [Iteration {i}]" for i in range(n_chunks)]

    # Warmup
    _ = model.encode(texts[:10], batch_size=32, device="cpu", show_progress_bar=False)

    # Timed run
    start_time = time.perf_counter()
    embs = model.encode(texts, batch_size=32, device="cpu", show_progress_bar=False, normalize_embeddings=True)
    elapsed = time.perf_counter() - start_time

    chunks_per_sec = round(n_chunks / elapsed, 2)
    ms_per_chunk = round((elapsed / n_chunks) * 1000.0, 3)

    print(f"  -> Processed {n_chunks} chunks in {elapsed:.2f}s ({chunks_per_sec} chunks/sec, {ms_per_chunk} ms/chunk)")
    return {
        "model_name": model_name,
        "device": "cpu",
        "n_chunks": n_chunks,
        "elapsed_seconds": round(elapsed, 4),
        "chunks_per_second": chunks_per_sec,
        "ms_per_chunk": ms_per_chunk,
        "embedding_dimension": int(embs.shape[1])
    }

def benchmark_whisper(sample_mp4: Path) -> dict:
    print(f"\n[2/3] Benchmarking Whisper-tiny ASR on '{sample_mp4.name}'...")
    if not sample_mp4.exists():
        print(f"  -> Sample MP4 not found at {sample_mp4}")
        return {"status": "FILE_NOT_FOUND"}

    extractor = VideoExtractor(model_name="openai/whisper-tiny", device="cpu")
    
    # Warmup load
    extractor._load_model()

    start_time = time.perf_counter()
    doc = extractor.extract(sample_mp4)
    elapsed = time.perf_counter() - start_time

    # Calculate audio duration from segments
    audio_duration = 0.0
    if doc.audio_segments:
        audio_duration = doc.audio_segments[-1].end_seconds
    elif doc.raw_text:
        # Fallback estimated duration from word count at 150 wpm
        audio_duration = max(5.0, len(doc.raw_text.split()) / 2.5)

    rtf = round(elapsed / audio_duration, 3) if audio_duration > 0 else 0.0
    speedup = round(audio_duration / elapsed, 2) if elapsed > 0 else 0.0

    print(f"  -> Audio Duration: {audio_duration:.2f}s | Transcription Time: {elapsed:.2f}s")
    print(f"  -> Real-Time Factor (RTF): {rtf}x | Inference Speedup: {speedup}x real-time")

    return {
        "model_name": "openai/whisper-tiny",
        "device": "cpu",
        "file_tested": sample_mp4.name,
        "audio_duration_seconds": round(audio_duration, 2),
        "transcription_seconds": round(elapsed, 3),
        "real_time_factor_rtf": rtf,
        "speedup_vs_realtime": speedup,
        "transcribed_word_count": len(doc.raw_text.split())
    }

def benchmark_faiss(n_vectors: int = 200_000, dim: int = 384, n_queries: int = 100) -> dict:
    print(f"\n[3/3] Benchmarking FAISS Flat vs HNSW on {n_vectors:,} vectors (dim={dim})...")
    np.random.seed(42)

    # 1. Generate normalized vectors
    print(f"  -> Generating {n_vectors:,} random 384-dimensional unit vectors...")
    data = np.random.randn(n_vectors, dim).astype(np.float32)
    faiss.normalize_L2(data)

    query_vectors = np.random.randn(n_queries, dim).astype(np.float32)
    faiss.normalize_L2(query_vectors)

    # 2. Benchmark IndexFlatIP
    mem_before_flat = get_process_memory_mb()
    t0 = time.perf_counter()
    index_flat = faiss.IndexFlatIP(dim)
    index_flat.add(data)
    flat_build_time = time.perf_counter() - t0
    mem_after_flat = get_process_memory_mb()
    flat_ram_mb = round(mem_after_flat - mem_before_flat, 2)

    # Timed queries on IndexFlatIP (k=10)
    t0 = time.perf_counter()
    for q_idx in range(n_queries):
        _ = index_flat.search(query_vectors[q_idx:q_idx+1], 10)
    flat_query_time_total = time.perf_counter() - t0
    flat_latency_ms = round((flat_query_time_total / n_queries) * 1000.0, 3)

    print(f"  -> IndexFlatIP: Build Time={flat_build_time:.2f}s | RAM={flat_ram_mb} MB | Latency={flat_latency_ms} ms/query")

    # Release flat index memory before HNSW benchmark
    del index_flat

    # 3. Benchmark IndexHNSWFlat
    mem_before_hnsw = get_process_memory_mb()
    t0 = time.perf_counter()
    M = 32
    index_hnsw = faiss.IndexHNSWFlat(dim, M, faiss.METRIC_INNER_PRODUCT)
    index_hnsw.hnsw.efSearch = 64
    index_hnsw.add(data)
    hnsw_build_time = time.perf_counter() - t0
    mem_after_hnsw = get_process_memory_mb()
    hnsw_ram_mb = round(mem_after_hnsw - mem_before_hnsw, 2)

    # Timed queries on IndexHNSWFlat (k=10)
    t0 = time.perf_counter()
    for q_idx in range(n_queries):
        _ = index_hnsw.search(query_vectors[q_idx:q_idx+1], 10)
    hnsw_query_time_total = time.perf_counter() - t0
    hnsw_latency_ms = round((hnsw_query_time_total / n_queries) * 1000.0, 3)

    print(f"  -> IndexHNSWFlat (M={M}): Build Time={hnsw_build_time:.2f}s | RAM={hnsw_ram_mb} MB | Latency={hnsw_latency_ms} ms/query")

    speedup = round(flat_latency_ms / hnsw_latency_ms, 1) if hnsw_latency_ms > 0 else 0.0

    return {
        "n_vectors": n_vectors,
        "dimension": dim,
        "n_queries_timed": n_queries,
        "index_flat": {
            "build_time_seconds": round(flat_build_time, 2),
            "ram_footprint_mb": flat_ram_mb,
            "query_latency_ms": flat_latency_ms,
            "queries_per_second": round(1000.0 / flat_latency_ms, 1) if flat_latency_ms > 0 else 0.0
        },
        "index_hnsw": {
            "m_parameter": M,
            "ef_search": 64,
            "build_time_seconds": round(hnsw_build_time, 2),
            "ram_footprint_mb": hnsw_ram_mb,
            "query_latency_ms": hnsw_latency_ms,
            "queries_per_second": round(1000.0 / hnsw_latency_ms, 1) if hnsw_latency_ms > 0 else 0.0
        },
        "hnsw_speedup_vs_flat": speedup
    }

def benchmark_roberta(model_name: str = "roberta-base-openai-detector", n_samples: int = 30) -> dict:
    print(f"\n[4/5] Benchmarking RoBERTa classifier '{model_name}' on CPU ({n_samples} samples)...")
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()

    sample_doc = (
        "The transition towards zero-emission commercial fleets requires systematic restructuring "
        "of utility charging interconnects, multi-megawatt depot substation capacity, and dynamic tariff "
        "arbitrage. Fleet telemetry demonstrates that nocturnal charging windows reduce peak coincident demand "
        "surcharges while extending battery life cycles through thermal regulation and balanced cell equalization."
    )
    texts = [f"{sample_doc} [Doc {i}]" for i in range(n_samples)]

    # Warmup
    inputs = tokenizer(texts[:2], return_tensors="pt", truncation=True, max_length=256, padding=True)
    with torch.no_grad():
        _ = model(**inputs)

    start_time = time.perf_counter()
    with torch.no_grad():
        for t in texts:
            inp = tokenizer(t, return_tensors="pt", truncation=True, max_length=256)
            _ = model(**inp)
    elapsed = time.perf_counter() - start_time

    docs_per_sec = round(n_samples / elapsed, 2)
    ms_per_doc = round((elapsed / n_samples) * 1000.0, 2)

    print(f"  -> Processed {n_samples} docs in {elapsed:.2f}s ({docs_per_sec} docs/sec, {ms_per_doc} ms/doc)")
    return {
        "model_name": model_name,
        "device": "cpu",
        "n_samples": n_samples,
        "elapsed_seconds": round(elapsed, 4),
        "docs_per_second": docs_per_sec,
        "ms_per_doc": ms_per_doc
    }

def benchmark_gpt2(model_name: str = "gpt2", n_samples: int = 20) -> dict:
    print(f"\n[5/5] Benchmarking GPT-2 perplexity causal LM '{model_name}' on CPU ({n_samples} samples)...")
    from transformers import GPT2LMHeadModel, GPT2TokenizerFast
    import torch

    tokenizer = GPT2TokenizerFast.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    model.eval()

    sample_doc = (
        "The transition towards zero-emission commercial fleets requires systematic restructuring "
        "of utility charging interconnects, multi-megawatt depot substation capacity, and dynamic tariff "
        "arbitrage. Fleet telemetry demonstrates that nocturnal charging windows reduce peak coincident demand "
        "surcharges while extending battery life cycles through thermal regulation and balanced cell equalization."
    )
    texts = [f"{sample_doc} [Doc {i}]" for i in range(n_samples)]

    # Warmup
    enc = tokenizer(texts[0], return_tensors="pt")
    with torch.no_grad():
        _ = model(enc.input_ids, labels=enc.input_ids)

    start_time = time.perf_counter()
    with torch.no_grad():
        for t in texts:
            enc = tokenizer(t, return_tensors="pt", truncation=True, max_length=256)
            _ = model(enc.input_ids, labels=enc.input_ids)
    elapsed = time.perf_counter() - start_time

    docs_per_sec = round(n_samples / elapsed, 2)
    ms_per_doc = round((elapsed / n_samples) * 1000.0, 2)

    print(f"  -> Processed {n_samples} docs in {elapsed:.2f}s ({docs_per_sec} docs/sec, {ms_per_doc} ms/doc)")
    return {
        "model_name": model_name,
        "device": "cpu",
        "n_samples": n_samples,
        "elapsed_seconds": round(elapsed, 4),
        "docs_per_second": docs_per_sec,
        "ms_per_doc": ms_per_doc
    }

def main():
    benchmarks_dir = Path("./benchmarks")
    benchmarks_dir.mkdir(parents=True, exist_ok=True)
    out_file = benchmarks_dir / "results.json"

    print("==================================================================")
    print("UNSTOP ENGINE: EMPIRICAL HARDWARE BENCHMARK EXECUTION")
    print("Measuring real compute, ASR, and vector latency on local workstation")
    print("==================================================================")

    results = {
        "benchmark_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hardware_context": {
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_count_physical": psutil.cpu_count(logical=False),
            "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "platform": sys.platform
        }
    }

    # (a) Embeddings Benchmark
    results["embeddings_benchmark"] = benchmark_embeddings(model_name="all-MiniLM-L6-v2", n_chunks=300)

    # (b) Whisper Benchmark
    sample_mp4 = Path("sample_submissions/submission_02_video_pitch.mp4")
    results["whisper_benchmark"] = benchmark_whisper(sample_mp4)

    # (c) FAISS Benchmark (200k vectors)
    results["faiss_benchmark"] = benchmark_faiss(n_vectors=200_000, dim=384, n_queries=100)

    # (d) RoBERTa Classifier Benchmark
    results["roberta_benchmark"] = benchmark_roberta(model_name="roberta-base-openai-detector", n_samples=30)

    # (e) GPT-2 Perplexity Benchmark
    results["gpt2_benchmark"] = benchmark_gpt2(model_name="gpt2", n_samples=20)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n==================================================================")
    print(f"Empirical benchmarks complete. Saved to: {out_file}")
    print("==================================================================")

if __name__ == "__main__":
    main()

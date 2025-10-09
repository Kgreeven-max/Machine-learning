#!/usr/bin/env python3
"""
Ollama Stress Test & Benchmark Suite
Tests performance, resource usage, and scalability
"""

import asyncio
import httpx
import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any
import sys

# Configuration
BASE_URL = "http://localhost:8080/v1/chat/completions"
API_KEY = "sk-oatisawesome-2024-ml-api"
MODEL = "llama3.1:8b"

# Test prompts of varying sizes
PROMPTS = {
    "small": "What is 2+2? Reply with just the number.",
    "medium": """Explain the concept of machine learning in 3-4 sentences.
    Include what it is, how it works, and give one practical example of its use in everyday life.""",
    "large": """You are a technical writer creating documentation. Write a detailed explanation
    of how neural networks work. Your explanation should cover:
    1. What neural networks are and their basic structure (neurons, layers)
    2. How they learn through training (forward propagation, backpropagation)
    3. Common activation functions and their purposes
    4. The difference between deep learning and traditional neural networks
    5. At least 3 real-world applications with specific examples

    Make it accessible to someone with basic programming knowledge but no AI background.
    Aim for about 300-400 words."""
}

class BenchmarkResults:
    """Store and analyze benchmark results"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.latencies: List[float] = []
        self.tokens_generated: List[int] = []
        self.tokens_per_second: List[float] = []
        self.errors: List[str] = []
        self.start_time: float = 0
        self.end_time: float = 0

    def add_result(self, latency: float, tokens: int, error: str = None):
        """Add a single request result"""
        if error:
            self.errors.append(error)
        else:
            self.latencies.append(latency)
            self.tokens_generated.append(tokens)
            if latency > 0:
                self.tokens_per_second.append(tokens / latency)

    def get_stats(self) -> Dict[str, Any]:
        """Calculate statistics from results"""
        if not self.latencies:
            return {"error": "No successful requests"}

        total_time = self.end_time - self.start_time
        total_requests = len(self.latencies) + len(self.errors)
        successful_requests = len(self.latencies)

        sorted_latencies = sorted(self.latencies)

        return {
            "test_name": self.test_name,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": len(self.errors),
            "success_rate": f"{(successful_requests/total_requests)*100:.1f}%",
            "total_time": f"{total_time:.2f}s",
            "requests_per_second": f"{successful_requests/total_time:.2f}",
            "latency": {
                "min": f"{min(self.latencies):.2f}s",
                "max": f"{max(self.latencies):.2f}s",
                "mean": f"{statistics.mean(self.latencies):.2f}s",
                "median": f"{statistics.median(self.latencies):.2f}s",
                "p95": f"{sorted_latencies[int(len(sorted_latencies)*0.95)]:.2f}s" if len(sorted_latencies) > 1 else "N/A",
                "p99": f"{sorted_latencies[int(len(sorted_latencies)*0.99)]:.2f}s" if len(sorted_latencies) > 1 else "N/A",
            },
            "tokens": {
                "total": sum(self.tokens_generated),
                "mean_per_request": f"{statistics.mean(self.tokens_generated):.0f}",
                "tokens_per_second_mean": f"{statistics.mean(self.tokens_per_second):.1f}",
                "tokens_per_second_max": f"{max(self.tokens_per_second):.1f}",
            }
        }

async def make_request(client: httpx.AsyncClient, prompt: str) -> Dict[str, Any]:
    """Make a single API request and measure performance"""
    start_time = time.time()

    try:
        response = await client.post(
            BASE_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=300.0
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            # Handle both OpenAI and Ollama response formats
            if "choices" in data:
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("completion_tokens", len(content.split()))
            else:
                content = data.get("message", {}).get("content", "")
                tokens = len(content.split())  # Rough estimate

            return {
                "success": True,
                "latency": elapsed,
                "tokens": tokens,
                "error": None
            }
        else:
            return {
                "success": False,
                "latency": elapsed,
                "tokens": 0,
                "error": f"HTTP {response.status_code}"
            }

    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "latency": elapsed,
            "tokens": 0,
            "error": str(e)
        }

async def run_concurrent_test(
    num_requests: int,
    concurrency: int,
    prompt: str,
    test_name: str
) -> BenchmarkResults:
    """Run benchmark with specified concurrency"""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"Requests: {num_requests} | Concurrency: {concurrency}")
    print(f"{'='*60}")

    results = BenchmarkResults(test_name)
    results.start_time = time.time()

    async with httpx.AsyncClient() as client:
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_request():
            async with semaphore:
                return await make_request(client, prompt)

        # Create all tasks
        tasks = [bounded_request() for _ in range(num_requests)]

        # Run with progress indication
        completed = 0
        for coro in asyncio.as_completed(tasks):
            result = await coro
            completed += 1

            results.add_result(
                result["latency"],
                result["tokens"],
                result["error"]
            )

            # Progress indicator
            if completed % max(1, num_requests // 10) == 0 or completed == num_requests:
                print(f"Progress: {completed}/{num_requests} requests completed...")

    results.end_time = time.time()
    return results

def print_results(results: BenchmarkResults):
    """Pretty print benchmark results"""
    stats = results.get_stats()

    if "error" in stats:
        print(f"\n❌ {stats['error']}")
        return

    print(f"\n{'='*60}")
    print(f"📊 Results: {stats['test_name']}")
    print(f"{'='*60}")
    print(f"\n📈 Request Statistics:")
    print(f"  Total Requests:      {stats['total_requests']}")
    print(f"  Successful:          {stats['successful_requests']}")
    print(f"  Failed:              {stats['failed_requests']}")
    print(f"  Success Rate:        {stats['success_rate']}")
    print(f"  Total Time:          {stats['total_time']}")
    print(f"  Requests/Second:     {stats['requests_per_second']}")

    print(f"\n⏱️  Latency (Response Time):")
    print(f"  Min:                 {stats['latency']['min']}")
    print(f"  Mean:                {stats['latency']['mean']}")
    print(f"  Median:              {stats['latency']['median']}")
    print(f"  95th percentile:     {stats['latency']['p95']}")
    print(f"  99th percentile:     {stats['latency']['p99']}")
    print(f"  Max:                 {stats['latency']['max']}")

    print(f"\n🔤 Token Generation:")
    print(f"  Total Tokens:        {stats['tokens']['total']}")
    print(f"  Mean/Request:        {stats['tokens']['mean_per_request']}")
    print(f"  Tokens/Second (avg): {stats['tokens']['tokens_per_second_mean']}")
    print(f"  Tokens/Second (max): {stats['tokens']['tokens_per_second_max']}")

    if results.errors:
        print(f"\n⚠️  Errors ({len(results.errors)}):")
        for i, error in enumerate(results.errors[:5], 1):
            print(f"  {i}. {error}")
        if len(results.errors) > 5:
            print(f"  ... and {len(results.errors) - 5} more")

    print(f"\n{'='*60}\n")

    return stats

async def main():
    """Run complete benchmark suite"""
    print("\n" + "="*60)
    print("🚀 OLLAMA STRESS TEST & BENCHMARK SUITE")
    print("="*60)
    print(f"\nModel: {MODEL}")
    print(f"Endpoint: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = []

    # Test 1: Baseline - Single request
    print("\n" + "="*60)
    print("TEST 1: BASELINE (Single Request)")
    print("="*60)
    result = await run_concurrent_test(1, 1, PROMPTS["small"], "Baseline - Single Request")
    all_results.append(print_results(result))

    # Test 2: Small prompts - Low concurrency
    print("\n" + "="*60)
    print("TEST 2: SMALL PROMPTS - LOW LOAD")
    print("="*60)
    result = await run_concurrent_test(10, 5, PROMPTS["small"], "Small Prompts - 5 Concurrent")
    all_results.append(print_results(result))

    # Test 3: Medium prompts - Low concurrency
    print("\n" + "="*60)
    print("TEST 3: MEDIUM PROMPTS - LOW LOAD")
    print("="*60)
    result = await run_concurrent_test(10, 5, PROMPTS["medium"], "Medium Prompts - 5 Concurrent")
    all_results.append(print_results(result))

    # Test 4: Medium prompts - Medium concurrency
    print("\n" + "="*60)
    print("TEST 4: MEDIUM PROMPTS - MEDIUM LOAD")
    print("="*60)
    result = await run_concurrent_test(20, 10, PROMPTS["medium"], "Medium Prompts - 10 Concurrent")
    all_results.append(print_results(result))

    # Test 5: Large prompts - Low concurrency
    print("\n" + "="*60)
    print("TEST 5: LARGE PROMPTS - LOW LOAD")
    print("="*60)
    result = await run_concurrent_test(5, 3, PROMPTS["large"], "Large Prompts - 3 Concurrent")
    all_results.append(print_results(result))

    # Test 6: Stress test - High concurrency
    print("\n" + "="*60)
    print("TEST 6: STRESS TEST - HIGH LOAD")
    print("="*60)
    result = await run_concurrent_test(30, 20, PROMPTS["medium"], "Stress Test - 20 Concurrent")
    all_results.append(print_results(result))

    # Summary
    print("\n" + "="*60)
    print("📋 BENCHMARK SUMMARY")
    print("="*60)
    print("\nAll tests completed successfully!")
    print(f"\nResults saved to benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    # Save detailed results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"benchmark_results_{timestamp}.json", "w") as f:
        json.dump(all_results, f, indent=2)

    return all_results

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        sys.exit(1)

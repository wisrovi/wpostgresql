"""
Stress test for wpostgresql library.

This test simulates multiple users making CONCURRENT requests
to verify the stability and performance of the library.

Usage:
    python run.py
    python run.py --async
    python run.py --users 100 --requests 10
"""

import argparse
import asyncio
import os
import random
import string
import sys
import time
from dataclasses import dataclass
from threading import Lock

from pydantic import BaseModel


@dataclass
class StressTestConfig:
    """Configuration for stress test."""

    num_users: int = 1000
    requests_per_user: int = 100
    db_config: dict = None
    use_async: bool = False
    verbose: bool = False

    def __post_init__(self):
        if self.db_config is None:
            self.db_config = {
                "dbname": os.getenv("POSTGRES_DB", "wpostgresql"),
                "user": os.getenv("POSTGRES_USER", "postgres"),
                "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
                "host": os.getenv("POSTGRES_HOST", "localhost"),
                "port": int(os.getenv("POSTGRES_PORT", "5432")),
            }


@dataclass
class StressTestResult:
    """Result of a stress test."""

    total_operations: int
    successful_operations: int
    failed_operations: int
    total_time: float
    operations_per_second: float
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    errors: list

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("STRESS TEST RESULTS")
        print("=" * 60)
        print(f"Total operations:    {self.total_operations:,}")
        print(f"Successful:           {self.successful_operations:,}")
        print(f"Failed:              {self.failed_operations:,}")
        print(
            f"Success rate:        {self.successful_operations / self.total_operations * 100:.2f}%"
        )
        print(f"Total time:          {self.total_time:.2f}s")
        print(f"Operations/sec:       {self.operations_per_second:.2f}")
        print(f"Avg response time:   {self.avg_response_time * 1000:.2f}ms")
        print(f"Min response time:   {self.min_response_time * 1000:.2f}ms")
        print(f"Max response time:  {self.max_response_time * 1000:.2f}ms")

        if self.errors:
            print("\n" + "-" * 60)
            print("ERRORS (top 10):")
            error_counts = {}
            for err in self.errors:
                error_counts[err] = error_counts.get(err, 0) + 1
            for i, (err, count) in enumerate(
                sorted(error_counts.items(), key=lambda x: -x[1])[:10]
            ):
                print(f"  {i + 1}. [{count}x] {err[:100]}")

        print("=" * 60)


class StressTestMetrics:
    """Metrics collector for stress test."""

    def __init__(self):
        self.lock = Lock()
        self.response_times = []
        self.successful = 0
        self.failed = 0
        self.errors = []

    def record_success(self, response_time: float):
        with self.lock:
            self.response_times.append(response_time)
            self.successful += 1

    def record_failure(self, error: str):
        with self.lock:
            self.failed += 1
            self.errors.append(error)

    def get_result(self, total_operations: int, total_time: float):
        with self.lock:
            response_times = self.response_times.copy()

        if response_times:
            avg = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
        else:
            avg = max_time = min_time = 0

        return StressTestResult(
            total_operations=total_operations,
            successful_operations=self.successful,
            failed_operations=self.failed,
            total_time=total_time,
            operations_per_second=total_operations / total_time if total_time > 0 else 0,
            avg_response_time=avg,
            max_response_time=max_time,
            min_response_time=min_time,
            errors=self.errors,
        )


class UserModel(BaseModel):
    """User model for stress testing."""

    id: int
    name: str
    email: str
    age: int
    balance: float
    status: str


def generate_random_user(user_id: int, req_id: int) -> UserModel:
    return UserModel(
        id=user_id * 100000 + req_id,
        name="".join(random.choices(string.ascii_letters, k=10)),
        email=f"user{user_id}_{req_id}@test.com",
        age=random.randint(18, 80),
        balance=random.uniform(0, 10000),
        status=random.choice(["active", "inactive", "pending"]),
    )


def run_sync_operation(db, operation_type: str, user_id: int, req_id: int):
    """Run a single sync operation."""
    start = time.time()
    try:
        user = generate_random_user(user_id, req_id)

        if operation_type == "insert":
            db.insert(user)
        elif operation_type == "get_all":
            db.get_all()
        elif operation_type == "get_by_field":
            db.get_by_field(id=user.id)
        elif operation_type == "update":
            db.update(user.id, user)
        elif operation_type == "delete":
            db.delete(user.id)
        elif operation_type == "count":
            db.count()
        elif operation_type == "paginated":
            db.get_paginated(limit=10, offset=0)

        return time.time() - start, None
    except Exception as e:
        return time.time() - start, f"{type(e).__name__}: {str(e)[:50]}"


async def run_async_operation(db, operation_type: str, user_id: int, req_id: int):
    """Run a single async operation."""
    start = time.time()
    try:
        user = generate_random_user(user_id, req_id)

        if operation_type == "insert":
            await db.insert_async(user)
        elif operation_type == "get_all":
            await db.get_all_async()
        elif operation_type == "get_by_field":
            await db.get_by_field_async(id=user.id)
        elif operation_type == "update":
            await db.update_async(user.id, user)
        elif operation_type == "delete":
            await db.delete_async(user.id)
        elif operation_type == "count":
            await db.count_async()
        elif operation_type == "paginated":
            await db.get_paginated_async(limit=10, offset=0)

        return time.time() - start, None
    except Exception as e:
        return time.time() - start, f"{type(e).__name__}: {str(e)[:50]}"


def run_sync_stress_test(config: StressTestConfig) -> StressTestResult:
    """Run synchronous stress test with TRUE CONCURRENCY."""
    from concurrent.futures import ThreadPoolExecutor

    from wpostgresql import TableSync, WPostgreSQL

    print("\n[SYNC] Setting up test database...")

    sync = TableSync(UserModel, config.db_config)
    sync.drop_table()
    sync.create_if_not_exists()

    metrics = StressTestMetrics()
    operations = ["insert", "get_all", "get_by_field", "update", "count", "paginated"]

    def worker_task(args):
        """Each worker runs ONE operation concurrently."""
        user_id, req_id = args
        db = WPostgreSQL(UserModel, config.db_config)
        op = random.choice(operations)
        response_time, error = run_sync_operation(db, op, user_id, req_id)

        if error:
            metrics.record_failure(error)
        else:
            metrics.record_success(response_time)

    print(
        f"[SYNC] Starting CONCURRENT stress test: {config.num_users} users x {config.requests_per_user} requests = {config.num_users * config.requests_per_user} total ops..."
    )
    start_time = time.time()

    # Create ALL tasks at once for TRUE CONCURRENCY
    all_tasks = [
        (user_id, req_id)
        for user_id in range(config.num_users)
        for req_id in range(config.requests_per_user)
    ]

    # Execute ALL tasks concurrently
    with ThreadPoolExecutor(max_workers=config.num_users * 2) as executor:
        list(executor.map(worker_task, all_tasks))

    total_time = time.time() - start_time
    total_ops = config.num_users * config.requests_per_user

    return metrics.get_result(total_ops, total_time)


async def run_async_stress_test(config: StressTestConfig) -> StressTestResult:
    """Run asynchronous stress test with TRUE CONCURRENCY."""
    from wpostgresql import AsyncTableSync, WPostgreSQL

    print("\n[ASYNC] Setting up test database...")

    sync = AsyncTableSync(UserModel, config.db_config)
    await sync.drop_table_async()
    await sync.create_if_not_exists_async()

    metrics = StressTestMetrics()
    operations = ["insert", "get_all", "get_by_field", "update", "count", "paginated"]

    async def worker_task(user_id: int, req_id: int):
        """Each worker runs ONE operation concurrently."""
        db = WPostgreSQL(UserModel, config.db_config)
        op = random.choice(operations)
        response_time, error = await run_async_operation(db, op, user_id, req_id)

        if error:
            metrics.record_failure(error)
        else:
            metrics.record_success(response_time)

    print(
        f"[ASYNC] Starting CONCURRENT stress test: {config.num_users} users x {config.requests_per_user} requests = {config.num_users * config.requests_per_user} total ops..."
    )
    start_time = time.time()

    # Create ALL tasks at once for TRUE CONCURRENCY
    tasks = []
    for user_id in range(config.num_users):
        for req_id in range(config.requests_per_user):
            tasks.append(worker_task(user_id, req_id))

    # Execute ALL tasks concurrently
    await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time
    total_ops = config.num_users * config.requests_per_user

    return metrics.get_result(total_ops, total_time)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Stress test for wpostgresql")
    parser.add_argument("--users", type=int, default=1000, help="Number of concurrent users")
    parser.add_argument("--requests", type=int, default=100, help="Requests per user")
    parser.add_argument("--async", dest="use_async", action="store_true", help="Run async test")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--host", type=str, default=None, help="PostgreSQL host")
    parser.add_argument("--port", type=int, default=None, help="PostgreSQL port")

    args = parser.parse_args()

    config = StressTestConfig(
        num_users=args.users,
        requests_per_user=args.requests,
        use_async=args.use_async,
        verbose=args.verbose,
    )

    if args.host:
        config.db_config["host"] = args.host
    if args.port:
        config.db_config["port"] = args.port

    print("wpostgresql CONCURRENT Stress Test")
    print("Configuration:")
    print(f"  Concurrent users: {config.num_users}")
    print(f"  Requests per user: {config.requests_per_user}")
    print(f"  TOTAL operations: {config.num_users * config.requests_per_user:,}")
    print(
        f"  Database: {config.db_config['host']}:{config.db_config['port']}/{config.db_config['dbname']}"
    )
    print(
        f"  Mode: {'ASYNC (truly concurrent)' if config.use_async else 'SYNC (thread-based concurrent)'}"
    )

    if config.use_async:
        result = asyncio.run(run_async_stress_test(config))
    else:
        result = run_sync_stress_test(config)

    result.print_summary()

    if result.failed_operations / result.total_operations > 0.01:
        print("\nERROR: More than 1% of operations failed!")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
wpostgresql - Stress Test CLI

Usage:
    python run_stress.py --users 100 --requests 100
    python run_stress.py --users 1000 --requests 100 --async
    python run_stress.py --preset massive
"""

import argparse
import asyncio
import os
import random
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock

from pydantic import BaseModel


@dataclass
class StressConfig:
    num_users: int
    requests_per_user: int
    db_config: dict
    use_async: bool
    verbose: bool


class Account(BaseModel):
    id: int
    name: str
    email: str
    age: int
    balance: float
    status: str


class Account(BaseModel):
    id: int
    name: str
    email: str
    age: int
    balance: float
    status: str


class Metrics:
    def __init__(self):
        self.lock = Lock()
        self.times = []
        self.success = 0
        self.errors = []

    def ok(self, t):
        with self.lock:
            self.times.append(t)
            self.success += 1

    def fail(self, e):
        with self.lock:
            self.errors.append(e[:80])


def rand_user(uid, rid):
    return Account(
        id=uid * 10000 + rid,
        name="".join(random.choices(string.ascii_letters, k=8)),
        email=f"u{uid}_{rid}@test.com",
        age=random.randint(18, 70),
        balance=random.uniform(0, 5000),
        status=random.choice(["active", "pending", "inactive"]),
    )


def sync_op(db, op, uid, rid):
    t0 = time.time()
    try:
        u = rand_user(uid, rid)
        if op == 0:
            db.insert(u)
        elif op == 1:
            db.get_all()
        elif op == 2:
            db.get_by_field(id=u.id)
        elif op == 3:
            db.update(u.id, u)
        elif op == 4:
            db.delete(u.id)
        elif op == 5:
            db.count()
        elif op == 6:
            db.get_paginated(10, 0)
        return time.time() - t0, None
    except Exception as e:
        return time.time() - t0, str(e)[:50]


async def async_op(db, op, uid, rid):
    t0 = time.time()
    try:
        u = rand_user(uid, rid)
        if op == 0:
            await db.insert_async(u)
        elif op == 1:
            await db.get_all_async()
        elif op == 2:
            await db.get_by_field_async(id=u.id)
        elif op == 3:
            await db.update_async(u.id, u)
        elif op == 4:
            await db.delete_async(u.id)
        elif op == 5:
            await db.count_async()
        elif op == 6:
            await db.get_paginated_async(10, 0)
        return time.time() - t0, None
    except Exception as e:
        return time.time() - t0, str(e)[:50]


def run_sync(cfg: StressConfig):
    from wpostgresql import TableSync, WPostgreSQL

    sync = TableSync(Account, cfg.db_config)
    sync.drop_table()
    sync.create_if_not_exists()

    m = Metrics()

    def work(args):
        uid, rid = args
        db = WPostgreSQL(Account, cfg.db_config)
        t, e = sync_op(db, random.randint(0, 6), uid, rid)
        if e:
            m.fail(e)
        else:
            m.ok(t)

    tasks = [(u, r) for u in range(cfg.num_users) for r in range(cfg.requests_per_user)]

    print(f"[SYNC] {cfg.num_users} users x {cfg.requests_per_user} = {len(tasks)} ops")
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=cfg.num_users) as ex:
        list(ex.map(work, tasks))

    return m, time.time() - t0


async def run_async(cfg: StressConfig):
    from wpostgresql import AsyncTableSync, WPostgreSQL

    sync = AsyncTableSync(Account, cfg.db_config)
    await sync.drop_table_async()
    await sync.create_if_not_exists_async()

    m = Metrics()

    async def work(uid, rid):
        db = WPostgreSQL(Account, cfg.db_config)
        t, e = await async_op(db, random.randint(0, 6), uid, rid)
        if e:
            m.fail(e)
        else:
            m.ok(t)

    tasks = [(u, r) for u in range(cfg.num_users) for r in range(cfg.requests_per_user)]

    print(f"[ASYNC] {cfg.num_users} users x {cfg.requests_per_user} = {len(tasks)} ops")
    t0 = time.time()

    await asyncio.gather(*[work(u, r) for u, r in tasks], return_exceptions=True)

    return m, time.time() - t0


def print_results(m, elapsed, total):
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Total:     {total:,}")
    print(f"Success:   {m.success:,}")
    print(f"Failed:    {len(m.errors):,}")
    print(f"Time:      {elapsed:.2f}s")
    print(f"Ops/sec:   {total / elapsed:.1f}")

    if m.times:
        print(f"Avg:       {sum(m.times) / len(m.times) * 1000:.1f}ms")
        print(f"Min:       {min(m.times) * 1000:.1f}ms")
        print(f"Max:       {max(m.times) * 1000:.1f}ms")

    if m.errors:
        print(f"\nErrors ({len(m.errors)}):")
        for e, c in __import__("collections").Counter(m.errors).most_common(5):
            print(f"  [{c}x] {e}")
    print("=" * 50)


def main():
    p = argparse.ArgumentParser(description="wpostgresql stress test")
    p.add_argument("-u", "--users", type=int, default=100)
    p.add_argument("-r", "--requests", type=int, default=100)
    p.add_argument("--async", dest="use_async", action="store_true")
    p.add_argument("--host", default=os.getenv("POSTGRES_HOST", "localhost"))
    p.add_argument("--port", type=int, default=5432)
    p.add_argument("--db", default=os.getenv("POSTGRES_DB", "wpostgresql"))
    p.add_argument("--user", default=os.getenv("POSTGRES_USER", "postgres"))
    p.add_argument("--pass", dest="password", default=os.getenv("POSTGRES_PASSWORD", "postgres"))
    p.add_argument(
        "--preset", choices=["small", "medium", "large", "massive"], help="Preset configurations"
    )
    a = p.parse_args()

    presets = {
        "small": (10, 50),
        "medium": (100, 100),
        "large": (500, 100),
        "massive": (1000, 100),
    }

    if a.preset:
        a.users, a.requests = presets[a.preset]

    cfg = StressConfig(
        num_users=a.users,
        requests_per_user=a.requests,
        db_config={
            "host": a.host,
            "port": a.port,
            "dbname": a.db,
            "user": a.user,
            "password": a.password,
        },
        use_async=a.use_async,
        verbose=False,
    )

    print("\nwpostgresql Stress Test")
    print(
        f"Accounts: {a.users}, Requests: {a.requests}, Mode: {'ASYNC' if a.use_async else 'SYNC'}"
    )
    print(f"DB: {a.host}:{a.port}/{a.db}")

    if a.use_async:
        m, elapsed = asyncio.run(run_async(cfg))
    else:
        m, elapsed = run_sync(cfg)

    print_results(m, elapsed, a.users * a.requests)

    if len(m.errors) / (a.users * a.requests) > 0.01:
        sys.exit(1)


if __name__ == "__main__":
    main()

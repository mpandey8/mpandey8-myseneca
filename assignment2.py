#!/usr/bin/env python3

import argparse
import os
import sys

def percent_to_graph(percent: float, length: int = 20) -> str:
    hashe = int(percent * length)
    space = length - hashe
    return f"[{'#' * hashe}{' ' * space} | {int(percent * 100)}%]"

def get_sys_mem() -> int:
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemTotal:'):
                return int(line.split()[1])
    raise ValueError("Unable to find MemTotal in /proc/meminfo")

def get_avail_mem() -> int:
    with open('/proc/meminfo', 'r') as f:
        availableM = 0
        for line in f:
            if line.startswith('MemAvailable:'):
                return int(line.split()[1])
            elif line.startswith('MemFree:'):
                availableM += int(line.split()[1])
            elif line.startswith('Buffers:') or line.startswith('Cached:'):
                availableM += int(line.split()[1])
        return availableM

def parse_command_args():
    parser = argparse.ArgumentParser(description='Memory Visualiser -- See Memory Usage Report with bar charts')
    parser.add_argument('-H', '--human-readable', action='store_true', help='Prints sizes in human-readable format')
    parser.add_argument('-l', '--length', type=int, default=20, help='Specify the length of the graph. Default is 20.')
    parser.add_argument('program', nargs='?', help='If a program is specified, show memory use of all associated processes.')
    return parser.parse_args()

def pids_of_prog(program: str) -> list:
    try:
        pids = os.popen(f'pidof {program}').read().strip().split()
        return [int(pid) for pid in pids] if pids else []
    except Exception:
        return []

def rss_mem_of_pid(pid: int) -> int:
    totalRss = 0
    try:
        with open(f'/proc/{pid}/smaps', 'r') as f:
            for line in f:
                if line.startswith('Rss:'):
                    totalRss += int(line.split()[1])
    except FileNotFoundError:
        pass
    return totalRss

def human_readable(size: int) -> str:
    for unit in ['KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024:
            return f"{size} {unit}"
        size //= 1024
    return f"{size} TiB"

def main():
    args = parse_command_args()
    totalMem = get_sys_mem()
    availableMem = get_avail_mem()
    usedMem = totalMem - availableMem

    if args.program:
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"{args.program} not found.")
            return
        
        for pid in pids:
            memRss = rss_mem_of_pid(pid)
            if args.human_readable:
                strRss = human_readable(memRss)
                totalMemStr = human_readable(totalMem)
                print(f"{pid:<15} {percent_to_graph(memRss / totalMem, args.length)} {strRss}/{totalMemStr}")
            else:
                print(f"{pid:<15} {percent_to_graph(memRss / totalMem, args.length)} {memRss}/{totalMem}")
    else:
        if args.human_readable:
            usedStr = human_readable(usedMem)
            totalMemStr = human_readable(totalMem)
            print(f"Memory         {percent_to_graph(usedMem / totalMem, args.length)} {usedStr}/{totalMemStr}")
        else:
            print(f"Memory         {percent_to_graph(usedMem / totalMem, args.length)} {usedMem}/{totalMem}")

if __name__ == "__main__":
    main()
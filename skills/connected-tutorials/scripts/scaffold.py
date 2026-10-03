#!/usr/bin/env python3
"""Copy the approved tutorial starter into a new or empty output directory."""
import argparse
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    destination = args.destination.expanduser().resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        parser.error('Destination must be new or empty; existing work is never overwritten.')
    source = Path(__file__).resolve().parents[1] / 'assets' / 'template'
    destination.mkdir(parents=True, exist_ok=True)
    for filename in ('index.html', 'style.css', 'guide.js'):
        shutil.copy2(source / filename, destination / filename)
    print(f'Created tutorial starter: {destination}')
    print('Replace the OSI sample content and SVG when authoring a different topic.')


if __name__ == '__main__':
    main()

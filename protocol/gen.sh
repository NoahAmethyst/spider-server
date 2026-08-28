#!/usr/bin/env bash
set -eu

script_dir=$(cd "$(dirname "$0")" && pwd)
python_bin=${PYTHON_BIN:-python3}

"$python_bin" -m grpc_tools.protoc \
  -I"$script_dir" \
  --python_out="$script_dir/../pb/" \
  --pyi_out="$script_dir/../pb/" \
  --grpc_python_out="$script_dir/../pb/" \
  "$script_dir/spider.proto"
"$python_bin" -c 'from pathlib import Path; import sys; path = Path(sys.argv[1]); path.write_text(path.read_text().replace("import spider_pb2 as spider__pb2", "from pb import spider_pb2 as spider__pb2"))' "$script_dir/../pb/spider_pb2_grpc.py"

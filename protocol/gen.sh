#!/usr/bin/env bash
set -eu

script_dir=$(cd "$(dirname "$0")" && pwd)
python_bin=${PYTHON_BIN:-python3}

"$python_bin" -m grpc_tools.protoc \
  -I"$script_dir" \
  --python_out="$script_dir/../pb/" \
  --pyi_out="$script_dir/../pb/" \
  --grpc_python_out="$script_dir/../pb/" \
  "$script_dir/spider.proto" \
  "$script_dir/qqbot.proto"

for proto_path in "$script_dir"/*.proto; do
  module_name=$(basename "$proto_path" .proto)
  "$python_bin" -c 'from pathlib import Path; import sys; module = sys.argv[1]; path = Path(sys.argv[2]); path.write_text(path.read_text().replace(f"import {module}_pb2 as {module}__pb2", f"from pb import {module}_pb2 as {module}__pb2"))' "$module_name" "$script_dir/../pb/${module_name}_pb2_grpc.py"
done

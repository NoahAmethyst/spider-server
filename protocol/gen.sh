#!/usr/bin/env bash
set -eu

script_dir=$(cd "$(dirname "$0")" && pwd)
python_bin=${PYTHON_BIN:-python3}
proto_basenames=(spider qqbot)
proto_files=()

for proto_basename in "${proto_basenames[@]}"; do
  proto_files+=("$script_dir/$proto_basename.proto")
done

"$python_bin" -m grpc_tools.protoc \
  -I"$script_dir" \
  --python_out="$script_dir/../pb/" \
  --pyi_out="$script_dir/../pb/" \
  --grpc_python_out="$script_dir/../pb/" \
  "${proto_files[@]}"

for proto_basename in "${proto_basenames[@]}"; do
  "$python_bin" -c 'from pathlib import Path; import sys; module = sys.argv[1]; path = Path(sys.argv[2]); path.write_text(path.read_text().replace(f"import {module}_pb2 as {module}__pb2", f"from pb import {module}_pb2 as {module}__pb2"))' "$proto_basename" "$script_dir/../pb/${proto_basename}_pb2_grpc.py"
done

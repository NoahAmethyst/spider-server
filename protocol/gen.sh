#protoc -m grpc_tools.protoc -I../protocol --python_out=. --pyi_out=. --grpc_python_out=. ./protos/spider.proto
#protoc --python_out=../pb/ *.proto
python3 -m grpc_tools.protoc -I./ --python_out=../pb/ --pyi_out=../pb/ --grpc_python_out=../pb/ ./spider.proto
python3 -c 'from pathlib import Path; path = Path("../pb/spider_pb2_grpc.py"); path.write_text(path.read_text().replace("import spider_pb2 as spider__pb2", "from pb import spider_pb2 as spider__pb2"))'

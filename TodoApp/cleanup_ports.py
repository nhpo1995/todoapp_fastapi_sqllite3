import subprocess
import re
import time
import sys
from typing import List, Tuple


def get_processes_on_port(port: int) -> List[Tuple[int, str]]:
    """Lấy danh sách các process đang sử dụng port cụ thể"""
    try:
        # Sử dụng netstat để tìm process trên port
        result = subprocess.run(
            ["netstat", "-ano"], capture_output=True, text=True, shell=True
        )

        processes = []
        for line in result.stdout.split("\n"):
            if f":{port}" in line and "LISTENING" in line:
                # Parse dòng netstat để lấy PID
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    try:
                        pid_int = int(pid)
                        # Lấy tên process
                        process_name = get_process_name(pid_int)
                        processes.append((pid_int, process_name))
                    except ValueError:
                        continue

        return processes
    except Exception as e:
        print(f"Lỗi khi kiểm tra port {port}: {e}")
        return []


def get_process_name(pid: int) -> str:
    """Lấy tên của process từ PID"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
            capture_output=True,
            text=True,
            shell=True,
        )

        lines = result.stdout.split("\n")
        if len(lines) >= 2:
            # Parse CSV format để lấy tên process
            parts = lines[1].split(",")
            if len(parts) >= 2:
                return parts[1].strip('"')

        return f"PID {pid}"
    except:
        return f"PID {pid}"


def kill_process(pid: int) -> bool:
    """Kill process với PID cụ thể"""
    try:
        result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/F"],
            capture_output=True,
            text=True,
            shell=True,
        )

        if result.returncode == 0:
            return True
        else:
            print(f"Không thể kill process {pid}: {result.stderr}")
            return False
    except Exception as e:
        print(f"Lỗi khi kill process {pid}: {e}")
        return False


def cleanup_port(port: int, force: bool = False) -> bool:
    """Dọn dẹp port cụ thể"""
    print(f"\n🔍 Đang kiểm tra port {port}...")

    processes = get_processes_on_port(port)

    if not processes:
        print(f"✅ Port {port} không có process nào đang sử dụng")
        return True

    print(f"⚠️  Tìm thấy {len(processes)} process trên port {port}:")

    for pid, name in processes:
        print(f"   - PID {pid}: {name}")

    if not force:
        response = input(
            f"\n❓ Bạn có muốn kill tất cả process trên port {port}? (y/N): "
        )
        if response.lower() not in ["y", "yes"]:
            print("❌ Hủy bỏ")
            return False

    print(f"\n🗑️  Đang kill các process trên port {port}...")

    success_count = 0
    for pid, name in processes:
        if kill_process(pid):
            print(f"   ✅ Đã kill {name} (PID {pid})")
            success_count += 1
        else:
            print(f"   ❌ Không thể kill {name} (PID {pid})")

    if success_count == len(processes):
        print(f"✅ Đã dọn dẹp xong port {port}")
        return True
    else:
        print(f"⚠️  Chỉ dọn dẹp được {success_count}/{len(processes)} process")
        return False


def cleanup_common_ports():
    """Dọn dẹp các port thường dùng"""
    common_ports = [8000, 3000, 5000, 8080, 4000, 6000, 7000, 9000]

    print("🚀 Bắt đầu dọn dẹp các port thường dùng...")

    for port in common_ports:
        cleanup_port(port, force=False)
        time.sleep(1)  # Đợi một chút giữa các port


def main():
    """Hàm chính"""
    print("🧹 PORT CLEANUP SCRIPT")
    print("=" * 50)

    if len(sys.argv) > 1:
        # Nếu có argument, dọn dẹp port cụ thể
        try:
            port = int(sys.argv[1])
            cleanup_port(port, force=False)
        except ValueError:
            print("❌ Port phải là số nguyên")
            print("Cách sử dụng: python cleanup_ports.py [port_number]")
    else:
        # Nếu không có argument, dọn dẹp các port thường dùng
        cleanup_common_ports()

    print("\n🎉 Hoàn thành!")


if __name__ == "__main__":
    main()

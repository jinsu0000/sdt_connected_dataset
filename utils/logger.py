
import time
import os
import sys

""" prepare logdir for tensorboard and logging output"""
def set_log(output_dir, cfg_file, log_name):
    t = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    base_name = os.path.basename(cfg_file).split('.')[0]
    log_dir = os.path.join(output_dir, base_name, log_name + "-" + t)
    logs = {}
    for temp in ['tboard', 'model', 'sample']:
        temp_dir = os.path.join(log_dir, temp)
        os.makedirs(temp_dir, exist_ok=True)
        logs[temp] = temp_dir
    return logs


_print_once_seen = set()

def print_once(*args, **kwargs):
    msg = " ".join(map(str, args))
    if msg not in _print_once_seen:
        _print_once_seen.add(msg)
        print(*args, **kwargs)
        sys.stdout.flush()  # 강제 flush


def log_stats(name, tensor):
    # tensor: [seq_len, batch_size, dim]
    mean_val = tensor.mean().item()
    var_val = tensor.var().item()
    print(f"{name} → mean: {mean_val:.4f}, var: {var_val:.4f}")
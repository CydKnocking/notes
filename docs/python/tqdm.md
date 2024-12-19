## 多线程/多进程 thread_map()/process_map()

可以使用tqdm监控多线程/进程任务进度。

用多进程process_map：
```
from time import sleep
from tqdm.contrib.concurrent import process_map

def worker(i, j):
    # 执行任务的函数
    if i == 0:
        sleep(5)
    else:
        sleep(0.1)
    return i

results = process_map(worker, zip(range(10), range(10)), total=10, max_workers=4)
```

其中`process_map(fn, *iterables, total : int, max_workers : int)`返回一个list，`fn`是需要被多线程处理的函数，`*iterables`是fn的参数打包后的迭代器，`total`指示一共有多少个任务，`max_workers`指示有多少个worker。

多线程`thread_map()`的用法和`process_map()`一样。

以下是它们的主要区别：

---

### 1. **并发模式**
- **`thread_map()`**  
  使用多线程（`ThreadPoolExecutor`）。适合 **I/O 密集型任务**，如文件读取/写入、网络请求等。
  
- **`process_map()`**  
  使用多进程（`ProcessPoolExecutor`）。适合 **CPU 密集型任务**，如计算密集型操作。

---

### 2. **性能特点**
- **`thread_map()`**  
  - 由于 Python 的全局解释器锁（GIL），多线程在执行纯 Python 代码的计算密集型任务时通常无法显著提升性能。  
  - 在 I/O 密集型任务中表现良好，因为线程可以在等待 I/O 时切换。

- **`process_map()`**  
  - 每个进程都有独立的 Python 解释器和 GIL，因此适合多核处理，能够显著提升 CPU 密集型任务的性能。  
  - 进程间通信的开销较大，启动新进程也更耗时，因此对小规模任务性能提升有限。

---

### 3. **适用场景**
- **`thread_map()`**
  - 网络爬虫：大量网络请求或网页下载。
  - 文件操作：并行读取/写入多个文件。
  - 数据库操作：并发数据库查询。

- **`process_map()`**
  - 数据处理：图像处理、大量矩阵计算。
  - 科学计算：数值分析、训练小规模模型。
  - 大规模数据转换：如解析 JSON 数据并计算统计信息。

---

### 4. **接口用法**
两者的使用方法相同，主要参数包括：
- `fn`：要并发执行的函数。
- `iterable`：输入数据的可迭代对象。
- `max_workers`：最大并发数（线程或进程）。
- `chunksize`：每个任务分块的大小（仅适用于 `process_map`）。

#### 示例代码

```python
from tqdm.contrib.concurrent import thread_map, process_map

# 示例函数
def compute(x):
    return x * x

data = list(range(10))

# 使用线程
results_thread = thread_map(compute, data, max_workers=4)
print("Thread results:", results_thread)

# 使用进程
results_process = process_map(compute, data, max_workers=4)
print("Process results:", results_process)
```

---

### 5. **注意事项**
- **`thread_map()`**：  
  - 适合任务开销较小的情况，避免频繁切换线程的额外开销。  
  - 在 I/O 密集型任务中提升显著，但不适合大量计算。

- **`process_map()`**：  
  - 进程间通信和进程启动的开销较大，适合较大的任务分块。  
  - 需要确保函数是可序列化的（如不能使用局部函数或 Lambda）。

---

根据任务性质选择适合的工具，可以有效提升程序性能。
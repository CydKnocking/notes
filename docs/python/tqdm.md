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

## `tqdm()`进度条设置

多层嵌套的进度条：
```
def test_tqdm():
    for i in tqdm(range(10), desc='outer loop'):
        for j in tqdm(range(10), desc='inner loop', leave=False):
            time.sleep(1)
```
其中设置`leave=False`可以使得内部进度条结束后不占用行，外层进度条不会跳行显示。还可以用`position: int`参数，详见下面参数解释。

设置进度条长度：`ncols: int`参数。

以下是完整的参数介绍。

### `tqdm()` 函数签名：
```python
tqdm(iterable=None, desc=None, total=None, ncols=None, miniters=1, maxinterval=10.0,
      mininterval=0.1, unit='it', unit_scale=False, dynamic_ncols=False, smoothing=0.3,
      bar_format=None, initial=0, position=None, delay=0.0, gui=False, disable=False,
      leave=True, file=None, position=None, colour=None, backend=None, **kwargs)
```

### 参数详细说明：

1. **`iterable`** (默认值 `None`)：
   - 你需要传入一个可迭代对象（如 `list`、`range`、`iter` 等）。`tqdm` 会包装这个对象并且监控进度。
   - 如果不传入可迭代对象，你也可以手动更新进度条（如使用 `tqdm.update()`）。

2. **`desc`** (默认值 `None`)：
   - 在进度条前显示的描述文本，帮助你更清晰地理解当前任务。
   - 例如：`tqdm(range(100), desc="Processing files")` 会显示 `Processing files:  50%|███████████████| 50/100`.

3. **`total`** (默认值 `None`)：
   - 总任务数。对于已知总数的任务，指定 `total` 是必须的。如果没有 `total`，`tqdm` 会动态计算任务进度（通过 `iterable`）。
   - 如果你手动更新进度条，指定 `total` 可以确保进度条能正确显示。

4. **`ncols`** (默认值 `None`)：
   - 进度条的宽度。默认值为 `None`，`tqdm` 会根据终端宽度自动调整进度条宽度。如果你想指定进度条的长度，可以设置为一个整数。
   - 例如：`ncols=100` 会设置进度条为 100 个字符宽。

5. **`miniters`** (默认值 `1`)：
   - 更新进度条的最小迭代次数。如果你不希望进度条每次迭代都更新，可以增大此值。例如，`miniters=10` 会每 10 次迭代更新一次进度条。

6. **`maxinterval`** (默认值 `10.0`)：
   - 更新进度条的最大时间间隔。如果进度更新间隔时间超过此值，进度条就会强制更新，即使迭代没有达到 `miniters` 的次数。

7. **`mininterval`** (默认值 `0.1`)：
   - 进度条更新的最小时间间隔。如果进度更新间隔小于此值，`tqdm` 会跳过更新，减少显示频率。
   
8. **`unit`** (默认值 `'it'`)：
   - 用于描述进度条单位的字符串，通常为 "it"（items）或 "s"（seconds）。例如，如果你的任务是处理文件，可以设置 `unit='file'`。

9. **`unit_scale`** (默认值 `False`)：
   - 如果设置为 `True`，则 `unit` 会被缩放。例如，如果任务是字节，设置为 `unit_scale=True` 后，进度条将显示为 "KB"、"MB" 等。

10. **`dynamic_ncols`** (默认值 `False`)：
    - 是否动态调整进度条的宽度。`True` 时，进度条的宽度会根据终端大小动态调整；`False` 时，宽度保持固定。

11. **`smoothing`** (默认值 `0.3`)：
    - 平滑因子，用于平滑进度条的更新。默认值为 `0.3`，即进度更新是基于过去的更新情况平滑的。如果设置为 `0`，则更新是直接的。

12. **`bar_format`** (默认值 `None`)：
    - 用于自定义进度条的格式。你可以使用一系列占位符来定制进度条的显示样式。常用占位符包括：
        - `{l_bar}`：左侧描述部分
        - `{n}/{total}`：当前进度和总进度
        - `{percent}`：百分比
        - `{bar}`：进度条的可视部分
    - 例如：`bar_format="{l_bar}{bar} | {percent}"` 会显示进度条和百分比。

13. **`initial`** (默认值 `0`)：
    - 设置进度条的初始值。适用于部分任务已经完成的情况。例如，如果你希望进度条从 50% 开始，你可以设置 `initial=50`。

14. **`position`** (默认值 `None`)：
    - 设置进度条的显示位置。当多个进度条在同一终端上显示时，你可以通过此参数控制它们的位置。

15. **`delay`** (默认值 `0.0`)：
    - 延迟显示进度条的时间，单位为秒。如果你希望在程序启动后等一段时间才显示进度条，可以设置该参数。

16. **`gui`** (默认值 `False`)：
    - 是否使用 GUI 模式（如 Jupyter Notebook），默认禁用。如果设置为 `True`，在 Jupyter 中会使用不同的显示方式。

17. **`disable`** (默认值 `False`)：
    - 如果设置为 `True`，进度条不会显示。常用于调试或禁用进度条。

18. **`leave`** (默认值 `True`)：
    - 是否在任务完成后保留进度条。如果为 `False`，进度条在任务完成后会消失。

19. **`file`** (默认值 `None`)：
    - 将进度条输出到指定的文件。如果指定了文件对象（如 `sys.stdout` 或文件句柄），进度条会输出到该文件。

20. **`colour`** (默认值 `None`)：
    - 设置进度条的颜色，支持的颜色包括 `red`、`green`、`blue` 等。

21. **`backend`** (默认值 `None`)：
    - 控制进度条的实现方式。可选值为 `tqdm` 或 `asyncio`，如果你正在使用异步任务，可以选择 `asyncio` 作为后端。

---

### `tqdm()` 使用示例

#### 自定义进度条格式：
```python
from tqdm import tqdm
import time

for i in tqdm(range(10), bar_format="{l_bar}{bar}|{n}/{total} [{elapsed}]"):
    time.sleep(0.1)
```
- `bar_format` 允许你自定义进度条的显示格式。在这个例子中，我们只显示进度条、当前进度、总进度和已用时间。

#### 使用 `position` 显示多个进度条：
```python
from tqdm import tqdm
import time

# 第一个进度条
for i in tqdm(range(10), desc="Task 1", position=0):
    time.sleep(0.1)

# 第二个进度条
for i in tqdm(range(10), desc="Task 2", position=1):
    time.sleep(0.1)
```
- `position` 参数让你在同一终端中显示多个进度条。

#### 设置进度条的初始值：
```python
from tqdm import tqdm
import time

# 设置初始值为 5
for i in tqdm(range(5, 15), desc="Processing", initial=5):
    time.sleep(0.1)
```
- `initial=5` 表示进度条从 5 开始，显示已完成 5 次。

---

### 总结：
- `tqdm()` 是一个非常灵活的进度条工具，适用于命令行和 Jupyter 环境。
- 你可以通过多种参数来定制进度条的显示样式、宽度、颜色等，同时支持实时更新和多线程/多进程
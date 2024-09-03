## Set proxy for `torch.hub.load(...)`

```
import os
import torch
os.environ['HTTPS_PROXY'] = '127.0.0.1:7890'   # Add this line

model = torch.hub.load(...)
```

or replace command line with `HTTPS_PROXY=127.0.0.1:7890 python ...`.

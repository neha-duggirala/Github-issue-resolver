import os
if "MODEL" in os.environ:
    model = os.environ("MODEL")
    print(model)
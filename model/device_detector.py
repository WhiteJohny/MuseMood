from torch import accelerator

DEVICE = accelerator.current_accelerator().type if accelerator.is_available() else "cpu"

print(f"Using {DEVICE} device")

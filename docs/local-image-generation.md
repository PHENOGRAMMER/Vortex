# Local image generation on this PC

This PC has an NVIDIA GTX 1650 with 4 GB VRAM. Use ComfyUI with a lightweight Stable Diffusion 1.5 checkpoint; NVIDIA NIM FLUX/SD 3.5 containers need significantly more GPU memory.

1. Install ComfyUI for Windows from its official desktop release, or clone it with Git and follow its Windows/NVIDIA setup guide.
2. Put `v1-5-pruned-emaonly-fp16.safetensors` in `C:\Users\cools\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\checkpoints\` for the installed Comfy Desktop app. This is the shared model directory configured by Comfy Desktop on this PC.
3. Start ComfyUI with `--lowvram` so it listens at `http://127.0.0.1:8188`.
4. In OmniGen choose **Local GPU - Stable Diffusion** and send an image prompt.

To use a different checkpoint, set `COMFYUI_CHECKPOINT` in `backend/.env` to the checkpoint filename and restart the backend.

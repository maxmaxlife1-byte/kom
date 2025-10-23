import os, time, requests
from typing import Any, Dict

FAL_KEY = os.environ.get("FAL_KEY")  # set in RunPod env vars

# fal Seedream v4 text-to-image endpoint ID (public on fal)
FAL_SUBMIT_URL = "https://fal.run/fal-ai/bytedance/seedream/v4/text-to-image"
# Alternative queue submit endpoint (older style) also exists in docs; this simple endpoint handles the job.

def call_seedream(prompt: str, width: int=1024, height: int=1024, seed: int=None, image_url: str=None):
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    payload = {
        "input": {
            "prompt": prompt,
            "width": width,
            "height": height
        }
    }
    if seed is not None:
        payload["input"]["seed"] = seed
    if image_url:
        # if you want img2img via v4 edit endpoint, you’d switch endpoint + include reference
        pass

    # submit and wait (fal handles long-poll under this endpoint)
    r = requests.post(FAL_SUBMIT_URL, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()
    # expected: { "images": [ { "url": "..." } ], ... } or { "image": { "url": "..." } }
    # normalize
    url = None
    if "images" in data and data["images"]:
        url = data["images"][0].get("url")
    elif "image" in data and isinstance(data["image"], dict):
        url = data["image"].get("url")
    else:
        url = data.get("image_url")

    if not url:
        raise RuntimeError(f"Seedream response missing URL: {data}")
    return url, data

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """RunPod entrypoint: event['input'] carries the user payload."""
    inp = event.get("input", {})
    prompt = inp.get("prompt")
    if not prompt:
        return {"error": "missing prompt"}

    width = int(inp.get("width", 1024))
    height = int(inp.get("height", 1024))
    seed = inp.get("seed")
    image_url = inp.get("image_url")

    url, raw = call_seedream(prompt, width=width, height=height, seed=seed, image_url=image_url)

    # (optional) download, but returning the URL is usually enough for Telegram
    return {
        "image_url": url,
        "meta": {
            "width": width,
            "height": height,
            "seed": seed,
        }
    }
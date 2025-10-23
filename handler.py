import os
import requests
from typing import Any, Dict

# fal Seedream v4 text-to-image endpoint ID (public on fal)
FAL_SUBMIT_URL = "https://fal.run/fal-ai/bytedance/seedream/v4/text-to-image"

def call_seedream(prompt: str, width: int=1024, height: int=1024, seed: int=None, image_url: str=None):
    """Calls the fal.ai API to generate an image."""
    
    # Get the API key from environment variables INSIDE the function
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        # If the key is missing, raise an error immediately. This will show in the logs.
        raise ValueError("FAL_KEY environment variable not found.")

    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    payload = {"input": {"prompt": prompt, "width": width, "height": height}}
    
    if seed is not None:
        payload["input"]["seed"] = seed
    
    # This function doesn't handle image_url, so we can ignore it for now.
    # if image_url:
    #     pass

    print("Submitting request to fal.ai...")
    r = requests.post(FAL_SUBMIT_URL, headers=headers, json=payload, timeout=90)
    
    # This will raise a detailed error if the request fails (e.g., 401 Unauthorized)
    r.raise_for_status()
    
    data = r.json()
    print("Received response from fal.ai.")

    # Extract the image URL from the response
    url = data.get("images", [{}])[0].get("url")
    if not url:
        raise RuntimeError(f"Seedream response is missing the image URL. Full response: {data}")
    
    return url, data

def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """RunPod entrypoint: event['input'] carries the user payload."""
    
    print(f"Handler received event: {event}")
    inp = event.get("input", {})
    prompt = inp.get("prompt")
    
    if not prompt:
        return {"error": "missing prompt"}

    try:
        width = int(inp.get("width", 1024))
        height = int(inp.get("height", 1024))
        seed = inp.get("seed")
        image_url = inp.get("image_url")

        url, raw_response = call_seedream(
            prompt, width=width, height=height, seed=seed, image_url=image_url
        )

        # Return a successful response
        return {
            "image_url": url,
            "meta": {"width": width, "height": height, "seed": seed},
        }
    except Exception as e:
        # If any error occurs during the process, log it and return an error message.
        print(f"An error occurred: {e}")
        return {"error": str(e)}
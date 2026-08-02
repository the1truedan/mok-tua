"""Build API-format Qwen Image Edit graph with multi-angle + next-scene LoRAs."""

from __future__ import annotations

from typing import Any


def build_qwen_edit_storyboard_graph(
    prompt: str,
    *,
    negative: str = "blurry, low quality, watermark, text, deformed",
    seed: int = 42,
    steps: int = 8,
    cfg: float = 1.0,
    width: int = 768,
    height: int = 768,
    filename_prefix: str = "mok_tua_qwen",
    unet_name: str = "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
    clip_name: str = "qwen_2.5_vl_7b_fp8_scaled.safetensors",
    vae_name: str = "qwen_image_vae.safetensors",
    lora_multi_angles: str = "Qwen-Edit-2509-Multiple-angles.safetensors",
    lora_next_scene: str = "next-scene_lora-v2-3000.safetensors",
    lora_lightning: str = "Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
    multi_angles_strength: float = 1.0,
    next_scene_strength: float = 0.75,
    lightning_strength: float = 1.0,
    use_lightning: bool = True,
    denoise: float = 1.0,
    sampler_name: str = "euler",
    scheduler: str = "simple",
) -> dict[str, Any]:
    """
    Headless API graph for Qwen Image Edit + storyboard LoRAs.

    Text-only first panel (no LoadImage): EmptyLatentImage + TextEncodeQwenImageEditPlus
    without image refs. For continue_from / I2I, inject LoadImage separately via
    inject_ref_image().
    """
    graph: dict[str, Any] = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {"unet_name": unet_name, "weight_dtype": "default"},
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": clip_name, "type": "qwen_image"},
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": vae_name},
        },
        # lightning optional chain start
        "10": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "lora_name": lora_lightning if use_lightning else lora_multi_angles,
                "strength_model": lightning_strength if use_lightning else multi_angles_strength,
                "model": ["1", 0],
            },
        },
        "11": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "lora_name": lora_multi_angles,
                "strength_model": multi_angles_strength,
                "model": ["10", 0],
            },
        },
        "12": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "lora_name": lora_next_scene,
                "strength_model": next_scene_strength,
                "model": ["11", 0],
            },
        },
        "20": {
            "class_type": "ModelSamplingAuraFlow",
            "inputs": {"shift": 3.0, "model": ["12", 0]},
        },
        "30": {
            "class_type": "TextEncodeQwenImageEditPlus",
            "inputs": {
                "prompt": prompt,
                "clip": ["2", 0],
                "vae": ["3", 0],
            },
        },
        "31": {
            "class_type": "TextEncodeQwenImageEditPlus",
            "inputs": {
                "prompt": negative,
                "clip": ["2", 0],
                "vae": ["3", 0],
            },
        },
        "40": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "50": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "denoise": denoise,
                "model": ["20", 0],
                "positive": ["30", 0],
                "negative": ["31", 0],
                "latent_image": ["40", 0],
            },
        },
        "60": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["50", 0], "vae": ["3", 0]},
        },
        "70": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": filename_prefix, "images": ["60", 0]},
        },
    }
    if not use_lightning:
        # rewire: 10 = multi, 11 = next, 12 unused → point 20 at 11
        graph["10"]["inputs"]["lora_name"] = lora_multi_angles
        graph["10"]["inputs"]["strength_model"] = multi_angles_strength
        graph["11"]["inputs"]["lora_name"] = lora_next_scene
        graph["11"]["inputs"]["strength_model"] = next_scene_strength
        graph["11"]["inputs"]["model"] = ["10", 0]
        graph["20"]["inputs"]["model"] = ["11", 0]
        del graph["12"]
    return graph


def qwen_graph_meta() -> dict[str, Any]:
    return {
        "title": "mok-tua Qwen Edit multi-angle + next-scene",
        "status": "api_ready",
        "builder": "qwen_graph.build_qwen_edit_storyboard_graph",
        "requires": [
            "diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors",
            "text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
            "vae/qwen_image_vae.safetensors",
            "loras/Qwen-Edit-2509-Multiple-angles.safetensors",
            "loras/next-scene_lora-v2-3000.safetensors",
            "loras/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
        ],
        "prompt_node": "30",
        "seed_node": "50",
    }

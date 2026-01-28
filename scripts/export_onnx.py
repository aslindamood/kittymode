"""Export sentence-transformers model to ONNX format for smaller, faster inference."""

import shutil
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer


def export_model():
    """Export all-MiniLM-L6-v2 to ONNX format."""
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    output_dir = Path(__file__).parent.parent / "models" / "onnx"
    
    print(f"Exporting {model_name} to ONNX...")
    print(f"Output directory: {output_dir}")
    
    # Clean output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load model and tokenizer
    print("Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    
    # Save tokenizer
    print("Saving tokenizer...")
    tokenizer.save_pretrained(output_dir)
    
    # Create dummy inputs for export
    dummy_text = "hello world"
    inputs = tokenizer(dummy_text, return_tensors="pt", padding=True, truncation=True)
    
    # Export to ONNX
    onnx_path = output_dir / "model.onnx"
    print(f"Exporting ONNX model to {onnx_path}...")
    
    torch.onnx.export(
        model,
        (inputs["input_ids"], inputs["attention_mask"]),
        str(onnx_path),
        input_names=["input_ids", "attention_mask"],
        output_names=["last_hidden_state"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence"},
            "attention_mask": {0: "batch_size", 1: "sequence"},
            "last_hidden_state": {0: "batch_size", 1: "sequence"},
        },
        opset_version=14,
        do_constant_folding=True,
    )
    
    print(f"\n✓ Model exported to {output_dir}")
    
    # Print size
    onnx_size = sum(f.stat().st_size for f in output_dir.rglob("*") if f.is_file())
    print(f"  ONNX model size: {onnx_size / 1024 / 1024:.1f} MB")
    
    # Test the exported model
    print("\nTesting exported model...")
    test_inference(output_dir)


def test_inference(model_dir: Path):
    """Test that the ONNX model works correctly."""
    import onnxruntime as ort
    from transformers import AutoTokenizer
    
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    
    onnx_path = model_dir / "model.onnx"
    session = ort.InferenceSession(str(onnx_path), providers=['CPUExecutionProvider'])
    
    test_texts = ["meow", "hello world", "asdjfkl"]
    
    for text in test_texts:
        inputs = tokenizer(text, return_tensors="np", padding=True, truncation=True)
        
        outputs = session.run(
            None,
            {
                "input_ids": inputs["input_ids"],
                "attention_mask": inputs["attention_mask"],
            }
        )
        
        # Mean pooling
        embeddings = outputs[0]
        attention_mask = inputs["attention_mask"]
        mask_expanded = np.expand_dims(attention_mask, -1)
        sum_embeddings = np.sum(embeddings * mask_expanded, axis=1)
        sum_mask = np.sum(mask_expanded, axis=1)
        pooled = sum_embeddings / sum_mask
        
        print(f"  '{text}' -> embedding shape: {pooled.shape}, norm: {np.linalg.norm(pooled):.4f}")
    
    print("\n✓ ONNX model test passed!")


if __name__ == "__main__":
    export_model()

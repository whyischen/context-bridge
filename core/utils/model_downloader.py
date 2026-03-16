import os
import tarfile
import urllib.request
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from core.i18n import t

console = Console(stderr=True)

def ensure_chroma_model():
    """
    Ensure the default ChromaDB model (all-MiniLM-L6-v2) is downloaded and extracted.
    This prevents ChromaDB from silently failing or showing ugly logs during initialization.
    """
    model_name = "all-MiniLM-L6-v2"
    cache_dir = Path.home() / ".cache" / "chroma" / "onnx_models" / model_name
    tar_path = cache_dir / "onnx.tar.gz"
    
    # Check if already extracted (ChromaDB looks for the model.onnx file)
    if (cache_dir / "model.onnx").exists():
        return

    console.print(t("mdl_first_run", model_name=model_name))
    console.print(t("mdl_desc"))
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    url = f"https://chroma-onnx-models.s3.amazonaws.com/{model_name}/onnx.tar.gz"
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(t("mdl_downloading"), total=None)
            
            def report_hook(count, block_size, total_size):
                if progress.tasks[task].total is None and total_size > 0:
                    progress.update(task, total=total_size)
                progress.update(task, advance=block_size)
                
            urllib.request.urlretrieve(url, tar_path, reporthook=report_hook)
            
        console.print(t("mdl_extracting"))
        
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=cache_dir)
            
        console.print(t("mdl_ready"))
        
    except Exception as e:
        console.print(t("mdl_failed", error=str(e)))
        console.print(t("mdl_hint"))
        console.print(t("mdl_manual", cache_dir=str(cache_dir)))
        console.print(f"[underline cyan]{url}[/underline cyan]\n")
        # Don't raise, let ChromaDB try its own fallback or fail naturally

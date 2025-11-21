import logfire
from loguru import logger
import sys

def setup_logging(
    project_name: str = "LFMSystem", 
    use_cloud: bool = True, 
    verbose: bool = True
):
    """
    Configures logging with a toggle for console verbosity.
    """
    # --- 1. Configure Loguru (Text Logs) ---
    logger.remove()
    
    if verbose:
        logger.add(
            sys.stderr, 
            format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>", 
            level="INFO"
        )
    else:
        logger.add(
            sys.stderr, 
            format="<red>{time:HH:mm:ss} | {level} | {message}</red>", 
            level="ERROR"
        )

    # --- 2. Configure Logfire (Spans & Traces) ---
    
    # FIX: We use a dictionary instead of 'True' to prevent the AttributeError.
    # If verbose=True, we pass explicit settings.
    # If verbose=False, we pass False.
    console_settings = {"min_log_level": "info"} if verbose else False

    logfire.configure(
        send_to_logfire=use_cloud,
        console=console_settings
    )
    
    logfire.instrument_pydantic()
    
    # Status Output
    mode_cloud = "Cloud ☁️" if use_cloud else "Offline 🚫"
    mode_verb = "Verbose 🔊" if verbose else "Quiet 🔇"
    
    # We use sys.stderr.write to ensure it prints even if logger is restricted
    print(f"[{project_name}] Logging: {mode_cloud} | Console: {mode_verb}")
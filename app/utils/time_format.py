def format_duration(ms: int) -> str:
    seconds = ms // 1000
    minutes = seconds // 60
    hours = minutes // 60
    if hours:
        return f"{hours}:{minutes % 60:02}:{seconds % 60:02}"
    else:
        return f"{minutes}:{seconds % 60:02}"
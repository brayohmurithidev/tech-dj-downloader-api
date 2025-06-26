from collections import defaultdict

download_progress = defaultdict(dict)

def make_progress_hook(video_id: str):
    def hook(d):
        if d['status'] == 'downloading':
            download_progress[video_id]['progress'] = d.get('_percent_str', '').strip()
            download_progress[video_id]['eta'] = d.get('eta')
        elif d['status'] == 'finished':
            download_progress[video_id]['progress'] = '100%'
            download_progress[video_id]['eta'] = 0
            download_progress[video_id]['done'] = True
        elif d['status'] == 'error':
            download_progress[video_id]['error'] = 'Download failed'
    return hook
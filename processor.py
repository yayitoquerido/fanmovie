import subprocess
import random
from pathlib import Path

def get_video_duration(file_path):
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration: {e}")
        return 0.0

def process_video(input_path, output_dir):
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    duration = get_video_duration(input_path)
    
    cortes_a_hacer = []
    if duration >= 3.0:
        cortes_a_hacer.extend([(duration * 0.25) - 0.5, (duration * 0.50) - 0.5, (duration * 0.75) - 0.5])
    elif duration >= 2.0:
        cortes_a_hacer.extend([(duration * 0.33) - 0.5, (duration * 0.66) - 0.5])
    elif duration >= 1.0:
        cortes_a_hacer.append((duration * 0.5) - 0.5)
    else:
        cortes_a_hacer.append(0.0)

    resultados_exitosos = []
    
    for i, start_time in enumerate(cortes_a_hacer):
        base_name = input_path.name.rsplit('.', 1)[0]
        zoom_type = "in" if i % 2 == 0 else "out"
        output_filename = f"cut_{zoom_type}_{i+1}_{base_name}.mp4"
        output_path = output_dir / output_filename
        
        start_time = max(0.0, start_time)

        if zoom_type == "in":
            zoom_cmd = "zoompan=z='min(1.05, 1.0+0.05*(on/30))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30"
        else:
            zoom_cmd = "zoompan=z='max(1.0, 1.05-0.05*(on/30))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30"

        color_filter = "eq=contrast=1.08:saturation=0.9:brightness=0.0,colorbalance=rs=-0.04:gs=-0.02:bs=0.06,vignette=angle=0.3"
        grain_filter = "noise=alls=8:allf=t+u"
        video_filters = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{color_filter},{zoom_cmd},{grain_filter},format=yuv420p"

        cmd = [
            "ffmpeg", "-y", "-ss", str(start_time), "-i", str(input_path),
            "-t", "1.0", "-vf", video_filters, "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-r", "30", str(output_path)
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=15)
            resultados_exitosos.append(output_filename)
        except Exception as e:
            print(f"Error processing cut: {e}")
            
    return resultados_exitosos

def generate_lost_tape(processed_dir, output_path, ig_user):
    processed_dir = Path(processed_dir)
    all_cuts = list(processed_dir.glob("cut_*.mp4"))
    
    if len(all_cuts) < 2:
        return None
        
    random.shuffle(all_cuts)
    list_file = processed_dir / "lost_tape_list.txt"
    
    with open(list_file, "w", encoding="utf-8") as f:
        for clip in all_cuts[:6]:
            f.write(f"file '{clip.resolve()}'\n")
            
    vf_chain = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,noise=alls=12:allf=t+u,drawtext=text='POV: {ig_user}':fontcolor=white:fontsize=50:x=60:y=h-th-80:shadowcolor=black:shadowx=2:shadowy=2"
    
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-vf", vf_chain,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-r", "30", "-an",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=30)
        if list_file.exists(): list_file.unlink()
        return output_path
    except Exception as e:
        print(f"Error generating Lost-Tape: {e}")
        if list_file.exists(): list_file.unlink()
        return None

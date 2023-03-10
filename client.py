import itertools
from torch import multiprocessing
import os
import shutil
import sys
import tarfile
import uuid

import aeneas.executetask
import aeneas.task
import ffmpeg
import nltk.tokenize
import requests
import torch
from aeneas.syncmap import SyncMapFragment
from pqdm.processes import pqdm
from pytube import YouTube
from tqdm import tqdm

import whisper


def align(file, text):
    # create a task object
    config_string = u"task_language=en|is_text_type=plain|os_task_file_format=json"
    t = aeneas.task.Task(config_string=config_string)
    t.audio_file_path_absolute = file
    t.text_file_path_absolute = text
    aeneas.executetask.ExecuteTask(t).execute()
    for segment in t.sync_map_leaves(SyncMapFragment.REGULAR):
        yield segment.begin, segment.end


def ingest(model, td, url):
    # download the video
    yt = YouTube(url.strip())

    print("downloading %s" % yt.video_id)
    # pick the audio stream
    stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    # download the audio
    if stream is None:
        return
    webmfile = stream.download()
    result = model.transcribe(webmfile, language="en")
    lines = nltk.tokenize.sent_tokenize(result["text"])
    tsfile = webmfile + '.transcript.txt'

    dir = td + "/yt-%s" % yt.video_id
    os.makedirs(dir)

    with open(tsfile, 'w') as f:
        f.write('\n'.join(lines))
    
    for i, (begin, end) in enumerate(align(webmfile, tsfile)):
        if i == 0:
            # ignore the first segment because it often contains an intro or something.
            continue
        key = td + "/yt-%s/%04d" % (yt.video_id, i)
        if end - begin < 3:
            # ignore segments less than 3 seconds because they are too noisy.
            continue
        try:
            ffmpeg.input(webmfile, ss=begin, to=end).output(key + ".wav").run(overwrite_output=True, quiet=True)
            with open(key + ".txt", "w") as f:
                f.write(lines[i])
        except:
            pass
    
    os.remove(webmfile)
    os.remove(tsfile)

def run(i, host):
    nltk.download('punkt') # download nltk tokenizer
    model = whisper.load_model('small.en', device="cuda:%d" % (i % torch.cuda.device_count()), in_memory=True)
    while True:
        td = uuid.uuid4().hex
        req = requests.get(host)
        if req.status_code != 200:
            # exiting
            return
        if req.text == "":
            continue # no work
        ingest(model, td, req.text)

        # tgz the data directory
        print("compressing data")
        with tarfile.open("%s.tar.gz" % td, "w:gz", compresslevel=3) as tar:
            tar.add(td, arcname=os.path.basename("data"))
        # delete the data directory
        print("deleting data")
        shutil.rmtree(td)
        # post the tgz file to the server
        print("posting data")
        with open("%s.tar.gz" % td, "rb") as f:
            requests.post(host, data=f)
        # delete the tgz file
        print("deleting tgz")
        os.remove("%s.tar.gz" % td)


def main():
    run(0, sys.argv[1])
    

if __name__ == "__main__":
    main()
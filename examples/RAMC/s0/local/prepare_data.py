import os
import sys
sys.path.append('./')
from tqdm import tqdm
import yaml
import librosa
import ttsfrd
from spokentts.frd.utils import g2p_madarin
from scipy.io import wavfile
import numpy as np

def prepare_data(config):
    data_path = config['data_path']
    save_path = config['save_path']
    fs = config['fs']
    max_value = config['max_value']
    ttsfrd_model = config['ttsfrd_model']
    # Load frontend model
    frontend = ttsfrd.TtsFrontendEngine()
    frontend.initialize(ttsfrd_model)
    frontend.set_lang_type('zhcn')
    # split wav file according to text
    filelist = os.listdir(os.path.join(data_path, 'WAV'))
    for file in tqdm(filelist):
        wav, _ = librosa.load(os.path.join(data_path, 'WAV', file), fs)
        wav = wav / max(abs(wav)) * (max_value - 1)
        with open(os.path.join(data_path, 'TXT', file[:-3] + 'txt'), 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if i == 0:
                continue
            start_end, speaker_id, _, text = line.strip().split('\t')
            text = text.replace('[+]', '')
            text = text.replace('[*]', '')
            if len(text) < 3:
                continue
            start, end = start_end.split(',')
            start, end = float(start[1:]), float(end[:-1])
            pinyin, prosody = g2p_madarin(frontend, text)
            os.makedirs(os.path.join(save_path, speaker_id), exist_ok=True)
            wavfile.write(
                os.path.join(save_path, speaker_id, str(i).zfill(6) + '.wav'),
                fs,
                wav[int(start*fs):int(end*fs)].astype(np.int16),
            )
            with open(os.path.join(save_path, speaker_id, str(i).zfill(6) + '_pinyin' + '.txt'), 'w') as f1:
                f1.write(' '.join(pinyin))
            with open(os.path.join(save_path, speaker_id, str(i).zfill(6) + '_prosody' + '.txt'), 'w') as f1:
                f1.write(' '.join(prosody))


if __name__ == '__main__':
    config = 'examples/RAMC/s0/conf/prepare_data_config.yaml'
    config = yaml.load(
        open(config, "r"), Loader=yaml.FullLoader
    )
    prepare_data(config)

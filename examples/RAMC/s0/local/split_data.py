import os
import sys
sys.path.append('./')
from tqdm import tqdm
import yaml


initials = [
    "b",
    "c",
    "ch",
    "d",
    "f",
    "g",
    "h",
    "j",
    "k",
    "l",
    "m",
    "n",
    "p",
    "q",
    "r",
    "s",
    "sh",
    "t",
    "w",
    "x",
    "y",
    "z",
    "zh",
]
finals = [
    "a1",
    "a2",
    "a3",
    "a4",
    "a5",
    "ai1",
    "ai2",
    "ai3",
    "ai4",
    "ai5",
    "an1",
    "an2",
    "an3",
    "an4",
    "an5",
    "ang1",
    "ang2",
    "ang3",
    "ang4",
    "ang5",
    "ao1",
    "ao2",
    "ao3",
    "ao4",
    "ao5",
    "e1",
    "e2",
    "e3",
    "e4",
    "e5",
    "ei1",
    "ei2",
    "ei3",
    "ei4",
    "ei5",
    "en1",
    "en2",
    "en3",
    "en4",
    "en5",
    "eng1",
    "eng2",
    "eng3",
    "eng4",
    "eng5",
    "er1",
    "er2",
    "er3",
    "er4",
    "er5",
    "i1",
    "i2",
    "i3",
    "i4",
    "i5",
    "ia1",
    "ia2",
    "ia3",
    "ia4",
    "ia5",
    "ian1",
    "ian2",
    "ian3",
    "ian4",
    "ian5",
    "iang1",
    "iang2",
    "iang3",
    "iang4",
    "iang5",
    "iao1",
    "iao2",
    "iao3",
    "iao4",
    "iao5",
    "ie1",
    "ie2",
    "ie3",
    "ie4",
    "ie5",
    "ii1",
    "ii2",
    "ii3",
    "ii4",
    "ii5",
    "iii1",
    "iii2",
    "iii3",
    "iii4",
    "iii5",
    "in1",
    "in2",
    "in3",
    "in4",
    "in5",
    "ing1",
    "ing2",
    "ing3",
    "ing4",
    "ing5",
    "iong1",
    "iong2",
    "iong3",
    "iong4",
    "iong5",
    "iou1",
    "iou2",
    "iou3",
    "iou4",
    "iou5",
    "o1",
    "o2",
    "o3",
    "o4",
    "o5",
    "ong1",
    "ong2",
    "ong3",
    "ong4",
    "ong5",
    "ou1",
    "ou2",
    "ou3",
    "ou4",
    "ou5",
    "u1",
    "u2",
    "u3",
    "u4",
    "u5",
    "ua1",
    "ua2",
    "ua3",
    "ua4",
    "ua5",
    "uai1",
    "uai2",
    "uai3",
    "uai4",
    "uai5",
    "uan1",
    "uan2",
    "uan3",
    "uan4",
    "uan5",
    "uang1",
    "uang2",
    "uang3",
    "uang4",
    "uang5",
    "uei1",
    "uei2",
    "uei3",
    "uei4",
    "uei5",
    "uen1",
    "uen2",
    "uen3",
    "uen4",
    "uen5",
    "uo1",
    "uo2",
    "uo3",
    "uo4",
    "uo5",
    "v1",
    "v2",
    "v3",
    "v4",
    "v5",
    "van1",
    "van2",
    "van3",
    "van4",
    "van5",
    "ve1",
    "ve2",
    "ve3",
    "ve4",
    "ve5",
    "vn1",
    "vn2",
    "vn3",
    "vn4",
    "vn5",
]
alphabet = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z"
]
valid_symbols = initials + finals + ["rr"]



def split_data(config):
    save_path = config['save_path']
    filelist = os.listdir(save_path)
    speaker_id = []
    pinyins = []
    prosody = []
    wav_file = []
    count = 0
    for speaker_i in tqdm(filelist):
        if speaker_i == 'G00000000':
            continue
        filenames = os.listdir(os.path.join(save_path, speaker_i))
        filenames = set([i[:6] for i in filenames])
        for file in filenames:
            with open(os.path.join(save_path, speaker_i, file + '_pinyin.txt'), 'r', encoding='utf-8') as f:
                temp = f.readlines()[0]
                temp_list = temp.split(' ')
            if all([i in valid_symbols for i in temp_list]):
                pinyins.append(temp)
            else:
                continue
            with open(os.path.join(save_path, speaker_i, file + '_prosody.txt'), 'r', encoding='utf-8') as f:
                prosody.append(f.readlines()[0])
            speaker_id.append(count)
            wav_file.append(os.path.join(save_path, speaker_i, file + '.wav'))

        count += 1

    with open('examples/RAMC/s0/local/train.txt', 'w', encoding='utf-8') as f:
        with open('examples/RAMC/s0/local/val.txt', 'w', encoding='utf-8') as f1:
            count = 0
            for p, pro, wave_filename, s in tqdm(
                    zip(pinyins, prosody, wav_file, speaker_id)):
                if count < 20:
                    f1.write(wave_filename + '|' + str(
                        s) + '|' + p + '|' + pro + '\n')
                    count += 1
                else:
                    f.write(wave_filename + '|' + str(
                        s) + '|' + p + '|' + pro + '\n')
                    count += 1

if __name__ == '__main__':
    config = 'examples/RAMC/s0/conf/prepare_data_config.yaml'
    config = yaml.load(
        open(config, "r"), Loader=yaml.FullLoader
    )
    split_data(config)

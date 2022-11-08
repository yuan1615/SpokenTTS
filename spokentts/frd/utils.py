import ttsfrd

def g2p_madarin(frontend, text):
    result = frontend.gen_tacotron_symbols(text)
    texts = [s for s in result.splitlines() if s != '']
    pinyin = []
    for line in texts:
        count = 0
        line = line.strip().split('\t')[1]
        lfeat_symbol = line.strip().split(' ')
        for this_lfeat_symbol in lfeat_symbol:
            this_lfeat_symbol = this_lfeat_symbol.strip('{').strip('}').split(
                '$')
            if this_lfeat_symbol[2] == 's_begin':
                # if this_lfeat_symbol[0] in ['ge', 'ga']:
                #     continue
                if this_lfeat_symbol[0].split('_')[0] == 'xx':
                    pinyin.append('x')
                else:
                    pinyin.append(this_lfeat_symbol[0].split('_')[0])
            else:
                if this_lfeat_symbol[0].split('_')[0] == 'ih':
                    pinyin.append('iii' + this_lfeat_symbol[1][-1])
                elif this_lfeat_symbol[0].split('_')[0] in ['e', 'an', 'a', 'ang', 'ao', 'o', 'ou', 'ong'] and pinyin[-1] == 'y':
                    pinyin.append('i' + this_lfeat_symbol[0].split('_')[0] + this_lfeat_symbol[1][-1])
                # elif this_lfeat_symbol[0].split('_')[0] + this_lfeat_symbol[1][-1] == 'er4':
                #     pinyin[-1] = 'e4'
                #     pinyin.append('rr')
                else:
                    if this_lfeat_symbol[1] == 'tone_none':
                        pinyin.append(this_lfeat_symbol[0])
                    else:
                        pinyin.append(this_lfeat_symbol[0].split('_')[0] + this_lfeat_symbol[1][-1])
    prosody = ['I' for _ in pinyin]
    for ii, p in enumerate(pinyin):
        if p == '#1':
            prosody[ii-2:ii] = ['B1', 'B1']
        if p == "#2":
            prosody[ii - 2:ii] = ['B2', 'B2']
        if p == "#3" or p == '#4':
            prosody[ii - 2:ii] = ['B3', 'B3']
    # 删除韵律标识
    # 删除 ge ga
    ind = []
    for ii, p in enumerate(pinyin):
        if p in ['ge', 'ga', 'go', '#1', '#2', '#3', '#4']:
            ind.append(ii)
    for a in ind[::-1]:
        pinyin.pop(a)
        prosody.pop(a)
    # print(prosody)
    # print(' '.join(pinyin))
    return pinyin, prosody

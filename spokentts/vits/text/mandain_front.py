import itertools
import re
import os

# 读入量词词库
import sys
sys.path.append("./text")

quantifier = ""
with open("text/dict_quantifier.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
        quantifier += line[0]

normaldict = ""
with open("text/dict_normal.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
        normaldict += line[0:]

# 记录各匹配规则
_decimal_number_re = re.compile(r'([0-9]+\.[0-9]+)')
_percent_number_re = re.compile(r'([0-9]+(\.[0-9]*)?|\.[0-9]+)\%')

_quantifier_number_re = re.compile(r'[0-9]+[%s]' % quantifier)
_normaldict_number_re = re.compile(r'[0-9]+%s' % normaldict)

_number_re = re.compile(r'[0-9]+')
_date_number_re = re.compile(r'\d{4}[/]\d{1,2}[/]\d{1,2}')

_date_re1 = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}')
_date_re2 = re.compile(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}')
_date_re3 = re.compile(r'\d{4}年')
_date_re4 = re.compile(r'\d{1,2}[日月]')

_time_re1 = re.compile(r'\d{1,2}[:：]\d{1,2}[:：]\d{1,2}')
_time_re2 = re.compile(r'\d{1,2}[:：]\d{1,2}')

_id_card_re = re.compile(r"([1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx])")
_phone_number_re = re.compile(r'(13\d{9}|14[5|7]\d{8}|15\d{9}|166{\d{8}|17[3|6|7]{\d{8}|18\d{9})')

_email_re = re.compile(r'[0-9a-zA-Z_\.]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}')
# _https_re = re.compile()

# 匹配工作的时间段
_work_time = re.compile(r'\d{1,2}[:：]\d{1,2}[-~]\d{1,2}[:：]\d{1,2}')

# 匹配带减号的电话号码
_minus_phone = re.compile(r'\d{3}-\d{3}-\d{4}')

# 匹配带减号的数字（减号在中间，更新为”至“）
_minus_number = re.compile(r'\d{1,2}[--]\d{1,2}')

# teshu

def _expand_work_time(m):
    time = str(m.group(0))
    if '-' in time:
        time = time.split("-")
    elif '~' in time:
        time = time.split("~")
    spoken_time = []
    for time_i in time:
        spoken_time_i = ""
        if ":" in time_i:
            time_i = time_i.split(":")
        else:
            time_i = time_i.split("：")
        hour = _expand_quantifier_number(time_i[0])
        if int(time_i[1]) == 30:
            spoken_time_i += hour + "点半"
        elif int(time_i[1]) == 0:
            minute = _expand_quantifier_number(time_i[1])
            spoken_time_i += hour + "点"
        else:
            minute = _expand_quantifier_number(time_i[1])
            spoken_time_i += hour + "点" + minute + "分"
        spoken_time.append(spoken_time_i)
    return "至".join(spoken_time)


def _expand_minus_phone(m):
    phone = str(m.group(0))
    phones = phone.split("-")
    spoken_phone = []
    for phone in phones:
        spoken_phone.append(_expand_normal_number(phone))
    return "-".join(spoken_phone)


def _expand_minus_number(m):
    number = str(m.group(0))
    number = number.split("-")
    spkoen_number = []
    for num_i in number:
        if num_i == '2':
            spkoen_number.append('二')
        else:
            spkoen_number.append(_expand_quantifier_number(num_i))
    return "至".join(spkoen_number)


def _expand_email(m):
    email = str(m.group(0))
    email = email.upper()
    email = email.replace('.', '点')
    email = email.replace('@', ' at ')
    email = email.replace('COM', 'com')
    email = email.replace('nNET', 'net')
    return email

def _expand_date1(m):
    date = str(m.group(0))
    if "/" in date:
        date = date.split("/")
    elif "-" in date:
        date = date.split("-")
    if int(date[1]) in [1, 3, 5, 7, 8, 10, 12] and int(date[2]) <= 31:
        result = date[0] + "/" + date[1] + "/" + date[2]
    elif int(date[1]) in [4, 6, 9, 11] and int(date[2]) <= 30:
        result = date[0] + "/" + date[1] + "/" + date[2]
    elif int(date[1]) == 2 and int(date[2]) <= 29:
        result = date[0] + "/" + date[1] + "/" + date[2]
    else:
        result = date[0] + " " + date[1] + " " + date[2]
    return result


def _expand_date2(m):
    date = str(m.group(0))
    if "/" in date:
        date = date.split("/")
    elif "-" in date:
        date = date.split("-")
    if int(date[0]) <= 12 and int(date[1]) <= 12:
        result = date[2] + "/" + date[0] + "/" + date[1]
    elif int(date[0]) > 12 and int(date[1]) < 12:
        result = date[2] + "/" + date[1] + "/" + date[0]
    elif int(date[1]) > 12 and int(date[0]) < 12:
        result = date[2] + "/" + date[0] + "/" + date[1]
    else:
        result = date[0] + " " + date[1] + " " + date[2]
    return result


def _expand_year(m):
    year = str(m.group(0))
    return _expand_normal_number(year[0:4]) + "年"

def _expand_month_day(m):
    tempchr = m.group(0)[-1]
    tempnum = m.group(0)[0:-1]
    if int(tempnum) == 2:
        result = "二" + tempchr
    else:
        result = _expand_quantifier_number(tempnum) + tempchr
    return result


def normalize_date(text):
    text = re.sub(_date_re1, _expand_date1, text)
    text = re.sub(_date_re2, _expand_date2, text)
    return text


def _expand_date_number(m):
    date = str(m.group(0)).split("/")
    year, month, day = date
    year = _expand_normal_number(year)
    if int(month) == 2:
        month = "二"
    else:
        month = _expand_quantifier_number(month)
    if int(day) == 2:
        day = "二"
    else:
        day = _expand_quantifier_number(day)
    return "/" + year + "年/" + month + "月" + day + "日/"


def _expand_time_number(m):
    time = str(m.group(0))
    if ":" in time:
        time = time.split(":")
    else:
        time = time.split("：")
    if len(time) == 2:
        if int(time[0]) == 2:
            hour = "二"
        else:
            hour = _expand_quantifier_number(time[0])
        if int(time[1]) == 2:
            minute = "二"
        else:
            minute = _expand_quantifier_number(time[1])
        result = hour + "点/" + minute + "分"
    else:
        if int(time[0]) == 2:
            hour = "二"
        else:
            hour = _expand_quantifier_number(time[0])
        if int(time[1]) == 2:
            minute = "二"
        else:
            minute = _expand_quantifier_number(time[1])
        if int(time[2]) == 2:
            second = "二"
        else:
            second = _expand_quantifier_number(time[2])

        result = "/" + hour + "点/" + minute + "分/" + second + "秒/"
    return result

def _expand_decimal_point(m):
    return m.group(1).replace('.', '点')


def _expand_percent(m):
    num = str(m.group(1))
    if "." in num:
        result = "百分之" + _expand_point_number(num)
    else:
        if int(num) == 2:
            result = "百分之二"
        else:
            result = "百分之" + _expand_quantifier_number(num)
    return result

def _expand_point_number(m):
    if type(m) != str:
        m = str(m.group(0))
    num = m.split(".")
    if int(num[0]) == 2:
         num_int = "二"
    else:
        num_int = _expand_quantifier_number(num[0])
    if int(num[1]) == 2:
        num_point = "二"
    else:
        num_point = _expand_normal_number(num[1])
    return num_int + "点" + num_point


def _expand_quantifier_number(m):
    if type(m) == str:
        num = int(m)
    else:
        num = int(m.group(0)[0:-1])
    # print(num)
    """
    Converts numbers to Chinese representations.
    `big`   : use financial characters.
    `simp`  : use simplified characters instead of traditional characters.
    `o`     : use 〇 for zero.
    `twoalt`: use 两/兩 for two when appropriate.
    Note that `o` and `twoalt` is ignored when `big` is used,
    and `twoalt` is ignored when `o` is used for formal representations.
    """
    # check num first
    nd = str(num)
    if abs(float(nd)) >= 1e48:
        raise ValueError('number out of range')
    elif 'e' in nd:
        raise ValueError('scientific notation is not supported')
    c_symbol = '正负点'
    c_basic = '零依二三四五六七八九'
    c_unit1 = '十百千'
    c_twoalt = '两'
    c_unit2 = '万亿兆京垓秭穰沟涧正载'
    revuniq = lambda l: ''.join(k for k, g in itertools.groupby(reversed(l)))

    # 特殊
    if len(str(num)) == 1 and num == 2:
        return "两" + m.group(0)[-1]
    nd = str(num)
    result = []
    if nd[0] == '+':
        result.append(c_symbol[0])
    elif nd[0] == '-':
        result.append(c_symbol[1])
    if '.' in nd:
        integer, remainder = nd.lstrip('+-').split('.')
    else:
        integer, remainder = nd.lstrip('+-'), None
    if int(integer):
        splitted = [integer[max(i - 4, 0):i]
                    for i in range(len(integer), 0, -4)]
        intresult = []
        for nu, unit in enumerate(splitted):
            # special cases
            if int(unit) == 0:  # 0000
                intresult.append(c_basic[0])
                continue
            elif nu > 0 and int(unit) == 2:  # 0002
                intresult.append(c_twoalt + c_unit2[nu - 1])
                continue
            ulist = []
            unit = unit.zfill(4)
            for nc, ch in enumerate(reversed(unit)):
                if ch == '0':
                    if ulist:  # ???0
                        ulist.append(c_basic[0])
                elif nc == 0:
                    ulist.append(c_basic[int(ch)])
                elif nc == 1 and ch == '1' and unit[1] == '0':
                    # special case for tens
                    # edit the 'elif' if you don't like
                    # 十四, 三千零十四, 三千三百一十四
                    ulist.append(c_unit1[0])
                elif nc > 1 and ch == '2':
                    ulist.append(c_twoalt + c_unit1[nc - 1])
                else:
                    ulist.append(c_basic[int(ch)] + c_unit1[nc - 1])
            ustr = revuniq(ulist)
            if nu == 0:
                intresult.append(ustr)
            else:
                intresult.append(ustr + c_unit2[nu - 1])
        result.append(revuniq(intresult).strip(c_basic[0]))
    else:
        result.append(c_basic[0])
    if remainder:
        result.append(c_symbol[2])
        result.append(''.join(c_basic[int(ch)] for ch in remainder))
    if type(m) != str:
        result.append(m.group(0)[-1])
    return ''.join(result)


def _expand_phone_number(num):
    """数字转中文"""
    if type(num) != str:
        num = str(num.group(0))
    num_dict = {"0": u"零", "1": u"幺", "2": u"二", "3": u"三", "4": u"四", "5": u"五", "6": u"六", "7": u"七", "8": u"八",
                "9": u"九"}
    listnum = list(num)
    shu = []
    for i in listnum:
        # print(num_dict[i])
        shu.append(num_dict[i])
    new_str = "".join(shu)
    return new_str[0:3] + "/" + new_str[3:7] + "/" + new_str[7:11]

def _expand_idcard_number(num):
    """数字转中文"""
    if type(num) != str:
        num = str(num.group(0))
    num_dict = {"0": u"零", "1": u"幺", "2": u"二", "3": u"三", "4": u"四", "5": u"五", "6": u"六", "7": u"七", "8": u"八",
                "9": u"九"}
    listnum = list(num)
    shu = []
    for i in listnum:
        # print(num_dict[i])
        shu.append(num_dict[i])
    new_str = "".join(shu)
    return new_str[0:3] + "/" + new_str[3:6] + "/" + new_str[6:10] + "/" + new_str[10:14]+ "/" + new_str[14:18]


def _expand_normaldict_number(m):
    """数字转中文"""
    if type(m) == str:
        num = str(m)
    else:
        num = str(m.group(0)[0:-2])

    num_dict = {"0": u"零", "1": u"依", "2": u"二", "3": u"三", "4": u"四", "5": u"五", "6": u"六", "7": u"七", "8": u"八",
                "9": u"九"}
    listnum = list(num)
    shu = []
    for i in listnum:
        # print(num_dict[i])
        shu.append(num_dict[i])
    new_str = "".join(shu)
    return new_str + m.group(0)[-2] + m.group(0)[-1]


def _expand_normal_number(num):
    """数字转中文"""
    if type(num) != str:
        num = str(num.group(0))
    num_dict = {"0": u"零", "1": u"依", "2": u"二", "3": u"三", "4": u"四", "5": u"五", "6": u"六", "7": u"七", "8": u"八",
                "9": u"九"}
    listnum = list(num)
    shu = []
    for i in listnum:
        # print(num_dict[i])
        shu.append(num_dict[i])
    new_str = "".join(shu)
    return new_str


def normalize_numbers(text):
    # 邮箱
    # print(text)
    # 新增
    text = re.sub(_work_time, _expand_work_time, text)
    text = re.sub(_minus_phone, _expand_minus_phone, text)
    text = re.sub(_minus_number, _expand_minus_number, text)
    # 新增

    # 日期
    text = normalize_date(text)
    text = re.sub(_date_number_re, _expand_date_number, text)
    text = re.sub(_date_re3, _expand_year, text)
    text = re.sub(_date_re4, _expand_month_day, text)
    text = re.sub(_time_re1, _expand_time_number, text)
    text = re.sub(_time_re2, _expand_time_number, text)
    # 电话和身份证
    text = re.sub(_id_card_re, _expand_idcard_number, text)
    text = re.sub(_phone_number_re, _expand_phone_number, text)
    # 特殊字符
    text = re.sub(_percent_number_re, _expand_percent, text)
    text = re.sub(_decimal_number_re, _expand_point_number, text)
    # 自定义正常词
    text = re.sub(_normaldict_number_re, _expand_normaldict_number, text)
    # 量词
    text = re.sub(_quantifier_number_re, _expand_quantifier_number, text)
    # print(text)
    # 其他场景使用num_to_char
    # 正常数字
    text = re.sub(_number_re, _expand_normal_number, text)

    # 邮箱处理

    return text

if __name__ == '__main__':
    text = "如您需要申请企业存管流水，请您在人工服务时间8:00-22:00进线，在对话框输入“人工”咨询。"
    text = normalize_numbers(text)
    print(text)
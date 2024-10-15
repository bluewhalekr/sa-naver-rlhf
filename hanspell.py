import requests
import json
import time
import sys
from collections import OrderedDict
import xml.etree.ElementTree as ET
import re
from cachetools import TTLCache
from urllib import parse
from collections import namedtuple


BASE_URL = 'https://m.search.naver.com/p/csearch/ocontent/util/SpellerProxy'


class CheckResult:
    PASSED = 0
    WRONG_SPELLING = 1
    WRONG_SPACING = 2
    AMBIGUOUS = 3
    STATISTICAL_CORRECTION = 4


_checked = namedtuple('Checked',
    ['result', 'original', 'checked', 'errors', 'words', 'time'])

cache = TTLCache(maxsize = 10, ttl = 3600)

def read_token():
    try:
        TOKEN = cache.get('PASSPORT_TOKEN')
        return TOKEN
    except KeyError:
        return None

def update_token(agent):

    html = agent.get(url='https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=맞춤법검사기')

    match = re.search('passportKey=([a-zA-Z0-9]+)', html.text)
    if match is not None:
        token = parse.unquote(match.group(1))
        cache['PASSPORT_TOKEN'] = token
    return token


def get_response(token, text):

    if token is None:
        token = update_token(_agent)

    payload = {
        'passportKey': token,
        'q': text,
        'color_blindness': 0
    }

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'referer': 'https://search.naver.com/',
    }

    r = _agent.get(BASE_URL, params=payload, headers=headers)
    data = json.loads(r.text)

    if 'error' in data['message'] :
        r = get_response(update_token(_agent), text)

    return r


class Checked(_checked):
    def __new__(cls, result=False, original='', checked='', errors=0, words=[], time=0.0):
        return super(Checked, cls).__new__(
            cls, result, original, checked, errors, words, time)

    def as_dict(self):
        d = {
            'result': self.result,
            'original': self.original,
            'checked': self.checked,
            'errors': self.errors,
            'words': self.words,
            'time': self.time,
        }
        return d

    def only_checked(self):
        return self.checked


_agent = requests.Session()
PY3 = sys.version_info[0] == 3


def _remove_tags(text):
    text = u'<content>{}</content>'.format(text).replace('<br>', '')
    if not PY3:
        text = text.encode('utf-8')

    result = ''.join(ET.fromstring(text).itertext())

    return result


def check(text):
    """
    매개변수로 입력받은 한글 문장의 맞춤법을 체크합니다.
    """
    if isinstance(text, list):
        result = []
        for item in text:
            checked = check(item)
            result.append(checked)
        return result

    # 최대 500자까지 가능.
    if len(text) > 500:
        return Checked(result=False)

    start_time = time.time()
    r = get_response(read_token(), text)
    passed_time = time.time() - start_time

    data = json.loads(r.text)
    html = data['message']['result']['html']
    result = {
        'result': True,
        'original': text,
        'checked': _remove_tags(html),
        'errors': data['message']['result']['errata_count'],
        'time': passed_time,
        'words': OrderedDict(),
    }

    # 띄어쓰기로 구분하기 위해 태그는 일단 보기 쉽게 바꿔둠.
    # ElementTree의 iter()를 써서 더 좋게 할 수 있는 방법이 있지만
    # 이 짧은 코드에 굳이 그렇게 할 필요성이 없으므로 일단 문자열을 치환하는 방법으로 작성.
    html = html.replace('<em class=\'green_text\'>', '<green>') \
        .replace('<em class=\'red_text\'>', '<red>') \
        .replace('<em class=\'violet_text\'>', '<violet>') \
        .replace('<em class=\'blue_text\'>', '<blue>') \
        .replace('</em>', '<end>')
    items = html.split(' ')
    words = []
    tmp = ''
    for word in items:
        if tmp == '' and word[:1] == '<':
            pos = word.find('>') + 1
            tmp = word[:pos]
        elif tmp != '':
            word = u'{}{}'.format(tmp, word)

        if word[-5:] == '<end>':
            word = word.replace('<end>', '')
            tmp = ''

        words.append(word)

    for word in words:
        check_result = CheckResult.PASSED
        if word[:5] == '<red>':
            check_result = CheckResult.WRONG_SPELLING
            word = word.replace('<red>', '')
        elif word[:7] == '<green>':
            check_result = CheckResult.WRONG_SPACING
            word = word.replace('<green>', '')
        elif word[:8] == '<violet>':
            check_result = CheckResult.AMBIGUOUS
            word = word.replace('<violet>', '')
        elif word[:6] == '<blue>':
            check_result = CheckResult.STATISTICAL_CORRECTION
            word = word.replace('<blue>', '')
        result['words'][word] = check_result

    result = Checked(**result)

    return result

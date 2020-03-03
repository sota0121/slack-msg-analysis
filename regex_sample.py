# regex sample
# https://hibiki-press.tech/learn_prog/python/regex_pattern/1099
# https://qiita.com/luohao0404/items/7135b2b96f9b0b196bf3
# https://teratail.com/questions/171096
import re


def main():
    url_str = '<https://twitter.com/masanork/status/1229977714062311424?s=12>'
    test_str = 'hello world. こんにちは、世界。12345678'
    input_str = test_str + url_str
    print('in  str: {0}'.format(input_str))
    regex = re.compile(r'\<.*?\>')
    mo = regex.sub('', input_str)
    print('out str: {0}'.format(mo))
    # check if url string excluded or not
    if mo == test_str:
        print('successed')
    else:
        print('failed')

if __name__ == "__main__":
    main()

#-*- using:utf-8 -*-
import urllib.request, urllib.error

with open('out.txt', 'w') as txt:
    txt.write("chdck result\n")

def checkURL(url):
    try:
        f = urllib.request.urlopen(url)
        f.close()
        return True
    except:
        return False

if __name__ == '__main__':

    with open("./input.txt") as f:
        for url in f:
            # print(url, end='')
            ret = checkURL(url)
            if ret == True:
                result = "OK:"
            else:
                result = "NotFound:"

            ret_text = result + url
            #ret_text = ret_text.replace('\n', '')
            print(ret_text)
            if ret != True:
                with open('out.txt', 'a') as txt:
                    txt.write(ret_text)

import urllib.request
import urllib.error

# check received url whethere it exists or not.
def checkURL(url) -> bool:
    try:
        f = urllib.request.urlopen(url)
        print('URL exists')
        f.close()
        return True
    except:
        print("URL doesn't exist")
        return False

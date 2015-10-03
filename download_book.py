import re
import requests


def download_book(page, book_url, file_save):
    with requests.session() as s:
        r = s.get(page)
        book_cookie = re.findall('cookie_string = "(.+)"', r.text)
        if book_cookie:
            cookies = {'java-book': book_cookie[0]}
        else:
            cookies = {}

        r = s.get(book_url, cookies=cookies, stream=True)
        if r.status_code == 200:
            with open(file_save, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

if __name__ == '__main__':
    download_book('http://javalibre.com.ua/java-book/book/2917866', 'http://javalibre.com.ua/files/Ctvorennya_VChK_-_interpretaciya_vidomoj_problemi_1378134741.txt', 'Ctvorennya_VChK_-_interpretaciya_vidomoj_problemi_1378134741.txt')
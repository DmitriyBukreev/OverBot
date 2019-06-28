from bs4 import BeautifulSoup
import requests as r

if __name__ == '__main__':
    response = r.get('https://playoverwatch.com/en-us/career/pc/DimedroN-21855')
    soup = BeautifulSoup(response.text, 'lxml')
    qp = soup.find('div', id='quickplay')
    option = qp.find('div', {'data-category-id': '0x0860000000000021'})
    for div in option.find_all('div', {'data-js': 'progressBar'}):
        url = div.img['src']
        name = div.find('div', class_="ProgressBar-title").text
        image = r.get(url)
        with open(f'heroes/{name}.png', 'wb') as f:
            f.write(image.content)
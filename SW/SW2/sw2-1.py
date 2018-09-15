import re

def open_files():
    with open('poem1.txt',encoding='utf-8') as f:
        text1 = f.read()
    text1 = re.sub('\ufeff','',text1)
    text1 = re.sub('[^а-яёА-ЯЁ-]',' ',text1)
    text1 = re.sub('\s+',' ',text1)
    text1 = text1.lower()
    with open('poem2.txt',encoding='utf-8') as f:
        text2 = f.read()
    text2 = re.sub('\ufeff','',text2)
    text2 = re.sub('[^а-яёА-ЯЁ-]',' ',text2)
    text2 = re.sub('\s+',' ',text2)
    text2 = text2.lower()
    return text1, text2

def make_word_set(x):
    poem1, poem2 = x
    #print(poem1)
    #print(poem2)
    words1 = set(poem1.split(' '))
    words2 = set(poem2.split(' '))
    #print(words1)
    #print(words2)
    return words1, words2

def compare(words):
    words1, words2 = words
    print('Пересечение: ',words1&words2)
    print('Симметрическая разность: ',words1^words2)

def main():
    compare(make_word_set(open_files()))

if __name__ == '__main__':
    main()
    
    

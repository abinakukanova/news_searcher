# news_searcher
Проект по курсу "Информационный поиск и базы данных", 4 курс

- `app.py` находится приложение

- `models.py` - модели данных бд

- `migrate.py` - создание базы данных
  
- `preprocessing.py` лежат функции для обработки текста, косинусной близости и сортировки текстов по ней

- `searcher_tfidf.py` реализован способ индексирования на основе TF-IDF и написана функция поиска

- `searcher_fasttext.py` реализован способ индексирования на основе FastText и написана функция поиска

- `fasttext_index_matrix.pickle` индексация на основе FastText

- `tfidf_index_matrix.pickle` индексация на основе TF-IDF

- `lemmatized_vectorizer.pickle` сохраненный векторизатор 


Модель FastText была скачена [отсюда](https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.ru.300.bin.gz). Модель не была загружена в репозиторий, поэтому необходимо скачать. 

Данные `ria-2023.csv` были скачаны путем краулинга с новостного агенства РИА Новости. Файл большой, поэтому скачивание доступно по этой [ссылке](https://drive.google.com/file/d/11hWxJcawybKaQejx8QFCVCLEP8tJErH7/view?usp=sharing)

Файлы `fasttext_index_matrix.pickle` и `tfidf_index_matrix.pickle` создаются при запуске приложения, если их нет. 

Чтобы посмотреть приложение, нужно запустить код `app.py`. 

На загрузку приложения выходит где-то не больше 4 минут, а запросы в поиске выходят сразу же. 

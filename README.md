# Продуктовый помощник Foodgram
## Дипломный проект YandexPracticum. Курс Python-разработчик


## О проекте

Сайт доступен по [ip](http://158.160.19.247/) и по [доменному имени](http://foodgramsamiel19.hopto.org)

Данный проект — сайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Страница автора на [github](https://github.com/Samiel19)

## Использованные технологии
При разработке данного приложения использовались следующие технологии:
Python 3.10.6
Django REST Framework
PostgreSQL
Docker
Приложение развернуто на сервере YandexCloud

## Функциональность проекта
Проект доступен по IP.
Все сервисы и страницы доступны для пользователей в соответствии с их правами. 
Рецепты на всех страницах сортируются по дате публикации (новые — выше).
Работает фильтрация по тегам, в том числе на странице избранного и на странице рецептов одного автора).
Работает пагинатор (в том числе при фильтрации по тегам).
Исходные данные предзагружены; добавлены тестовые пользователи и рецепты.

# Для авторизованных пользователей:

      1. Доступна главная страница.
      
      2. Доступна страница другого пользователя.
      
      3. Доступна страница отдельного рецепта.
      
      4. Доступна страница «Мои подписки».
      
            4.1. Можно подписаться и отписаться на странице рецепта.
      
            4.2. Можно подписаться и отписаться на странице автора.
            
            4.3. При подписке рецепты автора добавляются на страницу «Мои подписки» 
            и удаляются оттуда при отказе от подписки.
        
      5. Доступна страница «Избранное».
        
            5.1. На странице рецепта есть возможность добавить рецепт в список избранного и удалить его оттуда.
        
            5.2. На любой странице со списком рецептов есть возможность 
            добавить рецепт в список избранного и удалить его оттуда.
        
      6. Доступна страница «Список покупок».
      
            6.1. На странице рецепта есть возможность добавить рецепт в список покупок и удалить его оттуда.
      
            6.2. На любой странице со списком рецептов есть возможность добавить 
            рецепт в список покупок и удалить его оттуда.
      
            6.3. Есть возможность выгрузить файл (.txt) с перечнем и количеством необходимых 
            ингредиентов для рецептов из «Списка покупок».
      
            6.4. Ингредиенты в выгружаемом списке не повторяются, корректно подсчитывается 
            общее количество для каждого ингредиента.
      
      7. Доступна страница «Создать рецепт».
      
            7.1. Есть возможность опубликовать свой рецепт.
      
            7.2. Есть возможность отредактировать и сохранить изменения в своём рецепте.
      
            7.3. Есть возможность удалить свой рецепт.
      
      8. Доступна и работает форма изменения пароля.
      
      9. Доступна возможность выйти из системы (разлогиниться).
        
# Для неавторизованных пользователей

        1. Доступна главная страница.
        
        2. Доступна страница отдельного рецепта.
        
        3. Доступна и работает форма авторизации.
        
        4. Доступна и работает форма регистрации.
        
# Администратор и админ-зона

        1. Все модели выведены в админ-зону.
        
        2. Для модели пользователей включена фильтрация по имени и email.
        
        3. Для модели рецептов включена фильтрация по названию, автору и тегам.
        
        4. На админ-странице рецепта отображается общее число добавлений этого рецепта в избранное.
        
        5. Для модели ингредиентов включена фильтрация по названию.

# Инфраструктура

        1. Проект работает с СУБД PostgreSQL.
        
        2. Проект запущен на сервере в Яндекс.Облаке в трёх контейнерах: 
        nginx, PostgreSQL и Django+Gunicorn. Заготовленный контейнер с  фронтендом используется для сборки файлов.
        
        3. Контейнер с проектом обновляется на Docker Hub.
        
        4. В nginx настроена раздача статики, запросы с фронтенда переадресуются в контейнер с Gunicorn. 
        Джанго-админка работает напрямую через Gunicorn.
        
        5. Данные сохраняются в volumes.

# Тестирование

      В данный момент сайт наполнен данными для мануального тестирования. 
      
      Для тестового доступа к проекту используйте следующие данные:
      
                  ip 158.160.19.247
                  
                  Данные администратора:
                  
                  login - admin
                  password 1234qwer 

# Оформление кода

        Код соответствует PEP8.
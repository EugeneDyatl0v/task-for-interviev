# **Тестовое задание на позицию Junior Python Developer**   
   
## **1. API**   
### **Описание**   
Необходимо реализовать API для хранения ссылок пользователя.   
### Пользовательские требования   
- Пользователь должен иметь возможность зарегистрироваться (email, пароль)   
- Пользователь должен иметь возможность сменить пароль   
- Пользователь должен иметь возможность сбросить пароль   
- Пользователь должен иметь возможность аутентифицироваться   
- Пользователь должен иметь возможность управлять своими ссылками
(создавать, редактировать, удалять, просматривать).
   
- Пользователь должен иметь возможность управлять своими коллекциями
(создавать, редактировать, удалять, просматривать)
   
   
### Функциональные требования   
#### Ссылки   
Ссылка должна включать следующие поля:   
- заголовок страницы;   
- краткое описание;   
- ссылка на страницу;   
- картинка;   
- тип ссылки (website, book, article, music, video). Если не удалось получить тип страницы то по умолчанию используем тип website. Картинка превью берется из поля og:image.   
- дата и время создания;   
- дата и время изменения.   
   
При добавлении ссылки пользователь передает только url. Остальные данные сервис получает сам. Информация находится в open graph разметке в html коде страницы. Нужно загрузить код страницы и достать из него данные. Open Graph разметки может и не быть на странице. В таком случае берем информацию если она там есть из тегов title и meta description. Ознакомится с Open Graph можно по ссылке: *[https://yandex.ru/support/webmaster/open-graph/intro-open-graph.html](https://yandex.ru/support/webmaster/open-graph/intro-open-graph.html)*. или использовать любой другой источник информации.   
*Ссылки могут группироваться по коллекциям. Одна и та же ссылка может принадлежать разным коллекциям. Ссылки должны быть уникальны для пользователя.*   
#### Коллекции   
Коллекции должны включать следующие поля:   
- название (обязательное поле);   
- краткое описание (необязательное поле);   
- дата и время создания;   
- дата и время изменения.   
   
### **Нефункциональные требования**   
- Python 3.12+;   
- Django 5.0+ (Django Rest Framework);   
- документация к API в Swagger;   
- использовать Docker (без его использования кандидата рассматривать не будут);   
- описать процесс запуска в README.md.   
   
Будет плюсом:   
- Деплой проекта   
   
P.S. Можно использовать любые библиотеки или батарейки к Django   
## **2. SQL**   
**Описание**   
*Написать sql запрос*, который выводит 10 пользователей, у которых максимальное количество сохраненных ссылок, если количество ссылок одинаково у нескольких пользователей, выведете тех, кто раньше был зарегистрирован.

   
Вы можете написать скрипт или воспользоваться сторонними библиотеками для заполнения базы данных тестовыми данными   
   
Пример вывода в файле **2\_sql\_output\_example.png:**   
![2_sql_output_example.jpg](files/2_sql_output_example.jpg)    

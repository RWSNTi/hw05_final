**Yatube**
=====

Yatube - это сервис, позволяющий зарегистрированным пользователям вести онлайн-блоги - оставлять на своей странице записи, дополнять их изображениями. Так же зарегистрированные пользователи могут оставлять комментарии под чужими и своими записями, подписываться на интересующих их авторов. Так же есть возможность постить записи в тематических группах.


**Как запустить проект:**
-----

Клонировать репозиторий и перейти в него в командной строке:

.. code-block:: text

 git clone https://github.com/RWSNTi/hw05_final

Перейти в созданный репозиторий:

.. code-block:: text

 cd api_final_yatube

Cоздать и активировать виртуальное окружение:

.. code-block:: text

 python -m venv venv
 source venv/scripts/activate для Win или source/bin/activate для Unix-систем

Обновить установщик расширений pip

.. code-block:: text

 python -m pip install --upgrade pip

Установить зависимости из файла requirements.txt:

.. code-block:: text

 pip install -r requirements.txt
 
Выполнить миграции:

.. code-block:: text

 python manage.py migrate

Запустить проект:

.. code-block:: text

 python manage.py runserver

# GPB-Task
Тестовое задание

Выполнить разбор файла почтового лога, залить данные в БД и организовать поиск по адресу получателя.

Исходные данные:
1. Файл лога maillog
2. Схема таблиц в БД (допускается использовать postgresql или mysql):
```SQL
CREATE TABLE message (
created TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
id VARCHAR NOT NULL,
int_id CHAR(16) NOT NULL,
str VARCHAR NOT NULL,
status BOOL,
CONSTRAINT message_id_pk PRIMARY KEY(id)
);
CREATE INDEX message_created_idx ON message (created);
CREATE INDEX message_int_id_idx ON message (int_id);

CREATE TABLE log (
created TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
int_id CHAR(16) NOT NULL,
str VARCHAR,
address VARCHAR
);
CREATE INDEX log_address_idx ON log USING hash (address);
```
Пояснения:  
В качестве разделителя в файле лога используется символ пробела.

Значения первых полей:  
- дата  
- время  
- внутренний id сообщения  
- флаг  
- адрес получателя (либо отправителя)  
- другая информация

В качестве флагов используются следующие обозначения:  
<= прибытие сообщения (в этом случае за флагом следует адрес отправителя)  
=> нормальная доставка сообщения  
-> дополнительный адрес в той же доставке  
** доставка не удалась  
== доставка задержана (временная проблема)  

В случаях, когда в лог пишется общая информация, флаг и адрес получателя не указываются.

Задачи:
1. Выполнить разбор предлагаемого файла лога с заполнением таблиц БД:
В таблицу message должны попасть только строки прибытия сообщения (с флагом <=). Поля таблицы
должны содержать следующую информацию:  
- created - timestamp строки лога  
- id - значение поля id=xxxx из строки лога  
- int_id - внутренний id сообщения  
- str - строка лога (без временной метки)

В таблицу log записываются все остальные строки:  
- created - timestamp строки лога  
- int_id - внутренний id сообщения  
- str - строка лога (без временной метки)  
- address - адрес получателя

2. Создать html-страницу с поисковой формой, содержащей одно поле (type="text") для ввода адреса получателя.
Результатом отправки формы должен являться список найденных записей '<timestamp> <строка лога>' из двух
таблиц, отсортированных по идентификаторам сообщений (int_id) и времени их появления в логе.
Отображаемый результат необходимо ограничить сотней записей, если количество найденных строк превышает
указанный лимит, должно выдаваться соответствующее сообщение.



------
# Решение
### Комментарии к выбору оформления таблицы "как в ТехЗадании" (от Заказчика):

Требования к структуре таблиц странноватые, но возможно *"он художник, он так видит"*, либо заказчик отталкивается от уже существующей реализации. Поэтому сделаем первый вариант в соотвествии с ТЗ и еще один предложим заказчику скорректированный, возможно что-то его заинтересует.

Структура таблиц находится в файле _.create_table.sql_<br>
Коментарии к выбору:
- Попробуем реализовать на базе MySQL.
- `ENGINE=InnoDB`   -- Судя по вашему логу в день прилетает до 500_000 строк. Удобнее использовать неблокирующуюся на чтение базу.
- `CHARSET=latin1;` -- `utf8mb4` не сильно нужна. В логе нет кирилицы. Тем более, что при использлвании `utf8mb4` длина индекса сократится с 767 (для InnoDB) до 767/4 = 191, либо переходить на `COMPRESSED` строки, но это доп. нагрузка.
- У postgresql.`VARCHAR()` аналог mysql.`TEXT`
- `KEY (id(255))`   -- для поля `TEXT` необходимо указать размер ключа.
- `TIMESTAMP` по умолчанию в mysql - `NOT NULL`.
- Mysql.`BOOL` синоним mysql.`TINYINT(1)`, но позволяет работать с `true/false`.
- В MySQL HASH-индексы поддерживаются только в таблицах HEAP. Используются для четкого сопоставления и не позволяют извлекать диапазон в отличии от B-tree.
- `status` - это зарезервированное слово, поэтому оформление поля только через гравис \`status\`.
- `KEY message.id` не может быть `PRIMARY`, 
	- т.к. записи _'<= <> R=1RwtiW-0000T9-4K' (:blackhole:)_	отдадут одинаковый пустой id для разных записей.<br>
	А по ТЗ мы должны их тоже сохранить.
	- Тем более, что в `PRIMARY KEY` должна попасть _Вся_ запись и уместиться в размер длины индекса для однозначной идентификации. Поэтому фотмат `TEXT` для него - плохая реализация, но пока оставим как в ТЗ.

Странно что с флагом '<=' приходят события только с одного адреса tpxmuwr@somehost.ru

Из-за того что информация об адресе в таблице `message` находится сразу после флага, можем ускорить поиск, фиксированно привязать `LIKE` к левому краю.

<br><br>
### Желательно к исправлению:

- В таблице `message` не хватает индексированного поля `address`, при том что поиск делаем именно по почтовому адресу.
- Если осуществляем поиск по двум таблицам с одинаковыми данными - оптимальнее было бы иметь одинаковый набор столбцов, например для UNION.
- Либо парсить лог в Одну таблицу, т.к. данные в `message` занимают примерно 25% полезных данных лога.
- В варианте с Одной таблицей проще и удобнее делать выборку по адресу и дате с сортировкой, и не нагружать доп. работой сервер.
- Помимо этого, такой вариант позволит сделать при необходимости пагенацию страницы.

Для поиска в поле `str`, можно было бы сделать на поле `FULLTEXT` индексацию и воспользоваться `MATCH AGAINST`, <br>
... но были преценденты спонтанного разрастания FULLTEXT-индексов на таблицах InnoDB с забиванием дискового пространства.<br>
На MyISAM такой проблемы не наблюдалось.

- `DATETIME` удобнее в использовании чем `TIMESTAMP` (хотя не поддерживает ON UPDATE).
- Для поля `str` `TEXT` размером в 64kB многоват для данных. Максимальная строка в логе правее флага: 300 символов => `VARCHAR(512)`
- Для поля `address` `TEXT` также избыточен. Длина почтового поля: 64@255 => `VARCHAR(320)`
- Желательно добавить нумерацию строк в качестве `PRIMARY KEY`.




--------------------------------------------------------------------------
# Запуск
В файле _.cfg_ находятся параметры для доступа к mysql базе.<br>
Добавляем _.htaccess_ для блокирования чтения _.cfg_ и _*.pm_

Первоначально запускаем на сервере в консоле файл _init_ для проверки наличия библиотек и таблиц.<br>
``# init``

#### Комментарии к init:
- Непонятны разграничения и наличие прав на создание новой Базы/Таблицы с предоставленным login/passwd.
- Педположим что с этими правами у нас есть права на `CREATE/DROP` таблицы и база уже Cоздана, иначе нужны админские права на `CREATE DATABASE`.

Постараемся обойтись минимальным комплектом модулей, чтобы не засорять память.<br>
Первые 2 модуля обычно уже есть в базовом комплекте.
```
Data::Dumper
CGI
DBD
DBI::mysql
```
--------------------------------------------------------------------------
__Код тестировался на:__<br>
CentOS 7<br>
perl v5.16.3<br>
Apache v2.4.6 <br>
MariaDB v5.5.52<br>
Тестирование из под рутовых прав на базу.

Запуск парсера из консоли:<br>
``# log2table ./log/log.file``
- Проверяется наличие файла

Вторая версия парсера для однотабличной версии:<br>
``# log2table.v2 ./log/log.file``
- Проверяется наличие файла
- Проверяется что мы уже забирали эти данные: первые N строк уже есть в таблице.
- Попытка ускорить `INSERT`:  
	На 7500 записей ушло 75 сек.  
	Попытка с одним `prepare()` сделать цикл из `execute()`, ускорения не принесли.  
	Генерить длинный `VALUE (...),(...),(...)` нет желания из-за неопределённости в данных на отлов ошибок и инжектов.     
	Через '?,?' чужие данные надежнее паковать.  
	А вот если настроить права для пользователя telnet/apache на папку _./log_, то вариант `LOAD DATA LOCAL INFILE` занимает всего __0.25 сек__.




--------------------------------------------------------------------------
#### Web-страница:
``http://.../log2table.cgi``  
Вывод на экран флага надо оставить для понимания лога.  
Возможен неполный поиск с `mymail*`, `*@mail.ru`.
![Img1](img/scr26.png)
![Img1](img/scr24.png)


``http://.../log2table.v2.cgi`` (версия 2)  

В ``log2table.v2.cgi`` добавлена загрузка файла и запуск парсера через _web_    
Для работы загрузчика необходимо исправить права на создание/запись файлов в директорию _./log_ от имени _apache_. 

Для работы web, в папку _./js_ был залит `jquery.min` (чтобы не лезть в Inet).

![Img1](img/scr25.png)

---
##### P.S.
Подключение к вебу шаблонизаторов типа Bootstrap, Mojo..., для одностраничной задачи избыточно.

Возможны несостыковки в кодировке, т.к. тестировалось на apache/cp1251.


<br><br><br><br>



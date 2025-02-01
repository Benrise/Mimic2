# Решение команды №5

## Состав команды: 
- [Артём](https://t.me/benristar) - разработчик/ML-инженер
- [Ульяна](https://t.me/ubogd) - аналитик/промпт-инженер


## Описание
Пайплан разработки модели включает:
- Предобработку текстовых данных
- Генерацию дополнительных признаков
- Визуализацию частотного анализа
- Обучение модели логистической регрессии с использованием TF-IDF
- Экспорт модели для использования в продакшене

## Данные
Для обучения модели использовался 1 предварительно очищенный датасет:
- `bootcamp.csv` - сообщения участников диалога с меткой is_bot

Структура данных:
- `dialog_id` - идентификатор диалога
- `bot_name` - имя отправителя
- `is_bot` - метка класса (0 - человек, 1 - бот)
- `text` - текст сообщения

## Визуализации частотного анализа
### Облако слов для сообщений человека
![image](https://github.com/user-attachments/assets/7430d50c-3a12-4ee5-b867-2f4b79728532)


### Облако слов для сообщений бота
![image](https://github.com/user-attachments/assets/09e1948b-ffbc-4794-9a0c-6da25f53e74f)


## Сгенерированные признаки
- Длина текста
- Количество восклицательных и вопросительных знаков
- Количество эмодзи
- Счетчик повторяющихся слов

![image](https://github.com/user-attachments/assets/337ff45f-84c9-4bae-902f-8a471f147247)



## Обучение модели
- Использован TF-IDF с 5000 признаков
- Метрики обученной модели:
```
Accuracy: 0.75
Precision (боты): 0.78
Recall (боты): 0.56
```

## Развертывание
```bash
docker-compose up --build -d
```

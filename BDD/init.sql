USE emotion_db;

CREATE TABLE user (
    id NOT NULL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    birthdate DATE
);

CREATE TABLE texte (
    id NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    entered_text TEXT,
    publication_date DATE NOT NULL
);

COPY user
FROM 'C:\Users\Apprenant\Desktop\Dev IA\Emotion_app\BDD\user.csv' 
DELIMITER '|' 
CSV HEADER;

COPY texte
FROM 'C:\Users\Apprenant\Desktop\Dev IA\Emotion_app\BDD\text.csv' 
DELIMITER '|' 
CSV HEADER;
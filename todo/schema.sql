DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS todos;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    descr TEXT NOT NULL,
    priority TEXT NOT NULL,
    time TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    done BOOLEAN NOT NULL
    FOREIGN KEY (user_id) REFERENCES user (id)
);


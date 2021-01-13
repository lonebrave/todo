INSERT INTO user (username, password)
VALUES
    ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
    ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO todos (user_id, descr, priority, time)
VALUES
    (1, 'Test task 1', 'A', '5min'),
    (1, 'Test task 2', 'B', '1.5h'),
    (1, 'Test task 3', 'C', '3h');

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS quotes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
author TEXT NOT NULL,
text TEXT NOT NULL,
rating INTEGER NOT NULL
);
INSERT INTO quotes VALUES(1,'Rick Cook','Программирование сегодня — это гонка разработчиков программ...', 2);
INSERT INTO quotes VALUES(2,'Waldi Ravens','Программирование на С похоже на быстрые танцы на только...', 3);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('quotes',2);
COMMIT;

CREATE TABLE "operacoes" (
	"id"	INTEGER UNIQUE,
	"tipoOperacao"	INTEGER NOT NULL,
	"nomeBD"	TEXT NOT NULL,
	"associacoes"	TEXT,
	"dados"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
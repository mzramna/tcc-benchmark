CREATE TABLE "operacoes" (
	"id"	INTEGER UNIQUE,
	"tipoOperacao"	INTEGER NOT NULL,
	"nomeBD"	TEXT NOT NULL,
	"idNoBD" INTEGER NOT NULL,
	"associacoes"	TEXT,
	"dados"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "contadores" (
	"id"	INTEGER UNIQUE,
	"nomeBD"	TEXT NOT NULL,
	"numeroDDadosCadastrados" INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
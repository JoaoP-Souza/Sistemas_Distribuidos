DROP TABLE IF EXISTS "vendas";
DROP TABLE IF EXISTS "jogos";

CREATE TABLE "jogos" (
    "id" SERIAL PRIMARY KEY,
    "nome" VARCHAR(255) NOT NULL,
    "plataforma" VARCHAR(255) NOT NULL,
    "quantidade" INTEGER NOT NULL,
    "preco" FLOAT NOT NULL
);

CREATE TABLE "vendas" (
    "id" SERIAL PRIMARY KEY,
    "jogo_id" INTEGER REFERENCES jogos(id) ON DELETE CASCADE,
    "quantidade_vendida" INTEGER NOT NULL,
    "valor_venda" FLOAT NOT NULL,
    "data_venda" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO "jogos" ("nome", "plataforma", "quantidade", "preco") VALUES ('Counter Strike', 'PC', 8, 100.00);
INSERT INTO "jogos" ("nome", "plataforma", "quantidade", "preco") VALUES ('Zelda', 'Nintendo Switch', 5, 300.00);
INSERT INTO "jogos" ("nome", "plataforma", "quantidade", "preco") VALUES ('The Last of Us', 'PS5', 12, 350.00);
INSERT INTO "jogos" ("nome", "plataforma", "quantidade", "preco") VALUES ('Fable', 'Xbox', 7, 350.00);



# Script partially generated with CurreChat

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -d ".venv" ]; then
	python3 -m venv .venv
fi

./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install Flask

sqlite3 database.db < schema.sql

sqlite3 database.db <<'SQL'
INSERT OR IGNORE INTO categories (class, name) VALUES
  ('Markkina', 'OMX Helsinki'),
  ('Markkina', 'OMX Stockholm'),
  ('Markkina', 'NYSE / NASDAQ'),
  ('Markkina', 'DAX'),
  ('Markkina', 'Kehittyvät markkinat'),
  ('Markkina', 'Kryptomarkkinat'),
  ('Toimiala', 'Teknologia'),
  ('Toimiala', 'Rahoitus'),
  ('Toimiala', 'Terveydenhuolto'),
  ('Toimiala', 'Teollisuus'),
  ('Toimiala', 'Kulutustavarat'),
  ('Toimiala', 'Energia'),
  ('Toimiala', 'Kiinteistöt'),
  ('Strategia', 'Arvosijoittaminen'),
  ('Strategia', 'Kasvusijoittaminen'),
  ('Strategia', 'Osinkosijoittaminen'),
  ('Strategia', 'Indeksisijoittaminen'),
  ('Strategia', 'Laatusijoittaminen'),
  ('Strategia', 'Käänneyhtiö'),
  ('Strategia', 'Vastuullisuus / ESG');
SQL
export FLASK_APP=app
./.venv/bin/flask run

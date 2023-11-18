sqlite3 project.sqlite3 < DDL.sql
schemacrawler.sh --server=sqlite --database=project.sqlite3 --command=schema --output-format=png --output-file=diagram.png --info-level=standard --portable-names

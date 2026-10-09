CREATE TABLE IF NOT EXISTS reports (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  created     INTEGER NOT NULL,
  description TEXT    NOT NULL DEFAULT '',
  report      TEXT    NOT NULL DEFAULT '',
  screenshot  TEXT    NOT NULL DEFAULT '',
  version     TEXT    NOT NULL DEFAULT '',
  mode        TEXT    NOT NULL DEFAULT '',
  lang        TEXT    NOT NULL DEFAULT '',
  client      TEXT    NOT NULL DEFAULT '',
  status      TEXT    NOT NULL DEFAULT 'nuevo',
  note        TEXT    NOT NULL DEFAULT '',
  ip_hash     TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports (created);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports (status);
CREATE TABLE IF NOT EXISTS rate (
  ip_hash TEXT    NOT NULL,
  ts      INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rate_ip ON rate (ip_hash, ts);

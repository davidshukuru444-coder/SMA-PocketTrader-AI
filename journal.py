import json
from pathlib import Path
from typing import Dict, List, Optional


class Journal:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, row: Dict):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def all(self) -> List[Dict]:
        if not self.path.exists():
            return []
        rows = []
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return rows

    def stats(self, chat_id: Optional[int] = None):
        rows = [r for r in self.all() if r.get("status") == "CLOSED"]
        if chat_id is not None:
            rows = [r for r in rows if r.get("chat_id") == chat_id]
        wins = sum(r.get("result") == "WIN" for r in rows)
        losses = sum(r.get("result") == "LOSS" for r in rows)
        ties = sum(r.get("result") == "TIE" for r in rows)
        decisive = wins + losses
        pnl = sum(float(r.get("pnl", 0)) for r in rows)
        return {
            "trades": len(rows), "wins": wins, "losses": losses, "ties": ties,
            "win_rate": round(wins / decisive * 100, 2) if decisive else 0.0,
            "pnl": round(pnl, 2),
        }

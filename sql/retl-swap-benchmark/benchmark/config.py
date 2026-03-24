from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    host: str = "localhost"
    port: int = 5499
    dbname: str = "retl_benchmark"
    user: str = "bench"
    password: str = "bench"
    row_count: int = 16_000_000
    seed: int = 42
    batch_size: int = 50_000

    @property
    def conninfo(self) -> str:
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"

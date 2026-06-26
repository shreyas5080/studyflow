from src.database import Base, engine
import src.models as models  # noqa: F401


Base.metadata.create_all(bind=engine)

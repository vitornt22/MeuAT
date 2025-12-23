from sqlalchemy import Column, String, Float
from geoalchemy2 import Geometry
from ..database import Base


class Farm(Base):
    __tablename__ = "farms"

    imovel_code = Column(String, primary_key=True, index=True)  # cod_imovel
    city = Column(String, index=True)                         # municipio
    state_code = Column(String)                               # cod_estado
    area_size = Column(Float)                                 # num_area
    fiscal_module = Column(Float)                             # mod_fiscal
    status = Column(String)                                   # ind_status
    type = Column(String)                                     # ind_tipo
    created_at = Column(String)                               # dat_criaca
    geom = Column(Geometry('POLYGON', srid=4326))

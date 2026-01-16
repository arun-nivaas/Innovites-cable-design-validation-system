from sqlalchemy import Column, Integer, Float, Text
from ..database import Base

class ConductorSpec(Base):

    __tablename__ = "conductor_specs"

    id = Column(Integer, primary_key=True, index=True)
    csa_mm2 = Column(Float(10), nullable=False, index=True)
    
    # --- Copper Specs ---
    min_wires_cu_circular = Column(Integer)  
    min_wires_cu_compacted = Column(Integer)
    max_resistance_cu_plain = Column(Float(10))
    max_resistance_cu_tinned = Column(Float(10))
    
    # --- Aluminium Specs ---
    min_wires_al_circular = Column(Integer)
    min_wires_al_compacted = Column(Integer)

    max_resistance_al = Column(Float(10))
    
    note = Column(Text)
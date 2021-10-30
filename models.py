from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from .database import Base


class all_mut_patient(Base):
    __tablename__ = "all_mut_patient"

    id = Column(Integer, primary_key=True, index=True)
    gene_name = Column(String)
    mutation_type = Column(String)
    mutproteinPosStart = Column(Integer)
    patientId = Column(String)

class hotspots_prediction_filt(Base):
    __tablename__ = "hotspots_prediction_filt"

    id = Column(Integer, primary_key=True, index=True)
    gene_name = Column(String)
    gene_id = Column(String)
    mutation_type = Column(String)
    mut_site = Column(Integer)
    mut_count = Column(Integer)
    total_mut_count = Column(Integer)
    Hotspot_Predicted = Column(Integer)
    probability = Column(Float)

class all_hotspots(Base):
    __tablename__ = "all_hotspots"

    id = Column(Integer, primary_key=True, index=True)
    gene_name = Column(String)
    gene_id = Column(String)
    mutation_type = Column(String)
    mut_site = Column(Integer)
    mut_count = Column(Integer)
    total_mut_count = Column(Integer)
    patientid = Column(String)
    Hotspot_Predicted = Column(Integer)
    probability: Column = Column(Float)
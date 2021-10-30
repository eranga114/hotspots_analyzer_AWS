from typing import List, Optional

from pydantic import BaseModel


class all_mut_patientBase( BaseModel ):
    pass


class all_mut_patient( all_mut_patientBase ):
    id: int
    gene_name: str
    mutation_type: str
    mutproteinPosStart: int
    patientId: str

    class Config:
        orm_mode = True


class all_mut_patient_group( all_mut_patientBase ):
    gene_name: str
    patientCount: int

    class Config:
        orm_mode = True


class hotspots_prediction_filt( all_mut_patientBase ):
    id: int
    gene_name: str
    gene_id: str
    mutation_type: str
    mut_site: int
    mut_count: int
    total_mut_count: int
    Hotspot_Predicted: int
    probability: float

    class Config:
        orm_mode = True

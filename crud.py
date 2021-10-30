from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models, schemas


def get_all_mut_patient(db: Session):
    return db.query( models.all_mut_patient ).limit( 10 ).all()


def get_mut_by_genename(db: Session, gene_name: str):
    return db.query( models.all_mut_patient ).filter( models.all_mut_patient.gene_name == gene_name ).limit( 10 ).all()


def get_patient_ids(db: Session, gene_name: str, mut_type: str, mut_site: int):
    return db.query( models.all_mut_patient.patientId ). \
        filter( models.all_mut_patient.mutproteinPosStart == mut_site ). \
        filter( models.all_mut_patient.gene_name == gene_name ). \
        filter( models.all_mut_patient.mutation_type == mut_type ).all()


def get_patient_ids_group(db: Session, patient_ids: list):
    print("-----------------")
    print(patient_ids)
    return db.query( models.all_mut_patient.patientId,
                     func.count( models.all_mut_patient.id ).label( "count" ) ).filter(
        models.all_mut_patient.patientId.in_( patient_ids ) ).group_by( models.all_mut_patient.patientId ).limit(
        30 ).all()


def get_group_by_genename_mut_patientID(db: Session, patient_ids: list):
    return db.query( models.all_hotspots.gene_name, models.all_hotspots.mutation_type, models.all_hotspots.mut_site,
                     func.count( models.all_hotspots.id ).label( "count" ), models.all_hotspots.probability,models.all_hotspots.Hotspot_Predicted ).filter(
        models.all_hotspots.patientid.in_( patient_ids ) ).group_by( models.all_hotspots.gene_name,
                                                                     models.all_hotspots.mutation_type,
                                                                     models.all_hotspots.mut_site, models.all_hotspots.probability,models.all_hotspots.Hotspot_Predicted ).all()


def get_group_by_genename_patientID(db: Session, patient_ids: list):
    return db.query( models.all_hotspots.gene_name, func.count( models.all_hotspots.id ).label( "count" ) ).filter(
        models.all_hotspots.patientid.in_( patient_ids ) ).group_by( models.all_hotspots.gene_name ).all()

def get_patient_info(db: Session, patient_id: str):
    return db.query( models.all_hotspots.gene_name,models.all_hotspots.gene_id, models.all_hotspots.mutation_type,
                     models.all_hotspots.mut_site,models.all_hotspots.mut_count,models.all_hotspots.total_mut_count,
                     models.all_hotspots.probability, models.all_hotspots.Hotspot_Predicted).filter(models.all_hotspots.patientid==patient_id).all()


def get_hotspots_by_genenames(db: Session, gene_names: list):
    return db.query( models.hotspots_prediction_filt ).filter(
        models.hotspots_prediction_filt.gene_name.in_( gene_names ) ).filter(
        models.hotspots_prediction_filt.probability >= 0.7 ).all()


def get_group_by_genename(db: Session, gene_name: str):
    return db.query( models.all_mut_patient.gene_name,
                     func.count( models.all_mut_patient.patientId ).label( "patientCount" ) ).filter(
        models.all_mut_patient.gene_name == gene_name ).group_by( models.all_mut_patient.gene_name ).first()

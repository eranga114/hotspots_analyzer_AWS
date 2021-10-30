from typing import List
import pandas as pd
from fastapi import Depends, FastAPI, Form, Request, Response
from sqlalchemy.orm import Session

# from practice.main import templates
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.templating import Jinja2Templates
import pickle

with open( 'rfc_model_pickle', 'rb' ) as file:
    rf_pickle = pickle.load( file )
import uvicorn

models.Base.metadata.create_all( bind=engine )

templates = Jinja2Templates( directory="app/templates" )
app = FastAPI()


@app.middleware( "http" )
async def db_session_middleware(request: Request, call_next):
    response = Response( "Internal server error", status_code=500 )
    try:
        request.state.db = SessionLocal()
        response = await call_next( request )
    finally:
        request.state.db.close()
    return response


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
Home Page
"""
@app.get( '/' )
async def home(request: Request):
    return templates.TemplateResponse( "index.html", {"request": request} )

"""
Post Gene position, mutation count and total mutation count and run ML program and predict hotspots
"""
@app.post( '/submitform' )
async def handle_form(request: Request , startPosition: int = Form( ... ),
                      mut_count: int = Form( ... ),
                      total_mut_count: int = Form( ... ),
                      ):
    prediction = rf_pickle.predict( [[startPosition, mut_count, total_mut_count]] )

    prediction_prob = rf_pickle.predict_proba( [[startPosition, mut_count, total_mut_count]])
    li = []
    for t in prediction_prob:
        if t[1] > 0.95:
            prediction_= "High"
        elif t[1] > 0.85:
            prediction_ = "Medium"
        elif t[1] > 0.5:
            prediction_ = "Low"
        else:
            prediction_ = "Very Low"
    # li = tuple( li )

    # if prediction_prob['prob_one'] >0.95:
    #     probability = "High"
    # elif prediction_prob['prob_one'] > 0.85:
    #     probability = "Moderate"
    # else:
    #     probability = "Low"

    print(prediction_prob)
    if prediction == 1:
        hotspot = "It's a cancer hotspot"
        hot_val = 1
    else:
        hotspot = "It's not a cancer hotspot"
        hot_val = 0
    # print(prediction)
    # print(hotspot)
    return templates.TemplateResponse( "index.html", {"request": request, "prediction":prediction, "hotspot":hotspot, "prediction_":prediction_, "hot_val": hot_val} )


# @app.get( "/getAllMut", response_model=List[schemas.all_mut_patient] )
# async def getAllMut(db: Session = Depends( get_db )):
#     test = crud.get_all_mut_patient( db )
#     return test


# @app.get( "/getAllMut/{gene_name}", response_model=List[schemas.all_mut_patient] )
# async def getAllMut_byPatient(gene_name: str, db: Session = Depends( get_db )):
#     test = crud.get_mut_by_genename( db, gene_name )
#     return test
#

# @app.get( "/getAllHotspots/{gene_name}", response_model=List[schemas.hotspots_prediction_filt] )
# async def getAllHotspots(gene_name: str, db: Session = Depends( get_db )):
#     test = crud.get_hotspots_by_genename( db, gene_name.strip().upper() )
#     return test


# @app.post("/postAllHotspots", response_model=List[schemas.hotspots_prediction_filt])
# async def postAllHotspots(request: Request, gene_names: str, db: Session = Depends(get_db)):
#     # print(gene_names)
#     # print(gene_names.split(","))
#     test = crud.get_hotspots_by_genenames(db, gene_names.split(","))
#     print(test)
#     return templates.TemplateResponse( "index.html",
#                                        {"request": request,
#                                         "test": test} )

# return test

@app.post( "/postAllHotspots" )
async def postAllHotspots(request: Request, gene_names: str = Form( ... ), db: Session = Depends( get_db )):
    # print(gene_names)
    # print(gene_names.split(","))
    list_genes = [gene.strip() for gene in gene_names.split("\n")]
    print(list_genes)
    test = crud.get_hotspots_by_genenames( db, list_genes )

    li = []
    for t in test:
        if t.probability>0.95:
            li.append( (t.gene_name, t.gene_id, t.mutation_type, t.mut_site, t.mut_count, t.total_mut_count,
                    t.Hotspot_Predicted, "High") )
        elif t.probability>0.85:
            li.append( (t.gene_name, t.gene_id, t.mutation_type, t.mut_site, t.mut_count, t.total_mut_count,
                    t.Hotspot_Predicted, "Moderate") )
        else:
            li.append( (t.gene_name, t.gene_id, t.mutation_type, t.mut_site, t.mut_count, t.total_mut_count,
                        t.Hotspot_Predicted, "Low") )
    li = tuple( li )

    return templates.TemplateResponse( "index_two.html", {"request": request, "li": li} )


# @app.get("/getPatientCount/{gene_name}", response_model=schemas.all_mut_patient_group)
# async def getAllMut_byPatient_Count(gene_name: str, db: Session = Depends(get_db)):
#     test = crud.get_group_by_genename(db, gene_name)
#     return test

# @app.get("/getPatient/{gene_name}/{mut_type}/{mut_site}")
# async def getAllMut_byPatient_Count(gene_name: str,mut_type:str,mut_site:int, db: Session = Depends(get_db)):
#     print(gene_name)
#     print(mut_type)
#     print(mut_site)
#     test = set(crud.get_patient_ids(db, gene_name,mut_type,mut_site))
#
#     patientids = []
#
#     for id in test:
#         patientids.append(id.patientId)
#
#
#     result = crud.get_group_by_genename_patientID(db,patientids)
#
#     li = []
#     for t in result:
#         li.append((t.gene_name,t.count))
#
#     li = sorted(li,key=lambda x:x[1],reverse=True)
#     li = tuple( li[0:20] )
#     return li
@app.get( "/getmutpaty/{gene_names}/{mut_type}/{mut_site}" )
async def getpatmut(request: Request, gene_names, mut_type, mut_site, db: Session = Depends( get_db )):
    gene_names_group = set( crud.get_patient_ids( db, gene_names, mut_type, mut_site ) )

    patientids_genes_group = []

    for id in gene_names_group:
        patientids_genes_group.append( id.patientId )

    result_genes_group = crud.get_group_by_genename_patientID(db, patientids_genes_group )

    lis_genes_group = []
    for t in result_genes_group:
        lis_genes_group.append( (t.gene_name, t.count) )

    lis_genes_group = sorted( lis_genes_group, key=lambda x: x[1], reverse=True )
    lis_genes_group = tuple( lis_genes_group[0:20] )

    result_genes_mut_group = crud.get_group_by_genename_mut_patientID( db, patientids_genes_group )

    lis_genes_mut_group = []
    for t in result_genes_mut_group:
        lis_genes_mut_group.append( (t.gene_name, t.mutation_type, t.mut_site, t.count,t.Hotspot_Predicted,t.probability) )

    lis_genes_mut_group = sorted( lis_genes_mut_group, key=lambda x: x[3], reverse=True )
    lis_genes_mut_group = tuple( lis_genes_mut_group[0:20] )

    # return lis_genes_mut_group
    return templates.TemplateResponse( "index_mut.html",
                                       {"request": request,
                                        "lis_genes_group": lis_genes_group,
                                        "list_genes_mut_group": lis_genes_mut_group,
                                       "gene_names":gene_names, "mut_type": mut_type, "mut_site":mut_site} )

"""
@app.post( "/postmutpat" )
async def getAllMut_byPatient_Count(request: Request, gene_names: str = Form( ... ), mut_type: str = Form( ... ),
                                    mut_site: int = Form( ... ),  pat = None, gene= None, db: Session = Depends( get_db )):
    # print( gene_names )
    # print( mut_type )
    # print( mut_site )
    # print(gene)
    # print(pat)
    gene_names_group = set( crud.get_patient_ids( db, gene_names, mut_type, mut_site ) )

    patientids_genes_group = []

    for id in gene_names_group:
        patientids_genes_group.append( id.patientId )

    result_genes_group = crud.get_group_by_genename_patientID( db, patientids_genes_group )

    lis_genes_group = []
    for t in result_genes_group:
        lis_genes_group.append( (t.gene_name, t.count) )

    lis_genes_group = sorted( lis_genes_group, key=lambda x: x[1], reverse=True )
    lis_genes_group = tuple( lis_genes_group[0:20] )

    result_genes_mut_group = crud.get_group_by_genename_mut_patientID( db, patientids_genes_group )

    lis_genes_mut_group = []
    for t in result_genes_mut_group:
        lis_genes_mut_group.append( (t.gene_name,t.mutation_type,t.mut_site, t.count) )

    lis_genes_mut_group = sorted( lis_genes_mut_group, key=lambda x: x[3], reverse=True )
    lis_genes_mut_group = tuple( lis_genes_mut_group[0:20] )

    # return lis_genes_mut_group
    return templates.TemplateResponse( "index_mut.html",
                                       {"request": request,
                                        "lis_genes_group": lis_genes_group,
                                        "list_genes_mut_group":lis_genes_mut_group} )
"""

@app.get( "/getpat/{gene_names}/{mut_type}/{mut_site}")
async def getpatdata(request: Request, gene_names, mut_type, mut_site, db: Session = Depends( get_db )):
    patiend_ids = set( crud.get_patient_ids( db, gene_names, mut_type, mut_site ) )
    print("GENE NAME................................")
    print(gene_names)
    patient_id_list = []
    for id in patiend_ids:
        patient_id_list.append(id.patientId)
    patient_count = crud.get_patient_ids_group( db, patient_id_list)
    # print(patient_count)

    lis_patientid_group = []
    i = 1
    for t in patient_count:
        lis_patientid_group.append( (t.patientId, t.count,i) )
        i+=1

    lis_patientid_group = sorted( lis_patientid_group, key=lambda x: x[1] )
    lis_patientid_group = tuple( lis_patientid_group )

    # return lis_patientid_group
    return templates.TemplateResponse( "index_pat.html",
                                       {"request": request,
                                        "lis_patientid_group": lis_patientid_group} )


"""
get the patient_id from the index_pat.html and return mutation profile of the patient id 
"""
@app.get("/getpatall/{patient_id}")
async def getAllMut_byPatient_Count(request: Request, patient_id, db: Session = Depends( get_db )):
    patiend_ids = set( crud.get_patient_info( db, patient_id ) )

    lis_patientid_group = []

    i = 1
    for t in patiend_ids:
        # if t.probability>0.95:
        lis_patientid_group.append( (t.gene_name, t.gene_id, t.mutation_type, t.mut_site, t.mut_count, t.total_mut_count, t.Hotspot_Predicted, t.probability) )
        i+=1

    # lis_patientid_group = sorted( lis_patientid_group, key=lambda x: x[1] )
    lis_patientid_group = tuple( lis_patientid_group )

    # return lis_patientid_group
    return templates.TemplateResponse( "index_pat_two.html",
                                       {"request": request,
                                        "lis_patientid_group": lis_patientid_group} )




@app.post( "/postpatientfullinfo" )
async def getAllMut_byPatient_Count(request: Request, patient_id: str = Form( ... ), db: Session = Depends( get_db )):
    patiend_ids = set( crud.get_patient_info( db, patient_id ) )

    lis_patientid_group = []

    i = 1
    for t in patiend_ids:
        lis_patientid_group.append( (t.gene_name, t.gene_id, t.mutation_type, t.mut_site, t.mut_count, t.total_mut_count, t.Hotspot_Predicted, t.probability) )
        i+=1

    # lis_patientid_group = sorted( lis_patientid_group, key=lambda x: x[1] )
    lis_patientid_group = tuple( lis_patientid_group )

    # return lis_patientid_group
    return templates.TemplateResponse( "index_mut.html",
                                       {"request": request,
                                        "li": lis_patientid_group} )

@app.post( "/posttest" )
async def predict(protein_name: str = Form( ... )):
    print( protein_name )
    return {'post': protein_name}

# if __name__ == "__main__":
#     uvicorn.run(app, host= 'localhost', port = 8888)

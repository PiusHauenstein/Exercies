# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# File:     EB_to_Lines.py
#
# Projekt:  GKGR 2.0
# Author:   P. Hauenstein
# Version:  0.1.0 (xx.11.2021)
#
# Zweck:    Umwandlung der Polygone der Erfassungsbereiche in Linien, damit die Attribute
#           als Liniensymbole dargestellt werden können
#
# Input-Parameter:
#    <Input-FeatureClass mit EB_F>  (muss vorhanden sein)
#    <Output-FeatureClass mit EB_L> (muss vorhanden sein)
#
# Historie:
# 29.11.2021 Pius Hauenstein             Erstellung (V0.1.0)
#
# =========================================================================
# Copyright:
#
# Amt für Wald und Naturgefahren Graubünden
# Ringstrasse 10
# CH-7001 Chur
# =========================================================================
# Standard library imports
import sys
import datetime

# Third party imports
import arcpy


# -----------------------------------------------------------------------------
# Erstellung der EB-Linien-FeatureClass
def func_Create_EB_L(Input_EB_F, Tmp_EB_L):
    # Nur gültige EB
    arcpy.MakeFeatureLayer_management(in_features=Input_EB_F,
                                      out_layer="EB_F_Layer",
                                      where_clause="VERBINDLICHKEIT in ( 'B', 'E') AND DATE_IN IS NOT NULL AND DATE_OUT IS NULL")

    arcpy.PolygonToLine_management(in_features="EB_F_Layer",
                                   out_feature_class=Tmp_EB_L,
                                   neighbor_option="IDENTIFY_NEIGHBORS")

    arcpy.JoinField_management(in_data=Tmp_EB_L,
                               in_field="LEFT_FID",
                               join_table=Input_EB_F,
                               join_field="OBJECTID",
                               fields="EB_KATASTER")

    arcpy.JoinField_management(in_data=Tmp_EB_L,
                               in_field="RIGHT_FID",
                               join_table=Input_EB_F,
                               join_field="OBJECTID",
                               fields="EB_KATASTER")

    arcpy.AddField_management(in_table=Tmp_EB_L,
                              field_name="EB_L_KATASTER",
                              field_type="SHORT",
                              field_precision="",
                              field_scale="",
                              field_length="",
                              field_alias="",
                              field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED",
                              field_domain="")

    arcpy.MakeFeatureLayer_management(in_features=Tmp_EB_L,
                                      out_layer="EB_L_Layer")

    arcpy.SelectLayerByAttribute_management(in_layer_or_view="EB_L_Layer",
                                            selection_type="NEW_SELECTION",
                                            where_clause="(EB_KATASTER IS NULL AND EB_KATASTER_1 = 1) or ( EB_KATASTER = 1 AND EB_KATASTER_1 IS NULL) or ( EB_KATASTER = 1 AND EB_KATASTER_1 = 1)")

    arcpy.CalculateField_management(in_table="EB_L_Layer",
                                    field="EB_L_KATASTER",
                                    expression="1",
                                    expression_type="VB",
                                    code_block="")

    arcpy.SelectLayerByAttribute_management(in_layer_or_view="EB_L_Layer",
                                            selection_type="NEW_SELECTION",
                                            where_clause="(EB_KATASTER IS NULL AND EB_KATASTER_1 = 2) or ( EB_KATASTER = 2 AND EB_KATASTER_1 IS NULL) or ( EB_KATASTER = 2 AND EB_KATASTER_1 = 2)")

    arcpy.CalculateField_management(in_table="EB_L_Layer",
                                    field="EB_L_KATASTER",
                                    expression="2",
                                    expression_type="VB",
                                    code_block="")

    arcpy.SelectLayerByAttribute_management(in_layer_or_view="EB_L_Layer",
                                            selection_type="NEW_SELECTION",
                                            where_clause="(EB_KATASTER = 1 AND EB_KATASTER_1 = 2) or (EB_KATASTER = 2 AND EB_KATASTER_1 = 1)")

    arcpy.CalculateField_management(in_table="EB_L_Layer",
                                    field="EB_L_KATASTER",
                                    expression="3",
                                    expression_type="VB",
                                    code_block="")

    arcpy.MakeFeatureLayer_management(in_features=Tmp_EB_L,
                                      out_layer="EB_L_Output_Layer",
                                      where_clause="",
                                      workspace="",
                                      field_info="OBJECTID OBJECTID VISIBLE NONE;Shape Shape VISIBLE NONE;LEFT_FID LEFT_FID HIDDEN NONE;RIGHT_FID RIGHT_FID HIDDEN NONE;EB_KATASTER EB_KATASTER HIDDEN NONE;EB_KATASTER_1 EB_KATASTER_1 HIDDEN NONE;EB_L_KATASTER EB_KATASTER VISIBLE NONE")

    return()


# -----------------------------------------------------------------------------
# Ergebnis wird in die Output-FC geschrieben
def func_Import_to_SDE(Source, Target):
    arcpy.CopyFeatures_management(in_features=Source,
                                  out_feature_class=Target,
                                  config_keyword="",
                                  spatial_grid_1="0",
                                  spatial_grid_2="0",
                                  spatial_grid_3="0")
    #
    # arcpy.DeleteFeatures_management(TargetFC)
    # arcpy.Append_management(inputs=SourceFC,
    #                         target=TargetFC,
    #                         schema_type="NO_TEST", )
    return()


# -----------------------------------------------------------------------------
# Ergebnis wird in die Output-FC geschrieben
def func_CleanUp(Tmp_EB_L):
    for i in ['EB_L_Output_Layer', "EB_L_Layer", "EB_F_Layer", Tmp_EB_L]:
        arcpy.Delete_management(i)

    return()


# -----------------------------------------------------------------------------
def main(Input_EB_F, Output_EB_L):
    Tmp_EB_L = r'in_memory\Tmp_EB_L'
    func_Create_EB_L(Input_EB_F, Tmp_EB_L)
    func_Import_to_SDE('EB_L_Output_Layer', Output_EB_L)
    func_CleanUp(Tmp_EB_L)
    return()


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Input-Parameter
    Input_EB_F  = str(sys.argv[1])
    Output_EB_L = str(sys.argv[2])

    T1 = datetime.datetime.now()
    main(Input_EB_F, Output_EB_L)
    T2 = datetime.datetime.now()
    arcpy.AddMessage("%s EB_L fertig berechnet (Dauer: %s)." % (T2, T2 - T1))

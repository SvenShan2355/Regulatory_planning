# -*- coding: utf-8 -*-
"""
by Sven_SHAN  2022.7.21
"""
import os
import arcpy
from arcpy import analysis
from arcpy import management


def Model(centerline_path, interchanges, output_path, buffer_distance, chamfer_distance):  # 模型
    '''
    参数（中心线图层, 输出目录, 缓冲距离字段名称[缓冲距离为红线宽度的一半], 倒角距离字段名称）
    '''

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = False

    arcpy.ImportToolbox(r"c:\program files\arcgis\pro\Resources\ArcToolbox\toolboxes\Data Management Tools.tbx")
    # Model Environment settings
    with arcpy.EnvManager(
            cartographicCoordinateSystem="PROJCS[\"CGCS2000_3_Degree_GK_Zone_37\",GEOGCS[\"GCS_China_Geodetic_Coordinate_System_2000\",DATUM[\"D_China_2000\",SPHEROID[\"CGCS2000\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Gauss_Kruger\"],PARAMETER[\"False_Easting\",37500000.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",111.0],PARAMETER[\"Scale_Factor\",1.0],PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]]",
            scratchWorkspace=r"C:\Users\Administrator\Documents\ArcGIS\Default.gdb",
            workspace=r"C:\Users\Administrator\Documents\ArcGIS\Default.gdb"):
        arcpy.management.CreateFileGDB("C:\\", "TEMP_GDB", "CURRENT")

        # 整合路网
        road_carding1 = "C:\\TEMP_GDB.gdb\\road_carding"
        arcpy.management.Dissolve(in_features=centerline_path, out_feature_class=road_carding1,
                                  dissolve_field=[buffer_distance, chamfer_distance], statistics_fields=None,
                                  multi_part="MULTI_PART", unsplit_lines="UNSPLIT_LINES")

        # Process: 缓冲区 (缓冲区) (analysis)
        Undissolve_roadsurface = "C:\\TEMP_GDB.gdb\\Undissolve_roadsurface"
        arcpy.analysis.Buffer(in_features=road_carding1, out_feature_class=Undissolve_roadsurface,
                              buffer_distance_or_field=buffer_distance, line_side="FULL", line_end_type="FLAT",
                              dissolve_option="NONE", dissolve_field=[], method="PLANAR")
        print("complete Process: 缓冲区 (缓冲区) (analysis)")

        # Process: 面转线 (面转线) (management)
        Basic_boundary = "C:\\TEMP_GDB.gdb\\Basic_boundary"
        arcpy.management.PolygonToLine(in_features=Undissolve_roadsurface, out_feature_class=Basic_boundary,
                                       neighbor_option="IDENTIFY_NEIGHBORS")
        print("complete Process: 面转线 (面转线) (management)")

        # Process: 选择 (选择) (analysis)
        Selected_boundary = "C:\\TEMP_GDB.gdb\\Selected_boundary"
        arcpy.analysis.Select(in_features=Basic_boundary, out_feature_class=Selected_boundary,
                              where_clause="LEFT_FID = -1")
        print("complete Process: 选择 (选择) (analysis)")

        # Process: 标识 (2) (标识) (analysis)
        Selected_boundary_with_road_attribute = "C:\\TEMP_GDB.gdb\\Selected_boundary_with_road_attribute"
        arcpy.analysis.Identity(in_features=Selected_boundary, identity_features=Undissolve_roadsurface,
                                out_feature_class=Selected_boundary_with_road_attribute, join_attributes="ALL",
                                cluster_tolerance="", relationship="NO_RELATIONSHIPS")
        print("complete Process: 标识 (2) (标识) (analysis)")

        # Process: 要素折点转点 (要素折点转点) (management)
        Vertices_point = "C:\\TEMP_GDB.gdb\\Vertices_point"
        arcpy.management.FeatureVerticesToPoints(in_features=Selected_boundary_with_road_attribute,
                                                 out_feature_class=Vertices_point, point_location="BOTH_ENDS")
        print("complete Process: 要素折点转点 (要素折点转点) (management)")

        # Process: 缓冲区 (2) (缓冲区) (analysis)
        group_buffer1 = "C:\\TEMP_GDB.gdb\\group_buffer1"
        arcpy.analysis.Buffer(in_features=Vertices_point, out_feature_class=group_buffer1,
                              buffer_distance_or_field="1 Meters", line_side="FULL", line_end_type="ROUND",
                              dissolve_option="ALL", dissolve_field=[], method="PLANAR")
        print("complete Process: 缓冲区 (2) (缓冲区) (analysis)")

        # Process: 多部件至单部件 (多部件至单部件) (management)
        Group_buffer2 = "C:\\TEMP_GDB.gdb\\Group_buffer2"
        arcpy.management.MultipartToSinglepart(in_features=group_buffer1, out_feature_class=Group_buffer2)
        print("complete Process: 多部件至单部件 (多部件至单部件) (management)")

        # Process: 标识 (标识) (analysis)
        Grouped_point = "C:\\TEMP_GDB.gdb\\Grouped_point"
        arcpy.analysis.Identity(in_features=Vertices_point, identity_features=Group_buffer2,
                                out_feature_class=Grouped_point, join_attributes="ALL", cluster_tolerance="",
                                relationship="NO_RELATIONSHIPS")
        print("complete Process: 标识 (标识) (analysis)")

        # 通过融合操作将同一组的点的倒角距离设置为两线倒角距离的均值
        Dissolve_point = "C:\\TEMP_GDB.gdb\\Dissolve_point"
        arcpy.analysis.PairwiseDissolve(in_features=Grouped_point, out_feature_class=Dissolve_point,
                                        dissolve_field="FID_Group_buffer2",
                                        statistics_fields=[[chamfer_distance, "MEAN"]], multi_part="SINGLE_PART")

        # Process: 缓冲区 (3) (缓冲区) (analysis)
        buffer_by_Chamfer_distance = "C:\\TEMP_GDB.gdb\\buffer_by_Chamfer_distance"
        arcpy.analysis.Buffer(in_features=Dissolve_point, out_feature_class=buffer_by_Chamfer_distance,
                              buffer_distance_or_field="MEAN_" + chamfer_distance, line_side="FULL",
                              line_end_type="ROUND",
                              dissolve_option="NONE", dissolve_field=[], method="PLANAR")
        print("complete Process: 缓冲区 (3) (缓冲区) (analysis)")

        # Process: 标识 (3) (标识) (analysis)
        Selected_boundary_identity = "C:\\TEMP_GDB.gdb\\Selected_boundary_identity"
        arcpy.analysis.Identity(in_features=Selected_boundary,
                                identity_features=buffer_by_Chamfer_distance,
                                out_feature_class=Selected_boundary_identity, join_attributes="ALL",
                                cluster_tolerance="", relationship="NO_RELATIONSHIPS")
        print("complete Process: 标识 (3) (标识) (analysis)")

        # Process: 选择 (2) (选择) (analysis)
        # Two_line = "C:\\TEMP_GDB.gdb\\Two_line"
        # arcpy.analysis.Select(in_features=Selected_boundary_identity, out_feature_class=Two_line,
        #                       where_clause="RIGHT_FID = RIGHT_FID_1")

        # 由于不需要再选择每条路对应的缓冲距离，因此不再需要提前对路进行标识，通过被上一步缓冲圆的标识提取三角形双线
        Two_line = "C:\\TEMP_GDB.gdb\\Two_line"
        arcpy.analysis.Select(in_features=Selected_boundary_identity, out_feature_class=Two_line,
                              where_clause="FID_Group_buffer2 <> 0")
        print("complete Process: 选择 (2) (选择) (analysis)")

        # Process: 融合 (融合) (management)
        Two_line_Dissolve = "C:\\TEMP_GDB.gdb\\Two_line_Dissolve"
        arcpy.management.Dissolve(in_features=Two_line, out_feature_class=Two_line_Dissolve,
                                  dissolve_field=["FID_Group_buffer2"], statistics_fields=[], multi_part="MULTI_PART",
                                  unsplit_lines="DISSOLVE_LINES")
        print("complete Process: 融合 (融合) (management)")

        # Process: 要素折点转点 (2) (要素折点转点) (management)
        Third_line_point = "C:\\TEMP_GDB.gdb\\Third_line_point"
        arcpy.management.FeatureVerticesToPoints(in_features=Two_line_Dissolve, out_feature_class=Third_line_point,
                                                 point_location="BOTH_ENDS")
        print("complete Process: 要素折点转点 (2) (要素折点转点) (management)")

        # Process: 点集转线 (点集转线) (management)
        Third_line = "C:\\TEMP_GDB.gdb\\Third_line"
        arcpy.management.PointsToLine(Input_Features=Third_line_point, Output_Feature_Class=Third_line,
                                      Line_Field="FID_Group_buffer2", Sort_Field="", Close_Line="CLOSE")
        print("complete Process: 点集转线 (点集转线) (management)")

        # Process: 要素转面 (要素转面) (management)
        basic_Triangle = "C:\\TEMP_GDB.gdb\\basic_Triangle"
        arcpy.management.FeatureToPolygon(in_features=[Two_line, Third_line], out_feature_class=basic_Triangle,
                                          cluster_tolerance="", attributes="ATTRIBUTES", label_features="")
        print("complete Process: 要素转面 (要素转面) (management)")

        # Process: 融合 (3) (融合) (management)
        basic_Triangle_dissolve1 = "C:\\TEMP_GDB.gdb\\basic_Triangle_dissolve1"
        arcpy.management.Dissolve(in_features=basic_Triangle, out_feature_class=basic_Triangle_dissolve1,
                                  dissolve_field=[], statistics_fields=[], multi_part="MULTI_PART",
                                  unsplit_lines="DISSOLVE_LINES")
        print("complete Process: 融合 (3) (融合) (management)")

        # Process: 多部件至单部件 (2) (多部件至单部件) (management)
        basic_Triangle_dissolve2 = "C:\\TEMP_GDB.gdb\\basic_Triangle_dissolve2"
        arcpy.management.MultipartToSinglepart(in_features=basic_Triangle_dissolve1,
                                               out_feature_class=basic_Triangle_dissolve2)
        print("complete Process: 多部件至单部件 (2) (多部件至单部件) (management)")

        # Process: 空间连接 (空间连接) (analysis)
        basic_Triangle_spatialjoin = "C:\\TEMP_GDB.gdb\\basic_Triangle_spatialjoin"
        arcpy.analysis.SpatialJoin(target_features=basic_Triangle_dissolve2, join_features=Undissolve_roadsurface,
                                   out_feature_class=basic_Triangle_spatialjoin, join_operation="JOIN_ONE_TO_MANY",
                                   join_type="KEEP_ALL",
                                   match_option="SHARE_A_LINE_SEGMENT_WITH", search_radius="", distance_field_name="")
        print("complete Process: 空间连接 (空间连接) (analysis)")

        # Process: 融合 (2) (融合) (management)
        Triangle_joincont = "C:\\TEMP_GDB.gdb\\Triangle_joincont"
        arcpy.management.Dissolve(in_features=basic_Triangle_spatialjoin, out_feature_class=Triangle_joincont,
                                  dissolve_field=["TARGET_FID"], statistics_fields=[["Join_Count", "SUM"]],
                                  multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
        print("complete Process: 融合 (2) (融合) (management)")

        # Process: 选择 (3) (选择) (analysis)
        Selected_Triangle1 = "C:\\TEMP_GDB.gdb\\Selected_Triangle1"
        arcpy.analysis.Select(in_features=Triangle_joincont, out_feature_class=Selected_Triangle1,
                              where_clause="SUM_Join_Count <> 1")
        print("complete Process: 选择 (3) (选择) (analysis)")

        # Process: 选择 (4) (选择) (analysis)
        Undetermined_Triangle = "C:\\TEMP_GDB.gdb\\Undetermined_Triangle"
        arcpy.analysis.Select(in_features=Triangle_joincont, out_feature_class=Undetermined_Triangle,
                              where_clause="SUM_Join_Count = 1")
        print("complete Process: 选择 (4) (选择) (analysis)")

        # Process: 空间连接 (2) (空间连接) (analysis)
        Undetermined_Triangle_check = "C:\\TEMP_GDB.gdb\\Undetermined_Triangle_check"
        arcpy.analysis.SpatialJoin(target_features=Undetermined_Triangle, join_features=centerline_path,
                                   out_feature_class=Undetermined_Triangle_check, join_operation="JOIN_ONE_TO_ONE",
                                   join_type="KEEP_ALL", match_option="CROSSED_BY_THE_OUTLINE_OF")
        print("complete Process: 空间连接 (空间连接) (analysis)")

        # Process: 选择 (5) (选择) (analysis)
        Undetermined_Triangle_2 = "C:\\TEMP_GDB.gdb\\Undetermined_Triangle1"
        arcpy.analysis.Select(in_features=Undetermined_Triangle_check, out_feature_class=Undetermined_Triangle_2,
                              where_clause="Join_Count = 0")
        print("complete Process: 选择 (5) (选择) (analysis)")

        # Process: 选择 (6) (选择) (analysis)
        Selected_Triangle_2 = "C:\\TEMP_GDB.gdb\\Selected_Triangle2"
        arcpy.analysis.Select(in_features=Undetermined_Triangle_check, out_feature_class=Selected_Triangle_2,
                              where_clause="Join_Count <> 0")
        print("complete Process: 选择 (6)  (analysis)")

        # Process: 合并 (management)
        Triangle_output = "C:\\TEMP_GDB.gdb\\Triangle_output"
        arcpy.management.Merge(inputs=[Selected_Triangle1, Selected_Triangle_2], output=Triangle_output)
        print("complete Process: 合并 (management)")

        Merge_Roads = "C:\\TEMP_GDB.gdb\\Merge_Road"
        arcpy.management.Merge(inputs=[Triangle_output, Undissolve_roadsurface, interchanges], output=Merge_Roads)
        print("complete Process: 合并 (management)")

        output_roads = os.path.join(output_path, "output_roads_20230328")
        arcpy.management.Dissolve(in_features=Merge_Roads, out_feature_class=output_roads)

        arcpy.management.Delete(r"C:\TEMP_GDB.gdb", '')
        print("清除缓存")

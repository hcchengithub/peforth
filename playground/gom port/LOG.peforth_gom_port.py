
13:57 2020/11/11 extension name 用 .py 方便收合大結構

[X] 17:56 2020/09/23 用 peforth 查看 gom.app.project.parts['Part'].actual 的 (幾乎) 完整 properties
	\ This is the source code
		# -*- coding: utf-8 -*-

		import gom
		import peforth, peforth_gom_port

		#debug = True
		#if debug: peforth.ok('11>',loc=locals())

		gom.script.cad.hide_element (elements=[gom.app.project.parts['Part'].actual]) # mesh

		gom.script.cad.show_element (elements=[gom.app.project.parts['Part'].nominal]) # CAD

		CAD_ALIGNMENT=gom.script.alignment.create_prealignment (
			computation_mode='normal',
			compute_additional_bestfit=True,
			name_expression='Prealignment',
			parent_alignment=gom.app.project.parts['Part'].original_alignment,
			part=gom.app.project.parts['Part'])

		peforth.ok(cmd='py: help(ok)')

	\ gets all properties
	\ gom :> app.project.parts['Part'].actual.__doc__ . cr

	\ utilize peforth to run batch to dump all of them
	\ include c:\Users\8304018\Downloads\1
	\ These are the results

	OK include c:\Users\8304018\Downloads\1
	gom :> app.project.parts['Part'].actual.active_actual_mesh										   --> gom_part_measurement (<class 'str'>)
	gom :> app.project.parts['Part'].actual.active_height											   --> 433 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.active_width											   --> 849 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.actual_master											   --> gom_part_measurement (<class 'str'>)
	gom :> app.project.parts['Part'].actual.actual_type_text										   --> actual (<class 'str'>)
	gom :> app.project.parts['Part'].actual.alignment												   --> <Trait: Tom::CADAlignmentResult> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.alignment												   --> <Trait: Tom::CADAlignmentResult> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.alignment_at_calculation								   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.alignment_for_visualized_report_elements				   --> <Trait: Tom::CADAlignmentResult> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.allowed_temperature_difference							   --> 5.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.application_build_information							   --> <Trait: Tom::ApplicationInformation> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.application_name										   --> GOM Inspect Suite (<class 'str'>)
	gom :> app.project.parts['Part'].actual.application_version										   --> 2020-0 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.are_measurements_aligned								   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.area													   --> 207422.1875 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.assembly_tree											   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.automatic_exposure_time_mode							   --> no_exposure_computation (<class 'str'>)
	gom :> app.project.parts['Part'].actual.automatic_exposure_time_photogrammetry_mode				   --> no_exposure_computation (<class 'str'>)
	gom :> app.project.parts['Part'].actual.automation_move_to_endposition_on_abort					   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.avoid_points_at_strong_brightness_differences			   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.avoid_points_in_shadow_areas							   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.avoid_points_on_borders_in_scan_area					   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.avoid_points_on_groove_edges							   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.avoid_points_on_shiny_surfaces							   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.avoid_triple_scan_points								   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.avoid_triple_scan_points_at_strong_brightness_differences  --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.bounding_box											   --> <Trait: Tom::CAD::BoundingBox> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.cad_conversion_parameter								   --> <Trait: Tom::CAD::CadConvertParameter> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.cad_group												   --> gom_part (<class 'str'>)
	gom :> app.project.parts['Part'].actual.check_decalibrated_sensor								   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.check_lighting_change									   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.check_measurement_temperature							   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.check_missing_reference_points							   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.check_sensor_movement									   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.check_text												   --> check_text (<class 'str'>)
	gom :> app.project.parts['Part'].actual.check_transformation									   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.comment													   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.computation_error_code									   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.computation_information									   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.computation_status										   --> computed (<class 'gomlib.types.ComputationStatus'>)
	gom :> app.project.parts['Part'].actual.coordinate												   --> Indexable (item=gom.app.project.parts['Part'].actual, token=coordinate, size=709567) (<class 'gom.Indexable'>)
	gom :> app.project.parts['Part'].actual.creation_command_is_active								   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.creation_sequence										   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.creation_sequence_args									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.current_date											   --> 2020/09/23 (<class 'gomlib.types.Date'>)
	gom :> app.project.parts['Part'].actual.current_report_page										   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.current_stage_range										   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.current_user											   --> 8304018 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.currently_used_gpu_memory								   --> 760896 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.date_format												   --> [<Trait: Tom::DateFormatTrait>, <Trait: Tom::DateFormatTrait>, <Trait: Tom::DateFormatTrait>, <Trait: Tom::DateFormatTrait>, <Trait: Tom::DateFormatTrait>, <Trait: Tom::DateFormatTrait>, <Trait: Tom::DateFormatTrait>, <Trait: Tom::DateFormatTrait>, <Trait: Tom::DateFormatTrait>, <Trait: Tom::DateFormatTrait>] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.default_directory										   --> C:\Users\8304018\Documents (<class 'str'>)
	gom :> app.project.parts['Part'].actual.default_templates_info_draft							   --> {"element_properties":{"name":"Inspection","package":{"is_protected":false,"name":"Inspection","uuid":"a6769fbc-4bda-4cec-af9a-b189baf8b742","version":"1.0.0"},"uuid":"834f09ce-3daa-4fb6-a11d-309f2eb98523","variant":""},"keywordset":{"name":"Default","package":{"is_protected":false,"name":"Inspection","uuid":"a6769fbc-4bda-4cec-af9a-b189baf8b742","version":"1.0.0"},"uuid":"52d5e460-4ab2-4638-b647-3a3a9f43c3ab","variant":"en"}} (<class 'str'>)
	gom :> app.project.parts['Part'].actual.dependency_children										   --> {'actual_elements': [gom.app.project.parts['Part'].actual], 'nominal_elements': [], 'other_elements': []} (<class 'dict'>)
	gom :> app.project.parts['Part'].actual.depends_directly_on_elements							   --> {'actual_elements': [], 'nominal_elements': [], 'other_elements': []} (<class 'dict'>)
	gom :> app.project.parts['Part'].actual.depends_on_part_objects_draft							   --> [gom.app.project.parts['Part']] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.depth_limitation_mode									   --> calibrated (<class 'str'>)
	gom :> app.project.parts['Part'].actual.deviation_text											   --> deviation_text (<class 'str'>)
	gom :> app.project.parts['Part'].actual.dump_geo_surface_database								   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.element_could_represent_actual_part						   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.element_keywords										   --> [] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.exception_decalibrated_sensor_abort						   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.exception_decalibrated_sensor_delay						   --> 0.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.exception_decalibrated_sensor_number_of_repetitions		   --> 0 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.exception_lighting_change_abort							   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.exception_lighting_change_delay							   --> 0.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.exception_lighting_change_number_of_repetitions			   --> 3 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.exception_measurement_temperature_abort					   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.exception_measurement_temperature_delay					   --> 0.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.exception_measurement_temperature_number_of_repetitions	   --> 0 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.exception_sensor_movement_abort							   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.exception_sensor_movement_delay							   --> 0.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.exception_sensor_movement_number_of_repetitions			   --> 3 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.exception_transformation_abort							   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.exception_transformation_delay							   --> 0.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.exception_transformation_number_of_repetitions			   --> 0 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.explorer_category										   --> actual_part (<class 'str'>)
	gom :> app.project.parts['Part'].actual.explorer_tooltip										   --> export mesh to external application. (<class 'str'>)
	gom :> app.project.parts['Part'].actual.explorer_type_and_state									   --> mesh (<class 'gomlib.types.ObjectTypeAndState'>)
	gom :> app.project.parts['Part'].actual.first_measurement_date									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.first_measurement_time									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.gdat_tolerance_table									   --> <Trait: Tom::CAD::ToleranceTable> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.general_tolerance_table									   --> <Trait: Tom::CAD::ToleranceTable> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.gom_collision_check_since_load_import_copy_draft		   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.hole													   --> Indexable (item=gom.app.project.parts['Part'].actual, token=hole, size=10) (<class 'gom.Indexable'>)
	gom :> app.project.parts['Part'].actual.home_directory											   --> C:\Users\8304018\Documents (<class 'str'>)
	gom :> app.project.parts['Part'].actual.import_file												   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.import_file_name										   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.import_information										   --> <Trait: Tom::ImportInformationTrait> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.imported_name											   --> gom_part_measurement (<class 'str'>)
	gom :> app.project.parts['Part'].actual.inspections_not_in_reports								   --> [] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.inspections_out_of_tolerance							   --> [] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.is_active												   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_auto_recalc_enabled									   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_auto_recalc_for_stages_enabled						   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_element_in_clipboard									   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_element_modified_since_import						   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_global_csys_view_csys								   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_inspection_from_v7sr2								   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_label_visible										   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_modified												   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_modified_after_loading								   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_name_generated										   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_part_project											   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_part_representative_draft							   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_quality_triple_scan_points_checked					   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_referenced_in_inspection								   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_selected												   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_system_element										   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_visibility_locked									   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.is_visible												   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.kiosk_mode												   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.label													   --> <Trait: Tom::CAD::LabelInfo> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.label_offset_in_3d_view									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.language												   --> en (<class 'str'>)
	gom :> app.project.parts['Part'].actual.last_measurement_date									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.last_measurement_time									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.legend													   --> <Trait: Tom::Legend2::LegendInfo> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.local_all_directory										   --> C:\ProgramData\gom\2020 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.max_reference_points_depth_limitation					   --> 150.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.max_residual											   --> 0.2 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.max_residual_edge_point_adjustment						   --> 0.25 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.max_residual_edge_point_adjustment_for_photogrammetry	   --> 0.25 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.max_residual_gray_value_adjustment						   --> 0.055 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.max_residual_gray_value_adjustment_for_photogrammetry	   --> 0.055 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.max_scan_surface_depth_limitation						   --> 150.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.max_sensor_movement										   --> 0.1 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.max_viewing_angle_sensor_surface						   --> 1.3962634015954636 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.measurement_alignment_prior_sw2018						   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.measurement_alignment_residual							   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.measurement_alignment_residual_diff_too_high			   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.measurement_mesh_alignment_residual						   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.measurement_reference_point_alignment_residual			   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.measurement_resolution									   --> full_resolution (<class 'str'>)
	gom :> app.project.parts['Part'].actual.measurement_temperature									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.measurement_transformation_type							   --> by_reference_points_and_best_fit (<class 'str'>)
	gom :> app.project.parts['Part'].actual.measuring_task_project_building_block_draft				   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.memory_information										   --> <Trait: gom.MemoryInfo> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.min_ellipse_contrast_for_photogrammetry					   --> 25.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.min_ellipse_contrast_for_scanning						   --> 25.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.min_ellipse_radius										   --> 2.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.min_ellipse_radius_for_photogrammetry					   --> 2.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.min_fringe_contrast										   --> 15 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.min_reference_points_depth_limitation					   --> -200.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.min_scan_surface_depth_limitation						   --> -200.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.name													   --> gom_part_measurement (<class 'str'>)
	gom :> app.project.parts['Part'].actual.name													   --> gom_part_measurement (<class 'str'>)
	gom :> app.project.parts['Part'].actual.name_expression											   --> gom_part_measurement (<class 'str'>)
	gom :> app.project.parts['Part'].actual.nominal_element_names									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.normal													   --> Indexable (item=gom.app.project.parts['Part'].actual, token=normal, size=709567) (<class 'gom.Indexable'>)
	gom :> app.project.parts['Part'].actual.num_points												   --> 709567 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.num_triangles											   --> 1413630 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.number_of_date_formats									   --> 10 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.number_of_exposure_times								   --> 1 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.number_of_holes											   --> 10 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.object_family											   --> actual_part (<class 'gomlib.types.ObjectFamily'>)
	gom :> app.project.parts['Part'].actual.observe_gray_value_feature								   --> feature_no_computation (<class 'str'>)
	gom :> app.project.parts['Part'].actual.online_measurement_prognosis							   --> no prognosis (<class 'str'>)
	gom :> app.project.parts['Part'].actual.overview_explorer_alignments							   --> [] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.overview_explorer_alignments							   --> [] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.overview_explorer_computation_alignment					   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.overview_explorer_computation_information				   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.overview_explorer_coordinate_system						   --> [] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.overview_explorer_tacked_to_element						   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.package_database_info_draft								   -->
		{"installed":[{"author":"Sean","description":"training","displayname":"RATC Python
		Practice","enabled":false,"filepath":"C:/Users/8304018/AppData/Roaming/gom/2020/gom_packages/RATC Python Script
		Practice.package","labels":[],"level":"user","migrated_uuid":"00000000-0000-0000-0000-000000000000","protected":true,"prot
		ection_password_hash":"GoQCsL1mqgiiA7lv+ei6Lp9pVjC6zrx8jl3u7OJwmqniXxTiRQJtUBuhj2TcsgbERuluot56BPJlHv/A6b2A5A==","provider
		s":["scripts"],"sort_index":2147483647,"tags":[],"uuid":"3387cc7e-7f92-4f81-8191-d2903b8d0f25","version":"1.0.0"},{"author
		":"GOM GmbH (a ZEISS company)","description":"System package
		'Inspection'","displayname":"Inspection","enabled":true,"filepath":"C:/Program
		Files/GOM/2020/packages/inspection.package","labels":[],"level":"system","migrated_uuid":"00000000-0000-0000-0000-00000000
		0000","protected":false,"protection_password_hash":"","providers":["element_properties","inspection_style","keywordset","l
		abel","legend","license","perspective","report","scripts","surface_classification","table","tolerance_legend"],"sort_index
		":0,"tags":["system","exclusive","gom","buildsystem"],"uuid":"a6769fbc-4bda-4cec-af9a-b189baf8b742","version":"1.0.0"},{"a
		uthor":"GOM GmbH (a ZEISS company)","description":"System package
		'Deformation'","displayname":"Deformation","enabled":false,"filepath":"C:/Program
		Files/GOM/2020/packages/deformation.package","labels":[],"level":"system","migrated_uuid":"00000000-0000-0000-0000-0000000
		00000","protected":false,"protection_password_hash":"","providers":["element_properties","inspection_style","keywordset","
		label","legend","license","perspective","report","table","tolerance_legend"],"sort_index":1,"tags":["system","exclusive","
		gom","buildsystem"],"uuid":"e1096235-7f21-42c5-a63c-a06c8135c602","version":"1.0.0"}]} (<class 'str'>)

	gom :> app.project.parts['Part'].actual.package_information										   --> <Trait: Tom::MPRJ::PackageInformation> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.part													   --> gom.app.project.parts['Part'] (<class 'gom.Item'>)
	gom :> app.project.parts['Part'].actual.photogrametry_project_building_block_draft				   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.project_building_block_type_draft						   --> project (<class 'str'>)
	gom :> app.project.parts['Part'].actual.project_building_block_uuid_draft						   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.project_contains_preliminary_data						   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.project_creation_time									   --> 2020/09/17 10:05 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.project_data_reduction									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.project_file											   --> C:\Users\8304018\Documents\GOM\教材\gom part 教育訓練教材.ginspect (<class 'str'>)
	gom :> app.project.parts['Part'].actual.project_file_size										   --> 24132347 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.project_history											   --> GOM_INSPECT 04/11/19 2019-Beta2-rev117358 2019-Beta2-rev117410 2019-rev119334 2019-1-rev120565 2019-3-rev121775 2020-RC1-rev128129 2020-RC2-rev128400 2020-RC2-rev128466 2020-rev130639 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.project_keywords										   --> ['user_inspector', 'user_part_nr', 'user_date', 'user_location', 'user_company', 'user_department', 'user_project', 'user_system', 'user_charge_nr', 'user_version', 'user_part'] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.project_modification_time								   --> 2020/08/31 14:25 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.project_name											   --> gom part 教育訓練教材 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.project_statistics										   --> <Trait: Tom::Prj::StatisticData> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.project_template_directory								   --> C:\Users\8304018\Documents\GOM\Templates\2020\gom_project_templates (<class 'str'>)
	gom :> app.project.parts['Part'].actual.public_directory										   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.public_package_directory								   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.python_directory										   --> C:\Program Files\GOM\2020\python\ (<class 'str'>)
	gom :> app.project.parts['Part'].actual.quality_triple_scan_points_mode							   --> intersection (<class 'str'>)
	gom :> app.project.parts['Part'].actual.quality_triple_scan_points_threshold					   --> 0.3 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.recent_reasons											   --> 0 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.reduce_influence_of_border_areas						   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.reference_point_identification_method					   --> gray_value_adjustment (<class 'str'>)
	gom :> app.project.parts['Part'].actual.reference_point_identification_method_for_photogrammetry   --> gray_value_adjustment (<class 'str'>)
	gom :> app.project.parts['Part'].actual.reference_point_identification_settings					   --> best_quality (<class 'str'>)
	gom :> app.project.parts['Part'].actual.reference_point_identification_settings_for_photogrammetry --> best_quality (<class 'str'>)
	gom :> app.project.parts['Part'].actual.reference_point_size									   --> 1.5 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.reference_point_thickness								   --> 0.1 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.reference_point_type									   --> 3mm_round (<class 'str'>)
	gom :> app.project.parts['Part'].actual.reference_points_collection_type						   --> automatic (<class 'str'>)
	gom :> app.project.parts['Part'].actual.reference_stage											   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.reflection_detection									   --> off (<class 'str'>)
	gom :> app.project.parts['Part'].actual.render_complete_draw_time								   --> 81.9640000000023 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.render_driver_version									   --> 431.84 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.render_gpu_type											   --> Quadro T2000/PCIe/SSE2 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.render_scene_graph_update_time							   --> 0.3340000000000001 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.render_use_gpu_memory									   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.render_use_transparency									   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.rendered_frames											   --> 7743 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.rendered_overlay_2d_frames								   --> 141 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.rendered_overlay_3d_frames								   --> 138 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.rendered_scene_layer_frames								   --> 7464 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.rendered_temp_layer_frames								   --> 0 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.rigid_body_motion_compensation_at_calculation			   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.robogrammetry											   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.scalar_registry_info									   --> {"elements":[{"actual_expression":"","auto":false,"base_type":"","name":"Global coordinate system","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"coordinate_system","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"gom_part","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"cad","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"gom_part - Bodies","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"cad_body_group","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"gom_part - Coordinate Systems","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"coordinate_system_group","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"gom_part - Curves","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"cad_section_group","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"gom_part/Volumenkörper1","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"cad_body","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"gom_part_measurement","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"mesh","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"Line X","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"line","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"Line Y","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"line","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"Line Z","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"line","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"Plane X","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"plane","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"Plane Y","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"plane","unit":"","userdefined":false},{"actual_expression":"","auto":false,"base_type":"","name":"Plane Z","nominal_expression":"","scalar_package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"scalar_type":-1,"scalar_type_name":"","scalar_uuid":"00000000-0000-0000-0000-000000000000","type":"plane","unit":"","userdefined":false}],"registry":{"scalars":[{"abbrevation":"R","abbrevation_translation":"R","actual_expression":"","auto":false,"base_type":"radius","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"0","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Radius","type":"radius","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mR","abbrevation_translation":"rel_R","actual_expression":"","auto":false,"base_type":"radius","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"0","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Radius","type":"movement_radius","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vR","abbrevation_translation":"vR","actual_expression":"","auto":false,"base_type":"radius","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"0","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Radius","type":"velocity_radius","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aR","abbrevation_translation":"aR","actual_expression":"","auto":false,"base_type":"radius","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"0","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Radius","type":"acceleration_radius","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"D","abbrevation_translation":"Ø","actual_expression":"","auto":false,"base_type":"diameter","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"1","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Diameter","type":"diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mD","abbrevation_translation":"rel_Ø","actual_expression":"","auto":false,"base_type":"diameter","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"1","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Diameter","type":"movement_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vD","abbrevation_translation":"vØ","actual_expression":"","auto":false,"base_type":"diameter","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"1","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Diameter","type":"velocity_diameter","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aD","abbrevation_translation":"aØ","actual_expression":"","auto":false,"base_type":"diameter","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"1","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Diameter","type":"acceleration_diameter","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"L","abbrevation_translation":"L","actual_expression":"","auto":false,"base_type":"distance","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"2","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Distance","type":"distance","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mL","abbrevation_translation":"rel_L","actual_expression":"","auto":false,"base_type":"distance","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"2","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Distance","type":"movement_distance","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vL","abbrevation_translation":"vL","actual_expression":"","auto":false,"base_type":"distance","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"2","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Distance","type":"velocity_distance","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"aL","abbrevation_translation":"aL","actual_expression":"","auto":false,"base_type":"distance","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"2","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Distance","type":"acceleration_distance","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"A","abbrevation_translation":"∠","actual_expression":"","auto":false,"base_type":"angle","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"3","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Angle","type":"angle","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mA","abbrevation_translation":"Δ∠","actual_expression":"","auto":false,"base_type":"angle","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"3","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Angle Change","type":"movement_angle","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vA","abbrevation_translation":"v∠","actual_expression":"","auto":false,"base_type":"angle","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"3","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Angular Velocity","type":"velocity_angle","unit":"ANGLE_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"aA","abbrevation_translation":"a∠","actual_expression":"","auto":false,"base_type":"angle","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"3","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Angular Acceleration","type":"acceleration_angle","unit":"ANGLE_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"M","abbrevation_translation":"M","actual_expression":"","auto":false,"base_type":"material_thickness","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"4","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Material Thickness","type":"material_thickness","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mM","abbrevation_translation":"rel_M","actual_expression":"","auto":false,"base_type":"material_thickness","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"4","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Material Thickness","type":"movement_material_thickness","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vM","abbrevation_translation":"vM","actual_expression":"","auto":false,"base_type":"material_thickness","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"4","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Material Thickness","type":"velocity_material_thickness","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aM","abbrevation_translation":"aM","actual_expression":"","auto":false,"base_type":"material_thickness","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"4","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Material Thickness","type":"acceleration_material_thickness","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"L","abbrevation_translation":"L","actual_expression":"","auto":false,"base_type":"length","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"5","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Length","type":"length","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mL","abbrevation_translation":"rel_L","actual_expression":"","auto":false,"base_type":"length","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"5","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Length","type":"movement_length","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vL","abbrevation_translation":"vL","actual_expression":"","auto":false,"base_type":"length","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"5","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Length","type":"velocity_length","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aL","abbrevation_translation":"aL","actual_expression":"","auto":false,"base_type":"length","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"5","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Length","type":"acceleration_length","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"W","abbrevation_translation":"W","actual_expression":"","auto":false,"base_type":"width","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"6","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Width","type":"width","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mW","abbrevation_translation":"rel_W","actual_expression":"","auto":false,"base_type":"width","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"6","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Width","type":"movement_width","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vW","abbrevation_translation":"vW","actual_expression":"","auto":false,"base_type":"width","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"6","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Width","type":"velocity_width","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aW","abbrevation_translation":"aW","actual_expression":"","auto":false,"base_type":"width","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"6","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Width","type":"acceleration_width","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"R","abbrevation_translation":"R","actual_expression":"","auto":false,"base_type":"hole_radius","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"7","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Hole radius","type":"hole_radius","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mR","abbrevation_translation":"rel_R","actual_expression":"","auto":false,"base_type":"hole_radius","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"7","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Hole radius","type":"movement_hole_radius","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vR","abbrevation_translation":"vR","actual_expression":"","auto":false,"base_type":"hole_radius","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"7","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Hole radius","type":"velocity_hole_radius","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aR","abbrevation_translation":"aR","actual_expression":"","auto":false,"base_type":"hole_radius","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"7","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Hole radius","type":"acceleration_hole_radius","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"ID","abbrevation_translation":"Ø(i)","actual_expression":"","auto":false,"base_type":"inner_diameter","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"8","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Inner Diameter","type":"inner_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mID","abbrevation_translation":"rel_Ø(i)","actual_expression":"","auto":false,"base_type":"inner_diameter","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"8","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Inner Diameter","type":"movement_inner_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vID","abbrevation_translation":"vØ(i)","actual_expression":"","auto":false,"base_type":"inner_diameter","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"8","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Inner Diameter","type":"velocity_inner_diameter","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aID","abbrevation_translation":"aØ(i)","actual_expression":"","auto":false,"base_type":"inner_diameter","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"8","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Inner Diameter","type":"acceleration_inner_diameter","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"IR","abbrevation_translation":"R(i)","actual_expression":"","auto":false,"base_type":"inner_radius","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"9","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Inner Radius","type":"inner_radius","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mIR","abbrevation_translation":"rel_R(i)","actual_expression":"","auto":false,"base_type":"inner_radius","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"9","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Inner Radius","type":"movement_inner_radius","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vIR","abbrevation_translation":"vR(i)","actual_expression":"","auto":false,"base_type":"inner_radius","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"9","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Inner Radius","type":"velocity_inner_radius","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aIR","abbrevation_translation":"aR(i)","actual_expression":"","auto":false,"base_type":"inner_radius","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"9","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Inner Radius","type":"acceleration_inner_radius","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"Dsi","abbrevation_translation":"Ø(I)","actual_expression":"","auto":false,"base_type":"dimension_independency_principle","category":"GD&T","constructed":false,"deduction":"","dynamic":false,"id":"10","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Dimension (independency principle)","type":"dimension_independency_principle","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mDsi","abbrevation_translation":"rel_Ø(I)","actual_expression":"","auto":false,"base_type":"dimension_independency_principle","category":"GD&T","constructed":false,"deduction":"M","dynamic":false,"id":"10","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Dimension (independency principle)","type":"movement_dimension_independency_principle","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vDsi","abbrevation_translation":"vØ(I)","actual_expression":"","auto":false,"base_type":"dimension_independency_principle","category":"GD&T","constructed":false,"deduction":"V","dynamic":false,"id":"10","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Dimension (independency principle)","type":"velocity_dimension_independency_principle","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aDsi","abbrevation_translation":"aØ(I)","actual_expression":"","auto":false,"base_type":"dimension_independency_principle","category":"GD&T","constructed":false,"deduction":"A","dynamic":false,"id":"10","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Dimension (independency principle)","type":"acceleration_dimension_independency_principle","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"Dse","abbrevation_translation":"Ø(E)","actual_expression":"","auto":false,"base_type":"dimension_envelope_principle","category":"GD&T","constructed":false,"deduction":"","dynamic":false,"id":"11","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Dimension (envelope principle)","type":"dimension_envelope_principle","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mDse","abbrevation_translation":"rel_Ø(E)","actual_expression":"","auto":false,"base_type":"dimension_envelope_principle","category":"GD&T","constructed":false,"deduction":"M","dynamic":false,"id":"11","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Dimension (envelope principle)","type":"movement_dimension_envelope_principle","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vDse","abbrevation_translation":"vØ(E)","actual_expression":"","auto":false,"base_type":"dimension_envelope_principle","category":"GD&T","constructed":false,"deduction":"V","dynamic":false,"id":"11","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Dimension (envelope principle)","type":"velocity_dimension_envelope_principle","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aDse","abbrevation_translation":"aØ(E)","actual_expression":"","auto":false,"base_type":"dimension_envelope_principle","category":"GD&T","constructed":false,"deduction":"A","dynamic":false,"id":"11","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Dimension (envelope principle)","type":"acceleration_dimension_envelope_principle","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"L","abbrevation_translation":"L","actual_expression":"","auto":false,"base_type":"visualization_length","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"12","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"length (visualization)","type":"visualization_length","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mL","abbrevation_translation":"rel_L","actual_expression":"","auto":false,"base_type":"visualization_length","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"12","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: length (visualization)","type":"movement_visualization_length","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vL","abbrevation_translation":"vL","actual_expression":"","auto":false,"base_type":"visualization_length","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"12","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: length (visualization)","type":"velocity_visualization_length","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aL","abbrevation_translation":"aL","actual_expression":"","auto":false,"base_type":"visualization_length","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"12","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: length (visualization)","type":"acceleration_visualization_length","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"W","abbrevation_translation":"W","actual_expression":"","auto":false,"base_type":"visualization_width","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"13","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"width (visualization)","type":"visualization_width","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mW","abbrevation_translation":"rel_W","actual_expression":"","auto":false,"base_type":"visualization_width","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"13","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: width (visualization)","type":"movement_visualization_width","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vW","abbrevation_translation":"vW","actual_expression":"","auto":false,"base_type":"visualization_width","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"13","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: width (visualization)","type":"velocity_visualization_width","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aW","abbrevation_translation":"aW","actual_expression":"","auto":false,"base_type":"visualization_width","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"13","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: width (visualization)","type":"acceleration_visualization_width","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"DIM","abbrevation_translation":"DIM","actual_expression":"","auto":false,"base_type":"dimension","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"14","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Dimension","type":"dimension","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mDIM","abbrevation_translation":"rel_DIM","actual_expression":"","auto":false,"base_type":"dimension","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"14","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Dimension","type":"movement_dimension","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vDIM","abbrevation_translation":"vDIM","actual_expression":"","auto":false,"base_type":"dimension","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"14","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Dimension","type":"velocity_dimension","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aDIM","abbrevation_translation":"aDIM","actual_expression":"","auto":false,"base_type":"dimension","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"14","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Dimension","type":"acceleration_dimension","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"X","abbrevation_translation":"X","actual_expression":"","auto":false,"base_type":"x","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"15","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"X","type":"x","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mX","abbrevation_translation":"rel_X","actual_expression":"","auto":false,"base_type":"x","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"15","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: X","type":"movement_x","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vX","abbrevation_translation":"vX","actual_expression":"","auto":false,"base_type":"x","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"15","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: X","type":"velocity_x","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aX","abbrevation_translation":"aX","actual_expression":"","auto":false,"base_type":"x","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"15","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: X","type":"acceleration_x","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"Y","abbrevation_translation":"Y","actual_expression":"","auto":false,"base_type":"y","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"16","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Y","type":"y","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mY","abbrevation_translation":"rel_Y","actual_expression":"","auto":false,"base_type":"y","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"16","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Y","type":"movement_y","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vY","abbrevation_translation":"vY","actual_expression":"","auto":false,"base_type":"y","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"16","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Y","type":"velocity_y","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aY","abbrevation_translation":"aY","actual_expression":"","auto":false,"base_type":"y","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"16","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Y","type":"acceleration_y","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"Z","abbrevation_translation":"Z","actual_expression":"","auto":false,"base_type":"z","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"17","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Z","type":"z","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mZ","abbrevation_translation":"rel_Z","actual_expression":"","auto":false,"base_type":"z","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"17","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Z","type":"movement_z","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vZ","abbrevation_translation":"vZ","actual_expression":"","auto":false,"base_type":"z","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"17","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Z","type":"velocity_z","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aZ","abbrevation_translation":"aZ","actual_expression":"","auto":false,"base_type":"z","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"17","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Z","type":"acceleration_z","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"xyz","abbrevation_translation":"dXYZ","actual_expression":"","auto":false,"base_type":"xyz","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"18","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"dXYZ","type":"xyz","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mxyz","abbrevation_translation":"rel_dXYZ","actual_expression":"","auto":false,"base_type":"xyz","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"18","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: dXYZ","type":"movement_xyz","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vxyz","abbrevation_translation":"vdXYZ","actual_expression":"","auto":false,"base_type":"xyz","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"18","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: dXYZ","type":"velocity_xyz","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"axyz","abbrevation_translation":"adXYZ","actual_expression":"","auto":false,"base_type":"xyz","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"18","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: dXYZ","type":"acceleration_xyz","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"n","abbrevation_translation":"dN","actual_expression":"","auto":false,"base_type":"normal","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"19","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"dN","type":"normal","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mn","abbrevation_translation":"rel_dN","actual_expression":"","auto":false,"base_type":"normal","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"19","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: dN","type":"movement_normal","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vn","abbrevation_translation":"vdN","actual_expression":"","auto":false,"base_type":"normal","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"19","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: dN","type":"velocity_normal","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"an","abbrevation_translation":"adN","actual_expression":"","auto":false,"base_type":"normal","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"19","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: dN","type":"acceleration_normal","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"t","abbrevation_translation":"dT","actual_expression":"","auto":false,"base_type":"trim","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"20","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"dT","type":"trim","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mt","abbrevation_translation":"rel_dT","actual_expression":"","auto":false,"base_type":"trim","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"20","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: dT","type":"movement_trim","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vt","abbrevation_translation":"vdT","actual_expression":"","auto":false,"base_type":"trim","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"20","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: dT","type":"velocity_trim","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"at","abbrevation_translation":"adT","actual_expression":"","auto":false,"base_type":"trim","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"20","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: dT","type":"acceleration_trim","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"ip","abbrevation_translation":"dIP","actual_expression":"","auto":false,"base_type":"inplane","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"21","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"dIP","type":"inplane","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mip","abbrevation_translation":"rel_dIP","actual_expression":"","auto":false,"base_type":"inplane","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"21","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: dIP","type":"movement_inplane","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vip","abbrevation_translation":"vdIP","actual_expression":"","auto":false,"base_type":"inplane","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"21","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: dIP","type":"velocity_inplane","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aip","abbrevation_translation":"adIP","actual_expression":"","auto":false,"base_type":"inplane","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"21","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: dIP","type":"acceleration_inplane","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"sigma","abbrevation_translation":"σ","actual_expression":"","auto":false,"base_type":"adjustment_residual_sigma","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"22","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Adjustment Residual Sigma","type":"adjustment_residual_sigma","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"msigma","abbrevation_translation":"rel_σ","actual_expression":"","auto":false,"base_type":"adjustment_residual_sigma","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"22","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: Adjustment Residual Sigma","type":"movement_adjustment_residual_sigma","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vsigma","abbrevation_translation":"vσ","actual_expression":"","auto":false,"base_type":"adjustment_residual_sigma","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"22","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: Adjustment Residual Sigma","type":"velocity_adjustment_residual_sigma","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"asigma","abbrevation_translation":"aσ","actual_expression":"","auto":false,"base_type":"adjustment_residual_sigma","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"22","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: Adjustment Residual Sigma","type":"acceleration_adjustment_residual_sigma","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"range","abbrevation_translation":"Range","actual_expression":"","auto":false,"base_type":"adjustment_residual_range","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"23","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Adjustment Residual Range","type":"adjustment_residual_range","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mrange","abbrevation_translation":"rel_Range","actual_expression":"","auto":false,"base_type":"adjustment_residual_range","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"23","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: Adjustment Residual Range","type":"movement_adjustment_residual_range","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vrange","abbrevation_translation":"vRange","actual_expression":"","auto":false,"base_type":"adjustment_residual_range","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"23","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: Adjustment Residual Range","type":"velocity_adjustment_residual_range","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"arange","abbrevation_translation":"aRange","actual_expression":"","auto":false,"base_type":"adjustment_residual_range","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"23","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: Adjustment Residual Range","type":"acceleration_adjustment_residual_range","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"BD","abbrevation_translation":"BD","actual_expression":"","auto":false,"base_type":"bending_distance","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"24","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Bending Distance","type":"bending_distance","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mBD","abbrevation_translation":"rel_BD","actual_expression":"","auto":false,"base_type":"bending_distance","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"24","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Bending Distance","type":"movement_bending_distance","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vBD","abbrevation_translation":"vBD","actual_expression":"","auto":false,"base_type":"bending_distance","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"24","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Bending Distance","type":"velocity_bending_distance","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aBD","abbrevation_translation":"aBD","actual_expression":"","auto":false,"base_type":"bending_distance","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"24","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Bending Distance","type":"acceleration_bending_distance","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"F","abbrevation_translation":"F","actual_expression":"","auto":false,"base_type":"distance","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"25","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Flush","type":"flush","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mF","abbrevation_translation":"rel_F","actual_expression":"","auto":false,"base_type":"flush","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"25","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Flush","type":"movement_flush","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vF","abbrevation_translation":"vF","actual_expression":"","auto":false,"base_type":"flush","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"25","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Flush","type":"velocity_flush","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"aF","abbrevation_translation":"aF","actual_expression":"","auto":false,"base_type":"flush","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"25","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Flush","type":"acceleration_flush","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"G","abbrevation_translation":"G","actual_expression":"","auto":false,"base_type":"distance","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"26","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Gap","type":"gap","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mG","abbrevation_translation":"rel_G","actual_expression":"","auto":false,"base_type":"gap","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"26","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Gap","type":"movement_gap","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vG","abbrevation_translation":"vG","actual_expression":"","auto":false,"base_type":"gap","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"26","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Gap","type":"velocity_gap","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"aG","abbrevation_translation":"aG","actual_expression":"","auto":false,"base_type":"gap","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"26","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Gap","type":"acceleration_gap","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"minor_strain","abbrevation_translation":"eps2","actual_expression":"","auto":false,"base_type":"minor_strain","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"27","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Minor Strain","type":"minor_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mminor_strain","abbrevation_translation":"rel_eps2","actual_expression":"","auto":false,"base_type":"minor_strain","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"27","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Minor Strain","type":"movement_minor_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vminor_strain","abbrevation_translation":"eps2r","actual_expression":"","auto":false,"base_type":"minor_strain","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"27","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Minor Strain Rate","type":"velocity_minor_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aminor_strain","abbrevation_translation":"aeps2","actual_expression":"","auto":false,"base_type":"minor_strain","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"27","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Minor Strain","type":"acceleration_minor_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"major_strain","abbrevation_translation":"eps1","actual_expression":"","auto":false,"base_type":"major_strain","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"28","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Major Strain","type":"major_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mmajor_strain","abbrevation_translation":"rel_eps1","actual_expression":"","auto":false,"base_type":"major_strain","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"28","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Major Strain","type":"movement_major_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vmajor_strain","abbrevation_translation":"eps1r","actual_expression":"","auto":false,"base_type":"major_strain","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"28","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Major Strain Rate","type":"velocity_major_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"amajor_strain","abbrevation_translation":"aeps1","actual_expression":"","auto":false,"base_type":"major_strain","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"28","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Major Strain","type":"acceleration_major_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"","abbrevation_translation":"","actual_expression":"","auto":false,"base_type":"gdat_size","category":"GD&T","constructed":false,"deduction":"","dynamic":false,"id":"29","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"GD&T Tolerance","type":"gdat_size","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"m","abbrevation_translation":"rel_","actual_expression":"","auto":false,"base_type":"gdat_size","category":"GD&T","constructed":false,"deduction":"M","dynamic":false,"id":"29","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: GD&T Tolerance","type":"movement_gdat_size","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"v","abbrevation_translation":"v","actual_expression":"","auto":false,"base_type":"gdat_size","category":"GD&T","constructed":false,"deduction":"V","dynamic":false,"id":"29","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: GD&T Tolerance","type":"velocity_gdat_size","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"a","abbrevation_translation":"a","actual_expression":"","auto":false,"base_type":"gdat_size","category":"GD&T","constructed":false,"deduction":"A","dynamic":false,"id":"29","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: GD&T Tolerance","type":"acceleration_gdat_size","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"","abbrevation_translation":"","actual_expression":"","auto":false,"base_type":"dir1","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"30","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"_direction 1","type":"dir1","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"m","abbrevation_translation":"rel_","actual_expression":"","auto":false,"base_type":"dir1","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"30","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: _direction 1","type":"movement_dir1","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"v","abbrevation_translation":"v","actual_expression":"","auto":false,"base_type":"dir1","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"30","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: _direction 1","type":"velocity_dir1","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"a","abbrevation_translation":"a","actual_expression":"","auto":false,"base_type":"dir1","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"30","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: _direction 1","type":"acceleration_dir1","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"","abbrevation_translation":"","actual_expression":"","auto":false,"base_type":"dir2","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"31","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"_direction 2","type":"dir2","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"m","abbrevation_translation":"rel_","actual_expression":"","auto":false,"base_type":"dir2","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"31","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: _direction 2","type":"movement_dir2","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"v","abbrevation_translation":"v","actual_expression":"","auto":false,"base_type":"dir2","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"31","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: _direction 2","type":"velocity_dir2","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"a","abbrevation_translation":"a","actual_expression":"","auto":false,"base_type":"dir2","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"31","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: _direction 2","type":"acceleration_dir2","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"","abbrevation_translation":"","actual_expression":"","auto":false,"base_type":"dir3","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"32","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"_direction 3","type":"dir3","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"m","abbrevation_translation":"rel_","actual_expression":"","auto":false,"base_type":"dir3","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"32","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: _direction 3","type":"movement_dir3","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"v","abbrevation_translation":"v","actual_expression":"","auto":false,"base_type":"dir3","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"32","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: _direction 3","type":"velocity_dir3","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"a","abbrevation_translation":"a","actual_expression":"","auto":false,"base_type":"dir3","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"32","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: _direction 3","type":"acceleration_dir3","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"d","abbrevation_translation":"d","actual_expression":"","auto":false,"base_type":"displacement","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"33","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Displacement","type":"displacement","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"md","abbrevation_translation":"rel","actual_expression":"","auto":false,"base_type":"displacement","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"33","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative Movement","type":"movement_displacement","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vd","abbrevation_translation":"v","actual_expression":"","auto":false,"base_type":"displacement","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"33","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity","type":"velocity_displacement","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"ad","abbrevation_translation":"a","actual_expression":"","auto":false,"base_type":"displacement","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"33","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration","type":"acceleration_displacement","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"atd","abbrevation_translation":"ta","actual_expression":"","auto":false,"base_type":"displacement","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"33","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"T","translation":"Tangential Acceleration","type":"tangential_acceleration_displacement","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"acd","abbrevation_translation":"ca","actual_expression":"","auto":false,"base_type":"displacement","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"33","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"C","translation":"Centripetal Acceleration","type":"centripetal_acceleration_displacement","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"rx","abbrevation_translation":"Phi(X)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_x","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"34","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Rotation (X)","type":"six_dof_rotation_x","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mrx","abbrevation_translation":"rel_Phi(X)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_x","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"34","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Rotation (X)","type":"movement_six_dof_rotation_x","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vrx","abbrevation_translation":"vPhi(X)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_x","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"34","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Rotation (X)","type":"velocity_six_dof_rotation_x","unit":"ANGLE_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"arx","abbrevation_translation":"aPhi(X)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_x","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"34","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Rotation (X)","type":"acceleration_six_dof_rotation_x","unit":"ANGLE_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"ry","abbrevation_translation":"Theta(Y)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_y","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"35","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Rotation (Y)","type":"six_dof_rotation_y","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mry","abbrevation_translation":"rel_Theta(Y)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_y","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"35","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Rotation (Y)","type":"movement_six_dof_rotation_y","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vry","abbrevation_translation":"vTheta(Y)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_y","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"35","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Rotation (Y)","type":"velocity_six_dof_rotation_y","unit":"ANGLE_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"ary","abbrevation_translation":"aTheta(Y)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_y","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"35","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Rotation (Y)","type":"acceleration_six_dof_rotation_y","unit":"ANGLE_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"rz","abbrevation_translation":"Psi(Z)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_z","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"36","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Rotation (Z)","type":"six_dof_rotation_z","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mrz","abbrevation_translation":"rel_Psi(Z)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_z","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"36","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Rotation (Z)","type":"movement_six_dof_rotation_z","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vrz","abbrevation_translation":"vPsi(Z)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_z","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"36","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Rotation (Z)","type":"velocity_six_dof_rotation_z","unit":"ANGLE_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"arz","abbrevation_translation":"aPsi(Z)","actual_expression":"","auto":false,"base_type":"six_dof_rotation_z","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"36","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Rotation (Z)","type":"acceleration_six_dof_rotation_z","unit":"ANGLE_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"residuum","abbrevation_translation":"r","actual_expression":"","auto":false,"base_type":"adjustment_residual_medium","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"37","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Adjustment Residual","type":"adjustment_residual_medium","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mresiduum","abbrevation_translation":"rel_r","actual_expression":"","auto":false,"base_type":"adjustment_residual_medium","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"37","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: Adjustment Residual","type":"movement_adjustment_residual_medium","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vresiduum","abbrevation_translation":"vr","actual_expression":"","auto":false,"base_type":"adjustment_residual_medium","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"37","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: Adjustment Residual","type":"velocity_adjustment_residual_medium","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aresiduum","abbrevation_translation":"ar","actual_expression":"","auto":false,"base_type":"adjustment_residual_medium","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"37","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: Adjustment Residual","type":"acceleration_adjustment_residual_medium","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"number_points","abbrevation_translation":"Points","actual_expression":"","auto":false,"base_type":"number_of_creation_points","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"38","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Number Of Used Points","type":"number_of_creation_points","unit":"COUNT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mnumber_points","abbrevation_translation":"rel_Points","actual_expression":"","auto":false,"base_type":"number_of_creation_points","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"38","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: Number Of Used Points","type":"movement_number_of_creation_points","unit":"COUNT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vnumber_points","abbrevation_translation":"vPoints","actual_expression":"","auto":false,"base_type":"number_of_creation_points","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"38","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: Number Of Used Points","type":"velocity_number_of_creation_points","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"anumber_points","abbrevation_translation":"aPoints","actual_expression":"","auto":false,"base_type":"number_of_creation_points","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"38","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: Number Of Used Points","type":"acceleration_number_of_creation_points","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"k","abbrevation_translation":"κ","actual_expression":"","auto":false,"base_type":"curvature","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"39","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Curvature","type":"curvature","unit":"CURVATURE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mk","abbrevation_translation":"rel_κ","actual_expression":"","auto":false,"base_type":"curvature","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"39","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Curvature","type":"movement_curvature","unit":"CURVATURE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vk","abbrevation_translation":"vκ","actual_expression":"","auto":false,"base_type":"curvature","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"39","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Curvature","type":"velocity_curvature","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"ak","abbrevation_translation":"aκ","actual_expression":"","auto":false,"base_type":"curvature","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"39","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Curvature","type":"acceleration_curvature","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"thickness_reduction","abbrevation_translation":"-eps3","actual_expression":"","auto":false,"base_type":"thickness_reduction","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"40","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Thickness Reduction","type":"thickness_reduction","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mthickness_reduction","abbrevation_translation":"rel_-eps3","actual_expression":"","auto":false,"base_type":"thickness_reduction","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"40","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Thickness Reduction","type":"movement_thickness_reduction","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vthickness_reduction","abbrevation_translation":"-eps3r","actual_expression":"","auto":false,"base_type":"thickness_reduction","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"40","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Thickness Reduction Rate","type":"velocity_thickness_reduction","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"athickness_reduction","abbrevation_translation":"a-eps3","actual_expression":"","auto":false,"base_type":"thickness_reduction","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"40","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Thickness Reduction","type":"acceleration_thickness_reduction","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"epsilon_x","abbrevation_translation":"epsX","actual_expression":"","auto":false,"base_type":"epsilon_x","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"41","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Epsilon (X)","type":"epsilon_x","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mepsilon_x","abbrevation_translation":"rel_epsX","actual_expression":"","auto":false,"base_type":"epsilon_x","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"41","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Epsilon (X)","type":"movement_epsilon_x","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vepsilon_x","abbrevation_translation":"epsXr","actual_expression":"","auto":false,"base_type":"epsilon_x","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"41","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Epsilon (X) Rate","type":"velocity_epsilon_x","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aepsilon_x","abbrevation_translation":"aepsX","actual_expression":"","auto":false,"base_type":"epsilon_x","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"41","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Epsilon (X)","type":"acceleration_epsilon_x","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"epsilon_y","abbrevation_translation":"epsY","actual_expression":"","auto":false,"base_type":"epsilon_y","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"42","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Epsilon (Y)","type":"epsilon_y","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mepsilon_y","abbrevation_translation":"rel_epsY","actual_expression":"","auto":false,"base_type":"epsilon_y","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"42","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Epsilon (Y)","type":"movement_epsilon_y","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vepsilon_y","abbrevation_translation":"epsYr","actual_expression":"","auto":false,"base_type":"epsilon_y","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"42","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Epsilon (Y) Rate","type":"velocity_epsilon_y","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aepsilon_y","abbrevation_translation":"aepsY","actual_expression":"","auto":false,"base_type":"epsilon_y","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"42","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Epsilon (Y)","type":"acceleration_epsilon_y","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"epsilon_xy","abbrevation_translation":"epsXY","actual_expression":"","auto":false,"base_type":"epsilon_xy","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"43","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Epsilon (XY)","type":"epsilon_xy","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mepsilon_xy","abbrevation_translation":"rel_epsXY","actual_expression":"","auto":false,"base_type":"epsilon_xy","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"43","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Epsilon (XY)","type":"movement_epsilon_xy","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vepsilon_xy","abbrevation_translation":"vepsXY","actual_expression":"","auto":false,"base_type":"epsilon_xy","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"43","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Epsilon (XY)","type":"velocity_epsilon_xy","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aepsilon_xy","abbrevation_translation":"aepsXY","actual_expression":"","auto":false,"base_type":"epsilon_xy","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"43","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Epsilon (XY)","type":"acceleration_epsilon_xy","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"strain","abbrevation_translation":"epsL","actual_expression":"","auto":false,"base_type":"distance","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"44","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Length Change","type":"strain","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mstrain","abbrevation_translation":"rel_epsL","actual_expression":"","auto":false,"base_type":"strain","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"44","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Length Change","type":"movement_strain","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vstrain","abbrevation_translation":"vepsL","actual_expression":"","auto":false,"base_type":"strain","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"44","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Length Change","type":"velocity_strain","unit":"STRAIN_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"astrain","abbrevation_translation":"aepsL","actual_expression":"","auto":false,"base_type":"strain","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"44","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Length Change","type":"acceleration_strain","unit":"STRAIN_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"change rate","abbrevation_translation":"fcr","actual_expression":"","auto":false,"base_type":"form_change_rate","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"45","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Local Form Change Range","type":"form_change_rate","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mchange rate","abbrevation_translation":"rel_fcr","actual_expression":"","auto":false,"base_type":"form_change_rate","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"45","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Local Form Change Range","type":"movement_form_change_rate","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vchange rate","abbrevation_translation":"vfcr","actual_expression":"","auto":false,"base_type":"form_change_rate","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"45","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Local Form Change Range","type":"velocity_form_change_rate","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"achange rate","abbrevation_translation":"afcr","actual_expression":"","auto":false,"base_type":"form_change_rate","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"45","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Local Form Change Range","type":"acceleration_form_change_rate","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"area","abbrevation_translation":"A","actual_expression":"","auto":false,"base_type":"area","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"46","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Area","type":"area","unit":"AREA","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"marea","abbrevation_translation":"rel_A","actual_expression":"","auto":false,"base_type":"area","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"46","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: Area","type":"movement_area","unit":"AREA","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"varea","abbrevation_translation":"vA","actual_expression":"","auto":false,"base_type":"area","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"46","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: Area","type":"velocity_area","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aarea","abbrevation_translation":"aA","actual_expression":"","auto":false,"base_type":"area","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"46","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: Area","type":"acceleration_area","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"volume","abbrevation_translation":"V","actual_expression":"","auto":false,"base_type":"volume","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"47","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Volume","type":"volume","unit":"VOLUME","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mvolume","abbrevation_translation":"rel_V","actual_expression":"","auto":false,"base_type":"volume","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"47","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: Volume","type":"movement_volume","unit":"VOLUME","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vvolume","abbrevation_translation":"vV","actual_expression":"","auto":false,"base_type":"volume","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"47","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: Volume","type":"velocity_volume","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"avolume","abbrevation_translation":"aV","actual_expression":"","auto":false,"base_type":"volume","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"47","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: Volume","type":"acceleration_volume","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"strain_ref_length","abbrevation_translation":"l0","actual_expression":"","auto":false,"base_type":"strain_ref_length","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"48","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Strain Reference Length","type":"strain_ref_length","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mstrain_ref_length","abbrevation_translation":"rel_l0","actual_expression":"","auto":false,"base_type":"strain_ref_length","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"48","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Strain Reference Length","type":"movement_strain_ref_length","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vstrain_ref_length","abbrevation_translation":"vl0","actual_expression":"","auto":false,"base_type":"strain_ref_length","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"48","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Strain Reference Length","type":"velocity_strain_ref_length","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"astrain_ref_length","abbrevation_translation":"al0","actual_expression":"","auto":false,"base_type":"strain_ref_length","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"48","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Strain Reference Length","type":"acceleration_strain_ref_length","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"NX","abbrevation_translation":"dNX","actual_expression":"","auto":false,"base_type":"nx","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"49","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"dNX","type":"nx","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mNX","abbrevation_translation":"rel_dNX","actual_expression":"","auto":false,"base_type":"nx","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"49","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: dNX","type":"movement_nx","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vNX","abbrevation_translation":"vdNX","actual_expression":"","auto":false,"base_type":"nx","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"49","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: dNX","type":"velocity_nx","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"aNX","abbrevation_translation":"adNX","actual_expression":"","auto":false,"base_type":"nx","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"49","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: dNX","type":"acceleration_nx","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"NY","abbrevation_translation":"dNY","actual_expression":"","auto":false,"base_type":"ny","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"50","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"dNY","type":"ny","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mNY","abbrevation_translation":"rel_dNY","actual_expression":"","auto":false,"base_type":"ny","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"50","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: dNY","type":"movement_ny","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vNY","abbrevation_translation":"vdNY","actual_expression":"","auto":false,"base_type":"ny","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"50","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: dNY","type":"velocity_ny","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"aNY","abbrevation_translation":"adNY","actual_expression":"","auto":false,"base_type":"ny","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"50","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: dNY","type":"acceleration_ny","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"NZ","abbrevation_translation":"dNZ","actual_expression":"","auto":false,"base_type":"nz","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"51","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"dNZ","type":"nz","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mNZ","abbrevation_translation":"rel_dNZ","actual_expression":"","auto":false,"base_type":"nz","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"51","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: dNZ","type":"movement_nz","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vNZ","abbrevation_translation":"vdNZ","actual_expression":"","auto":false,"base_type":"nz","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"51","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: dNZ","type":"velocity_nz","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"aNZ","abbrevation_translation":"adNZ","actual_expression":"","auto":false,"base_type":"nz","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"51","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: dNZ","type":"acceleration_nz","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"intersection_error","abbrevation_translation":"Intersection deviation","actual_expression":"","auto":false,"base_type":"intersection_error","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"52","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Intersection Deviation","type":"intersection_error","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mintersection_error","abbrevation_translation":"rel_Intersection deviation","actual_expression":"","auto":false,"base_type":"intersection_error","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"52","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Intersection Deviation","type":"movement_intersection_error","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vintersection_error","abbrevation_translation":"vIntersection deviation","actual_expression":"","auto":false,"base_type":"intersection_error","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"52","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Intersection Deviation","type":"velocity_intersection_error","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aintersection_error","abbrevation_translation":"aIntersection deviation","actual_expression":"","auto":false,"base_type":"intersection_error","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"52","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Intersection Deviation","type":"acceleration_intersection_error","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"suitability","abbrevation_translation":"Suitability","actual_expression":"","auto":false,"base_type":"suitability_for_tacking","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"53","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Suitability For Tacking","type":"suitability_for_tacking","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"msuitability","abbrevation_translation":"rel_Suitability","actual_expression":"","auto":false,"base_type":"suitability_for_tacking","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"53","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: Suitability For Tacking","type":"movement_suitability_for_tacking","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vsuitability","abbrevation_translation":"vSuitability","actual_expression":"","auto":false,"base_type":"suitability_for_tacking","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"53","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: Suitability For Tacking","type":"velocity_suitability_for_tacking","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"asuitability","abbrevation_translation":"aSuitability","actual_expression":"","auto":false,"base_type":"suitability_for_tacking","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"53","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: Suitability For Tacking","type":"acceleration_suitability_for_tacking","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"facet_deformation_residual","abbrevation_translation":"ResD","actual_expression":"","auto":false,"base_type":"facet_deformation_residual","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"54","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Residual after deformation","type":"facet_deformation_residual","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mfacet_deformation_residual","abbrevation_translation":"rel_ResD","actual_expression":"","auto":false,"base_type":"facet_deformation_residual","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"54","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Residual after deformation","type":"movement_facet_deformation_residual","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vfacet_deformation_residual","abbrevation_translation":"vResD","actual_expression":"","auto":false,"base_type":"facet_deformation_residual","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"54","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Residual after deformation","type":"velocity_facet_deformation_residual","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"afacet_deformation_residual","abbrevation_translation":"aResD","actual_expression":"","auto":false,"base_type":"facet_deformation_residual","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"54","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Residual after deformation","type":"acceleration_facet_deformation_residual","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"facet_stereo_residual","abbrevation_translation":"ResS","actual_expression":"","auto":false,"base_type":"facet_stereo_residual","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"55","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Stereo residual","type":"facet_stereo_residual","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mfacet_stereo_residual","abbrevation_translation":"rel_ResS","actual_expression":"","auto":false,"base_type":"facet_stereo_residual","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"55","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Stereo residual","type":"movement_facet_stereo_residual","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vfacet_stereo_residual","abbrevation_translation":"vResS","actual_expression":"","auto":false,"base_type":"facet_stereo_residual","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"55","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Stereo residual","type":"velocity_facet_stereo_residual","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"afacet_stereo_residual","abbrevation_translation":"aResS","actual_expression":"","auto":false,"base_type":"facet_stereo_residual","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"55","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Stereo residual","type":"acceleration_facet_stereo_residual","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"facet_deformation_accuracy","abbrevation_translation":"fda","actual_expression":"","auto":false,"base_type":"facet_deformation_accuracy","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"56","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"deformation accuracy","type":"facet_deformation_accuracy","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mfacet_deformation_accuracy","abbrevation_translation":"rel_fda","actual_expression":"","auto":false,"base_type":"facet_deformation_accuracy","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"56","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: deformation accuracy","type":"movement_facet_deformation_accuracy","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vfacet_deformation_accuracy","abbrevation_translation":"vfda","actual_expression":"","auto":false,"base_type":"facet_deformation_accuracy","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"56","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: deformation accuracy","type":"velocity_facet_deformation_accuracy","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"afacet_deformation_accuracy","abbrevation_translation":"afda","actual_expression":"","auto":false,"base_type":"facet_deformation_accuracy","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"56","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: deformation accuracy","type":"acceleration_facet_deformation_accuracy","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"facet_stereo_accuracy","abbrevation_translation":"fsa","actual_expression":"","auto":false,"base_type":"facet_stereo_accuracy","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"57","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"stereo accuracy","type":"facet_stereo_accuracy","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mfacet_stereo_accuracy","abbrevation_translation":"rel_fsa","actual_expression":"","auto":false,"base_type":"facet_stereo_accuracy","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"57","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: stereo accuracy","type":"movement_facet_stereo_accuracy","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vfacet_stereo_accuracy","abbrevation_translation":"vfsa","actual_expression":"","auto":false,"base_type":"facet_stereo_accuracy","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"57","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: stereo accuracy","type":"velocity_facet_stereo_accuracy","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"afacet_stereo_accuracy","abbrevation_translation":"afsa","actual_expression":"","auto":false,"base_type":"facet_stereo_accuracy","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"57","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: stereo accuracy","type":"acceleration_facet_stereo_accuracy","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"tensile_stress_technical","abbrevation_translation":"sigma","actual_expression":"","auto":false,"base_type":"tensile_stress_technical","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"58","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Stress","type":"tensile_stress_technical","unit":"PRESSURE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mtensile_stress_technical","abbrevation_translation":"rel_sigma","actual_expression":"","auto":false,"base_type":"tensile_stress_technical","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"58","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Stress","type":"movement_tensile_stress_technical","unit":"PRESSURE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vtensile_stress_technical","abbrevation_translation":"vsigma","actual_expression":"","auto":false,"base_type":"tensile_stress_technical","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"58","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Stress","type":"velocity_tensile_stress_technical","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"atensile_stress_technical","abbrevation_translation":"asigma","actual_expression":"","auto":false,"base_type":"tensile_stress_technical","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"58","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Stress","type":"acceleration_tensile_stress_technical","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"tensile_stress_const_volume","abbrevation_translation":"sigmaVC","actual_expression":"","auto":false,"base_type":"tensile_stress_const_volume","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"59","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"True stress (constant volume)","type":"tensile_stress_const_volume","unit":"PRESSURE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mtensile_stress_const_volume","abbrevation_translation":"rel_sigmaVC","actual_expression":"","auto":false,"base_type":"tensile_stress_const_volume","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"59","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: True stress (constant volume)","type":"movement_tensile_stress_const_volume","unit":"PRESSURE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vtensile_stress_const_volume","abbrevation_translation":"vsigmaVC","actual_expression":"","auto":false,"base_type":"tensile_stress_const_volume","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"59","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: True stress (constant volume)","type":"velocity_tensile_stress_const_volume","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"atensile_stress_const_volume","abbrevation_translation":"asigmaVC","actual_expression":"","auto":false,"base_type":"tensile_stress_const_volume","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"59","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: True stress (constant volume)","type":"acceleration_tensile_stress_const_volume","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"tensile_stress_isotropic","abbrevation_translation":"sigmaISO","actual_expression":"","auto":false,"base_type":"tensile_stress_isotropic","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"60","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"True stress (isotropic)","type":"tensile_stress_isotropic","unit":"PRESSURE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mtensile_stress_isotropic","abbrevation_translation":"rel_sigmaISO","actual_expression":"","auto":false,"base_type":"tensile_stress_isotropic","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"60","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: True stress (isotropic)","type":"movement_tensile_stress_isotropic","unit":"PRESSURE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vtensile_stress_isotropic","abbrevation_translation":"vsigmaISO","actual_expression":"","auto":false,"base_type":"tensile_stress_isotropic","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"60","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: True stress (isotropic)","type":"velocity_tensile_stress_isotropic","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"atensile_stress_isotropic","abbrevation_translation":"asigmaISO","actual_expression":"","auto":false,"base_type":"tensile_stress_isotropic","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"60","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: True stress (isotropic)","type":"acceleration_tensile_stress_isotropic","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"tensile_stress_sym_z_disp","abbrevation_translation":"sigmaSZD","actual_expression":"","auto":false,"base_type":"tensile_stress_sym_z_disp","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"61","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"True stress (symmetrical Z displacement)","type":"tensile_stress_sym_z_disp","unit":"PRESSURE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mtensile_stress_sym_z_disp","abbrevation_translation":"rel_sigmaSZD","actual_expression":"","auto":false,"base_type":"tensile_stress_sym_z_disp","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"61","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: True stress (symmetrical Z displacement)","type":"movement_tensile_stress_sym_z_disp","unit":"PRESSURE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vtensile_stress_sym_z_disp","abbrevation_translation":"vsigmaSZD","actual_expression":"","auto":false,"base_type":"tensile_stress_sym_z_disp","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"61","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: True stress (symmetrical Z displacement)","type":"velocity_tensile_stress_sym_z_disp","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"atensile_stress_sym_z_disp","abbrevation_translation":"asigmaSZD","actual_expression":"","auto":false,"base_type":"tensile_stress_sym_z_disp","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"61","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: True stress (symmetrical Z displacement)","type":"acceleration_tensile_stress_sym_z_disp","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"Dls","abbrevation_translation":"S","actual_expression":"","auto":false,"base_type":"dimension_linear_size","category":"GD&T","constructed":false,"deduction":"","dynamic":false,"id":"62","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Linear Size","type":"dimension_linear_size","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mDls","abbrevation_translation":"rel_S","actual_expression":"","auto":false,"base_type":"dimension_linear_size","category":"GD&T","constructed":false,"deduction":"M","dynamic":false,"id":"62","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Linear Size","type":"movement_dimension_linear_size","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vDls","abbrevation_translation":"vS","actual_expression":"","auto":false,"base_type":"dimension_linear_size","category":"GD&T","constructed":false,"deduction":"V","dynamic":false,"id":"62","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Linear Size","type":"velocity_dimension_linear_size","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aDls","abbrevation_translation":"aS","actual_expression":"","auto":false,"base_type":"dimension_linear_size","category":"GD&T","constructed":false,"deduction":"A","dynamic":false,"id":"62","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Linear Size","type":"acceleration_dimension_linear_size","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"major_strain_dir","abbrevation_translation":"dirEps1","actual_expression":"","auto":false,"base_type":"major_strain_direction","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"63","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Direction major strain","type":"major_strain_direction","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mmajor_strain_dir","abbrevation_translation":"rel_dirEps1","actual_expression":"","auto":false,"base_type":"major_strain_direction","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"63","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Direction major strain","type":"movement_major_strain_direction","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vmajor_strain_dir","abbrevation_translation":"vdirEps1","actual_expression":"","auto":false,"base_type":"major_strain_direction","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"63","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Direction major strain","type":"velocity_major_strain_direction","unit":"STRAIN_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"amajor_strain_dir","abbrevation_translation":"adirEps1","actual_expression":"","auto":false,"base_type":"major_strain_direction","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"63","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Direction major strain","type":"acceleration_major_strain_direction","unit":"STRAIN_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"minor_strain_dir","abbrevation_translation":"dirEps2","actual_expression":"","auto":false,"base_type":"minor_strain_direction","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"64","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Direction minor strain","type":"minor_strain_direction","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mminor_strain_dir","abbrevation_translation":"rel_dirEps2","actual_expression":"","auto":false,"base_type":"minor_strain_direction","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"64","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Direction minor strain","type":"movement_minor_strain_direction","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vminor_strain_dir","abbrevation_translation":"vdirEps2","actual_expression":"","auto":false,"base_type":"minor_strain_direction","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"64","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Direction minor strain","type":"velocity_minor_strain_direction","unit":"STRAIN_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aminor_strain_dir","abbrevation_translation":"adirEps2","actual_expression":"","auto":false,"base_type":"minor_strain_direction","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"64","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Direction minor strain","type":"acceleration_minor_strain_direction","unit":"STRAIN_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"tresca_strain","abbrevation_translation":"phiT","actual_expression":"","auto":false,"base_type":"tresca_strain","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"65","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Equivalent Tresca strain","type":"tresca_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mtresca_strain","abbrevation_translation":"rel_phiT","actual_expression":"","auto":false,"base_type":"tresca_strain","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"65","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Equivalent Tresca strain","type":"movement_tresca_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vtresca_strain","abbrevation_translation":"vphiT","actual_expression":"","auto":false,"base_type":"tresca_strain","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"65","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Equivalent Tresca strain","type":"velocity_tresca_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"atresca_strain","abbrevation_translation":"aphiT","actual_expression":"","auto":false,"base_type":"tresca_strain","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"65","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Equivalent Tresca strain","type":"acceleration_tresca_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mises_strain","abbrevation_translation":"phiM","actual_expression":"","auto":false,"base_type":"mises_strain","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"66","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Equivalent Mises strain","type":"mises_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mmises_strain","abbrevation_translation":"rel_phiM","actual_expression":"","auto":false,"base_type":"mises_strain","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"66","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Equivalent Mises strain","type":"movement_mises_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vmises_strain","abbrevation_translation":"vphiM","actual_expression":"","auto":false,"base_type":"mises_strain","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"66","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Equivalent Mises strain","type":"velocity_mises_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"amises_strain","abbrevation_translation":"aphiM","actual_expression":"","auto":false,"base_type":"mises_strain","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"66","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Equivalent Mises strain","type":"acceleration_mises_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"shear_angle","abbrevation_translation":"theta","actual_expression":"","auto":false,"base_type":"shear_angle","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"67","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Shear angle","type":"shear_angle","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mshear_angle","abbrevation_translation":"rel_theta","actual_expression":"","auto":false,"base_type":"shear_angle","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"67","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Shear angle","type":"movement_shear_angle","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vshear_angle","abbrevation_translation":"vtheta","actual_expression":"","auto":false,"base_type":"shear_angle","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"67","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Shear angle","type":"velocity_shear_angle","unit":"ANGLE_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"ashear_angle","abbrevation_translation":"atheta","actual_expression":"","auto":false,"base_type":"shear_angle","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"67","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Shear angle","type":"acceleration_shear_angle","unit":"ANGLE_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"user","abbrevation_translation":"User","actual_expression":"","auto":false,"base_type":"construct_user_defined","category":"-","constructed":true,"deduction":"","dynamic":false,"id":"68","internal":false,"nominal_expression":"0.0","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"User-Defined","type":"construct_user_defined","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"muser","abbrevation_translation":"rel_User","actual_expression":"","auto":false,"base_type":"construct_user_defined","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"68","internal":true,"nominal_expression":"0.0","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: User-Defined","type":"movement_construct_user_defined","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vuser","abbrevation_translation":"vUser","actual_expression":"","auto":false,"base_type":"construct_user_defined","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"68","internal":true,"nominal_expression":"0.0","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: User-Defined","type":"velocity_construct_user_defined","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"auser","abbrevation_translation":"aUser","actual_expression":"","auto":false,"base_type":"construct_user_defined","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"68","internal":true,"nominal_expression":"0.0","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: User-Defined","type":"acceleration_construct_user_defined","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"","abbrevation_translation":"","actual_expression":"","auto":true,"base_type":"","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"69","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"","type":"","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"m","abbrevation_translation":"rel_","actual_expression":"","auto":true,"base_type":"","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"69","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: ","type":"movement_","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"v","abbrevation_translation":"v","actual_expression":"","auto":true,"base_type":"","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"69","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: ","type":"velocity_","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"a","abbrevation_translation":"a","actual_expression":"","auto":true,"base_type":"","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"69","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: ","type":"acceleration_","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"curve_length","abbrevation_translation":"Curve length","actual_expression":"","auto":false,"base_type":"curve_length","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"70","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Curve length","type":"curve_length","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mcurve_length","abbrevation_translation":"rel_Curve length","actual_expression":"","auto":false,"base_type":"curve_length","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"70","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: Curve length","type":"movement_curve_length","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vcurve_length","abbrevation_translation":"vCurve length","actual_expression":"","auto":false,"base_type":"curve_length","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"70","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: Curve length","type":"velocity_curve_length","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"acurve_length","abbrevation_translation":"aCurve length","actual_expression":"","auto":false,"base_type":"curve_length","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"70","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: Curve length","type":"acceleration_curve_length","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"user statistics","abbrevation_translation":"User","actual_expression":"","auto":false,"base_type":"construct_user_defined_statistics","category":"-","constructed":true,"deduction":"","dynamic":false,"id":"71","internal":false,"nominal_expression":"0.0","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"User-Defined (Scalar)","type":"construct_user_defined_statistics","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"muser statistics","abbrevation_translation":"rel_User","actual_expression":"","auto":false,"base_type":"construct_user_defined_statistics","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"71","internal":true,"nominal_expression":"0.0","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: User-Defined (Scalar)","type":"movement_construct_user_defined_statistics","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vuser statistics","abbrevation_translation":"vUser","actual_expression":"","auto":false,"base_type":"construct_user_defined_statistics","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"71","internal":true,"nominal_expression":"0.0","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: User-Defined (Scalar)","type":"velocity_construct_user_defined_statistics","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"auser statistics","abbrevation_translation":"aUser","actual_expression":"","auto":false,"base_type":"construct_user_defined_statistics","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"71","internal":true,"nominal_expression":"0.0","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: User-Defined (Scalar)","type":"acceleration_construct_user_defined_statistics","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"epsilon_x_strain_dir","abbrevation_translation":"dirEpsX","actual_expression":"","auto":false,"base_type":"epsilon_x_direction","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"72","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Direction epsilon (X)","type":"epsilon_x_direction","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mepsilon_x_strain_dir","abbrevation_translation":"rel_dirEpsX","actual_expression":"","auto":false,"base_type":"epsilon_x_direction","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"72","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Direction epsilon (X)","type":"movement_epsilon_x_direction","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vepsilon_x_strain_dir","abbrevation_translation":"vdirEpsX","actual_expression":"","auto":false,"base_type":"epsilon_x_direction","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"72","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Direction epsilon (X)","type":"velocity_epsilon_x_direction","unit":"STRAIN_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aepsilon_x_strain_dir","abbrevation_translation":"adirEpsX","actual_expression":"","auto":false,"base_type":"epsilon_x_direction","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"72","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Direction epsilon (X)","type":"acceleration_epsilon_x_direction","unit":"STRAIN_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"epsilon_y_strain_dir","abbrevation_translation":"dirEpsY","actual_expression":"","auto":false,"base_type":"epsilon_y_direction","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"73","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Direction epsilon (Y)","type":"epsilon_y_direction","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mepsilon_y_strain_dir","abbrevation_translation":"rel_dirEpsY","actual_expression":"","auto":false,"base_type":"epsilon_y_direction","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"73","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Direction epsilon (Y)","type":"movement_epsilon_y_direction","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vepsilon_y_strain_dir","abbrevation_translation":"vdirEpsY","actual_expression":"","auto":false,"base_type":"epsilon_y_direction","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"73","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Direction epsilon (Y)","type":"velocity_epsilon_y_direction","unit":"STRAIN_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aepsilon_y_strain_dir","abbrevation_translation":"adirEpsY","actual_expression":"","auto":false,"base_type":"epsilon_y_direction","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"73","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Direction epsilon (Y)","type":"acceleration_epsilon_y_direction","unit":"STRAIN_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"DV","abbrevation_translation":"sdv","actual_expression":"","auto":false,"base_type":"defect_map_value","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"74","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Surface Defect Value","type":"defect_map_value","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mDV","abbrevation_translation":"rel_sdv","actual_expression":"","auto":false,"base_type":"defect_map_value","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"74","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Surface Defect Value","type":"movement_defect_map_value","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vDV","abbrevation_translation":"vsdv","actual_expression":"","auto":false,"base_type":"defect_map_value","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"74","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Surface Defect Value","type":"velocity_defect_map_value","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aDV","abbrevation_translation":"asdv","actual_expression":"","auto":false,"base_type":"defect_map_value","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"74","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Surface Defect Value","type":"acceleration_defect_map_value","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"imported_value","abbrevation_translation":"imp","actual_expression":"","auto":false,"base_type":"imported_value","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"75","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"imported value","type":"imported_value","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mimported_value","abbrevation_translation":"rel_imp","actual_expression":"","auto":false,"base_type":"imported_value","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"75","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: imported value","type":"movement_imported_value","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vimported_value","abbrevation_translation":"vimp","actual_expression":"","auto":false,"base_type":"imported_value","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"75","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: imported value","type":"velocity_imported_value","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"aimported_value","abbrevation_translation":"aimp","actual_expression":"","auto":false,"base_type":"imported_value","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"75","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: imported value","type":"acceleration_imported_value","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"OD","abbrevation_translation":"Ø(o)","actual_expression":"","auto":false,"base_type":"outer_diameter","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"76","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Outer Diameter","type":"outer_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mOD","abbrevation_translation":"rel_Ø(o)","actual_expression":"","auto":false,"base_type":"outer_diameter","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"76","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Outer Diameter","type":"movement_outer_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vOD","abbrevation_translation":"vØ(o)","actual_expression":"","auto":false,"base_type":"outer_diameter","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"76","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Outer Diameter","type":"velocity_outer_diameter","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aOD","abbrevation_translation":"aØ(o)","actual_expression":"","auto":false,"base_type":"outer_diameter","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"76","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Outer Diameter","type":"acceleration_outer_diameter","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"OR","abbrevation_translation":"R(o)","actual_expression":"","auto":false,"base_type":"outer_radius","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"77","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Outer Radius","type":"outer_radius","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mOR","abbrevation_translation":"rel_R(o)","actual_expression":"","auto":false,"base_type":"outer_radius","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"77","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Outer Radius","type":"movement_outer_radius","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vOR","abbrevation_translation":"vR(o)","actual_expression":"","auto":false,"base_type":"outer_radius","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"77","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Outer Radius","type":"velocity_outer_radius","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aOR","abbrevation_translation":"aR(o)","actual_expression":"","auto":false,"base_type":"outer_radius","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"77","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Outer Radius","type":"acceleration_outer_radius","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"thickness_strain","abbrevation_translation":"eps3","actual_expression":"","auto":false,"base_type":"thickness_strain","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"78","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Thickness Strain","type":"thickness_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mthickness_strain","abbrevation_translation":"rel_eps3","actual_expression":"","auto":false,"base_type":"thickness_strain","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"78","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Thickness Strain","type":"movement_thickness_strain","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vthickness_strain","abbrevation_translation":"eps3r","actual_expression":"","auto":false,"base_type":"thickness_strain","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"78","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Thickness Strain Rate","type":"velocity_thickness_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"athickness_strain","abbrevation_translation":"aeps3","actual_expression":"","auto":false,"base_type":"thickness_strain","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"78","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Thickness Strain","type":"acceleration_thickness_strain","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"SL","abbrevation_translation":"sd","actual_expression":"","auto":false,"base_type":"surface_distance_value","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"79","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Surface Distance Value","type":"surface_distance_value","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mSL","abbrevation_translation":"rel_sd","actual_expression":"","auto":false,"base_type":"surface_distance_value","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"79","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Surface Distance Value","type":"movement_surface_distance_value","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vSL","abbrevation_translation":"vsd","actual_expression":"","auto":false,"base_type":"surface_distance_value","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"79","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Surface Distance Value","type":"velocity_surface_distance_value","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aSL","abbrevation_translation":"asd","actual_expression":"","auto":false,"base_type":"surface_distance_value","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"79","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Surface Distance Value","type":"acceleration_surface_distance_value","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"DA","abbrevation_translation":"da","actual_expression":"","auto":false,"base_type":"draft_angle","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"80","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Draft angle","type":"draft_angle","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mDA","abbrevation_translation":"rel_da","actual_expression":"","auto":false,"base_type":"draft_angle","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"80","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Draft angle","type":"movement_draft_angle","unit":"ANGLE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vDA","abbrevation_translation":"vda","actual_expression":"","auto":false,"base_type":"draft_angle","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"80","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Draft angle","type":"velocity_draft_angle","unit":"ANGLE_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aDA","abbrevation_translation":"ada","actual_expression":"","auto":false,"base_type":"draft_angle","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"80","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Draft angle","type":"acceleration_draft_angle","unit":"ANGLE_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"point_quality","abbrevation_translation":"pq","actual_expression":"","auto":false,"base_type":"point_quality","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"81","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Scan point quality","type":"point_quality","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mpoint_quality","abbrevation_translation":"rel_pq","actual_expression":"","auto":false,"base_type":"point_quality","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"81","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Scan point quality","type":"movement_point_quality","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vpoint_quality","abbrevation_translation":"vpq","actual_expression":"","auto":false,"base_type":"point_quality","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"81","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Scan point quality","type":"velocity_point_quality","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"apoint_quality","abbrevation_translation":"apq","actual_expression":"","auto":false,"base_type":"point_quality","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"81","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Scan point quality","type":"acceleration_point_quality","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"lighting change sigma","abbrevation_translation":"light ch. (sig.)","actual_expression":"","auto":false,"base_type":"lighting_change_sigma","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"82","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Lighting change (sigma)","type":"lighting_change_sigma","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mlighting change sigma","abbrevation_translation":"rel_light ch. (sig.)","actual_expression":"","auto":false,"base_type":"lighting_change_sigma","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"82","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Lighting change (sigma)","type":"movement_lighting_change_sigma","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vlighting change sigma","abbrevation_translation":"vlight ch. (sig.)","actual_expression":"","auto":false,"base_type":"lighting_change_sigma","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"82","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Lighting change (sigma)","type":"velocity_lighting_change_sigma","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"alighting change sigma","abbrevation_translation":"alight ch. (sig.)","actual_expression":"","auto":false,"base_type":"lighting_change_sigma","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"82","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Lighting change (sigma)","type":"acceleration_lighting_change_sigma","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mean intersection deviation","abbrevation_translation":"mean int. dev.","actual_expression":"","auto":false,"base_type":"mean_intersection_deviation","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"83","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Mean intersection deviation","type":"mean_intersection_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mmean intersection deviation","abbrevation_translation":"rel_mean int. dev.","actual_expression":"","auto":false,"base_type":"mean_intersection_deviation","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"83","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Mean intersection deviation","type":"movement_mean_intersection_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vmean intersection deviation","abbrevation_translation":"vmean int. dev.","actual_expression":"","auto":false,"base_type":"mean_intersection_deviation","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"83","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Mean intersection deviation","type":"velocity_mean_intersection_deviation","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"amean intersection deviation","abbrevation_translation":"amean int. dev.","actual_expression":"","auto":false,"base_type":"mean_intersection_deviation","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"83","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Mean intersection deviation","type":"acceleration_mean_intersection_deviation","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"sensor movement","abbrevation_translation":"sen. move","actual_expression":"","auto":false,"base_type":"sensor_movement","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"84","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Sensor movement","type":"sensor_movement","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"msensor movement","abbrevation_translation":"rel_sen. move","actual_expression":"","auto":false,"base_type":"sensor_movement","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"84","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Sensor movement","type":"movement_sensor_movement","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vsensor movement","abbrevation_translation":"vsen. move","actual_expression":"","auto":false,"base_type":"sensor_movement","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"84","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Sensor movement","type":"velocity_sensor_movement","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"asensor movement","abbrevation_translation":"asen. move","actual_expression":"","auto":false,"base_type":"sensor_movement","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"84","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Sensor movement","type":"acceleration_sensor_movement","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"transformation deviation","abbrevation_translation":"trans. dev.","actual_expression":"","auto":false,"base_type":"transformation_deviation","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"85","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Transformation deviation","type":"transformation_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mtransformation deviation","abbrevation_translation":"rel_trans. dev.","actual_expression":"","auto":false,"base_type":"transformation_deviation","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"85","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Transformation deviation","type":"movement_transformation_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vtransformation deviation","abbrevation_translation":"vtrans. dev.","actual_expression":"","auto":false,"base_type":"transformation_deviation","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"85","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Transformation deviation","type":"velocity_transformation_deviation","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"atransformation deviation","abbrevation_translation":"atrans. dev.","actual_expression":"","auto":false,"base_type":"transformation_deviation","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"85","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Transformation deviation","type":"acceleration_transformation_deviation","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"alignment residual (measurements)","abbrevation_translation":"align. res. (meas.)","actual_expression":"","auto":false,"base_type":"measurement_alignment_residual","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"86","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Alignment residual (measurements)","type":"measurement_alignment_residual","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"malignment residual (measurements)","abbrevation_translation":"rel_align. res. (meas.)","actual_expression":"","auto":false,"base_type":"measurement_alignment_residual","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"86","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Alignment residual (measurements)","type":"movement_measurement_alignment_residual","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"valignment residual (measurements)","abbrevation_translation":"valign. res. (meas.)","actual_expression":"","auto":false,"base_type":"measurement_alignment_residual","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"86","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Alignment residual (measurements)","type":"velocity_measurement_alignment_residual","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aalignment residual (measurements)","abbrevation_translation":"aalign. res. (meas.)","actual_expression":"","auto":false,"base_type":"measurement_alignment_residual","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"86","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Alignment residual (measurements)","type":"acceleration_measurement_alignment_residual","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"alignment residual (preview mesh)","abbrevation_translation":"align. res. (prev. mesh)","actual_expression":"","auto":false,"base_type":"measurement_mesh_alignment_residual","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"87","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Alignment residual (preview meshes)","type":"measurement_mesh_alignment_residual","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"malignment residual (preview mesh)","abbrevation_translation":"rel_align. res. (prev. mesh)","actual_expression":"","auto":false,"base_type":"measurement_mesh_alignment_residual","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"87","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Alignment residual (preview meshes)","type":"movement_measurement_mesh_alignment_residual","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"valignment residual (preview mesh)","abbrevation_translation":"valign. res. (prev. mesh)","actual_expression":"","auto":false,"base_type":"measurement_mesh_alignment_residual","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"87","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Alignment residual (preview meshes)","type":"velocity_measurement_mesh_alignment_residual","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aalignment residual (preview mesh)","abbrevation_translation":"aalign. res. (prev. mesh)","actual_expression":"","auto":false,"base_type":"measurement_mesh_alignment_residual","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"87","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Alignment residual (preview meshes)","type":"acceleration_measurement_mesh_alignment_residual","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"alignment residual (reference points)","abbrevation_translation":"align. res. (ref. pts.)","actual_expression":"","auto":false,"base_type":"measurement_reference_point_alignment_residual","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"88","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Alignment residual (reference points)","type":"measurement_reference_point_alignment_residual","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"malignment residual (reference points)","abbrevation_translation":"rel_align. res. (ref. pts.)","actual_expression":"","auto":false,"base_type":"measurement_reference_point_alignment_residual","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"88","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Alignment residual (reference points)","type":"movement_measurement_reference_point_alignment_residual","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"valignment residual (reference points)","abbrevation_translation":"valign. res. (ref. pts.)","actual_expression":"","auto":false,"base_type":"measurement_reference_point_alignment_residual","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"88","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Alignment residual (reference points)","type":"velocity_measurement_reference_point_alignment_residual","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aalignment residual (reference points)","abbrevation_translation":"aalign. res. (ref. pts.)","actual_expression":"","auto":false,"base_type":"measurement_reference_point_alignment_residual","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"88","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Alignment residual (reference points)","type":"acceleration_measurement_reference_point_alignment_residual","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"number of coded points in image","abbrevation_translation":"no. cod. image pts.","actual_expression":"","auto":false,"base_type":"coded_image_points","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"89","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Number of coded image points","type":"coded_image_points","unit":"COUNT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mnumber of coded points in image","abbrevation_translation":"rel_no. cod. image pts.","actual_expression":"","auto":false,"base_type":"coded_image_points","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"89","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Number of coded image points","type":"movement_coded_image_points","unit":"COUNT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vnumber of coded points in image","abbrevation_translation":"vno. cod. image pts.","actual_expression":"","auto":false,"base_type":"coded_image_points","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"89","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Number of coded image points","type":"velocity_coded_image_points","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"anumber of coded points in image","abbrevation_translation":"ano. cod. image pts.","actual_expression":"","auto":false,"base_type":"coded_image_points","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"89","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Number of coded image points","type":"acceleration_coded_image_points","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"average point deviation","abbrevation_translation":"avg. pt. dev.","actual_expression":"","auto":false,"base_type":"average_point_deviation","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"90","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Average point deviation","type":"average_point_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"maverage point deviation","abbrevation_translation":"rel_avg. pt. dev.","actual_expression":"","auto":false,"base_type":"average_point_deviation","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"90","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Average point deviation","type":"movement_average_point_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vaverage point deviation","abbrevation_translation":"vavg. pt. dev.","actual_expression":"","auto":false,"base_type":"average_point_deviation","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"90","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Average point deviation","type":"velocity_average_point_deviation","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aaverage point deviation","abbrevation_translation":"aavg. pt. dev.","actual_expression":"","auto":false,"base_type":"average_point_deviation","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"90","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Average point deviation","type":"acceleration_average_point_deviation","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"number of uncoded reference points","abbrevation_translation":"no. uncod. ref. pts.","actual_expression":"","auto":false,"base_type":"uncoded_reference_points","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"91","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Number of uncoded reference points","type":"uncoded_reference_points","unit":"COUNT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mnumber of uncoded reference points","abbrevation_translation":"rel_no. uncod. ref. pts.","actual_expression":"","auto":false,"base_type":"uncoded_reference_points","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"91","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Number of uncoded reference points","type":"movement_uncoded_reference_points","unit":"COUNT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vnumber of uncoded reference points","abbrevation_translation":"vno. uncod. ref. pts.","actual_expression":"","auto":false,"base_type":"uncoded_reference_points","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"91","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Number of uncoded reference points","type":"velocity_uncoded_reference_points","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"anumber of uncoded reference points","abbrevation_translation":"ano. uncod. ref. pts.","actual_expression":"","auto":false,"base_type":"uncoded_reference_points","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"91","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Number of uncoded reference points","type":"acceleration_uncoded_reference_points","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"average image point deviation","abbrevation_translation":"avg. image pt. dev.","actual_expression":"","auto":false,"base_type":"average_image_point_deviation","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"92","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Average image point deviation","type":"average_image_point_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"maverage image point deviation","abbrevation_translation":"rel_avg. image pt. dev.","actual_expression":"","auto":false,"base_type":"average_image_point_deviation","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"92","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Average image point deviation","type":"movement_average_image_point_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vaverage image point deviation","abbrevation_translation":"vavg. image pt. dev.","actual_expression":"","auto":false,"base_type":"average_image_point_deviation","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"92","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Average image point deviation","type":"velocity_average_image_point_deviation","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aaverage image point deviation","abbrevation_translation":"aavg. image pt. dev.","actual_expression":"","auto":false,"base_type":"average_image_point_deviation","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"92","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Average image point deviation","type":"acceleration_average_image_point_deviation","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"average reference point deviation","abbrevation_translation":"avg. ref. pt. dev.","actual_expression":"","auto":false,"base_type":"average_reference_point_deviation","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"93","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Average reference point deviation","type":"average_reference_point_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"maverage reference point deviation","abbrevation_translation":"rel_avg. ref. pt. dev.","actual_expression":"","auto":false,"base_type":"average_reference_point_deviation","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"93","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Average reference point deviation","type":"movement_average_reference_point_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vaverage reference point deviation","abbrevation_translation":"vavg. ref. pt. dev.","actual_expression":"","auto":false,"base_type":"average_reference_point_deviation","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"93","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Average reference point deviation","type":"velocity_average_reference_point_deviation","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aaverage reference point deviation","abbrevation_translation":"aavg. ref. pt. dev.","actual_expression":"","auto":false,"base_type":"average_reference_point_deviation","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"93","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Average reference point deviation","type":"acceleration_average_reference_point_deviation","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"average scale bar discrepancy","abbrevation_translation":"avg. scale bar discr.","actual_expression":"","auto":false,"base_type":"average_scale_bar_discrepancy","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"94","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Average scale bar discrepancy","type":"average_scale_bar_discrepancy","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"maverage scale bar discrepancy","abbrevation_translation":"rel_avg. scale bar discr.","actual_expression":"","auto":false,"base_type":"average_scale_bar_discrepancy","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"94","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Average scale bar discrepancy","type":"movement_average_scale_bar_discrepancy","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vaverage scale bar discrepancy","abbrevation_translation":"vavg. scale bar discr.","actual_expression":"","auto":false,"base_type":"average_scale_bar_discrepancy","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"94","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Average scale bar discrepancy","type":"velocity_average_scale_bar_discrepancy","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aaverage scale bar discrepancy","abbrevation_translation":"aavg. scale bar discr.","actual_expression":"","auto":false,"base_type":"average_scale_bar_discrepancy","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"94","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Average scale bar discrepancy","type":"acceleration_average_scale_bar_discrepancy","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"user classification","abbrevation_translation":"sdcl","actual_expression":"","auto":false,"base_type":"construct_user_defined_surface_classification","category":"-","constructed":true,"deduction":"","dynamic":false,"id":"95","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Surface Defect Classification","type":"construct_user_defined_surface_classification","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"muser classification","abbrevation_translation":"rel_sdcl","actual_expression":"","auto":false,"base_type":"construct_user_defined_surface_classification","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"95","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Surface Defect Classification","type":"movement_construct_user_defined_surface_classification","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vuser classification","abbrevation_translation":"vsdcl","actual_expression":"","auto":false,"base_type":"construct_user_defined_surface_classification","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"95","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Surface Defect Classification","type":"velocity_construct_user_defined_surface_classification","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"auser classification","abbrevation_translation":"asdcl","actual_expression":"","auto":false,"base_type":"construct_user_defined_surface_classification","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"95","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Surface Defect Classification","type":"acceleration_construct_user_defined_surface_classification","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"hole deviation","abbrevation_translation":"HD","actual_expression":"","auto":false,"base_type":"hole_deviation","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"96","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"dHD","type":"hole_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mhole deviation","abbrevation_translation":"rel_HD","actual_expression":"","auto":false,"base_type":"hole_deviation","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"96","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: dHD","type":"movement_hole_deviation","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vhole deviation","abbrevation_translation":"vHD","actual_expression":"","auto":false,"base_type":"hole_deviation","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"96","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: dHD","type":"velocity_hole_deviation","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"ahole deviation","abbrevation_translation":"aHD","actual_expression":"","auto":false,"base_type":"hole_deviation","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"96","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: dHD","type":"acceleration_hole_deviation","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"clamping force","abbrevation_translation":"cf","actual_expression":"","auto":false,"base_type":"clamping_force","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"97","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Clamping force","type":"clamping_force","unit":"FORCE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mclamping force","abbrevation_translation":"rel_cf","actual_expression":"","auto":false,"base_type":"clamping_force","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"97","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Clamping force","type":"movement_clamping_force","unit":"FORCE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vclamping force","abbrevation_translation":"vcf","actual_expression":"","auto":false,"base_type":"clamping_force","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"97","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Clamping force","type":"velocity_clamping_force","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aclamping force","abbrevation_translation":"acf","actual_expression":"","auto":false,"base_type":"clamping_force","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"97","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Clamping force","type":"acceleration_clamping_force","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"clamping displacement","abbrevation_translation":"cd","actual_expression":"","auto":false,"base_type":"clamping_displacement","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"98","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Clamping displacement","type":"clamping_displacement","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mclamping displacement","abbrevation_translation":"rel_cd","actual_expression":"","auto":false,"base_type":"clamping_displacement","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"98","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Clamping displacement","type":"movement_clamping_displacement","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vclamping displacement","abbrevation_translation":"vcd","actual_expression":"","auto":false,"base_type":"clamping_displacement","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"98","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Clamping displacement","type":"velocity_clamping_displacement","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aclamping displacement","abbrevation_translation":"acd","actual_expression":"","auto":false,"base_type":"clamping_displacement","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"98","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Clamping displacement","type":"acceleration_clamping_displacement","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"pattern_quality","abbrevation_translation":"patQ","actual_expression":"","auto":false,"base_type":"pattern_quality","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"99","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Pattern quality","type":"pattern_quality","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mpattern_quality","abbrevation_translation":"rel_patQ","actual_expression":"","auto":false,"base_type":"pattern_quality","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"99","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Pattern quality","type":"movement_pattern_quality","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vpattern_quality","abbrevation_translation":"vpatQ","actual_expression":"","auto":false,"base_type":"pattern_quality","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"99","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Pattern quality","type":"velocity_pattern_quality","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"apattern_quality","abbrevation_translation":"apatQ","actual_expression":"","auto":false,"base_type":"pattern_quality","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"99","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Pattern quality","type":"acceleration_pattern_quality","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"porosity","abbrevation_translation":"PG","actual_expression":"","auto":false,"base_type":"porosity","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"100","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Volume porosity (global)","type":"porosity","unit":"FRACTION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mporosity","abbrevation_translation":"rel_PG","actual_expression":"","auto":false,"base_type":"porosity","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"100","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Relative: Volume porosity (global)","type":"movement_porosity","unit":"FRACTION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vporosity","abbrevation_translation":"vPG","actual_expression":"","auto":false,"base_type":"porosity","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"100","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Velocity: Volume porosity (global)","type":"velocity_porosity","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aporosity","abbrevation_translation":"aPG","actual_expression":"","auto":false,"base_type":"porosity","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"100","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":true,"restriction":"","translation":"Acceleration: Volume porosity (global)","type":"acceleration_porosity","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_volume","abbrevation_translation":"Vp","actual_expression":"","auto":false,"base_type":"defect_volume","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"101","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Defect volume","type":"defect_volume","unit":"VOLUME","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_volume","abbrevation_translation":"rel_Vp","actual_expression":"","auto":false,"base_type":"defect_volume","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"101","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Defect volume","type":"movement_defect_volume","unit":"VOLUME","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_volume","abbrevation_translation":"vVp","actual_expression":"","auto":false,"base_type":"defect_volume","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"101","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Defect volume","type":"velocity_defect_volume","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_volume","abbrevation_translation":"aVp","actual_expression":"","auto":false,"base_type":"defect_volume","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"101","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Defect volume","type":"acceleration_defect_volume","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_size_x","abbrevation_translation":"SXp","actual_expression":"","auto":false,"base_type":"defect_size_x","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"102","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Defect size X","type":"defect_size_x","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_size_x","abbrevation_translation":"rel_SXp","actual_expression":"","auto":false,"base_type":"defect_size_x","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"102","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Defect size X","type":"movement_defect_size_x","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_size_x","abbrevation_translation":"vSXp","actual_expression":"","auto":false,"base_type":"defect_size_x","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"102","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Defect size X","type":"velocity_defect_size_x","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_size_x","abbrevation_translation":"aSXp","actual_expression":"","auto":false,"base_type":"defect_size_x","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"102","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Defect size X","type":"acceleration_defect_size_x","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_size_y","abbrevation_translation":"SYp","actual_expression":"","auto":false,"base_type":"defect_size_y","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"103","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Defect size Y","type":"defect_size_y","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_size_y","abbrevation_translation":"rel_SYp","actual_expression":"","auto":false,"base_type":"defect_size_y","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"103","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Defect size Y","type":"movement_defect_size_y","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_size_y","abbrevation_translation":"vSYp","actual_expression":"","auto":false,"base_type":"defect_size_y","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"103","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Defect size Y","type":"velocity_defect_size_y","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_size_y","abbrevation_translation":"aSYp","actual_expression":"","auto":false,"base_type":"defect_size_y","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"103","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Defect size Y","type":"acceleration_defect_size_y","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_size_z","abbrevation_translation":"SZp","actual_expression":"","auto":false,"base_type":"defect_size_z","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"104","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Defect size Z","type":"defect_size_z","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_size_z","abbrevation_translation":"rel_SZp","actual_expression":"","auto":false,"base_type":"defect_size_z","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"104","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Defect size Z","type":"movement_defect_size_z","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_size_z","abbrevation_translation":"vSZp","actual_expression":"","auto":false,"base_type":"defect_size_z","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"104","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Defect size Z","type":"velocity_defect_size_z","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_size_z","abbrevation_translation":"aSZp","actual_expression":"","auto":false,"base_type":"defect_size_z","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"104","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Defect size Z","type":"acceleration_defect_size_z","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_max_diameter","abbrevation_translation":"SDp","actual_expression":"","auto":false,"base_type":"defect_max_diameter","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"105","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Max. defect diagonal","type":"defect_max_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_max_diameter","abbrevation_translation":"rel_SDp","actual_expression":"","auto":false,"base_type":"defect_max_diameter","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"105","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Max. defect diagonal","type":"movement_defect_max_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_max_diameter","abbrevation_translation":"vSDp","actual_expression":"","auto":false,"base_type":"defect_max_diameter","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"105","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Max. defect diagonal","type":"velocity_defect_max_diameter","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_max_diameter","abbrevation_translation":"aSDp","actual_expression":"","auto":false,"base_type":"defect_max_diameter","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"105","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Max. defect diagonal","type":"acceleration_defect_max_diameter","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_diameter","abbrevation_translation":"Øp","actual_expression":"","auto":false,"base_type":"defect_diameter","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"106","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Defect diameter","type":"defect_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_diameter","abbrevation_translation":"rel_Øp","actual_expression":"","auto":false,"base_type":"defect_diameter","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"106","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Defect diameter","type":"movement_defect_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_diameter","abbrevation_translation":"vØp","actual_expression":"","auto":false,"base_type":"defect_diameter","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"106","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Defect diameter","type":"velocity_defect_diameter","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_diameter","abbrevation_translation":"aØp","actual_expression":"","auto":false,"base_type":"defect_diameter","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"106","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Defect diameter","type":"acceleration_defect_diameter","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_area","abbrevation_translation":"Ap","actual_expression":"","auto":false,"base_type":"defect_area","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"107","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Defect area","type":"defect_area","unit":"AREA","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_area","abbrevation_translation":"rel_Ap","actual_expression":"","auto":false,"base_type":"defect_area","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"107","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Defect area","type":"movement_defect_area","unit":"AREA","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_area","abbrevation_translation":"vAp","actual_expression":"","auto":false,"base_type":"defect_area","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"107","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Defect area","type":"velocity_defect_area","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_area","abbrevation_translation":"aAp","actual_expression":"","auto":false,"base_type":"defect_area","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"107","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Defect area","type":"acceleration_defect_area","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"outer_surface_distance","abbrevation_translation":"da","actual_expression":"","auto":false,"base_type":"outer_surface_distance","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"108","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Distance to outer surface","type":"outer_surface_distance","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mouter_surface_distance","abbrevation_translation":"rel_da","actual_expression":"","auto":false,"base_type":"outer_surface_distance","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"108","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Distance to outer surface","type":"movement_outer_surface_distance","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vouter_surface_distance","abbrevation_translation":"vda","actual_expression":"","auto":false,"base_type":"outer_surface_distance","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"108","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Distance to outer surface","type":"velocity_outer_surface_distance","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aouter_surface_distance","abbrevation_translation":"ada","actual_expression":"","auto":false,"base_type":"outer_surface_distance","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"108","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Distance to outer surface","type":"acceleration_outer_surface_distance","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_compactness","abbrevation_translation":"𝒞","actual_expression":"","auto":false,"base_type":"defect_compactness","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"109","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Compactness","type":"defect_compactness","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_compactness","abbrevation_translation":"rel_𝒞","actual_expression":"","auto":false,"base_type":"defect_compactness","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"109","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Compactness","type":"movement_defect_compactness","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_compactness","abbrevation_translation":"v𝒞","actual_expression":"","auto":false,"base_type":"defect_compactness","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"109","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Compactness","type":"velocity_defect_compactness","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_compactness","abbrevation_translation":"a𝒞","actual_expression":"","auto":false,"base_type":"defect_compactness","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"109","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Compactness","type":"acceleration_defect_compactness","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_sphericity","abbrevation_translation":"Ψ","actual_expression":"","auto":false,"base_type":"defect_sphericity","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"110","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Sphericity","type":"defect_sphericity","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_sphericity","abbrevation_translation":"rel_Ψ","actual_expression":"","auto":false,"base_type":"defect_sphericity","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"110","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Sphericity","type":"movement_defect_sphericity","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_sphericity","abbrevation_translation":"vΨ","actual_expression":"","auto":false,"base_type":"defect_sphericity","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"110","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Sphericity","type":"velocity_defect_sphericity","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_sphericity","abbrevation_translation":"aΨ","actual_expression":"","auto":false,"base_type":"defect_sphericity","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"110","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Sphericity","type":"acceleration_defect_sphericity","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"defect_equiv_diameter","abbrevation_translation":"Øe","actual_expression":"","auto":false,"base_type":"defect_equiv_diameter","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"111","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Equivalent diameter","type":"defect_equiv_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdefect_equiv_diameter","abbrevation_translation":"rel_Øe","actual_expression":"","auto":false,"base_type":"defect_equiv_diameter","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"111","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Equivalent diameter","type":"movement_defect_equiv_diameter","unit":"LENGTH","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdefect_equiv_diameter","abbrevation_translation":"vØe","actual_expression":"","auto":false,"base_type":"defect_equiv_diameter","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"111","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Equivalent diameter","type":"velocity_defect_equiv_diameter","unit":"VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adefect_equiv_diameter","abbrevation_translation":"aØe","actual_expression":"","auto":false,"base_type":"defect_equiv_diameter","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"111","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Equivalent diameter","type":"acceleration_defect_equiv_diameter","unit":"ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"fine alignment vertex quality","abbrevation_translation":"favq","actual_expression":"","auto":false,"base_type":"fine_alignment_vertex_quality","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"130","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"fine alignment: vertex quality","type":"fine_alignment_vertex_quality","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mfine alignment vertex quality","abbrevation_translation":"rel_favq","actual_expression":"","auto":false,"base_type":"fine_alignment_vertex_quality","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"130","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: fine alignment: vertex quality","type":"movement_fine_alignment_vertex_quality","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vfine alignment vertex quality","abbrevation_translation":"vfavq","actual_expression":"","auto":false,"base_type":"fine_alignment_vertex_quality","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"130","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: fine alignment: vertex quality","type":"velocity_fine_alignment_vertex_quality","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"afine alignment vertex quality","abbrevation_translation":"afavq","actual_expression":"","auto":false,"base_type":"fine_alignment_vertex_quality","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"130","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: fine alignment: vertex quality","type":"acceleration_fine_alignment_vertex_quality","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"fine alignment vertex cluster","abbrevation_translation":"favc","actual_expression":"","auto":false,"base_type":"fine_alignment_vertex_cluster","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"131","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"fine alignment: vertex cluster","type":"fine_alignment_vertex_cluster","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mfine alignment vertex cluster","abbrevation_translation":"rel_favc","actual_expression":"","auto":false,"base_type":"fine_alignment_vertex_cluster","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"131","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: fine alignment: vertex cluster","type":"movement_fine_alignment_vertex_cluster","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vfine alignment vertex cluster","abbrevation_translation":"vfavc","actual_expression":"","auto":false,"base_type":"fine_alignment_vertex_cluster","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"131","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: fine alignment: vertex cluster","type":"velocity_fine_alignment_vertex_cluster","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"afine alignment vertex cluster","abbrevation_translation":"afavc","actual_expression":"","auto":false,"base_type":"fine_alignment_vertex_cluster","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"131","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: fine alignment: vertex cluster","type":"acceleration_fine_alignment_vertex_cluster","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"surface_curvature","abbrevation_translation":"kappa","actual_expression":"","auto":false,"base_type":"surface_curvature","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"132","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Surface curvature","type":"surface_curvature","unit":"CURVATURE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"msurface_curvature","abbrevation_translation":"rel_kappa","actual_expression":"","auto":false,"base_type":"surface_curvature","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"132","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Surface curvature","type":"movement_surface_curvature","unit":"CURVATURE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vsurface_curvature","abbrevation_translation":"vkappa","actual_expression":"","auto":false,"base_type":"surface_curvature","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"132","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Surface curvature","type":"velocity_surface_curvature","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"asurface_curvature","abbrevation_translation":"akappa","actual_expression":"","auto":false,"base_type":"surface_curvature","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"132","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Surface curvature","type":"acceleration_surface_curvature","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"distance_flc","abbrevation_translation":"distflc","actual_expression":"","auto":false,"base_type":"distance_flc","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"133","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Distance To Forming Limit Curve","type":"distance_flc","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mdistance_flc","abbrevation_translation":"rel_distflc","actual_expression":"","auto":false,"base_type":"distance_flc","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"133","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Distance To Forming Limit Curve","type":"movement_distance_flc","unit":"STRAIN","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vdistance_flc","abbrevation_translation":"vdistflc","actual_expression":"","auto":false,"base_type":"distance_flc","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"133","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Distance To Forming Limit Curve","type":"velocity_distance_flc","unit":"STRAIN_VELOCITY","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"adistance_flc","abbrevation_translation":"adistflc","actual_expression":"","auto":false,"base_type":"distance_flc","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"133","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Distance To Forming Limit Curve","type":"acceleration_distance_flc","unit":"STRAIN_ACCELERATION","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"relative_distance_flc","abbrevation_translation":"reldistflc","actual_expression":"","auto":false,"base_type":"relative_distance_flc","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"134","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative Distance To Forming Limit Curve","type":"relative_distance_flc","unit":"FRACTION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"mrelative_distance_flc","abbrevation_translation":"rel_reldistflc","actual_expression":"","auto":false,"base_type":"relative_distance_flc","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"134","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Relative Distance To Forming Limit Curve","type":"movement_relative_distance_flc","unit":"FRACTION","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"vrelative_distance_flc","abbrevation_translation":"vreldistflc","actual_expression":"","auto":false,"base_type":"relative_distance_flc","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"134","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Relative Distance To Forming Limit Curve","type":"velocity_relative_distance_flc","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"arelative_distance_flc","abbrevation_translation":"areldistflc","actual_expression":"","auto":false,"base_type":"relative_distance_flc","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"134","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Relative Distance To Forming Limit Curve","type":"acceleration_relative_distance_flc","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":false},{"abbrevation":"formability","abbrevation_translation":"formability","actual_expression":"","auto":false,"base_type":"formability","category":"-","constructed":false,"deduction":"","dynamic":false,"id":"135","internal":false,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Formability","type":"formability","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"mformability","abbrevation_translation":"rel_formability","actual_expression":"","auto":false,"base_type":"formability","category":"Kin.","constructed":false,"deduction":"M","dynamic":false,"id":"135","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Relative: Formability","type":"movement_formability","unit":"UNIT_NONE","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"vformability","abbrevation_translation":"vformability","actual_expression":"","auto":false,"base_type":"formability","category":"Kin.","constructed":false,"deduction":"V","dynamic":false,"id":"135","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Velocity: Formability","type":"velocity_formability","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true},{"abbrevation":"aformability","abbrevation_translation":"aformability","actual_expression":"","auto":false,"base_type":"formability","category":"Kin.","constructed":false,"deduction":"A","dynamic":false,"id":"135","internal":true,"nominal_expression":"","package_reference":{"name":"","protected":false,"uuid":"00000000-0000-0000-0000-000000000000","version":""},"reduced":false,"restriction":"","translation":"Acceleration: Formability","type":"acceleration_formability","unit":"NO_UNIT","uuid":"00000000-0000-0000-0000-000000000000","visible":true}]},"templates":[{"actual_expression":"","i_inspect_pos":-1,"imported_type":10000001,"level":"system","name":"gom_press-shop-spots","nominal_expression":"aspect_ratio = length / width\nclass_result = grad (atan ((pow (max_depth_height_3sigma*100, 2)) / width))\narea > 5 and aspect_ratio < 50 ? class_result : 0","package":{"name":"Inspection","protected":false,"uuid":"a6769fbc-4bda-4cec-af9a-b189baf8b742","version":"1.0.0"},"sort_index":0,"uuid":"d75e9e7b-9b05-4572-a995-c469894f5b23"}]} (<class 'str'>)
	gom :> app.project.parts['Part'].actual.scan_area_avoid_direct_reflections						   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.scan_area_avoid_fixture									   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.scan_area_direct_reflections_angle						   --> 0.08726646259971647 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.scan_area_offset										   --> 5.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.scan_area_restricted_to_cad								   --> False (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.scan_area_usage											   --> manual (<class 'str'>)
	gom :> app.project.parts['Part'].actual.scan_data_avoid_direct_reflections_angle				   --> 0.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.scanning_template										   --> <Trait: gom.ApplicationTemplateInfo> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.selected_area											   --> 0.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.selection_arg_base										   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.selection_arg_target									   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.skin													   --> <Trait: Tom::MPRJ::SkinInfo> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.software_directory										   --> C:\Program Files\GOM\2020 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.stage													   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.system_package_directory								   --> C:\Program Files\GOM\2020\packages (<class 'str'>)
	gom :> app.project.parts['Part'].actual.table													   --> <Trait: Tom::MPRJ::TableInfo> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.tags													   --> [] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.temp_directory											   --> C:\Users\8304018\AppData\Local\gom\tmp (<class 'str'>)
	gom :> app.project.parts['Part'].actual.template												   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.template_database_info_draft							   -->
		{"element_defaults":{"creator":"element_properties","default_id":"834f09ce-3daa-4fb6-a11d-309f2eb98523","default_varia
		...snip... 這東西超大超大
		ame":"Inspection","version":"1.0.0"},"sort_index":0,"variants":[]}]},"udips":{"creator":"udip","default_id":"00000000-
		0000-0000-0000-000000000000","default_variant":"","flags":[],"modified":2,"sources":[{"ids":[],"type":"class
		Tom::Package::PackageTemplateSource"}],"templates":[]}} (<class 'str'>)
	gom :> app.project.parts['Part'].actual.template_info_draft										   --> {"element":{"name":"","package_reference":{"name":"Inspection","protected":false,"uuid":"a6769fbc-4bda-4cec-af9a-b189baf8b742","version":"1.0"},"uuid":"834f09ce-3daa-4fb6-a11d-309f2eb98523"},"label":{"name":"Name","package_reference":{"name":"Inspection","protected":false,"uuid":"a6769fbc-4bda-4cec-af9a-b189baf8b742","version":"1.0"},"uuid":"4a6ef87a-5214-4089-bdc3-5a96cf8b5108"}} (<class 'str'>)
	gom :> app.project.parts['Part'].actual.template_name											   --> Name (<class 'str'>)
	gom :> app.project.parts['Part'].actual.template_package_draft									   --> {'is_protected': False, 'name': 'Inspection', 'uuid': 'a6769fbc-4bda-4cec-af9a-b189baf8b742', 'version': '1.0'} (<class 'dict'>)
	gom :> app.project.parts['Part'].actual.template_uuid											   --> 4a6ef87a-5214-4089-bdc3-5a96cf8b5108 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_extrema_level										   --> 150.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.tol_neg_extrema_color									   --> #ff0000 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_neg_extrema_text									   --> Ext (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_neg_fail_color										   --> #ff0000 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_neg_fail_text										   --> Fail (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_neg_pass_color										   --> #00ff00 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_neg_pass_text										   --> Pass (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_neg_warn_color										   --> #e0e038 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_neg_warn_text										   --> Warn (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_novalue_color										   --> #000000 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_novalue_text										   --> No value (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_pos_extrema_color									   --> #ff0000 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_pos_extrema_text									   --> Ext (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_pos_fail_color										   --> #ff0000 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_pos_fail_text										   --> Fail (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_pos_pass_color										   --> #00ff00 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_pos_pass_text										   --> Pass (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_pos_warn_color										   --> #e0e038 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_pos_warn_text										   --> Warn (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_unused_color										   --> #425c77 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_unused_text											   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.tol_warning_level										   --> 75.0 (<class 'float'>)
	gom :> app.project.parts['Part'].actual.transformation_category									   --> actual (<class 'gomlib.types.TransformationCategory'>)
	gom :> app.project.parts['Part'].actual.type													   --> mesh (<class 'gomlib.types.ObjectType'>)

	gom :> app.project.parts['Part'].actual.type --> mesh (<class 'gomlib.types.ObjectType'>)
	gom :> app.project.parts['Part'].nominal.type --> cad (<class 'gomlib.types.ObjectType'>)

	gom :> app.project.parts['Part'].actual.undo_is_history_complete								   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.undo_num_redo_steps										   --> 0 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.undo_num_undo_steps										   --> 4 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.unit_acceleration										   --> mm/s² (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_angle												   --> ° (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_angle_acceleration									   --> °/s² (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_angle_velocity										   --> °/s (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_area												   --> mm² (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_count												   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_curvature											   --> / mm (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_density											   --> t/mm³ (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_exposure_time										   --> ms (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_force												   --> N (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_length												   --> mm (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_mass												   --> kg (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_no_unit											   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_no_unit_acceleration								   --> 1/s² (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_no_unit_velocity									   --> 1/s (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_power												   --> W (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_rate												   --> Hz (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_report												   --> mm (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_statistics_cp										   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_strain												   --> % (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_strain_acceleration								   --> %/s² (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_strain_rate										   --> %/s (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_temperature										   --> °C (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_time												   --> s (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_true_strain										   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_true_strain_acceleration							   --> 1/s² (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_true_strain_rate									   --> 1/s (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_velocity											   --> mm/s (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_voltage											   --> V (<class 'str'>)
	gom :> app.project.parts['Part'].actual.unit_volume												   --> mm³ (<class 'str'>)
	gom :> app.project.parts['Part'].actual.use_reference_point_size								   --> True (<class 'bool'>)
	gom :> app.project.parts['Part'].actual.use_user_defined_reference_point_size					   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.used_gdat_tolerances									   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.used_general_tolerances									   -->	(<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_charge_nr											   --> -/- (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_company											   --> GOM a Zeiss Company (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_date												   --> 2020/06/11 (<class 'gomlib.types.Date'>)
	gom :> app.project.parts['Part'].actual.user_defined_reference_point_color						   --> white (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_defined_reference_point_size						   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.user_defined_reference_point_thickness					   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.user_defined_reference_point_type						   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.user_department											   --> 3D Metrology (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_inspector											   --> GOM Employee (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_local_directory									   --> C:\Users\8304018\AppData\Local\gom\2020 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_location											   --> Braunschweig (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_package_directory									   --> C:\Users\8304018\AppData\Roaming\gom\2020\gom_packages (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_part												   --> GOM Training Object (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_part_nr											   --> 12345 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_project											   --> Demonstration Data (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_roaming_directory									   --> C:\Users\8304018\AppData\Roaming\gom\2020 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_system												   --> ATOS (<class 'str'>)
	gom :> app.project.parts['Part'].actual.user_version											   --> 2020 (<class 'str'>)
	gom :> app.project.parts['Part'].actual.vdi_base_name											   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.view_csys												   --> gom.app.project.nominal_elements['system_global_coordinate_system'] (<class 'gom.Item'>)
	gom :> app.project.parts['Part'].actual.viewport_height											   --> 460 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.viewport_width											   --> 849 (<class 'int'>)
	gom :> app.project.parts['Part'].actual.views													   --> <Trait: Tom::GRTProxy::Cameras> (<class 'gom.Object'>)
	gom :> app.project.parts['Part'].actual.visible_views											   --> ['3d_toolbar', '3d_view', 'atos2_glcanvas', 'explorer', 'left_docking_area', 'project_status_embedded', 'related'] (<class 'list'>)
	gom :> app.project.parts['Part'].actual.vmr_project_building_block_draft						   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.volume													   --> None (<class 'NoneType'>)
	gom :> app.project.parts['Part'].actual.workspace												   --> inspection (<class 'str'>)
*[X] 10:34 2020/09/24 usage : import peforth, peforth_gom_port
	so peforth_gom_port.py must be at the working directory
	[x] 19:22 2020/09/24 兩邊用 hard link 同步起來
			vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv user-defined-scripts (opposed to System scripts)
			C:\Users\8304018\AppData\Roaming\gom\2020\gom_scripts>mklink /H c:\Users\8304018\Documents\GitHub\gomforth\peforth_gom_port.py PEFORT~1.PY
			Hardlink created for c:\Users\8304018\Documents\GitHub\gomforth\peforth_gom_port.py <<===>> PEFORT~1.PY
		這樣 GitHub/gomforth 就可以管理好 peforth_gom_port.py 的版本控制了。
[ ] 10:35 2020/09/24 strange! ok() 裡 execute() 不行，改成 dictate() 才可以
    path c:\Users\8304018\AppData\Roaming\gom\2020\python\peforth\__init__.py
	while True:
		i += 1
		if cmd == "":
			if vm.tick('accept') and not vm.multiple:
				vm.dictate('accept')  # [ ] 怎麼會傳回 None 待解 <-- 根本沒有跑到 accept!!! 由 execute 改用 dictate 就好了，待解。
				cmd = vm.pop().strip()
			elif vm.tick('<accept>') and vm.multiple:
	--> 就先用 dictate 了，待將來水落石出。
[X] 10:55 2020/09/24 Gom 裡所有的 input 都不能用，所以 input() function 有必要改成可以抽換。
	vm.panic 裡面 input() 用最多，2nd argument 都用 False 避開了。
[X] 22:07 2020/10/03 gomforth 需要 repeat command line 否則只看到 outputs 看不出是幹嘛的。
	--> 22:20 2020/10/03 shit! c:\Users\8304018\Documents\GitHub\gomforth\peforth_gom_port.py already done this by the 'accept'
		command. 要訣：出現在 ok 之後的就是 command line input
[ ] 22:30 2020/10/03 複習 python 的 object 與 dict 不同，而 JavaScript 兩者是一樣的。分析兩著的不同，如何查看兩者：

	(see) keys dict>keys obj.__doc__ .members
	obj <py> [ i for i in pop()] </pyV> -->
[X] 14:56 2020/10/08 input box to show prompt
		DIALOG=gom.script.sys.create_user_defined_dialog (content='<dialog>' \
		' <title>g o m f o r t h  command line</title>' \
		' <style></style>' \
		' <control id="OkCancel"/>' \
		' <position>automatic</position>' \
		' <embedding>always_toplevel</embedding>' \
		' <sizemode>automatic</sizemode>' \
		' <size width="304" height="119"/>' \
		' <content rows="1" columns="2">' \
	--> '  <widget row="0" type="input::string" column="0" columnspan="1" rowspan="1">' \
	--> '	<name>prompt</name>' \
	--> '	<tooltip></tooltip>' \
	--> '	<value></value>' \
	--> '	<read_only>false</read_only>' \
	--> '  </widget>' \
		'  <widget row="0" type="input::string" column="1" columnspan="1" rowspan="1">' \
		'	<name>input</name>' \
		'	<tooltip></tooltip>' \
		'	<value></value>' \
		'	<read_only>false</read_only>' \
		'  </widget>' \
		' </content>' \
		'</dialog>')
[X] 15:32 2020/10/08 import gom <--- can be done on jupyternotebook. But an error happened later:
		C:\Program Files\GOM\2020\lib\python\gom_script_server\gomlib\network.py in request(command, params)
			287
			288					if not Connection.is_configured ():
		--> 289							raise RuntimeError ('Connection parameters (host/port) are not configured')
			290
			291					if not isinstance (command, Connection.Request):
		RuntimeError: Connection parameters (host/port) are not configured
	--> ask Gom or search the net for how to make the connection
[X] 14:39 2020/10/15 Code pattern : 掃描全部 CAD models 的 patchs 找出所有 color 的集合
	\ Code pattern : 掃描全部 CAD models 的 patchs 找出所有 color 的集合
	\ subst w: .
	\ include w:/1
	gom <py>
	colors = set()	# A 集合 of patch colors
	cads = list()  # list of all CAD models
	count = len(colors)
	for file in pop().app.project.parts['Part'].nominal.file:	# all files
		for body in file:										# all bodies in each file
			for cad in body:									# all CAD files in each body
				patchs = cad.patch	# get patchs of the CAD file
				for patch in patchs: colors.add(patch.color)
				if len(colors) > count : print(colors, end=" ")
				print(cad.name)		# print model names, which is filename of the model
				cads.append(cad)	# the cad object
				count = len(colors)
	push((cads,colors,count))
	</py> ( cads,colors,count ) value result result :> [2] ( count of colors found ) -->
	stop
[X] 06:23 2020/10/18 Code pattern : 自動開檔
	\ Code pattern : 自動開檔
	# Reload the working project file
	peforth.dictate('''
		s' D:\\OneDrive\\OneDrive - Wistron Corporation\\Gom\\Work\\20201005\\Case2\\Case2_eng_v2.ginspect' constant filename
		gom <py> getattr(pop().app,'project',False) </pyV> [if]
			filename gom :> app.project.project_file = [if] [else]
				gom :: script.sys.close_project()
				filename gom :: script.sys.load_project(file=pop(1))
			[then]
		[else]
			filename gom :: script.sys.load_project(file=pop(1))
		[then]
		''')
	peforth.ok()
[X] 13:24 2020/10/22 忘了為何要改成 gomforth? 直接用 peforth 不行嗎？ --> 不行，期待 v1.25 修正一些地方才行。
	16:44 2020/10/23 remove gom python peforth

	sys --> <module 'sys' (built-in)> (<class 'module'>)
	py> sys :> executable --> C:\Program Files\GOM\2020\python\python.exe (<class 'str'>)
	16:52 2020/10/23 so cd to C:\Program Files\GOM\2020\python

	17:18 2020/10/23 setup path like this is correct I believe,
		path=%path%;c:\Program Files\GOM\2020\python;c:\Program Files\GOM\2020\python\Scripts;
	17:20 2020/10/23 but "c:\Program Files\GOM\2020\python\Scripts\pip.exe" 跑不起來，GOM 有保護。
		C:\Program Files\GOM\2020\python\Scripts>pip
		Fatal error in launcher: Unable to create process using '"e:\tom\3rd\pythonng-3.7.3_gom1\windows-vc-14.0-64\python.exe"	 "C:\Program Files\GOM\2020\python\Scripts\pip.exe" '

		C:\Program Files\GOM\2020\python\Scripts>pip3.7 list
		Fatal error in launcher: Unable to create process using '"e:\tom\3rd\pythonng-3.7.3_gom1\windows-vc-14.0-64\python.exe"	 "C:\Program Files\GOM\2020\python\Scripts\pip3.7.exe" list'

		C:\Program Files\GOM\2020\python\Scripts>pip3.exe
		Fatal error in launcher: Unable to create process using '"e:\tom\3rd\pythonng-3.7.3_gom1\windows-vc-14.0-64\python.exe"	 "C:\Program Files\GOM\2020\python\Scripts\pip3.exe" '

	[X] 17:26 2020/10/23 所以要 remove peforth 只好手動 remove these two folders:
		c:\Users\8304018\AppData\Roaming\gom\2020\python\peforth-1.24.dist-info
		c:\Users\8304018\AppData\Roaming\gom\2020\python\peforth
		--> done
	[X] 17:26 2020/10/23 pip install through GOM's standard way :
		Scripting > script choice > tools > install python package >
			package list : peforth
			[x] from network
			[x] roaming user directory
		--> the above deleted directory come back instantly! and it's v1.24 correctly.
	[X] 這兩個 .py 要改 projectk.py, __init__.py 所以確定 peforth pypi 版不能直接用，將來改版到 v1.25
		要修正這個問題。
		--> v1.25 上了 Pypi and 測過成功了。
[X] 13:41 2020/10/29 multiple shell ok() needs to save-restore the prompt or the later will overwrite it and
	after the return to parent ok() the prompt will be incorrect.
	--> fixed in peforth > __init__.py > ok()
[X] 12:50 2020/11/05 if __name__ == '__main__': makes peforth_gom_port.py can run stand alone.
[X] 13:18 2020/11/05 改寫 word for gom to wrap long line
	code words # ( <pattern> -- ) List all words, in the active vocabularies, with the pattern in their name. Modified for Gom.
		pattern = nexttoken('\\n|\\r').strip() # avoid selftest to read TIB too much
		if pattern:        # ^^^^^^^ 這個地方 debug 好久, 放進 peforth.gom.port.py 是在 python string 裡面，要改成 doulbe backslash
			screened = [w.name for w in words['forth'][1:] if w.name.find(pattern)!=-1]
		else:
			screened = [w.name for w in words['forth'][1:]]
		j = 0
		for i in screened:
			print(i, end=" ")
			j += 1
			if j % 10 == 0 : print()
		print()
		end-code
		/// Examples of listing screened words:
		/// 1.List all code words
		///	  <py> [w.name for w in words['forth'][1:] if 'code' in w.type] </pyV>
		/// 2.List all words that have not passed their own selftest
		///	  <py> [w.name for w in words['forth'][1:] if 'pass'!=getattr(w,'selftest',False)] </pyV>
		/// 3.List all words that have 'Cast' in their name, help, or comment
		///	  <py> eval("[w.name for w in words['forth'][1:] if (w.name.find('{{0}}')!=-1 or w.help.find('{{0}}')!=-1 or w.comment.find('{{0}}')!=-1)]".format('Cast'))</pyV>
[X] 14:33 2020/11/11 屋簷下選不到可能是範圍太小？--> Nope, see BB1247#12
    Video "c:\Users\8304018\Downloads\gom python case2 deselection leftings.mp4" 
    # -*- coding: utf-8 -*-

    import gom
    gom.script.selection3d.select_inside_cube (
        center={'point': gom.Vec3d (140.0, 4.0, 20.0)}, 
        csys=gom.app.project.nominal_elements['system_global_coordinate_system'], 
        height=50.0, 
        length=70.0, 
        width=10.0)
        
    print(gom.script.selection3d.deselect_in_viewing_direction.__doc__)

    # 10/27:注意要照選點的順序
    gom.script.selection3d.deselect_in_viewing_direction (
        coordinates=[gom.Vec3d (105.0, 10.0, -5.0), 
                    gom.Vec3d (105.0, 10.0, 45.0), 
                    gom.Vec3d (175.0, 10.0, 45.0),
                    gom.Vec3d (175.0, 10.0, -5.0), ], 
        target=gom.app.project.parts['Part'].actual, 
        view_direction=gom.Vec3d (0.0, 1.0, 0.0))
[X] 18:08 2020/11/10 get-view 用 gom.app.project.parts['Part'].actual.views 不如 gom.app.get('views.active') 
	: get-view // ( -- view ) Get recent view, an object with 'up direction', 'view direction', 'position' and 'scale'.
		py> gom :> app.project.parts['Part'].actual.views.active ;
        \ Bros found the better method
        \ scale = gom.app.get('views.active.scale')
        \ up = [gom.app.get('views.active.up_direction.' + i ) for i in ( 'x', 'y', 'z' )]
        \ view = [gom.app.get( 'views.active.view_direction.' + i ) for i in ( 'x', 'y', 'z' )]
        \ gom :> app.get('views.active.up_direction') --> gom.Vec3d (0.032334163784980774, -0.14412397146224976, 0.989031195640564) (<class 'gom.Vec3d'>)
        \ gom :> app.get('views.active') (see) 

    <py> gom.app.get ('software_directory')</pyV> --> C:\Program Files\GOM\2020 (<class 'str'>)
    <py> gom.app.get ('application_name')</pyV> --> GOM Inspect Suite (<class 'str'>)
    <py> gom.app.get ('application_version')</pyV> --> 2020-1 (<class 'str'>)
    <py> gom.app.get ('language')</pyV> --> en (<class 'str'>)
    <py> gom.app.get ("undo_is_history_complete")</pyV> --> True (<class 'bool'>)
    <py> gom.app.get ("undo_num_undo_steps")</pyV> --> 6 (<class 'int'>)
    py> gom.app.get('user_roaming_directory') --> C:\Users\8304018\AppData\Roaming\gom\2020 (<class 'str'>)

    py> gom.app.get('views') --> <Trait: Tom::GRTProxy::Cameras> (<class 'gom.Object'>)
    {
        "__class__": "Object",
        "__module__": "gom",
        "__object_type__": "Tom::GRTProxy::Cameras",
        "__object_repr__": "<Trait: Tom::GRTProxy::Cameras>",
        "active": {
            "__class__": "Object",
            "__module__": "gom",
            "__object_type__": "Tom::GRTProxy::GLSingleCamera",
            "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
            "position": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 10.464004516601562,
                "y": -279.3534240722656,
                "z": 76.06610870361328
            },
            "view_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 0.0,
                "y": -1.0,
                "z": 0.0
            },
            "up_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 0.0,
                "y": 0.0,
                "z": 1.0
            },
            "scale": 126.4019546508789
        },
        "main": {
            "__class__": "Object",
            "__module__": "gom",
            "__object_type__": "Tom::GRTProxy::GLSingleCamera",
            "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
            "position": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 10.464004516601562,
                "y": -279.3534240722656,
                "z": 76.06610870361328
            },
            "view_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 0.0,
                "y": -1.0,
                "z": 0.0
            },
            "up_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 0.0,
                "y": 0.0,
                "z": 1.0
            },
            "scale": 132.34768676757812
        },
        "pip": {
            "__class__": "Object",
            "__module__": "gom",
            "__object_type__": "Tom::GRTProxy::GLSingleCamera",
            "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
            "position": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            "view_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 1.0,
                "y": 0.0,
                "z": 0.0
            },
            "up_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 0.0,
                "y": 1.0,
                "z": 0.0
            },
            "scale": 1.0
        },
        "section": {
            "__class__": "Object",
            "__module__": "gom",
            "__object_type__": "Tom::GRTProxy::GLSingleCamera",
            "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
            "position": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            "view_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 1.0,
                "y": 0.0,
                "z": 0.0
            },
            "up_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "x": 0.0,
                "y": 1.0,
                "z": 0.0
            },
            "scale": 1.0
        },
        "active_frustum": {
            "__class__": "Object",
            "__module__": "gom",
            "__object_type__": "Tom::GRTProxy::Frustum",
            "__object_repr__": "<Trait: Tom::GRTProxy::Frustum>",
            "top_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 0.0,
                    "y": 0.0,
                    "z": 1.0
                },
                "distance_to_origin": -202.4680633544922
            },
            "bottom_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": -0.0,
                    "y": -0.0,
                    "z": -1.0
                },
                "distance_to_origin": -50.335845947265625
            },
            "left_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": -1.0,
                    "y": -0.0,
                    "z": 0.0
                },
                "distance_to_origin": -190.81021118164062
            },
            "right_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 1.0,
                    "y": 0.0,
                    "z": -0.0
                },
                "distance_to_origin": -211.73822021484375
            },
            "front_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 0.0,
                    "y": -1.0,
                    "z": 0.0
                },
                "distance_to_origin": -14.83843994140625
            },
            "back_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": -0.0,
                    "y": 1.0,
                    "z": -0.0
                },
                "distance_to_origin": 1.7286376953125
            }
        },
        "main_frustum": {
            "__class__": "Object",
            "__module__": "gom",
            "__object_type__": "Tom::GRTProxy::Frustum",
            "__object_repr__": "<Trait: Tom::GRTProxy::Frustum>",
            "top_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 0.0,
                    "y": 0.0,
                    "z": 1.0
                },
                "distance_to_origin": -214.35953521728516
            },
            "bottom_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": -0.0,
                    "y": -0.0,
                    "z": -1.0
                },
                "distance_to_origin": -50.335845947265625
            },
            "left_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": -1.0,
                    "y": -0.0,
                    "z": 0.0
                },
                "distance_to_origin": -190.81021118164062
            },
            "right_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 1.0,
                    "y": 0.0,
                    "z": -0.0
                },
                "distance_to_origin": -211.73822021484375
            },
            "front_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 0.0,
                    "y": -1.0,
                    "z": 0.0
                },
                "distance_to_origin": -14.83843994140625
            },
            "back_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": -0.0,
                    "y": 1.0,
                    "z": -0.0
                },
                "distance_to_origin": 1.7286376953125
            }
        },
        "pip_frustum": {
            "__class__": "Object",
            "__module__": "gom",
            "__object_type__": "Tom::GRTProxy::Frustum",
            "__object_repr__": "<Trait: Tom::GRTProxy::Frustum>",
            "top_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 0.0,
                    "y": 0.0,
                    "z": 1.0096579590313e-311
                },
                "distance_to_origin": 1.010069996499e-311
            },
            "bottom_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 1.0096579590313e-311,
                    "y": 1.0096579590313e-311,
                    "z": 1.0
                },
                "distance_to_origin": 0.0
            },
            "left_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 0.0,
                    "y": 1.0,
                    "z": 0.0
                },
                "distance_to_origin": 0.0
            },
            "right_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 0.0,
                    "y": 0.0,
                    "z": 1.0
                },
                "distance_to_origin": 0.0
            },
            "front_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 0.0,
                    "y": 0.0,
                    "z": 4.49808684089e-312
                },
                "distance_to_origin": 1.0096553774474e-311
            },
            "back_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 1e-12,
                    "y": 0.0,
                    "z": 0.0
                },
                "distance_to_origin": 0.0
            }
        },
        "section_frustum": {
            "__class__": "Object",
            "__module__": "gom",
            "__object_type__": "Tom::GRTProxy::Frustum",
            "__object_repr__": "<Trait: Tom::GRTProxy::Frustum>",
            "top_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 1.0109968444497e-311,
                    "y": 6.9527688404581e-310,
                    "z": 5e-324
                },
                "distance_to_origin": 1.009628330966e-311
            },
            "bottom_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 1.0093087088325e-311,
                    "y": 0.0,
                    "z": 5.517189089e-313
                },
                "distance_to_origin": 6.9527688542879e-310
            },
            "left_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 1.009628330966e-311,
                    "y": 6.9527688432061e-310,
                    "z": 1.009628330966e-311
                },
                "distance_to_origin": 1.009628330966e-311
            },
            "right_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 2.69656717432753e-310,
                    "y": 6.9527688279023e-310,
                    "z": 1.0
                },
                "distance_to_origin": 0.0
            },
            "front_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 0.0,
                    "y": 0.0,
                    "z": 1e-12
                },
                "distance_to_origin": 0.0
            },
            "back_plane": {
                "__class__": "Object",
                "__module__": "gom",
                "__object_type__": "Tom::GRTProxy::FrustumPlane",
                "__object_repr__": "<Trait: Tom::GRTProxy::FrustumPlane>",
                "normal": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "x": 5.517189089e-313,
                    "y": 1.544812936608e-311,
                    "z": 5e-324
                },
                "distance_to_origin": 1.0093087088325e-311
            }
        }
    }

    py> gom.app.get('views.active.scale') --> 126.4019546508789 (<class 'float'>)
    py> gom.app.get('views.active.up_direction') --> gom.Vec3d (0.0, 0.0, 1.0) (<class 'gom.Vec3d'>)
    py> gom.app.get('views.active.up_direction.x') --> 0.0 (<class 'float'>)
    py> gom.app.get('project_template_directory') --> C:\Users\8304018\Documents\GOM\Templates\2020\gom_project_templates (<class 'str'>)
    py> gom.app.get('home_directory') --> C:\Users\8304018\Documents (<class 'str'>)
    py> gom.app.get('temp_directory') --> C:\Users\8304018\AppData\Local\gom\tmp (<class 'str'>)

    py> gom.app.get('skin') (see)
    {
        "__class__": "Object",
        "__module__": "gom",
        "__doc__":
        "__object_type__": "Tom::MPRJ::SkinInfo",
        "__object_repr__": "<Trait: Tom::MPRJ::SkinInfo>",
        "config_level": "system",
        "name": ""
    }

    偉大的 Bryan!!! again, you released me out of the darkness . . . .
    <py> gom.app.get('memory_information') </pyV> --> <Trait: gom.MemoryInfo> (<class 'gom.Object'>) 
    Gotcha!!!        
    [‎2020/‎11/‎11 14:45]  Bryan Chen/WHQ/Wistron:  
    gom.app.get應該是python的語法吧
    A.get 並非是GOM提供的函式
    [‎2020/‎11/‎11 14:58]  
    gom.app 有一大堆東西, 超大一堆
    用  gom.app.get_tokens()   列出來，很多。
    上面例子是讀到了其中之一，證明你對 get method 的猜測
    他不需要出手冊，因為可以直接查！
    py> gom.app.get_tokens() --> [
        gom.TokenInfo ('application_build_information', 'Application build information', 'user', 'application'), 
        gom.TokenInfo ('current_date', 'Current date', 'string', 'application'), 
        gom.TokenInfo ('current_user', 'Current user', 'string', 'application'), 
        gom.TokenInfo ('package_information', 'Package information', 'user', 'cat_internal'), 
        gom.TokenInfo ('application_name', 'Application name', 'string', 'application'), 
        gom.TokenInfo ('application_version', 'Application version', 'string', 'cat_internal'), 
        gom.TokenInfo ('language', 'Software language', 'string', 'application'), 
        gom.TokenInfo ('kiosk_mode', 'Kiosk mode', 'bool', 'application'), 
        gom.TokenInfo ('unit_length', 'Length unit', 'string', 'units'), 
        gom.TokenInfo ('unit_time', 'Time unit', 'string', 'units'), 
        gom.TokenInfo ('unit_temperature', 'Temperature unit', 'string', 'units'), 
        gom.TokenInfo ('unit_report', 'Report unit', 'string', 'units'), 
        gom.TokenInfo ('unit_exposure_time', 'Exposure time unit', 'string', 'units'), 
        gom.TokenInfo ('unit_area', 'Area unit', 'string', 'units'), 
        gom.TokenInfo ('unit_angle', 'Angle unit', 'string', 'units'), 
        gom.TokenInfo ('unit_strain', 'Technical/Green\'s strain unit', 'string', 'units'), 
        gom.TokenInfo ('unit_true_strain', 'True strain unit', 'string', 'units'), 
        gom.TokenInfo ('unit_volume', 'Volume unit', 'string', 'units'), 
        gom.TokenInfo ('unit_density', 'Density', 'string', 'units'), 
        gom.TokenInfo ('unit_mass', 'Mass', 'string', 'units'), 
        gom.TokenInfo ('unit_curvature', 'Curvature', 'string', 'units'), 
        gom.TokenInfo ('unit_velocity', 'Velocity unit', 'string', 'units'), 
        gom.TokenInfo ('unit_acceleration', 'Acceleration unit', 'string', 'units'), 
        gom.TokenInfo ('unit_angle_velocity', 'Angular velocity unit', 'string', 'units'), 
        gom.TokenInfo ('unit_angle_acceleration', 'Angular acceleration unit', 'string', 'units'), 
        gom.TokenInfo ('unit_strain_rate', 'Technical/Green\'s strain rate unit', 'string', 'units'), 
        gom.TokenInfo ('unit_true_strain_rate', 'True strain rate unit', 'string', 'units'), 
        gom.TokenInfo ('unit_strain_acceleration', 'Technical/Green\'s strain acceleration unit', 'string', 'units'), 
        gom.TokenInfo ('unit_true_strain_acceleration', 'True strain acceleration unit', 'string', 'units'), 
        gom.TokenInfo ('unit_force', 'Force', 'string', 'units'), 
        gom.TokenInfo ('unit_statistics_cp', 'Statistic values cp, pp, cpk, ppk', 'string', 'units'), 
        gom.TokenInfo ('unit_rate', 'Frame rate', 'string', 'units'), 
        gom.TokenInfo ('unit_voltage', 'Voltage', 'string', 'units'), 
        gom.TokenInfo ('unit_power', 'Power', 'string', 'units'), 
        gom.TokenInfo ('unit_count', 'Amount', 'string', 'units'), 
        gom.TokenInfo ('unit_no_unit', 'Values without unit', 'string', 'units'), 
        gom.TokenInfo ('unit_no_unit_velocity', '1st derivative of values without unit', 'string', 'units'), 
        gom.TokenInfo ('unit_no_unit_acceleration', '2nd derivative of values without unit', 'string', 'units'), 
        gom.TokenInfo ('tol_pos_pass_text', 'Text for \'Pos. pass\'', 'string', 'application'), 
        gom.TokenInfo ('tol_pos_warn_text', 'Text for \'Pos. warn\'', 'string', 'application'), 
        gom.TokenInfo ('tol_pos_fail_text', 'Text for \'Pos. fail\'', 'string', 'application'), 
        gom.TokenInfo ('tol_pos_extrema_text', 'Text for \'Pos. extrema\'', 'string', 'application'), 
        gom.TokenInfo ('tol_unused_text', 'Text for \'Unused values\'', 'string', 'application'), 
        gom.TokenInfo ('tol_novalue_text', 'Text for \'Missing values\'', 'string', 'application'), 
        gom.TokenInfo ('tol_neg_pass_text', 'Text for \'Neg. pass\'', 'string', 'application'), 
        gom.TokenInfo ('tol_neg_warn_text', 'Text for \'Neg. warn\'', 'string', 'application'), 
        gom.TokenInfo ('tol_neg_fail_text', 'Text for \'Neg. fail\'', 'string', 'application'), 
        gom.TokenInfo ('tol_neg_extrema_text', 'Text for \'Neg. extrema\'', 'string', 'application'), 
        gom.TokenInfo ('tol_pos_pass_color', 'Color for \'Pos. pass\'', 'string', 'application'), 
        gom.TokenInfo ('tol_pos_warn_color', 'Color for \'Pos. warn\'', 'string', 'application'), 
        gom.TokenInfo ('tol_pos_fail_color', 'Color for \'Pos. fail\'', 'string', 'application'), 
        gom.TokenInfo ('tol_pos_extrema_color', 'Color for \'Pos. extrema\'', 'string', 'application'), 
        gom.TokenInfo ('tol_unused_color', 'Color for \'Unused values\'', 'string', 'application'), 
        gom.TokenInfo ('tol_novalue_color', 'Color for \'Missing values\'', 'string', 'application'), 
        gom.TokenInfo ('tol_neg_pass_color', 'Color for \'Neg. pass\'', 'string', 'application'), 
        gom.TokenInfo ('tol_neg_warn_color', 'Color for \'Neg. warn\'', 'string', 'application'), 
        gom.TokenInfo ('tol_neg_fail_color', 'Color for \'Neg. fail\'', 'string', 'application'), 
        gom.TokenInfo ('tol_neg_extrema_color', 'Color for \'Neg. extrema\'', 'string', 'application'), 
        gom.TokenInfo ('tol_warning_level', 'Warning level', 'double', 'application'), 
        gom.TokenInfo ('tol_extrema_level', 'Extrema level', 'double', 'application'), 
        gom.TokenInfo ('undo_num_undo_steps', 'undo num undo steps', 'double', 'cat_internal'), 
        gom.TokenInfo ('undo_num_redo_steps', 'undo num redo steps', 'double', 'cat_internal'), 
        gom.TokenInfo ('undo_is_history_complete', 'undo is history complete', 'bool', 'cat_internal'), 
        gom.TokenInfo ('render_gpu_type', 'render gpu type', 'string', 'cat_internal'), 
        gom.TokenInfo ('render_driver_version', 'render driver version', 'string', 'cat_internal'), 
        gom.TokenInfo ('render_use_gpu_memory', 'render use gpu memory', 'bool', 'cat_internal'), 
        gom.TokenInfo ('render_use_transparency', 'render use transparency', 'bool', 'cat_internal'), 
        gom.TokenInfo ('rendered_frames', 'rendered frames', 'double', 'cat_internal'), 
        gom.TokenInfo ('rendered_scene_layer_frames', 'rendered scene layer frames', 'double', 'cat_internal'), 
        gom.TokenInfo ('rendered_temp_layer_frames', 'rendered temp layer frames', 'double', 'cat_internal'), 
        gom.TokenInfo ('rendered_overlay_3d_frames', 'rendered overlay 3d frames', 'double', 'cat_internal'), 
        gom.TokenInfo ('rendered_overlay_2d_frames', 'rendered overlay 2d frames', 'double', 'cat_internal'), 
        gom.TokenInfo ('render_scene_graph_update_time', 'render_scene_graph_update_time', 'double', 'cat_internal'), 
        gom.TokenInfo ('render_complete_draw_time', 'render complete draw time', 'double', 'cat_internal'), 
        gom.TokenInfo ('viewport_width', 'viewport width', 'double', 'cat_internal'), 
        gom.TokenInfo ('viewport_height', 'viewport height', 'double', 'cat_internal'), 
        gom.TokenInfo ('active_width', 'active width', 'double', 'cat_internal'), 
        gom.TokenInfo ('active_height', 'active height', 'double', 'cat_internal'), 
        gom.TokenInfo ('currently_used_gpu_memory', 'currently used gpu memory kb', 'double', 'cat_internal'), 
        gom.TokenInfo ('visible_views', 'currently visible views', 'user', 'cat_internal'), 
        gom.TokenInfo ('views', 'Views', 'user', 'application'), 
        gom.TokenInfo ('home_directory', 'Home directory', 'string', 'application'), 
        gom.TokenInfo ('user_roaming_directory', 'roaming user config directory', 'string', 'cat_internal'), 
        gom.TokenInfo ('user_local_directory', 'local user config directory', 'string', 'cat_internal'), 
        gom.TokenInfo ('local_all_directory', 'local config directory for all users', 'string', 'cat_internal'), 
        gom.TokenInfo ('project_template_directory', 'Project template directory', 'string', 'application'), 
        gom.TokenInfo ('public_directory', 'Public directory', 'string', 'application'), 
        gom.TokenInfo ('temp_directory', 'Temporary directory', 'string', 'application'), 
        gom.TokenInfo ('software_directory', 'Software directory', 'string', 'application'), 
        gom.TokenInfo ('default_directory', 'Default directory', 'string', 'application'), 
        gom.TokenInfo ('python_directory', 'Python directory', 'string', 'application'), 
        gom.TokenInfo ('user_package_directory', 'Package directory (user)', 'string', 'application'), 
        gom.TokenInfo ('public_package_directory', 'Package directory (public)', 'string', 'application'), 
        gom.TokenInfo ('system_package_directory', 'Package directory (system)', 'string', 'application'), 
        gom.TokenInfo ('number_of_date_formats', 'Number of date formats', 'double', 'application'), 
        gom.TokenInfo ('date_format', 'Date format', 'user', 'application', indexed=True), 
        gom.TokenInfo ('memory_information', 'Memory information', 'user', 'application'), 
        gom.TokenInfo ('workspace', 'Active workspace', 'string', 'application'), 
        gom.TokenInfo ('legend', 'Legend', 'user', 'application'), 
        gom.TokenInfo ('table', 'Table', 'user', 'application'), 
        gom.TokenInfo ('skin', 'Skin', 'user', 'application'), 
        gom.TokenInfo ('scalar_registry_info', 'scalar registry', 'string', 'cat_internal'), 
        gom.TokenInfo ('template_database_info_draft', 'template database', 'string', 'cat_internal'), 
        gom.TokenInfo ('package_database_info_draft', 'package database', 'string', 'cat_internal'), 
        gom.TokenInfo ('default_templates_info_draft', 'default templates', 'string', 'cat_internal'), 
        gom.TokenInfo ('num_selected_visible_points', 'Number of selected visible points', 'double', 'info'), 
        gom.TokenInfo ('main_view_information_text', '3D view information text', 'string', 'info'), 
        gom.TokenInfo ('drc_computer_communication', 'computer communication for double robot measuring cell', 'user', 'cat_internal'), 
        gom.TokenInfo ('last_movement_aborted_with_estop', 'last movement command was aborted via emergency stop', 'bool', 'cat_internal'), 
        gom.TokenInfo ('measurement_progress_remaining_time', 'remaining time of measurement progress', 'time', 'cat_internal'), 
        gom.TokenInfo ('sys_automation_controller', 'Automation controller', 'user', 'cat_hardware_info'), 
        gom.TokenInfo ('sys_fixed_room_temperature', 'Fixed room temperature', 'string', 'cat_hardware_info'), 
        gom.TokenInfo ('sys_is_sensor_initialized', 'State: Is sensor initialized?', 'bool', 'cat_hardware_info'), 
        gom.TokenInfo ('sys_measurement_temperature_source', 'Measurement temperature source', 'string', 'cat_hardware_info'), 
        gom.TokenInfo ('sys_sensor_configuration', 'Sensor configuration', 'user', 'cat_hardware_info'), 
        gom.TokenInfo ('sys_sensor_identifier', 'Sensor identifier', 'string', 'cat_hardware_info'), 
        gom.TokenInfo ('sys_sensor_internal_statistics', 'Sensor statistics', 'user', 'cat_internal'), 
        gom.TokenInfo ('sys_sensor_light_factor_live', 'Light factor', 'double', 'cat_internal'), 
        gom.TokenInfo ('sys_scan_area_editor_crc', 'checksum of scan area in scan area editor', 'double', 'cat_internal')] (<class 'list'>)
        
    py> gom.app.project.get_tokens() --> [
        gom.TokenInfo ('name', 'Name', 'string', 'info'),
        gom.TokenInfo ('project_statistics', 'Project statistics', 'user', 'statistics'),
        gom.TokenInfo ('alignment', 'Alignment', 'user', 'project_info'),
        gom.TokenInfo ('alignment_for_visualized_report_elements', 'alignment for visualized report elements', 'user', 'cat_internal'),
        gom.TokenInfo ('stage', 'Stage', 'user', 'project_info'),
        gom.TokenInfo ('current_stage_range', 'Current stage range', 'string', 'project_info'),
        gom.TokenInfo ('reference_stage', 'Reference stage', 'user', 'project_info'),
        gom.TokenInfo ('actual_master', 'Actual master', 'string', 'project_info'),
        gom.TokenInfo ('active_actual_mesh', 'Active actual mesh', 'string', 'project_info'),
        gom.TokenInfo ('cad_group', 'CAD group', 'string', 'project_info'),
        gom.TokenInfo ('current_report_page', 'Current report page', 'user', 'project_info'),
        gom.TokenInfo ('automation_move_to_endposition_on_abort', 'State: Move to end position on abort?', 'bool', 'project_info'),
        gom.TokenInfo ('project_file', 'Project file', 'string', 'info'),
        gom.TokenInfo ('project_modification_time', 'Project modification time', 'string', 'info'),
        gom.TokenInfo ('project_creation_time', 'Project creation time', 'string', 'info'),
        gom.TokenInfo ('project_file_size', 'Project file size', 'string', 'info'),
        gom.TokenInfo ('project_name', 'Project name', 'string', 'info'),
        gom.TokenInfo ('project_data_reduction', 'Project data reduction', 'string', 'info'),
        gom.TokenInfo ('project_history', 'GOM: Save Project History', 'string', 'cat_internal'),
        gom.TokenInfo ('scanning_template', 'Scanning template', 'user', 'project_info'),
        gom.TokenInfo ('project_building_block_type_draft', 'Automation module type', 'string', 'project_info'),
        gom.TokenInfo ('project_building_block_uuid_draft', 'Automation module unique identifier', 'string', 'project_info'),
        gom.TokenInfo ('vmr_project_building_block_draft', 'VMR module', 'user', 'project_info'),
        gom.TokenInfo ('photogrametry_project_building_block_draft', 'Photogrammetry module', 'user', 'project_info'),
        gom.TokenInfo ('measuring_task_project_building_block_draft', 'Digitizing and inspection module', 'user', 'project_info'),
        gom.TokenInfo ('is_modified', 'GOM: is_modified', 'bool', 'cat_internal'),
        gom.TokenInfo ('is_modified_after_loading', 'GOM: is_modified_after_loading', 'bool', 'cat_internal'),
        gom.TokenInfo ('template', 'Template information', 'user', 'project_info'),
        gom.TokenInfo ('gom_collision_check_since_load_import_copy_draft', 'GOM: is a collision check computed since the last project load, import or element copy? (used in test scripts only)', 'bool', 'cat_internal'),
        gom.TokenInfo ('used_general_tolerances', 'Used standard "General tolerances" (tolerance table)', 'string', 'project_info'),
        gom.TokenInfo ('used_gdat_tolerances', 'Used standard "GD&T tolerances" (tolerance table)', 'string', 'project_info'),
        gom.TokenInfo ('general_tolerance_table', 'General tolerance table', 'user', 'cat_internal'),
        gom.TokenInfo ('gdat_tolerance_table', 'GD&T tolerance table', 'user', 'cat_internal'),
        gom.TokenInfo ('user_inspector', '检测人', 'string', 'user_defined'),
        gom.TokenInfo ('user_part_nr', '部件编号', 'string', 'user_defined'),
        gom.TokenInfo ('user_date', '日期 ', 'string', 'user_defined'),
        gom.TokenInfo ('user_location', '地点', 'string', 'user_defined'),
        gom.TokenInfo ('user_company', '公司', 'string', 'user_defined'),
        gom.TokenInfo ('user_department', '部门', 'string', 'user_defined'),
        gom.TokenInfo ('user_project', '项目', 'string', 'user_defined'),
        gom.TokenInfo ('user_system', '系统 ', 'string', 'user_defined'),
        gom.TokenInfo ('user_charge_nr', '批号', 'string', 'user_defined'),
        gom.TokenInfo ('user_version', '版本 ', 'string', 'user_defined'),
        gom.TokenInfo ('user_part', '部件', 'string', 'user_defined'),
        gom.TokenInfo ('project_keywords', 'Project keywords (list of project keywords)', 'user', 'project_info'),
        gom.TokenInfo ('recent_reasons', 'recent reasons', 'double', 'cat_internal'),
        gom.TokenInfo ('inspections_not_in_reports', 'Inspection elements (list) - not in reports', 'user', 'project_info'),
        gom.TokenInfo ('is_part_project', 'State: Is this a "part project"?', 'bool', 'info'),
        gom.TokenInfo ('view_csys', 'Viewing coordinate system', 'user', 'project_info'),
        gom.TokenInfo ('is_global_csys_view_csys', 'State: Is global coordinate system used for viewing?', 'bool', 'project_info'),
        gom.TokenInfo ('project_contains_preliminary_data', 'State: Project contains preliminary data?', 'bool', 'cat_internal'),
        gom.TokenInfo ('is_inspection_from_v7sr2', 'is the inspection in this project from the old v7sr2 workflow?', 'bool', 'cat_internal'),
        gom.TokenInfo ('is_auto_recalc_enabled', 'State: Is automatic recalculation for visible elements enabled?', 'bool', 'cat_internal'),
        gom.TokenInfo ('is_auto_recalc_for_stages_enabled', 'State: is automatic recalculation for visible elements in all stages enabled?', 'bool', 'cat_internal'),
        gom.TokenInfo ('reference_point_identification_settings', 'Reference point identification settings for scanning', 'string', 'project_info'),
        gom.TokenInfo ('max_residual_edge_point_adjustment', 'Max. residual edge point adjustment for scanning', 'double', 'project_info'),
        gom.TokenInfo ('max_residual_gray_value_adjustment', 'Max. residual gray value adjustment for scanning', 'double', 'project_info'),
        gom.TokenInfo ('min_ellipse_radius', 'Min. ellipse size for scanning', 'double', 'project_info'),
        gom.TokenInfo ('min_ellipse_contrast_for_scanning', 'Min. ellipse contrast for scanning', 'double', 'project_info'),
        gom.TokenInfo ('reference_point_identification_method', 'Method for reference point identification for scanning', 'string', 'project_info'),
        gom.TokenInfo ('reference_point_identification_settings_for_photogrammetry', 'Reference point identification settings for photogrammetry', 'string', 'project_info'),
        gom.TokenInfo ('max_residual_edge_point_adjustment_for_photogrammetry', 'Max. residual edge point adjustment for photogrammetry', 'double', 'project_info'),
        gom.TokenInfo ('max_residual_gray_value_adjustment_for_photogrammetry', 'Max. residual gray value for photogrammetry', 'double', 'project_info'),
        gom.TokenInfo ('min_ellipse_radius_for_photogrammetry', 'Min. ellipse size for photogrammetry', 'double', 'project_info'),
        gom.TokenInfo ('min_ellipse_contrast_for_photogrammetry', 'Min. ellipse contrast for photogrammetry', 'double', 'project_info'),
        gom.TokenInfo ('reference_point_identification_method_for_photogrammetry', 'Method for reference point identification for photogrammetry', 'string', 'project_info'),
        gom.TokenInfo ('measurement_temperature', 'Measurement temperature', 'temperature', 'project_info'),
        gom.TokenInfo ('first_measurement_date', 'Date of first measurement', 'string', 'project_info'),
        gom.TokenInfo ('first_measurement_time', 'Time of first measurement', 'string', 'project_info'),
        gom.TokenInfo ('last_measurement_date', 'Date of last measurement', 'string', 'project_info'),
        gom.TokenInfo ('last_measurement_time', 'Time of last measurement', 'string', 'project_info'),
        gom.TokenInfo ('use_reference_point_size', 'State: Use reference point size?', 'bool', 'project_info'),
        gom.TokenInfo ('reference_point_type', 'Reference point type', 'string', 'project_info'),
        gom.TokenInfo ('reference_point_size', 'Reference point size', 'length', 'project_info'),
        gom.TokenInfo ('reference_point_thickness', 'Reference point thickness', 'length', 'project_info'),
        gom.TokenInfo ('use_user_defined_reference_point_size', 'State: Use user-defined reference point size?', 'bool', 'project_info', indexed=True),
        gom.TokenInfo ('user_defined_reference_point_type', 'User-defined reference point type', 'string', 'project_info', indexed=True),
        gom.TokenInfo ('user_defined_reference_point_size', 'User-defined reference point size', 'length', 'project_info', indexed=True),
        gom.TokenInfo ('user_defined_reference_point_thickness', 'User-defined reference point thickness', 'length', 'project_info', indexed=True),
        gom.TokenInfo ('user_defined_reference_point_color', 'User-defined reference point color', 'string', 'project_info'),
        gom.TokenInfo ('reference_points_collection_type', 'Type of reference point collection', 'string', 'project_info'),
        gom.TokenInfo ('measurement_transformation_type', 'Measurement transformation type', 'string', 'project_info'),
        gom.TokenInfo ('robogrammetry', 'State: Robogrammetry?', 'bool', 'project_info'),
        gom.TokenInfo ('min_fringe_contrast', 'Min. fringe contrast', 'double', 'project_info'),
        gom.TokenInfo ('check_missing_reference_points', 'State: Check missing reference points?', 'bool', 'project_info'),
        gom.TokenInfo ('check_sensor_movement', 'State: Check "Sensor movement"?', 'bool', 'project_info'),
        gom.TokenInfo ('max_sensor_movement', 'Max. sensor movement', 'double', 'project_info'),
        gom.TokenInfo ('check_lighting_change', 'State: Check "Lighting change"?', 'bool', 'project_info'),
        gom.TokenInfo ('check_transformation', 'State: Check "Transformation"?', 'bool', 'project_info'),
        gom.TokenInfo ('check_decalibrated_sensor', 'State: Check "Decalibrated sensor"?', 'bool', 'project_info'),
        gom.TokenInfo ('check_measurement_temperature', 'State: Check "Measurement temperature"?', 'bool', 'project_info'),
        gom.TokenInfo ('allowed_temperature_difference', 'Allowed temperature difference', 'double', 'project_info'),
        gom.TokenInfo ('depth_limitation_mode', 'Depth limitation mode', 'string', 'project_info'),
        gom.TokenInfo ('min_scan_surface_depth_limitation', 'Min. depth limitation scan surface', 'length', 'project_info'),
        gom.TokenInfo ('max_scan_surface_depth_limitation', 'Max. depth limitation scan surface', 'length', 'project_info'),
        gom.TokenInfo ('min_reference_points_depth_limitation', 'Min. depth limitation reference points', 'length', 'project_info'),
        gom.TokenInfo ('max_reference_points_depth_limitation', 'Max. depth limitation reference points', 'length', 'project_info'),
        gom.TokenInfo ('avoid_points_at_strong_brightness_differences', 'State: Avoid points at strong brightness differences?', 'bool', 'project_info'),
        gom.TokenInfo ('avoid_triple_scan_points_at_strong_brightness_differences', 'State: Avoid Triple Scan points at strong brightness differences?', 'bool', 'project_info'),
        gom.TokenInfo ('avoid_points_on_shiny_surfaces', 'State: Avoid points on shiny surfaces?', 'bool', 'project_info'),
        gom.TokenInfo ('avoid_points_on_borders_in_scan_area', 'State: Avoid points on borders in scan area?', 'bool', 'project_info'),
        gom.TokenInfo ('avoid_triple_scan_points', 'State: Avoid Triple Scan points?', 'string', 'project_info'),
        gom.TokenInfo ('max_residual', 'Max. residual', 'double', 'project_info'),
        gom.TokenInfo ('avoid_points_in_shadow_areas', 'State: Avoid points in shadow areas?', 'bool', 'project_info'),
        gom.TokenInfo ('avoid_points_on_groove_edges', 'State: Avoid points on groove edges?', 'bool', 'project_info'),
        gom.TokenInfo ('max_viewing_angle_sensor_surface', 'Max. viewing angle sensor/surface', 'angle', 'project_info'),
        gom.TokenInfo ('scan_data_avoid_direct_reflections_angle', 'Angle (Avoid direct reflection in scan data)', 'angle', 'cat_internal'),
        gom.TokenInfo ('measurement_resolution', 'Measurement resolution', 'string', 'project_info'),
        gom.TokenInfo ('number_of_exposure_times', 'Number of exposure times', 'double', 'project_info'),
        gom.TokenInfo ('observe_gray_value_feature', 'State: Observe gray value feature?', 'string', 'project_info'),
        gom.TokenInfo ('automatic_exposure_time_mode', 'Automatic exposure time (mode)', 'string', 'project_info'),
        gom.TokenInfo ('automatic_exposure_time_photogrammetry_mode', 'Automatic exposure time photogrammetry (mode)', 'string', 'project_info'),
        gom.TokenInfo ('reflection_detection', 'Reflection detection', 'string', 'project_info'),
        gom.TokenInfo ('scan_area_usage', 'mask generation mode', 'string', 'cat_internal'),
        gom.TokenInfo ('scan_area_restricted_to_cad', 'State: Restricted to CAD (scan area)?', 'bool', 'project_info'),
        gom.TokenInfo ('scan_area_avoid_fixture', 'State: Avoid fixture (scan area)?', 'bool', 'project_info'),
        gom.TokenInfo ('scan_area_avoid_direct_reflections', 'State: Avoid direct reflections (scan area)?', 'bool', 'project_info'),
        gom.TokenInfo ('scan_area_direct_reflections_angle', 'Angle (Avoid direct reflections in scan area)', 'double', 'project_info'),
        gom.TokenInfo ('scan_area_offset', 'Offset (scan area)', 'double', 'project_info'),
        gom.TokenInfo ('are_measurements_aligned', 'State: Are measurements aligned?', 'bool', 'project_info'),
        gom.TokenInfo ('measurement_alignment_residual', 'Alignment residual (measurements)', 'length', 'project_info'),
        gom.TokenInfo ('measurement_mesh_alignment_residual', 'Alignment residual (preview meshes)', 'length', 'project_info'),
        gom.TokenInfo ('measurement_reference_point_alignment_residual', 'Alignment residual (reference points)', 'length', 'project_info'),
        gom.TokenInfo ('measurement_alignment_residual_diff_too_high', 'Alignment residual difference too high (measurements)', 'bool', 'cat_internal'),
        gom.TokenInfo ('measurement_alignment_prior_sw2018', 'Measurement alignment computed before sw2018', 'length', 'cat_internal'),
        gom.TokenInfo ('is_quality_triple_scan_points_checked', 'State: Is quality Triple Scan points checked?', 'bool', 'project_info'),
        gom.TokenInfo ('quality_triple_scan_points_mode', 'Quality check Triple Scan points', 'string', 'project_info'),
        gom.TokenInfo ('quality_triple_scan_points_threshold', 'Threshold for quality Triple Scan points', 'double', 'project_info'),
        gom.TokenInfo ('reduce_influence_of_border_areas', 'State: Reduce influence of border areas for polygonization?', 'bool', 'project_info'),
        gom.TokenInfo ('exception_sensor_movement_number_of_repetitions', 'Exception "Sensor movement": number of repetitions', 'double', 'project_info'),
        gom.TokenInfo ('exception_sensor_movement_delay', 'Exception "Sensor movement": delay', 'time', 'project_info'),
        gom.TokenInfo ('exception_sensor_movement_abort', 'Exception "Sensor movement": abort?', 'bool', 'project_info'),
        gom.TokenInfo ('exception_lighting_change_number_of_repetitions', 'Exception "Lighting change": number of repetitions', 'double', 'project_info'),
        gom.TokenInfo ('exception_lighting_change_delay', 'Exception "Lighting change": delay', 'time', 'project_info'),
        gom.TokenInfo ('exception_lighting_change_abort', 'Exception "Lighting change": abort?', 'bool', 'project_info'),
        gom.TokenInfo ('exception_transformation_number_of_repetitions', 'Exception "Transformation": number of repetitions', 'double', 'project_info'),
        gom.TokenInfo ('exception_transformation_delay', 'Exception "Transformation": delay', 'time', 'project_info'),
        gom.TokenInfo ('exception_transformation_abort', 'Exception "Transformation": abort?', 'bool', 'project_info'),
        gom.TokenInfo ('exception_decalibrated_sensor_number_of_repetitions', 'Exception "Decalibrated": number of repetitions', 'double', 'project_info'),
        gom.TokenInfo ('exception_decalibrated_sensor_delay', 'Exception "Decalibrated": delay', 'time', 'project_info'),
        gom.TokenInfo ('exception_decalibrated_sensor_abort', 'Exception "Decalibrated": abort?', 'bool', 'project_info'),
        gom.TokenInfo ('exception_measurement_temperature_number_of_repetitions', 'Exception "Measurement temperature": number of repetitions', 'double', 'project_info'),
        gom.TokenInfo ('exception_measurement_temperature_delay', 'Exception "Measurement temperature": delay', 'time', 'project_info'),
        gom.TokenInfo ('exception_measurement_temperature_abort', 'Exception "Measurement temperature": abort?', 'bool', 'project_info')] (<class 'list'>)

    
[X] 15:48 2020/11/11 Code pattern : sorted bounding_box xyz 
    : sorted-xyz // ( -- ['x','z','y'] ) Sorted xyz of bounding box bigest to smallest
        <py>
        bb = gom.app.project.parts[0].nominal.bounding_box	 # bounding box
        dim = bb.max - bb.min
        dim = {'x':dim.x, 'y':dim.y, 'z':dim.z}
        xyz = sorted(dim, key=dim.get, reverse=True)  # xyz is a sorted list like ['x', 'z', 'y'] where [0] is the biggest
        push(xyz) 
        </py> ;
[X] 16:45 2020/11/11 new word needed : reload-project 
    We already have reset-project then we need reload-project
    : reload-project // ( -- ) Reload the current project file 
        <py>
        pathname = gom.app.project.project_file
        gom.script.sys.close_project()
        gom.script.sys.load_project(file=pathname)
        </py> ;
[X] 09:42 2020/11/12 觀察 alignments array 
    gom :> app.project.alignments --> gom.app.project.alignments (<class 'gom.Item'>)
    gom :> app.project.alignments count --> 3 (<class 'int'>)
    gom :> app.project.alignments[0] --> gom.app.project.parts['Part'].original_alignment (<class 'gom.Item'>)
    gom :> app.project.alignments[1] --> gom.app.project.alignments['Prealignment'] (<class 'gom.Item'>)
    gom :> app.project.alignments[2] --> gom.app.project.alignments['Local_Best-fit#1'] (<class 'gom.Item'>)
    gom :> app.project.alignments[0] gom :> app.project.alignments[1]  = --> False (<class 'bool'>)
[X] 09:46 2020/11/12 repeating 重複工作 e.g. 新的 local best fit 之前都要先把 active alignment 改回 prealignment,
    否則 GOM 會用最後一組 local best fit 當參考。
    <py> gom.script.manage_alignment.set_alignment_active (cad_alignment=gom.app.project.alignments['Prealignment']) </py>
[X] 2020/11/12 剛研究了一下 GOM directories 都怎麼取得，也許有用，如下：
    Sent: Thursday, November 12, 2020 5:04 PM
    To: Bryan Cheng/WHQ/Wistron <Bryan_Cheng@wistron.com>; Alvin Yeh/WHQ/Wistron <Alvin_Yeh@wistron.com>; Jimmy Fan/WHQ/Wistron <Jimmy_Fan@wistron.com>; Toy Ho/WHQ/Wistron <Toy_Ho@wistron.com>; Winnie Wu/WHQ/Wistron <Winnie_Wu@wistron.com>
    Cc: H.C. Chen/WHQ/Wistron <H.C._CHEN@WISTRON.COM>
    Subject: RE: BB1296_01, Gom python plugin case2.5 user 希望用 Select Inside Cube 的 UI 多選
    剛研究了一下 GOM directories 都怎麼取得，也許有用，如下：
    py> gom.app.get('default_directory') --> C:\Users\8304018\Documents (<class 'str'>)
    py> gom.app.get('home_directory') --> C:\Users\8304018\Documents (<class 'str'>)
    py> gom.app.get('local_all_directory') --> C:\ProgramData\gom\2020 (<class 'str'>)
    py> gom.app.get('public_directory') --> None (<class 'NoneType'>)
    py> gom.app.get('project_template_directory') --> C:\Users\8304018\Documents\GOM\Templates\2020\gom_project_templates (<class 'str'>)
    py> gom.app.get('public_package_directory') -->  (<class 'str'>)
    py> gom.app.get('python_directory') --> C:\Program Files\GOM\2020\python\ (<class 'str'>)
    py> gom.app.get('software_directory') --> C:\Program Files\GOM\2020 (<class 'str'>)
    py> gom.app.get('system_package_directory') --> C:\Program Files\GOM\2020\packages (<class 'str'>)
    py> gom.app.get('temp_directory') --> C:\Users\8304018\AppData\Local\gom\tmp (<class 'str'>)
    py> gom.app.get('user_local_directory') --> C:\Users\8304018\AppData\Local\gom\2020 (<class 'str'>)
    py> gom.app.get('user_package_directory') --> C:\Users\8304018\AppData\Roaming\gom\2020\gom_packages (<class 'str'>)
    py> gom.app.get('user_roaming_directory') --> C:\Users\8304018\AppData\Roaming\gom\2020 (<class 'str'>)
    py> gom.app.project.get('project_file') --> d:\OneDrive\OneDrive - Wistron Corporation\Gom\Work\20201005\Case2\Case2_eng_v2_Cube.ginspect (<class 'str'>)
[X] get_coordinates() 與 get_view_direction() lookup table 
    <py>
    def get_coordinates(mesh_point_center_coordinate, size_of_cube, front_up_view):
        # 建立 deselect_in_viewing_direction() 框選 deselect 範圍的 lookup table for the coordinate argument
        # 整個表隨 點位、Select inside Cube 的長寬高、以及視角而改變。
        # front_up_view e.g. 'xpY+' 表示 xp 從螢幕朝向人的臉 Y+ 是朝上的 axis
        # Output 是照順時間轉四個方向傳回四個點位, 也就是 gom.script.selection3d.deselect_in_viewing_direction() 的 coordinates argument.

        p = mesh_point_center_coordinate
        s = size_of_cube  # [setup.parameter['cube_size']]*3 或者從 user 錄製的 selected_cubes.py 而來。
        table = {
            "xpY+": [gom.Vec3d(p.x, p.y+s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z+s[2]/2)],
            "xpZ+": [gom.Vec3d(p.x, p.y-s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z-s[2]/2)],
            "xpY-": [gom.Vec3d(p.x, p.y-s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z-s[2]/2)],
            "xpZ-": [gom.Vec3d(p.x, p.y+s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z+s[2]/2)],

            "xmY+": [gom.Vec3d(p.x, p.y+s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z-s[2]/2)],
            "xmZ-": [gom.Vec3d(p.x, p.y-s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z+s[2]/2)],
            "xmY-": [gom.Vec3d(p.x, p.y-s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z+s[2]/2)],
            "xmZ+": [gom.Vec3d(p.x, p.y+s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z+s[2]/2), gom.Vec3d(p.x, p.y-s[1]/2, p.z-s[2]/2), gom.Vec3d(p.x, p.y+s[1]/2, p.z-s[2]/2)],

            "ypX+": [gom.Vec3d(p.x+s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z-s[2]/2)],
            "ypZ-": [gom.Vec3d(p.x-s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z+s[2]/2)],
            "ypX-": [gom.Vec3d(p.x-s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z+s[2]/2)],
            "ypZ+": [gom.Vec3d(p.x+s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z-s[2]/2)],

            "ymX+": [gom.Vec3d(p.x+s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z+s[2]/2)],
            "ymZ+": [gom.Vec3d(p.x-s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z-s[2]/2)],
            "ymX-": [gom.Vec3d(p.x-s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z-s[2]/2)],
            "ymZ-": [gom.Vec3d(p.x+s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z-s[2]/2), gom.Vec3d(p.x-s[0]/2, p.y, p.z+s[2]/2), gom.Vec3d(p.x+s[0]/2, p.y, p.z+s[2]/2)],

            "zpX+": [gom.Vec3d(p.x+s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y+s[1]/2, p.z)],
            "zpY+": [gom.Vec3d(p.x-s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y-s[1]/2, p.z)],
            "zpX-": [gom.Vec3d(p.x-s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y-s[1]/2, p.z)],
            "zpY-": [gom.Vec3d(p.x+s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y+s[1]/2, p.z)],

            "zmX+": [gom.Vec3d(p.x+s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y-s[1]/2, p.z)],
            "zmY-": [gom.Vec3d(p.x-s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y+s[1]/2, p.z)],
            "zmX-": [gom.Vec3d(p.x-s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y+s[1]/2, p.z)],
            "zmY+": [gom.Vec3d(p.x+s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y+s[1]/2, p.z), gom.Vec3d(p.x-s[0]/2, p.y-s[1]/2, p.z), gom.Vec3d(p.x+s[0]/2, p.y-s[1]/2, p.z)],
            }
        return table[front_up_view]
    push(get_coordinates)
    </py> constant get_coordinates

    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"xpY+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"xpZ+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"xpY-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"xpZ-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"xmY+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"xmZ-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"xmY-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"xmZ+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"ypX+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"ypZ-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"ypX-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"ypZ+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"ymX+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"ymZ+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"ymX-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"ymZ-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"zpX+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"zpY+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"zpX-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"zpY-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"zmX+") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"zmY-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"zmX-") -->
    get_coordinates :> (gom.Vec3d(122.80,-9.65,182.01),[80.0]*3,"zmY+") -->


    <py>
    # 這個在 Case_2_5_20201110.py 沒用到，弟兄的方法比較聰明、且通用。
    def get_view_direction(view_angle):
        # 建立 view_direction 的 lookup table
        #     Input 是 24 種 view angle 之一 e.g. xmY+ xmZ- xmY- xmZ+, from setup.parameter['cavity_side']
        #     Output 是 對應的 gom.Vec3d(1.0, 0.0, 0.0), gom.Vec3d(-1.0, 0.0, 0.0), ...

        table = {
            "xp": gom.Vec3d(+1.0, 0.0, 0.0),
            "xm": gom.Vec3d(-1.0, 0.0, 0.0),
            "yp": gom.Vec3d( 0.0,+1.0, 0.0),
            "ym": gom.Vec3d( 0.0,-1.0, 0.0),
            "zp": gom.Vec3d( 0.0, 0.0,+1.0),
            "zm": gom.Vec3d( 0.0, 0.0,-1.0),
            }
        
        return table[view_angle[0:2]]
    push(get_view_direction)
    </py> constant get_view_direction

    get_view_direction :> ('xp') -->
    get_view_direction :> ('xm') -->
    get_view_direction :> ('yp') -->
    get_view_direction :> ('ym') -->
    get_view_direction :> ('zp') -->
    get_view_direction :> ('zm') -->
[X] 08:35 2020/11/13 用 peforth 埋斷點，幾下就可以拉出 JSON objects like BB1360#05  of the 6 samples of 象限。我等下來轉，仍用 “ypZ+” 的格式當 index。
    1. BB1247#11 6 standard view 
    2. 公模面對應六種視角(X+/X-/Y+/Y-/Z+/Z-)的Script已上傳至Sharepoint，如以下連結，謝謝 https://wistron.sharepoint.com/:f:/r/sites/R360/Shared%20Documents/Auto%20test/Gom%20python%20plugin%20cases/Case4/6%E5%80%8B%E8%A6%96%E8%A7%92%E7%9A%84Script?csf=1&web=1&e=AX2rJx

    [X] use view24 to confirm the 6 out of the 24 view angles
          ------------------  
            24view   Std
            index    view 
          ------------------  
             xmZ+     X- 
             xpZ+     X+ 
             ymZ+     Y- 
             ypZ+     Y+      <----- Case4_v2_1.py 舉的例子
             zmY+     Z- 
             zpY+     Z+ 
          ------------------  
    [X] 給 6 個 sample code 都埋下斷點。先用 C:\Users\8304018\AppData\Roaming\gom\2020\gom_scripts\Case4_v2_1.py 複習一遍：

        斷點都是設在 create report page 之前，如下例： 
            peforth.ok("66-1> ")
            gom.script.report.create_report_page (
    
        reDef unknown
        reDef -->
        p e f o r t h    v1.25
        source code http://github.com/hcchengithub/peforth
        Type 'peforth.ok()' to enter forth interpreter, 'exit' to come back.

        reDef accept
        reDef words
        11> exit
        66-1> get-view (see)
        {
            "__class__": "Object",
            "__module__": "gom",
            "__doc__":
            "__object_type__": "Tom::GRTProxy::GLSingleCamera",
            "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
            "position": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": -58.4036979675293,
                "y": 68.2017822265625,
                "z": 106.61565399169922
            },
            "view_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": 0.5773502588272095,
                "y": 0.5773502588272095,
                "z": -0.5773502588272095
            },
            "up_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": -0.40824833512306213,
                "y": 0.8164966702461243,
                "z": 0.40824833512306213
            },
            "scale": 3.7676610946655273
        }
        66-1> exit
        66-2> get-view (see)
        {
            "__class__": "Object",
            "__module__": "gom",
            "__doc__":
            "__object_type__": "Tom::GRTProxy::GLSingleCamera",
            "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
            "position": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": 61.988712310791016,
                "y": 69.67323303222656,
                "z": 104.61857604980469
            },
            "view_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": -0.5773502588272095,
                "y": 0.5773502588272095,
                "z": -0.5773502588272095
            },
            "up_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": 0.40824833512306213,
                "y": 0.8164966702461243,
                "z": 0.40824833512306213
            },
            "scale": 3.7676610946655273
        }
        66-2> exit
        66-3> get-view (see)
        {
            "__class__": "Object",
            "__module__": "gom",
            "__doc__":
            "__object_type__": "Tom::GRTProxy::GLSingleCamera",
            "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
            "position": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": 60.55759048461914,
                "y": 71.57561492919922,
                "z": 97.37842559814453
            },
            "view_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": -0.5773502588272095,
                "y": 0.5773502588272095,
                "z": 0.5773502588272095
            },
            "up_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": 0.40824833512306213,
                "y": 0.8164966702461243,
                "z": -0.40824833512306213
            },
            "scale": 3.7676610946655273
        }
        66-3> exit
        66-4> get-view (see)
        {
            "__class__": "Object",
            "__module__": "gom",
            "__doc__":
            "__object_type__": "Tom::GRTProxy::GLSingleCamera",
            "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
            "position": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": -60.75394821166992,
                "y": 71.55109405517578,
                "z": 97.71573638916016
            },
            "view_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": 0.5773502588272095,
                "y": 0.5773502588272095,
                "z": 0.5773502588272095
            },
            "up_direction": {
                "__class__": "Vec3d",
                "__module__": "gom",
                "__doc__":
                "x": -0.40824833512306213,
                "y": 0.8164966702461243,
                "z": -0.40824833512306213
            },
            "scale": 3.7676610946655273
        }
        66-4> exit
    [X] 14:03 2020/11/13 與 BB1360#05 比對 --> 差別很多！ position 不一樣，因為點位動過了？抓原來的 project 檔來試試看。。。
        --> 可能是因為沒有先做 prealignment 之故 --> 從頭先做好 prealignment --> 果然好了！！
    [X] 14:19 2020/11/13 開始給 6 個 standard view 範例下斷點抓 JSON . . . 
        [X] must use Stan's project file that has points constructed already for each of the 6 Parts
            [‎2020/‎11/‎13 15:11]  Stan KH Huang/WHQ/Wistron:  
            補充說明
            如果要正常運作Script，須先把所有報告頁刪除
            再把各Script內的report頁數依序改為'report' 'report 1' 'report 2' 'report 3'
        [X] 14:50 2020/11/13 相關 project 檔前所未見之大，其中有 6 個 parts ，此前都只有一個 ~.parts['Part']
            py> gom.app.project.parts[0] --> gom.app.project.parts['Y-'] (<class 'gom.Item'>)
            py> gom.app.project.parts[1] --> gom.app.project.parts['Y+'] (<class 'gom.Item'>)
            py> gom.app.project.parts[2] --> gom.app.project.parts['X+'] (<class 'gom.Item'>)
            py> gom.app.project.parts[3] --> gom.app.project.parts['Z-'] (<class 'gom.Item'>)
            py> gom.app.project.parts[4] --> gom.app.project.parts['Z+'] (<class 'gom.Item'>)
            py> gom.app.project.parts[5] --> gom.app.project.parts['X-'] (<class 'gom.Item'>)
            --> 15:06 2020/11/13 果然 get-view 以為固定是 parts['Part'] 這下出了問題。
            --> 這個
                    py> gom :> app.project.parts['Part'].actual.views.active
                要改用弟兄發現之更好的方法，如下，成功了！ 抓目前 active view 
                    py> gom.app.get('views').active (see)
                [ ] 15:15 2020/11/13 get-view 要改。
        [X] X+
            先手動切到 X+ Part, 其他都 hide, 然後開始執行家好斷點的 X_Plus.py . . . 
            1X+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 76.78382873535156,
                    "y": 58.2014045715332,
                    "z": 105.50321197509766
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.8164966702461243,
                    "y": 0.40824833512306213,
                    "z": 0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            1X+> exit
            2X+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 76.67015838623047,
                    "y": -54.79628372192383,
                    "z": 108.7531967163086
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.8164966702461243,
                    "y": -0.40824833512306213,
                    "z": 0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            2X+> exit
            3X+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 70.59303283691406,
                    "y": -55.17518997192383,
                    "z": 102.13175201416016
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.8164966702461243,
                    "y": -0.40824833512306213,
                    "z": -0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            3X+> exit
            4X+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 75.92952728271484,
                    "y": 59.62583541870117,
                    "z": 101.20441436767578
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.8164966702461243,
                    "y": 0.40824833512306213,
                    "z": -0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            4X+> 
        [X] X-
            先手動切到 X- Part, 其他都 hide, 然後開始執行加好斷點的 .py . . . 
            1X-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -76.63652801513672,
                    "y": -53.82017135620117,
                    "z": 109.73446655273438
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": 0.5773502588272095,
              exit      "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.8164966702461243,
                    "y": -0.40824833512306213,
                    "z": 0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            1X-> 
            2X-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -80.46768951416016,
                    "y": 57.8674201965332,
                    "z": 109.47547149658203
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.8164966702461243,
                    "y": 0.40824833512306213,
                    "z": 0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            2X-> exit
            3X-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -73.5959243774414,
                    "y": 56.478572845458984,
                    "z": 100.4369125366211
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.8164966702461243,
                    "y": 0.40824833512306213,
                    "z": -0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            3X-> exit
            4X-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -77.49742126464844,
                    "y": -58.45075607299805,
                    "z": 98.46472930908203
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.8164966702461243,
                    "y": -0.40824833512306213,
                    "z": -0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            4X->             
        [X] Y+
            先手動切到 Y+ Part, 其他都 hide, 然後開始執行加好斷點的 .py . . . 
            py> gom.app.get('views').active (see)
            1Y+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -54.6088752746582,
                    "y": 75.862060546875,
                    "z": 108.17430877685547
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.40824833512306213,
                    "y": 0.8164966702461243,
                    "z": 0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            1Y+> exit
            2Y+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 56.29256820678711,
                    "y": 74.9645767211914,
                    "z": 105.5517578125
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.40824833512306213,
                    "y": 0.8164966702461243,
                    "z": 0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            2Y+> exit
            3Y+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 59.35079574584961,
                    "y": 75.0299301147461,
                    "z": 101.87092590332031
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.40824833512306213,
                    "y": 0.8164966702461243,
                    "z": -0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            3Y+> exit
            4Y+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -57.798702239990234,
                    "y": 76.58206176757812,
                    "z": 98.72528839111328
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.40824833512306213,
                    "y": 0.8164966702461243,
                    "z": -0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            4Y+> bye
        [X] Y-
            先手動切到 Y- Part, 其他都 hide, 然後開始執行加好斷點的 .py . . . 
            py> gom.app.get('views').active (see)
            1Y-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 55.577640533447266,
                    "y": -75.45479583740234,
                    "z": 106.7942123413086
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.40824833512306213,
                    "y": -0.8164966702461243,
                    "z": 0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            1Y-> exit
            2Y-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -57.24943923950195,
                    "y": -76.0992660522461,
                    "z": 105.72566986083984
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.40824833512306213,
                    "y": -0.8164966702461243,
                    "z": 0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            2Y-> exit
            3Y-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -57.26175308227539,
                    "y": -75.16160583496094,
                    "z": 99.65372467041016
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.40824833512306213,
                    "y": -0.8164966702461243,
                    "z": -0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            3Y-> exit
            4Y-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 57.79751205444336,
                    "y": -77.36634826660156,
                    "z": 97.94353485107422
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.40824833512306213,
                    "y": -0.8164966702461243,
                    "z": -0.40824833512306213
                },
                "scale": 5.629594326019287
            }
            4Y-> bye
        [X] Z+
            先手動切到 Z+ Part, 其他都 hide, 然後開始執行加好斷點的 .py . . . 
            py> gom.app.get('views').active (see)
            1Z+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 53.670963287353516,
                    "y": 108.41083526611328,
                    "z": 75.1684799194336
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.40824833512306213,
                    "y": 0.40824833512306213,
                    "z": 0.8164966702461243
                },
                "scale": 5.629594326019287
            }
            1Z+> exit
            2Z+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -58.07223129272461,
                    "y": 105.76551818847656,
                    "z": 76.9627914428711
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.40824833512306213,
                    "y": 0.40824833512306213,
                    "z": 0.8164966702461243
                },
                "scale": 5.629594326019287
            }
            2Z+> exit
            3Z+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -58.699642181396484,
                    "y": 99.78173828125,
                    "z": 76.46417236328125
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.40824833512306213,
                    "y": -0.40824833512306213,
                    "z": 0.8164966702461243
                },
                "scale": 5.629594326019287
            }
            3Z+> exit
            4Z+> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 57.7989387512207,
                    "y": 99.50801849365234,
                    "z": 75.79884338378906
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": 0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.40824833512306213,
                    "y": -0.40824833512306213,
                    "z": 0.8164966702461243
                },
                "scale": 5.629594326019287
            }
            4Z+> exit
        [X] Z-
            先手動切到 Z- Part, 其他都 hide, 然後開始執行加好斷點的 .py . . . 
            py> gom.app.get('views').active (see)
            1Z-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -56.0842399597168,
                    "y": -97.30796813964844,
                    "z": -76.33911895751953
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.40824833512306213,
                    "y": 0.40824833512306213,
                    "z": -0.8164966702461243
                },
                "scale": 5.629594326019287
            }
            1Z-> exit
            2Z-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 60.555049896240234,
                    "y": -98.70931243896484,
                    "z": -79.35337829589844
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": -0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.40824833512306213,
                    "y": 0.40824833512306213,
                    "z": -0.8164966702461243
                },
                "scale": 5.629594326019287
            }
            2Z-> exit
            3Z-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 59.47977066040039,
                    "y": -108.73897552490234,
                    "z": -81.29280090332031
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.40824833512306213,
                    "y": -0.40824833512306213,
                    "z": -0.8164966702461243
                },
                "scale": 5.629594326019287
            }
            3Z-> exit
            4Z-> py> gom.app.get('views').active (see)
            {
                "__class__": "Object",
                "__module__": "gom",
                "__doc__":
                "__object_type__": "Tom::GRTProxy::GLSingleCamera",
                "__object_repr__": "<Trait: Tom::GRTProxy::GLSingleCamera>",
                "position": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": -58.57441329956055,
                    "y": -109.3995361328125,
                    "z": -81.1032485961914
                },
                "view_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__":
                    "x": 0.5773502588272095,
                    "y": 0.5773502588272095,
                    "z": -0.5773502588272095
                },
                "up_direction": {
                    "__class__": "Vec3d",
                    "__module__": "gom",
                    "__doc__": 
                    "x": -0.40824833512306213,
                    "y": -0.40824833512306213,
                    "z": -0.8164966702461243
                },
                "scale": 5.629594326019287
            }
            4Z-> bye
[X] 10:58 2020/11/16 用到 ~['Part'] 的寫法都要檢討，改用 active part. 受影響的有 case1, peofrth_gom_port.py 所有的
    words. 參考 CASE4_6個view.ginspect https://wistron.sharepoint.com/:u:/r/sites/R360/Shared%20Documents/Auto%20test/Gom%20python%20plugin%20cases/Case4/6%E5%80%8B%E8%A6%96%E8%A7%92%E7%9A%84Script/CASE4_6%E5%80%8Bview.ginspect?csf=1&web=1&e=dDT5Da
    它的 parts 變成了 X+ X- 等六個 standard view !!!
[X] Case1_asm_v103.py 以為 gom.app.project.parts['Part'].nominal.file 以下是三層結構，錯！往上還有一層 part !!!

    check if there's something like gom.app.project. active part 

    py> gom.app.project.__doc__ --> Object "CASE4_6個view" of type "project"
    Keywords:
    Name                                                       | Description                                                                                                         | Type                             
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    active_actual_mesh                                         | Active actual mesh                                                                                                  | String                           
    actual_master                                              | Actual master                                                                                                       | String                           
    alignment                                                  | Alignment                                                                                                           | Tom::Traits::CADAlignmentResult  
    alignment_for_visualized_report_elements                   | alignment for visualized report elements                                                                            | Tom::Traits::CADAlignmentResult  
    allowed_temperature_difference                             | Allowed temperature difference                                                                                      | Double                           
    are_measurements_aligned                                   | State: Are measurements aligned?                                                                                    | Boolean                          
    automatic_exposure_time_mode                               | Automatic exposure time (mode)                                                                                      | String                           
    automatic_exposure_time_photogrammetry_mode                | Automatic exposure time photogrammetry (mode)                                                                       | String                           
    automation_move_to_endposition_on_abort                    | State: Move to end position on abort?                                                                               | Boolean                          
    avoid_points_at_strong_brightness_differences              | State: Avoid points at strong brightness differences?                                                               | Boolean                          
    avoid_points_in_shadow_areas                               | State: Avoid points in shadow areas?                                                                                | Boolean                          
    avoid_points_on_borders_in_scan_area                       | State: Avoid points on borders in scan area?                                                                        | Boolean                          
    avoid_points_on_groove_edges                               | State: Avoid points on groove edges?                                                                                | Boolean                          
    avoid_points_on_shiny_surfaces                             | State: Avoid points on shiny surfaces?                                                                              | Boolean                          
    avoid_triple_scan_points                                   | State: Avoid Triple Scan points?                                                                                    | String                           
    avoid_triple_scan_points_at_strong_brightness_differences  | State: Avoid Triple Scan points at strong brightness differences?                                                   | Boolean                          
    cad_group                                                  | CAD group                                                                                                           | String                           
    check_decalibrated_sensor                                  | State: Check "Decalibrated sensor"?                                                                                 | Boolean                          
    check_lighting_change                                      | State: Check "Lighting change"?                                                                                     | Boolean                          
    check_measurement_temperature                              | State: Check "Measurement temperature"?                                                                             | Boolean                          
    check_missing_reference_points                             | State: Check missing reference points?                                                                              | Boolean                          
    check_sensor_movement                                      | State: Check "Sensor movement"?                                                                                     | Boolean                          
    check_transformation                                       | State: Check "Transformation"?                                                                                      | Boolean                          
    current_report_page                                        | Current report page                                                                                                 | Tom::Reference                   
    current_stage_range                                        | Current stage range                                                                                                 | String                           
    depth_limitation_mode                                      | Depth limitation mode                                                                                               | String                           
    exception_decalibrated_sensor_abort                        | Exception "Decalibrated": abort?                                                                                    | Boolean                          
    exception_decalibrated_sensor_delay                        | Exception "Decalibrated": delay                                                                                     | Time                             
    exception_decalibrated_sensor_number_of_repetitions        | Exception "Decalibrated": number of repetitions                                                                     | Double                           
    exception_lighting_change_abort                            | Exception "Lighting change": abort?                                                                                 | Boolean                          
    exception_lighting_change_delay                            | Exception "Lighting change": delay                                                                                  | Time                             
    exception_lighting_change_number_of_repetitions            | Exception "Lighting change": number of repetitions                                                                  | Double                           
    exception_measurement_temperature_abort                    | Exception "Measurement temperature": abort?                                                                         | Boolean                          
    exception_measurement_temperature_delay                    | Exception "Measurement temperature": delay                                                                          | Time                             
    exception_measurement_temperature_number_of_repetitions    | Exception "Measurement temperature": number of repetitions                                                          | Double                           
    exception_sensor_movement_abort                            | Exception "Sensor movement": abort?                                                                                 | Boolean                          
    exception_sensor_movement_delay                            | Exception "Sensor movement": delay                                                                                  | Time                             
    exception_sensor_movement_number_of_repetitions            | Exception "Sensor movement": number of repetitions                                                                  | Double                           
    exception_transformation_abort                             | Exception "Transformation": abort?                                                                                  | Boolean                          
    exception_transformation_delay                             | Exception "Transformation": delay                                                                                   | Time                             
    exception_transformation_number_of_repetitions             | Exception "Transformation": number of repetitions                                                                   | Double                           
    first_measurement_date                                     | Date of first measurement                                                                                           | String                           
    first_measurement_time                                     | Time of first measurement                                                                                           | String                           
    gdat_tolerance_table                                       | GD&T tolerance table                                                                                                | Tom::CAD::Traits::ToleranceTable 
    general_tolerance_table                                    | General tolerance table                                                                                             | Tom::CAD::Traits::ToleranceTable 
    gom_collision_check_since_load_import_copy_draft           | GOM: is a collision check computed since the last project load, import or element copy? (used in test scripts only) | Boolean                          
    inspections_not_in_reports                                 | Inspection elements (list) - not in reports                                                                         |                                  
    is_auto_recalc_enabled                                     | State: Is automatic recalculation for visible elements enabled?                                                     | Boolean                          
    is_auto_recalc_for_stages_enabled                          | State: is automatic recalculation for visible elements in all stages enabled?                                       | Boolean                          
    is_global_csys_view_csys                                   | State: Is global coordinate system used for viewing?                                                                | Boolean                          
    is_inspection_from_v7sr2                                   | is the inspection in this project from the old v7sr2 workflow?                                                      | Boolean                          
    is_modified                                                | GOM: is_modified                                                                                                    | Boolean                          
    is_modified_after_loading                                  | GOM: is_modified_after_loading                                                                                      | Boolean                          
    is_part_project                                            | State: Is this a "part project"?                                                                                    | Boolean                          
    is_quality_triple_scan_points_checked                      | State: Is quality Triple Scan points checked?                                                                       | Boolean                          
    last_measurement_date                                      | Date of last measurement                                                                                            | String                           
    last_measurement_time                                      | Time of last measurement                                                                                            | String                           
    max_reference_points_depth_limitation                      | Max. depth limitation reference points                                                                              | Length                           
    max_residual                                               | Max. residual                                                                                                       | Double                           
    max_residual_edge_point_adjustment                         | Max. residual edge point adjustment for scanning                                                                    | Double                           
    max_residual_edge_point_adjustment_for_photogrammetry      | Max. residual edge point adjustment for photogrammetry                                                              | Double                           
    max_residual_gray_value_adjustment                         | Max. residual gray value adjustment for scanning                                                                    | Double                           
    max_residual_gray_value_adjustment_for_photogrammetry      | Max. residual gray value for photogrammetry                                                                         | Double                           
    max_scan_surface_depth_limitation                          | Max. depth limitation scan surface                                                                                  | Length                           
    max_sensor_movement                                        | Max. sensor movement                                                                                                | Double                           
    max_viewing_angle_sensor_surface                           | Max. viewing angle sensor/surface                                                                                   | Angle                            
    measurement_alignment_prior_sw2018                         | Measurement alignment computed before sw2018                                                                        | Length                           
    measurement_alignment_residual                             | Alignment residual (measurements)                                                                                   | Length                           
    measurement_alignment_residual_diff_too_high               | Alignment residual difference too high (measurements)                                                               | Boolean                          
    measurement_mesh_alignment_residual                        | Alignment residual (preview meshes)                                                                                 | Length                           
    measurement_reference_point_alignment_residual             | Alignment residual (reference points)                                                                               | Length                           
    measurement_resolution                                     | Measurement resolution                                                                                              | String                           
    measurement_temperature                                    | Measurement temperature                                                                                             | Temperature                      
    measurement_transformation_type                            | Measurement transformation type                                                                                     | String                           
    measuring_task_project_building_block_draft                | Digitizing and inspection module                                                                                    | Tom::Prj::ProjectBBlockInfo      
    min_ellipse_contrast_for_photogrammetry                    | Min. ellipse contrast for photogrammetry                                                                            | Double                           
    min_ellipse_contrast_for_scanning                          | Min. ellipse contrast for scanning                                                                                  | Double                           
    min_ellipse_radius                                         | Min. ellipse size for scanning                                                                                      | Double                           
    min_ellipse_radius_for_photogrammetry                      | Min. ellipse size for photogrammetry                                                                                | Double                           
    min_fringe_contrast                                        | Min. fringe contrast                                                                                                | Double                           
    min_reference_points_depth_limitation                      | Min. depth limitation reference points                                                                              | Length                           
    min_scan_surface_depth_limitation                          | Min. depth limitation scan surface                                                                                  | Length                           
    name                                                       | Name                                                                                                                | String                           
    number_of_exposure_times                                   | Number of exposure times                                                                                            | Double                           
    observe_gray_value_feature                                 | State: Observe gray value feature?                                                                                  | String                           
    photogrametry_project_building_block_draft                 | Photogrammetry module                                                                                               | Tom::Prj::ProjectBBlockInfo      
    project_building_block_type_draft                          | Automation module type                                                                                              | String                           
    project_building_block_uuid_draft                          | Automation module unique identifier                                                                                 | String                           
    project_contains_preliminary_data                          | State: Project contains preliminary data?                                                                           | Boolean                          
    project_creation_time                                      | Project creation time                                                                                               | String                           
    project_data_reduction                                     | Project data reduction                                                                                              | String                           
    project_file                                               | Project file                                                                                                        | String                           
    project_file_size                                          | Project file size                                                                                                   | String                           
    project_history                                            | GOM: Save Project History                                                                                           | String                           
    project_keywords                                           | Project keywords (list of project keywords)                                                                         |                                  
    project_modification_time                                  | Project modification time                                                                                           | String                           
    project_name                                               | Project name                                                                                                        | String                           
    project_statistics                                         | Project statistics                                                                                                  | Tom::Prj::StatisticData          
    quality_triple_scan_points_mode                            | Quality check Triple Scan points                                                                                    | String                           
    quality_triple_scan_points_threshold                       | Threshold for quality Triple Scan points                                                                            | Double                           
    recent_reasons                                             | recent reasons                                                                                                      | Double                           
    reduce_influence_of_border_areas                           | State: Reduce influence of border areas for polygonization?                                                         | Boolean                          
    reference_point_identification_method                      | Method for reference point identification for scanning                                                              | String                           
    reference_point_identification_method_for_photogrammetry   | Method for reference point identification for photogrammetry                                                        | String                           
    reference_point_identification_settings                    | Reference point identification settings for scanning                                                                | String                           
    reference_point_identification_settings_for_photogrammetry | Reference point identification settings for photogrammetry                                                          | String                           
    reference_point_size                                       | Reference point size                                                                                                | Length                           
    reference_point_thickness                                  | Reference point thickness                                                                                           | Length                           
    reference_point_type                                       | Reference point type                                                                                                | String                           
    reference_points_collection_type                           | Type of reference point collection                                                                                  | String                           
    reference_stage                                            | Reference stage                                                                                                     | Tom::Traits::StageTimelineInfo   
    reflection_detection                                       | Reflection detection                                                                                                | String                           
    robogrammetry                                              | State: Robogrammetry?                                                                                               | Boolean                          
    scan_area_avoid_direct_reflections                         | State: Avoid direct reflections (scan area)?                                                                        | Boolean                          
    scan_area_avoid_fixture                                    | State: Avoid fixture (scan area)?                                                                                   | Boolean                          
    scan_area_direct_reflections_angle                         | Angle (Avoid direct reflections in scan area)                                                                       | Double                           
    scan_area_offset                                           | Offset (scan area)                                                                                                  | Double                           
    scan_area_restricted_to_cad                                | State: Restricted to CAD (scan area)?                                                                               | Boolean                          
    scan_area_usage                                            | mask generation mode                                                                                                | String                           
    scan_data_avoid_direct_reflections_angle                   | Angle (Avoid direct reflection in scan data)                                                                        | Angle                            
    scanning_template                                          | Scanning template                                                                                                   | Tom::Prj::ApplicationTemplateInfo
    stage                                                      | Stage                                                                                                               | Tom::Traits::StageTimelineInfo   
    template                                                   | Template information                                                                                                | Tom::Prj::TemplateInfo           
    use_reference_point_size                                   | State: Use reference point size?                                                                                    | Boolean                          
    use_user_defined_reference_point_size                      | State: Use user-defined reference point size?                                                                       | Boolean                          
    used_gdat_tolerances                                       | Used standard "GD&T tolerances" (tolerance table)                                                                   | String                           
    used_general_tolerances                                    | Used standard "General tolerances" (tolerance table)                                                                | String                           
    user_charge_nr                                             | 批号                                                                                                                  | String                           
    user_company                                               | 公司                                                                                                                  | String                           
    user_date                                                  | 日期                                                                                                                  | String                           
    user_defined_reference_point_color                         | User-defined reference point color                                                                                  | String                           
    user_defined_reference_point_size                          | User-defined reference point size                                                                                   | Length                           
    user_defined_reference_point_thickness                     | User-defined reference point thickness                                                                              | Length                           
    user_defined_reference_point_type                          | User-defined reference point type                                                                                   | String                           
    user_department                                            | 部门                                                                                                                  | String                           
    user_inspector                                             | 检测人                                                                                                                 | String                           
    user_location                                              | 地点                                                                                                                  | String                           
    user_part                                                  | 部件                                                                                                                  | String                           
    user_part_nr                                               | 部件编号                                                                                                                | String                           
    user_project                                               | 项目                                                                                                                  | String                           
    user_system                                                | 系统                                                                                                                  | String                           
    user_version                                               | 版本                                                                                                                  | String                           
    view_csys                                                  | Viewing coordinate system                                                                                           | Tom::Reference                   
    vmr_project_building_block_draft                           | VMR module                                                                                                          | Tom::Prj::ProjectBBlockInfo      
     (<class 'str'>)
    OK 

    查看某一個點
    <py> gom.app.project.inspection['Point 9']</pyV> adjust-view

        "__doc__": 
        "__id__": "I!#:1516",
        "__category__": 0,
        "__stage__": -1
    }
    OK 
    <py> gom.app.project.inspection['Point 5']</pyV> :> __doc__ --> Object "Point 5" of type "inspection_point"

    Keywords:

    Name                                                       | Description                                                                                                         | Type                                  
    -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    active_actual_mesh                                         | Active actual mesh                                                                                                  | String                                
    active_height                                              | active height                                                                                                       | Double                                
    active_width                                               | active width                                                                                                        | Double                                
    actual                                                     | Actual element (link)                                                                                               | Tom::Reference                        
    actual_element                                             | Actual element                                                                                                      | Tom::Reference                        
    actual_master                                              | Actual master                                                                                                       | String                                
    actual_type_text                                           | actual                                                                                                              | String                                
    adjustment_result                                          | Adjustment result                                                                                                   | Tom::CAD::Traits::AdjustmentResult    
    alignment                                                  | Alignment                                                                                                           | Tom::Traits::CADAlignmentResult       
    alignment_at_calculation                                   | Required alignment for calculation                                                                                  | Tom::Reference                        
    alignment_for_visualized_report_elements                   | alignment for visualized report elements                                                                            | Tom::Traits::CADAlignmentResult       
    allowed_temperature_difference                             | Allowed temperature difference                                                                                      | Double                                
    application_build_information                              | Application build information                                                                                       | Tom::Traits::ApplicationInformation   
    application_name                                           | Application name                                                                                                    | String                                
    application_version                                        | Application version                                                                                                 | String                                
    are_measurements_aligned                                   | State: Are measurements aligned?                                                                                    | Boolean                               
    assembly_tree                                              | CAD assembly tree node                                                                                              | Tom::Reference                        
    automatic_exposure_time_mode                               | Automatic exposure time (mode)                                                                                      | String                                
    automatic_exposure_time_photogrammetry_mode                | Automatic exposure time photogrammetry (mode)                                                                       | String                                
    automation_move_to_endposition_on_abort                    | State: Move to end position on abort?                                                                               | Boolean                               
    avoid_points_at_strong_brightness_differences              | State: Avoid points at strong brightness differences?                                                               | Boolean                               
    avoid_points_in_shadow_areas                               | State: Avoid points in shadow areas?                                                                                | Boolean                               
    avoid_points_on_borders_in_scan_area                       | State: Avoid points on borders in scan area?                                                                        | Boolean                               
    avoid_points_on_groove_edges                               | State: Avoid points on groove edges?                                                                                | Boolean                               
    avoid_points_on_shiny_surfaces                             | State: Avoid points on shiny surfaces?                                                                              | Boolean                               
    avoid_triple_scan_points                                   | State: Avoid Triple Scan points?                                                                                    | String                                
    avoid_triple_scan_points_at_strong_brightness_differences  | State: Avoid Triple Scan points at strong brightness differences?                                                   | Boolean                               
    cad_conversion_parameter                                   | CAD conversion parameter                                                                                            | Tom::CAD::CadConvertParameter         
    cad_group                                                  | CAD group                                                                                                           | String                                
    center_coordinate                                          | Center coordinate                                                                                                   | Tom::Vec3d                            
    check_decalibrated_sensor                                  | State: Check "Decalibrated sensor"?                                                                                 | Boolean                               
    check_lighting_change                                      | State: Check "Lighting change"?                                                                                     | Boolean                               
    check_measurement_temperature                              | State: Check "Measurement temperature"?                                                                             | Boolean                               
    check_missing_reference_points                             | State: Check missing reference points?                                                                              | Boolean                               
    check_sensor_movement                                      | State: Check "Sensor movement"?                                                                                     | Boolean                               
    check_text                                                 | check                                                                                                               | String                                
    check_transformation                                       | State: Check "Transformation"?                                                                                      | Boolean                               
    comment                                                    | Comment                                                                                                             | String                                
    computation_error_code                                     | Computation error code                                                                                              | String                                
    computation_information                                    | Computation information                                                                                             | String                                
    computation_status                                         | Computation status                                                                                                  | String                                
    creation_command_is_active                                 | element creation command is active                                                                                  | Boolean                               
    creation_sequence                                          | command which was used for creation                                                                                 | String                                
    creation_sequence_args                                     | parameters which was used for creation                                                                              | QVariantMap                           
    current_date                                               | Current date                                                                                                        | String                                
    current_report_page                                        | Current report page                                                                                                 | Tom::Reference                        
    current_stage_range                                        | Current stage range                                                                                                 | String                                
    current_user                                               | Current user                                                                                                        | String                                
    currently_used_gpu_memory                                  | currently used gpu memory kb                                                                                        | Double                                
    date_format                                                | Date format                                                                                                         | Tom::MSystem::Traits::DateFormatTrait 
    default_directory                                          | Default directory                                                                                                   | String                                
    default_templates_info_draft                               | default templates                                                                                                   | String                                
    dependency_children                                        | Direct dependend children of requesting element                                                                     |                                       
    depends_directly_on_elements                               | Depends directly on elements                                                                                        |                                       
    depends_on_part_objects_draft                              | object depends on which assembly groups                                                                             | QVariantList                          
    depth_limitation_mode                                      | Depth limitation mode                                                                                               | String                                
    deviation_text                                             | deviation                                                                                                           | String                                
    dump_geo_surface_database                                  | dumps the geo_surface database configuration to svg                                                                 | String                                
    element_could_represent_actual_part                        | is the element able to represent the actual part?                                                                   | Boolean                               
    element_keywords                                           | Element keywords (list of element keywords)                                                                         |                                       
    exception_decalibrated_sensor_abort                        | Exception "Decalibrated": abort?                                                                                    | Boolean                               
    exception_decalibrated_sensor_delay                        | Exception "Decalibrated": delay                                                                                     | Time                                  
    exception_decalibrated_sensor_number_of_repetitions        | Exception "Decalibrated": number of repetitions                                                                     | Double                                
    exception_lighting_change_abort                            | Exception "Lighting change": abort?                                                                                 | Boolean                               
    exception_lighting_change_delay                            | Exception "Lighting change": delay                                                                                  | Time                                  
    exception_lighting_change_number_of_repetitions            | Exception "Lighting change": number of repetitions                                                                  | Double                                
    exception_measurement_temperature_abort                    | Exception "Measurement temperature": abort?                                                                         | Boolean                               
    exception_measurement_temperature_delay                    | Exception "Measurement temperature": delay                                                                          | Time                                  
    exception_measurement_temperature_number_of_repetitions    | Exception "Measurement temperature": number of repetitions                                                          | Double                                
    exception_sensor_movement_abort                            | Exception "Sensor movement": abort?                                                                                 | Boolean                               
    exception_sensor_movement_delay                            | Exception "Sensor movement": delay                                                                                  | Time                                  
    exception_sensor_movement_number_of_repetitions            | Exception "Sensor movement": number of repetitions                                                                  | Double                                
    exception_transformation_abort                             | Exception "Transformation": abort?                                                                                  | Boolean                               
    exception_transformation_delay                             | Exception "Transformation": delay                                                                                   | Time                                  
    exception_transformation_number_of_repetitions             | Exception "Transformation": number of repetitions                                                                   | Double                                
    explorer_category                                          | Explorer category                                                                                                   | String                                
    explorer_tooltip                                           | explorer tooltip                                                                                                    | String                                
    explorer_type_and_state                                    | explorer type and state                                                                                             | String                                
    first_measurement_date                                     | Date of first measurement                                                                                           | String                                
    first_measurement_time                                     | Time of first measurement                                                                                           | String                                
    gdat_tolerance_table                                       | GD&T tolerance table                                                                                                | Tom::CAD::Traits::ToleranceTable      
    general_tolerance_table                                    | General tolerance table                                                                                             | Tom::CAD::Traits::ToleranceTable      
    geometrical_shape                                          | Geometrical shape                                                                                                   | String                                
    gom_collision_check_since_load_import_copy_draft           | GOM: is a collision check computed since the last project load, import or element copy? (used in test scripts only) | Boolean                               
    group_elements                                             | Group elements                                                                                                      | Tom::Reference                        
    group_membership                                           | to which groups does this object belong to                                                                          | QVariantList                          
    groups_created_on_element                                  | Groups based on this element                                                                                        | Tom::Reference                        
    home_directory                                             | Home directory                                                                                                      | String                                
    icon (explorer_type_and_state)                             | Object type and state icon                                                                                          | Tom::Expression::ScaledIcon           
    icon (geometrical_shape)                                   | Geometrical shape icon                                                                                              | Tom::Expression::ScaledIcon           
    icon (measuring_principle_command)                         | Measuring principle command icon                                                                                    | Tom::Expression::ScaledIcon           
    icon (type)                                                | Object type icon                                                                                                    | Tom::Expression::ScaledIcon           
    import_file                                                | Import file                                                                                                         | String                                
    import_file_name                                           | Import file name                                                                                                    | String                                
    import_information                                         | Import information                                                                                                  | Tom::Traits::ImportInformationTrait   
    imported_name                                              | Name (imported)                                                                                                     | String                                
    inspections_not_in_reports                                 | Inspection elements (list) - not in reports                                                                         |                                       
    inspections_out_of_tolerance                               | Inspections out of tolerance on this element (element list)                                                         |                                       
    is_auto_recalc_enabled                                     | State: Is automatic recalculation for visible elements enabled?                                                     | Boolean                               
    is_auto_recalc_for_stages_enabled                          | State: is automatic recalculation for visible elements in all stages enabled?                                       | Boolean                               
    is_element_in_clipboard                                    | State: Is element in clipboard?                                                                                     | Boolean                               
    is_element_modified_since_import                           | State: is element modified since import?                                                                            | Boolean                               
    is_global_csys_view_csys                                   | State: Is global coordinate system used for viewing?                                                                | Boolean                               
    is_inspection_from_v7sr2                                   | is the inspection in this project from the old v7sr2 workflow?                                                      | Boolean                               
    is_label_visible                                           | State: Is label visible?                                                                                            | Boolean                               
    is_modified                                                | GOM: is_modified                                                                                                    | Boolean                               
    is_modified_after_loading                                  | GOM: is_modified_after_loading                                                                                      | Boolean                               
    is_name_generated                                          | State: Is name generated?                                                                                           | Boolean                               
    is_part_project                                            | State: Is this a "part project"?                                                                                    | Boolean                               
    is_quality_triple_scan_points_checked                      | State: Is quality Triple Scan points checked?                                                                       | Boolean                               
    is_referenced_in_inspection                                | State: Is referenced in inspection element?                                                                         | Boolean                               
    is_selected                                                | State: Is element selected?                                                                                         | Boolean                               
    is_stage_range_restricted                                  | State: Is stage range restricted?                                                                                   | Boolean                               
    is_system_element                                          | State: Is system element?                                                                                           | Boolean                               
    is_visibility_locked                                       | State: Is visibility state locked?                                                                                  | Boolean                               
    is_visible                                                 | State: Is element visible?                                                                                          | Boolean                               
    kiosk_mode                                                 | Kiosk mode                                                                                                          | Boolean                               
    label                                                      | Label information                                                                                                   | Tom::CAD::Traits::LabelInfo           
    label_offset_in_3d_view                                    | Label offset in 3D view                                                                                             | Tom::Vec3d                            
    language                                                   | Software language                                                                                                   | String                                
    last_measurement_date                                      | Date of last measurement                                                                                            | String                                
    last_measurement_time                                      | Time of last measurement                                                                                            | String                                
    legend                                                     | Legend                                                                                                              | Tom::Legend2::LegendInfo              
    local_all_directory                                        | local config directory for all users                                                                                | String                                
    max_reference_points_depth_limitation                      | Max. depth limitation reference points                                                                              | Length                                
    max_residual                                               | Max. residual                                                                                                       | Double                                
    max_residual_edge_point_adjustment                         | Max. residual edge point adjustment for scanning                                                                    | Double                                
    max_residual_edge_point_adjustment_for_photogrammetry      | Max. residual edge point adjustment for photogrammetry                                                              | Double                                
    max_residual_gray_value_adjustment                         | Max. residual gray value adjustment for scanning                                                                    | Double                                
    max_residual_gray_value_adjustment_for_photogrammetry      | Max. residual gray value for photogrammetry                                                                         | Double                                
    max_scan_surface_depth_limitation                          | Max. depth limitation scan surface                                                                                  | Length                                
    max_sensor_movement                                        | Max. sensor movement                                                                                                | Double                                
    max_viewing_angle_sensor_surface                           | Max. viewing angle sensor/surface                                                                                   | Angle                                 
    measurement_alignment_prior_sw2018                         | Measurement alignment computed before sw2018                                                                        | Length                                
    measurement_alignment_residual                             | Alignment residual (measurements)                                                                                   | Length                                
    measurement_alignment_residual_diff_too_high               | Alignment residual difference too high (measurements)                                                               | Boolean                               
    measurement_mesh_alignment_residual                        | Alignment residual (preview meshes)                                                                                 | Length                                
    measurement_reference_point_alignment_residual             | Alignment residual (reference points)                                                                               | Length                                
    measurement_resolution                                     | Measurement resolution                                                                                              | String                                
    measurement_temperature                                    | Measurement temperature                                                                                             | Temperature                           
    measurement_transformation_type                            | Measurement transformation type                                                                                     | String                                
    measuring_principle_command                                | Measuring principle command                                                                                         | QString                               
    measuring_task_project_building_block_draft                | Digitizing and inspection module                                                                                    | Tom::Prj::ProjectBBlockInfo           
    memory_information                                         | Memory information                                                                                                  | Tom::MCADBase::MemoryInfo             
    min_ellipse_contrast_for_photogrammetry                    | Min. ellipse contrast for photogrammetry                                                                            | Double                                
    min_ellipse_contrast_for_scanning                          | Min. ellipse contrast for scanning                                                                                  | Double                                
    min_ellipse_radius                                         | Min. ellipse size for scanning                                                                                      | Double                                
    min_ellipse_radius_for_photogrammetry                      | Min. ellipse size for photogrammetry                                                                                | Double                                
    min_fringe_contrast                                        | Min. fringe contrast                                                                                                | Double                                
    min_reference_points_depth_limitation                      | Min. depth limitation reference points                                                                              | Length                                
    min_scan_surface_depth_limitation                          | Min. depth limitation scan surface                                                                                  | Length                                
    name                                                       | Name                                                                                                                | String                                
    name_expression                                            | name expression                                                                                                     | String                                
    nominal                                                    | Nominal element (link)                                                                                              | Tom::Reference                        
    nominal_element                                            | Nominal element                                                                                                     | Tom::Reference                        
    nominal_reference_type                                     | Nominal reference type                                                                                              | String                                
    number_of_date_formats                                     | Number of date formats                                                                                              | Double                                
    number_of_exposure_times                                   | Number of exposure times                                                                                            | Double                                
    object_family                                              | Object family                                                                                                       | String                                
    observe_gray_value_feature                                 | State: Observe gray value feature?                                                                                  | String                                
    online_measurement_prognosis                               | online measurement prognosis                                                                                        | String                                
    overview_explorer_alignments                               | alignment name of element for the overview explorer                                                                 |                                       
    overview_explorer_computation_alignment                    | computation alignment for the overview explorer                                                                     | String                                
    overview_explorer_computation_information                  | computation information for the overview explorer                                                                   | String                                
    overview_explorer_coordinate_system                        | elements using evaluation coordinate system for the overview explorer                                               |                                       
    overview_explorer_tacked_to_element                        | elements that are tacked to other elements for the overview explorer                                                |                                       
    package_database_info_draft                                | package database                                                                                                    | String                                
    package_information                                        | Package information                                                                                                 | Tom::MPRJ::PackageInformation         
    part                                                       | Part                                                                                                                | String                                
    photogrametry_project_building_block_draft                 | Photogrammetry module                                                                                               | Tom::Prj::ProjectBBlockInfo           
    project_building_block_type_draft                          | Automation module type                                                                                              | String                                
    project_building_block_uuid_draft                          | Automation module unique identifier                                                                                 | String                                
    project_contains_preliminary_data                          | State: Project contains preliminary data?                                                                           | Boolean                               
    project_creation_time                                      | Project creation time                                                                                               | String                                
    project_data_reduction                                     | Project data reduction                                                                                              | String                                
    project_file                                               | Project file                                                                                                        | String                                
    project_file_size                                          | Project file size                                                                                                   | String                                
    project_history                                            | GOM: Save Project History                                                                                           | String                                
    project_keywords                                           | Project keywords (list of project keywords)                                                                         |                                       
    project_modification_time                                  | Project modification time                                                                                           | String                                
    project_name                                               | Project name                                                                                                        | String                                
    project_statistics                                         | Project statistics                                                                                                  | Tom::Prj::StatisticData               
    project_template_directory                                 | Project template directory                                                                                          | String                                
    public_directory                                           | Public directory                                                                                                    | String                                
    public_package_directory                                   | Package directory (public)                                                                                          | String                                
    python_directory                                           | Python directory                                                                                                    | String                                
    quality_triple_scan_points_mode                            | Quality check Triple Scan points                                                                                    | String                                
    quality_triple_scan_points_threshold                       | Threshold for quality Triple Scan points                                                                            | Double                                
    recent_reasons                                             | recent reasons                                                                                                      | Double                                
    reduce_influence_of_border_areas                           | State: Reduce influence of border areas for polygonization?                                                         | Boolean                               
    reference_point_identification_method                      | Method for reference point identification for scanning                                                              | String                                
    reference_point_identification_method_for_photogrammetry   | Method for reference point identification for photogrammetry                                                        | String                                
    reference_point_identification_settings                    | Reference point identification settings for scanning                                                                | String                                
    reference_point_identification_settings_for_photogrammetry | Reference point identification settings for photogrammetry                                                          | String                                
    reference_point_size                                       | Reference point size                                                                                                | Length                                
    reference_point_thickness                                  | Reference point thickness                                                                                           | Length                                
    reference_point_type                                       | Reference point type                                                                                                | String                                
    reference_points_collection_type                           | Type of reference point collection                                                                                  | String                                
    reference_stage                                            | Reference stage                                                                                                     | Tom::Traits::StageTimelineInfo        
    reflection_detection                                       | Reflection detection                                                                                                | String                                
    render_complete_draw_time                                  | render complete draw time                                                                                           | Double                                
    render_driver_version                                      | render driver version                                                                                               | String                                
    render_gpu_type                                            | render gpu type                                                                                                     | String                                
    render_scene_graph_update_time                             | render_scene_graph_update_time                                                                                      | Double                                
    render_use_gpu_memory                                      | render use gpu memory                                                                                               | Boolean                               
    render_use_transparency                                    | render use transparency                                                                                             | Boolean                               
    rendered_frames                                            | rendered frames                                                                                                     | Double                                
    rendered_overlay_2d_frames                                 | rendered overlay 2d frames                                                                                          | Double                                
    rendered_overlay_3d_frames                                 | rendered overlay 3d frames                                                                                          | Double                                
    rendered_scene_layer_frames                                | rendered scene layer frames                                                                                         | Double                                
    rendered_temp_layer_frames                                 | rendered temp layer frames                                                                                          | Double                                
    restricted_stage_range                                     | Restricted stage range                                                                                              | Tom::Reference                        
    result_distance                                            | Distance                                                                                                            | Tom::Legend2::ResultVec3dTokenData    
    result_worst_case                                          | Worst-case                                                                                                          | Tom::Legend2::ResultDeviationTokenData
    result_x                                                   | X                                                                                                                   | Tom::Legend2::ResultScalarTokenData   
    result_y                                                   | Y                                                                                                                   | Tom::Legend2::ResultScalarTokenData   
    result_z                                                   | Z                                                                                                                   | Tom::Legend2::ResultScalarTokenData   
    rigid_body_motion_compensation_at_calculation              | Required rigid body motion compensation for calculation                                                             | Tom::Reference                        
    robogrammetry                                              | State: Robogrammetry?                                                                                               | Boolean                               
    rps_element                                                | Use of geometry in RPS                                                                                              | Tom::CAD::GeometryUsedInAlignment     
    scalar_registry_info                                       | scalar registry                                                                                                     | String                                
    scan_area_avoid_direct_reflections                         | State: Avoid direct reflections (scan area)?                                                                        | Boolean                               
    scan_area_avoid_fixture                                    | State: Avoid fixture (scan area)?                                                                                   | Boolean                               
    scan_area_direct_reflections_angle                         | Angle (Avoid direct reflections in scan area)                                                                       | Double                                
    scan_area_offset                                           | Offset (scan area)                                                                                                  | Double                                
    scan_area_restricted_to_cad                                | State: Restricted to CAD (scan area)?                                                                               | Boolean                               
    scan_area_usage                                            | mask generation mode                                                                                                | String                                
    scan_data_avoid_direct_reflections_angle                   | Angle (Avoid direct reflection in scan data)                                                                        | Angle                                 
    scanning_template                                          | Scanning template                                                                                                   | Tom::Prj::ApplicationTemplateInfo     
    selection_arg_base                                         | base elements for selection argument                                                                                | String                                
    selection_arg_target                                       | target elements for selection argument                                                                              | String                                
    skin                                                       | Skin                                                                                                                | Tom::MPRJ::SkinInfo                   
    software_directory                                         | Software directory                                                                                                  | String                                
    stage                                                      | Stage                                                                                                               | Tom::Traits::StageTimelineInfo        
    system_package_directory                                   | Package directory (system)                                                                                          | String                                
    table                                                      | Table                                                                                                               | Tom::MPRJ::TableInfo                  
    tags                                                       | Tags (list of element tags)                                                                                         |                                       
    temp_directory                                             | Temporary directory                                                                                                 | String                                
    template                                                   | Template information                                                                                                | Tom::Prj::TemplateInfo                
    template_database_info_draft                               | template database                                                                                                   | String                                
    template_info_draft                                        | template info                                                                                                       | String                                
    template_name                                              | Template name                                                                                                       | String                                
    template_package_draft                                     | template package                                                                                                    | Tom::PackageReference                 
    template_uuid                                              | Template UUID                                                                                                       | Tom::UUId                             
    tol_extrema_level                                          | Extrema level                                                                                                       | Double                                
    tol_neg_extrema_color                                      | Color for 'Neg. extrema'                                                                                            | String                                
    tol_neg_extrema_text                                       | Text for 'Neg. extrema'                                                                                             | String                                
    tol_neg_fail_color                                         | Color for 'Neg. fail'                                                                                               | String                                
    tol_neg_fail_text                                          | Text for 'Neg. fail'                                                                                                | String                                
    tol_neg_pass_color                                         | Color for 'Neg. pass'                                                                                               | String                                
    tol_neg_pass_text                                          | Text for 'Neg. pass'                                                                                                | String                                
    tol_neg_warn_color                                         | Color for 'Neg. warn'                                                                                               | String                                
    tol_neg_warn_text                                          | Text for 'Neg. warn'                                                                                                | String                                
    tol_novalue_color                                          | Color for 'Missing values'                                                                                          | String                                
    tol_novalue_text                                           | Text for 'Missing values'                                                                                           | String                                
    tol_pos_extrema_color                                      | Color for 'Pos. extrema'                                                                                            | String                                
    tol_pos_extrema_text                                       | Text for 'Pos. extrema'                                                                                             | String                                
    tol_pos_fail_color                                         | Color for 'Pos. fail'                                                                                               | String                                
    tol_pos_fail_text                                          | Text for 'Pos. fail'                                                                                                | String                                
    tol_pos_pass_color                                         | Color for 'Pos. pass'                                                                                               | String                                
    tol_pos_pass_text                                          | Text for 'Pos. pass'                                                                                                | String                                
    tol_pos_warn_color                                         | Color for 'Pos. warn'                                                                                               | String                                
    tol_pos_warn_text                                          | Text for 'Pos. warn'                                                                                                | String                                
    tol_unused_color                                           | Color for 'Unused values'                                                                                           | String                                
    tol_unused_text                                            | Text for 'Unused values'                                                                                            | String                                
    tol_warning_level                                          | Warning level                                                                                                       | Double                                
    transformation_category                                    | Transformation category                                                                                             | String                                
    type                                                       | Object type                                                                                                         | String                                
    undo_is_history_complete                                   | undo is history complete                                                                                            | Boolean                               
    undo_num_redo_steps                                        | undo num redo steps                                                                                                 | Double                                
    undo_num_undo_steps                                        | undo num undo steps                                                                                                 | Double                                
    unit_acceleration                                          | Acceleration unit                                                                                                   | String                                
    unit_angle                                                 | Angle unit                                                                                                          | String                                
    unit_angle_acceleration                                    | Angular acceleration unit                                                                                           | String                                
    unit_angle_velocity                                        | Angular velocity unit                                                                                               | String                                
    unit_area                                                  | Area unit                                                                                                           | String                                
    unit_count                                                 | Amount                                                                                                              | String                                
    unit_curvature                                             | Curvature                                                                                                           | String                                
    unit_density                                               | Density                                                                                                             | String                                
    unit_exposure_time                                         | Exposure time unit                                                                                                  | String                                
    unit_force                                                 | Force                                                                                                               | String                                
    unit_length                                                | Length unit                                                                                                         | String                                
    unit_mass                                                  | Mass                                                                                                                | String                                
    unit_no_unit                                               | Values without unit                                                                                                 | String                                
    unit_no_unit_acceleration                                  | 2nd derivative of values without unit                                                                               | String                                
    unit_no_unit_velocity                                      | 1st derivative of values without unit                                                                               | String                                
    unit_power                                                 | Power                                                                                                               | String                                
    unit_rate                                                  | Frame rate                                                                                                          | String                                
    unit_report                                                | Report unit                                                                                                         | String                                
    unit_statistics_cp                                         | Statistic values cp, pp, cpk, ppk                                                                                   | String                                
    unit_strain                                                | Technical/Green's strain unit                                                                                       | String                                
    unit_strain_acceleration                                   | Technical/Green's strain acceleration unit                                                                          | String                                
    unit_strain_rate                                           | Technical/Green's strain rate unit                                                                                  | String                                
    unit_temperature                                           | Temperature unit                                                                                                    | String                                
    unit_time                                                  | Time unit                                                                                                           | String                                
    unit_true_strain                                           | True strain unit                                                                                                    | String                                
    unit_true_strain_acceleration                              | True strain acceleration unit                                                                                       | String                                
    unit_true_strain_rate                                      | True strain rate unit                                                                                               | String                                
    unit_velocity                                              | Velocity unit                                                                                                       | String                                
    unit_voltage                                               | Voltage                                                                                                             | String                                
    unit_volume                                                | Volume unit                                                                                                         | String                                
    use_reference_point_size                                   | State: Use reference point size?                                                                                    | Boolean                               
    use_user_defined_reference_point_size                      | State: Use user-defined reference point size?                                                                       | Boolean                               
    used_gdat_tolerances                                       | Used standard "GD&T tolerances" (tolerance table)                                                                   | String                                
    used_general_tolerances                                    | Used standard "General tolerances" (tolerance table)                                                                | String                                
    user_charge_nr                                             | 批号                                                                                                                  | String                                
    user_company                                               | 公司                                                                                                                  | String                                
    user_date                                                  | 日期                                                                                                                  | String                                
    user_defined_reference_point_color                         | User-defined reference point color                                                                                  | String                                
    user_defined_reference_point_size                          | User-defined reference point size                                                                                   | Length                                
    user_defined_reference_point_thickness                     | User-defined reference point thickness                                                                              | Length                                
    user_defined_reference_point_type                          | User-defined reference point type                                                                                   | String                                
    user_department                                            | 部门                                                                                                                  | String                                
    user_inspector                                             | 检测人                                                                                                                 | String                                
    user_local_directory                                       | local user config directory                                                                                         | String                                
    user_location                                              | 地点                                                                                                                  | String                                
    user_package_directory                                     | Package directory (user)                                                                                            | String                                
    user_part                                                  | 部件                                                                                                                  | String                                
    user_part_nr                                               | 部件编号                                                                                                                | String                                
    user_project                                               | 项目                                                                                                                  | String                                
    user_roaming_directory                                     | roaming user config directory                                                                                       | String                                
    user_system                                                | 系统                                                                                                                  | String                                
    user_version                                               | 版本                                                                                                                  | String                                
    vdi_base_name                                              | base name for vdi test elements                                                                                     | String                                
    view_csys                                                  | Viewing coordinate system                                                                                           | Tom::Reference                        
    viewport_height                                            | viewport height                                                                                                     | Double                                
    viewport_width                                             | viewport width                                                                                                      | Double                                
    views                                                      | Views                                                                                                               | Tom::GRTProxy::Traits::CamerasTrait   
    visible_views                                              | currently visible views                                                                                             |                                       
    vmr_project_building_block_draft                           | VMR module                                                                                                          | Tom::Prj::ProjectBBlockInfo           
    workspace                                                  | Active workspace                                                                                                    | String                                
     (<class 'str'>)
    OK 

[X] 13:06 2020/11/16 有這種 point 'Point 2 Copy 5' --> 如何像 patchs 一樣，把所有的 points 都列出來？
    #gom.script.sys.restore_point_selection (elements=[gom.app.project.inspection['Point 5']])
    #gom.ElementSelection ({'category': ['key', 'elements', 'part', gom.app.project.parts['X+'], 'explorer_category', 'actual', 'object_family', 'geometrical_element']})
    #gom.ElementSelection ({'category': ['key', 'elements', 'part', gom.app.project.parts['Z+'], 'explorer_category', 'nominal', 'object_family', 'geometrical_element']})
    #gom.ElementSelection ({'category': ['key', 'elements', 'part', gom.app.project.parts['Z-'], 'explorer_category', 'nominal', 'object_family', 'geometrical_element', 'type', 'inspection_point']})
    #gom.app.project.nominal_elements['14D Copy 6'].file['14D'].bodies
    #gom.app.project.actual_elements['Point 1 Copy 2'].project_statistics.inspection_edge_point    

    [X] 14:06 2020/11/16 重點是，point 與 part 是同一層的 element！ py> gom.app.project.nominal_elements count --> 32 (<class 'int'>)
        32 [for] t@ 1- dup . space py> gom.app.project.nominal_elements[pop()] --> [next]
        32 [for] t@ 1- dup . space py> gom.app.project.actual_elements[pop()] --> [next]
    
    [X] 13:52 2020/11/16 有突破了，從 __doc__ 發現有 type 可分辨哪些是 points, 可以列出所有的 points 了
        32 [for] t@ 1- dup . space py> gom.app.project.nominal_elements[pop()] :> type --> [next]
        32 [for] t@ 1- dup . space py> gom.app.project.actual_elements[pop()] :> type --> [next]
        py> gom.app.project.parts count --> 6 (<class 'int'>)
        py> gom.app.project.parts[0] :> actual --> gom.app.project.parts['Y-'].actual (<class 'gom.Item'>)
        py> gom.app.project.parts[0] :> nominal --> gom.app.project.parts['Y-'].nominal (<class 'gom.Item'>)

    [X] 14:41 2020/11/16 列出所有打在 CAD 上的點  list all CAD points 
        <py>
        count = 0 
        for e in gom.app.project.nominal_elements:
            if e.type == 'point':
                push(e).push(count).dictate(". space -->")
                count += 1
        </py>
    [X] 14:41 2020/11/16 列出所有打在 Mesh 上的點 list all mesh points 
        <py>
        count = 0 
        for e in gom.app.project.actual_elements:
            if e.type == 'point':
                push(e).push(count).dictate(". space -->")
                count += 1
        </py>
    [X] 14:45 2020/11/16 從點反查 part、name、type、CAD or Mesh、inspection or report or etc 
        --> 可以！ 
        e :> type --> point (<class 'gomlib.types.ObjectType'>)
        e :> part --> gom.app.project.parts['Y-'] (<class 'gom.Item'>)
        e :> name --> Point 1 (<class 'str'>)
        e :> workspace --> inspection (<class 'str'>)
        e :> depends_directly_on_elements --> {'actual_elements': [gom.app.project.parts['Y-'].actual], 'nominal_elements': [], 'other_elements': []} (<class 'dict'>)
            e :> depends_directly_on_elements['actual_elements'] bool --> True (<class 'bool'>)
            e :> depends_directly_on_elements['nominal_elements'] bool --> False (<class 'bool'>)
            e :> depends_directly_on_elements['other_elements'] bool --> False (<class 'bool'>)
            
        e :> dependency_children --> {'actual_elements': [], 'nominal_elements': [], 'other_elements': []} (<class 'dict'>)
        e :> group_membership --> [gom.app.project.parts['Y-']] (<class 'list'>)
        e :> element_keywords --> [] (<class 'list'>)
        e :> active_actual_mesh -->  (<class 'str'>)
    [X] 14:53 2020/11/16 use adjust-view to see those points and their attributes 
        <py>
        c = 0 
        for e in gom.app.project.actual_elements: # 這次用 CAD 將來都用 Mesh 打點
            if e.type == 'point':
                push(e).push(c).push(locals()).ok("11> ",cmd="""  # 停下來 press ESC 繼續
                    to _locals_ 
                    cr . cr
                    ." Type: " dup :> type . cr
                    ." Part: " dup :> part . cr
                    ." Where: " dup :> depends_directly_on_elements . cr
                    ." Workspace: " dup :> workspace . cr     
                    ." Object: " dup . cr
                    adjust-view
                """)
                c += 1
        </py>
[X] 15:50 2020/11/16 上面有辦法查看所有的 points 了，接著繼續檢查 我的 SixViewsQuadrants.py
    [X] 10:35 2020/11/16 Testing SixViewsQuadrants.py  https://wistron.sharepoint.com/:u:/r/sites/R360/Shared%20Documents/Auto%20test/Gom%20python%20plugin%20cases/Case4/6%E5%80%8B%E8%A6%96%E8%A7%92%E7%9A%84Script/SixViewsQuadrants.py?csf=1&web=1&e=EPoFNa
        char SixViewsQuadrants (import) constant quadrants // 四象限視角表
        quadrants --> \ <module 'SixViewsQuadrants' from 'C:\\Users\\8304018\\AppData\\Roaming\\gom\\2020\\gom_scripts\\SixViewsQuadrants.py'> (<class 'module'>)
        quadrants :> a --> \ ['xp1', 'xp2', 'xp3', 'xp4', 'xm1', 'xm2', 'xm3', 'xm4', 'yp1', 'yp2', 'yp3', 'yp4', 'ym1', 'ym2', 'ym3', 'ym4', 'zp1', 'zp2', 'zp3', 'zp4', 'zm1', 'zm2', 'zm3', 'zm4'] (<class 'list'>)
        quadrants :> c['xp1'] dict>view set-view
        quadrants :> c['zm4'] dict>view set-view
        確定有切到預期的點位，無誤。
[X] 10:41 2020/11/17 trace _Case_4_20201112.py_ 發現
    弟兄們用來抓 points 的方式好像更好.... 一樣。
    上面 14:53 2020/11/16 是最好的方式，只分 cad and mesh 能容各種不同 points 
        points = gom.ElementSelection ({
            'category': [
                'key', 'elements', 
                'part', gom.app.project.parts['Part'], 
                'explorer_category', 'actual', 
                'object_family', 'geometrical_element', 
                'type', 'point'
            ]
        })
    我的方式
	: mesh-points // ( -- ElementSelection ) Mesh points created by: CONSTRUCT > point > point
		<py>
		points = gom.ElementSelection({
			'category':[
				'key', 'elements',
				'part', gom.app.project.parts['Part'],
				'explorer_category', 'actual',
				'object_family', 'geometrical_element',
				'type', 'point']
		})
		push(points) </py> ;
[X] 14:51 2020/11/23 verify TR _BB1247_01_ for the known problem 
    C:\Users\8304018\AppData\Roaming\gom\2020\gom_scripts\Case_Points.py
    def fComparison_Mesh_CAD(num):
[X] 15:51 2020/11/23 cubes :> cubes 
    cubes :> cubes --> [
        {
            'center': {
                'interpolated': True, 
                'normal': (-0.02351616323, -0.998755157, 0.0439914614), 
                'point': (-180.1291289, -0.05448691875, 244.0563948)
                }, 
            'csys': 'system_global_coordinate_system', 
            'height': 47.0,  # y
            'length': 59.0,  # x
            'width': 23.0    # z
            }, 
        {'center': {'interpolated': True, 'normal': (-0.01242606249, -0.9999197721, -0.002455234528), 'point': (-113.8902993, -0.7512857542, 240.7244127)}, 'csys': 'system_global_coordinate_system', 'height': 50.0, 'length': 72.0, 'width': 23.0}, 
        {'center': {'interpolated': True, 'normal': (-0.1111847311, -0.9937341213, -0.01142175868), 'point': (-174.481426, -1.990842873, 31.76333484)}, 'csys': 'system_global_coordinate_system', 'height': 71.0, 'length': 72.0, 'width': 23.0}, 
        {'center': {'interpolated': True, 'normal': (-0.004245250951, -0.9968857765, 0.07874464989), 'point': (-56.06718604, -2.563568558, 36.48895021)}, 'csys': 'system_global_coordinate_system', 'height': 71.0, 'length': 72.0, 'width': 23.0}, 
        {'center': {'interpolated': True, 'normal': (-0.08109087497, -0.9967066646, 0.0001649308397), 'point': (187.4964281, -1.685223127, 112.1768009)}, 'csys': 'system_global_coordinate_system', 'height': 71.0, 'length': 72.0, 'width': 23.0}, 
        {'center': {'interpolated': True, 'normal': (0.05508308485, -0.998455584, 0.007233268581), 'point': (166.8722756, -0.1874153514, 238.5734015)}, 'csys': 'system_global_coordinate_system', 'height': 71.0, 'length': 72.0, 'width': 23.0}, 
        {'center': {'interpolated': True, 'normal': (-0.01812336966, -0.9998323917, 0.002589342417), 'point': (-32.88738681, -2.285430838, 166.0942262)}, 'csys': 'system_global_coordinate_system', 'height': 71.0, 'length': 145.0, 'width': 23.0}, 
        {'center': {'interpolated': True, 'normal': (0.006664484739, -0.9997825027, -0.01976365969), 'point': (111.1870556, -1.894055612, 33.21575126)}, 'csys': 'system_global_coordinate_system', 'height': 71.0, 'length': 82.0, 'width': 23.0}
    ] (<class 'list'>)

    cube_cntr --> gom.Vec3d (-9.352804908650285, 144.00353445704832, 22.863689396624387) (<class 'gom.Vec3d'>)
    _locals_ :> ['dict'] --> {'cube_size_x': 80, 'cube_size_y': 80, 'cube_size_z': 80} (<class 'dict'>)

    cubes :> cubes :> [0]['center']['point'] --> (-180.1291289, -0.05448691875, 244.0563948) (<class 'tuple'>)
    cubes :> cubes :> [0]['height'] --> 47.0 (<class 'float'>)
    cubes :> cubes :> [0]['length'] --> 59.0 (<class 'float'>)
    cubes :> cubes :> [0]['width'] --> 23.0 (<class 'float'>)
    fLoopToGenerateCube 3> 
[X] 17:00 2020/11/23 case_points_v100.py 好了
[X] 14:06 2020/11/24 check list for a release
    [X] remove or disable import peforth and import peforth_gom_port 
    [X] remove or disable all debug breakpoints that probably have 'peforth' in the line 
    [X] 結束的 workspace, view angle 的切換
    [X] 一開始清除所有的東西，一切重來。僅限 'Part' 下。[ ] 若有多 part 則提出警告然後停止執行。
    [X] 最後不要自動 save 
    [X] 一開始的 workspace, standard view angle 要切換好
    [X] 附上最新版的 setup.py 
    [X] 檢查 source code 頭尾的版號
    [X] 檢查 email subject and body 版號
[X] 14:16 2020/11/24 debug BB1247_02 「九宮格自動擬合」v101 設定 5x4 切割就會亂跳 
    [x] 14:20 2020/11/24 compare 101 and 102 , no big difference so start using v102 to debug
        亂跳 v102 解了(吧？)  local best fit 異常造成整個 project 偏斜的現象 -- not a problem. 
[X] 09:08 2020/11/26 簡化 peforth breakpoint 的構想, 利用以下方法擴充 peforth.bp(id=1, locals=locals()) 
        def hi():
            %f .( hello world !! ) cr
        %f hi py: vm.hi=pop() 
        %f py: vm.hi()
    定義：
        def bp(id=None,locals=None):
            if id==None: 
                id = 0
                prompt='bp> '
            else:
                prompt="bp{}>".format(id)
            if id in peforth.bps: peforth.push(locals).ok(prompt, cmd="to _locals_")
        peforth.bp=bp
        peforth.bps=[i for i in range(1000)]
    實際執行 
        peforth.bp()   # drop a breakpoint using default prompt bp> 
        peforth.bp(11) # drop a breakpoint using prompt bp11> w/p passing locals()
        peforth.bp(22,locals())  # drop a breakpoint using prompt bp22> with locals()
        peforth.bps=[] # disable all breakpoints
        peforth.dictate("peforth :: bps=[]") # disable all breakpoints
        peforth.dictate("peforth :: bps=[123,345,567]") # enable only listed breakpoints 
        peforth.dictate("peforth :: bps[123]=0") # disable the breakpoint 123
        peforth.dictate("peforth :: pop(111)")   # disable the breakpoint 111
        for i in [11,22,33]: peforth.bps[i]=0    # disable breakpoints 11,22,33 
        peforth.bps=[i for i in range(1000)]     # reload and enable all breakpoints    
[/] 14:04 2020/11/26 我覺得 def fAdjustDirectionByQuadrant(inp_x, inp_y, inp_z) 裡面翻轉時用 
    mesh_cntr 為中心不對，應該用  gom.Vec3d(inp_x, inp_y, inp_z) 
    --> 轉軸對了就對了，
            rotation_axis='cube_x', 
        出 report 時已 selection 為中心即可，這個沒差。
[X] setup 與 input files 都用 scrip 所在 directory, see BB1296_02
    [X] 15:11 2020/11/25 如何查出 GOM python Script 所在的 folder?  
        老師好，
            我們寫的 GOM python script 好像都是由 GOM 的 
                    C:\Program Files\GOM\2020\lib\python\gom_script_server\gom_script_server.py
            來啟動的，所以要怎麼知道我們寫的 script 本身所在的 folder 就不能用一般的方法了！怎麼辦？

            一般的方法：https://stackoverflow.com/questions/4934806/how-can-i-find-scripts-directory-with-python
            import os
            print(os.path.realpath(__file__))
            print(os.path.dirname(os.path.realpath(__file__)))
            結果不對
            C:\Program Files\GOM\2020\lib\python\gom_script_server\gom_script_server.py
            C:\Program Files\GOM\2020\lib\python\gom_script_server
        This is the solution:
            # Get pathname of cubes.py the selections 如果 setup.py 有指定完整路徑就照辦；如果只給檔名就從 script 所在 folder 找。
            pathname = os.path.dirname(gomlib.args.name) + '/' + pathname if os.path.dirname(pathname)=="" else pathname 
            cubes = InsideCube_FileName(pathname)
[X] 11:57 2020/11/26 據報, C:/Users/8304018/AppData/Roaming/gom/2020/gom_scripts/Case_Points_v102.py
    第三象限的 view angle 不對，經查，九宮格、自由框選都有一樣的問題 --> reproduced on the above .py with the 6v2 
    --> 12:35 2020/11/26 find the point putting the view --> fAdjustDirectionByQuadrant(cube_cntr.x, cube_cntr.y, cube_cntr.z)
    --> 與我當初給的 table BB1360#05.02 
            https://wistron.sharepoint.com/sites/R360/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FR360%2FShared%20Documents%2FAuto%20test%2FGom%20python%20plugin%20cases%2FCase4%2F6%E5%80%8B%E8%A6%96%E8%A7%92%E7%9A%84Script%2FSixViewsQuadrants%2Epy&parent=%2Fsites%2FR360%2FShared%20Documents%2FAuto%20test%2FGom%20python%20plugin%20cases%2FCase4%2F6%E5%80%8B%E8%A6%96%E8%A7%92%E7%9A%84Script
        比對看看。。。。
    [/] fChangeToQuadrant() 查象限，都對嗎？
    [X] 14:33 2020/11/26 重新錄製 X+ Quadrant3 的翻轉過程
        # -*- coding: utf-8 -*-

        import gom, peforth, peforth_gom_port, setup
        # import sklearn

        # bounding box center 
        # the first repoprt view angle 

        gom.script.view.set_view_direction_and_up_direction (
            rotation_center=gom.Vec3d (-5.471191863, -0.2504186606, 103.4102926), 
            use_animation=False, 
            view_direction=gom.Vec3d (0.7071067812, 0.0, -0.7071067812), 
            widget='3d_view')

        gom.script.view.set_view_direction_and_up_direction (
            rotation_center=gom.Vec3d (-5.471191863, -0.2504186606, 103.4102926), 
            use_animation=False, 
            view_direction=gom.Vec3d (0.5773502692, 0.5773502692, 0.5773502692), 
            widget='3d_view')

        # the 180 flipped 

        gom.script.view.set_view_direction_and_up_direction (
            rotation_center=gom.Vec3d (-5.471191863, -0.2504186606, 103.4102926), 
            use_animation=False, 
            view_direction=gom.Vec3d (0.7071067812, 0.0, -0.7071067812), 
            widget='3d_view')

        gom.script.view.set_view_direction_and_up_direction (
            rotation_center=gom.Vec3d (-5.471191863, -0.2504186606, 103.4102926), 
            use_animation=False, 
            view_direction=gom.Vec3d (0.5773502692, 0.5773502692, 0.5773502692), 
            widget='3d_view')

        gom.script.view.rotate_3d_view (
            rotation_angle=180.0, 
            rotation_axis='cube_x', 
            rotation_center=gom.Vec3d (-5.471191863, -0.2504186606, 103.4102926), 
            use_animation=False, 
            widget='3d_view')


        # center at a point 
        # the first repoprt view angle 

        gom.script.view.set_view_direction_and_up_direction (
            rotation_center=gom.Vec3d (-9.083445245, -19.03402432, 74.21955757), 
            use_animation=False, 
            view_direction=gom.Vec3d (0.7071067812, 0.0, -0.7071067812), 
            widget='3d_view')

        gom.script.view.set_view_direction_and_up_direction (
            rotation_center=gom.Vec3d (-9.083445245, -19.03402432, 74.21955757), 
            use_animation=False, 
            view_direction=gom.Vec3d (0.5773502692, 0.5773502692, 0.5773502692), 
            widget='3d_view')


        # the 180 flipped 

        gom.script.view.rotate_3d_view (
            rotation_angle=180.0, 
            rotation_axis='cube_x', 
            rotation_center=gom.Vec3d (-9.083445245, -19.03402432, 74.21955757), 
            use_animation=False, 
            widget='3d_view')
    [X] 14:34 2020/11/26 Stan 強調，只有 X+ 才有這個問題，其他 5 個都 OK。
        --> 那比對有何不同即可...
        RI: 
            # will have different rotate angle according to core_side.
            if private_variable['core_side'] == 'xpZ+':
                if Quadrant == '(+,+)':
                    fSetMeshDirection(mesh_cntr, gom.Vec3d (0.7071067812, 0.0, -0.7071067812))
                    fSetMeshDirection(mesh_cntr, gom.Vec3d (0.5773502692, -0.5773502692, -0.5773502692))
                elif Quadrant == '(-,+)':
                    fSetMeshDirection(mesh_cntr, gom.Vec3d (0.7071067812, 0.0, -0.7071067812))
                    fSetMeshDirection(mesh_cntr, gom.Vec3d (0.5773502692, 0.5773502692, -0.5773502692))	
                elif Quadrant == '(-,-)':
                    fSetMeshDirection(mesh_cntr, gom.Vec3d (0.7071067812, 0.0, -0.7071067812))  
                                                                               ^^^^^^^^^^^^^ <-------- 少一個負號，當初弟兄建表時的 typo
                    fSetMeshDirection(mesh_cntr, gom.Vec3d (0.5773502692, 0.5773502692, 0.5773502692))
                elif Quadrant == '(+,-)':
                    fSetMeshDirection(mesh_cntr, gom.Vec3d (0.7071067812, 0.0, -0.7071067812))
                    fSetMeshDirection(mesh_cntr, gom.Vec3d (0.5773502692, -0.5773502692, 0.5773502692))
    [x] points v102
    [ ] blocks v103 
        
[X] 15:33 2020/11/26 新增 setup item 'scale'
	fSetMeshScale(absolute_pos, parameter['scale'])	
    [x] points v102
    [X] blocks v103 
    --> released  https://wistron.sharepoint.com/sites/R360/Shared%20Documents/Forms/AllItems.aspx?e=5%3Acd4fe1cdc77741678f4a552676d85f94&at=9&FolderCTID=0x0120003601C040A0F7FC489F7AC70CDC05B2B9&viewid=e4ec2867%2Db8e7%2D4c6a%2Da4e0%2Dfdf2959c963d&id=%2Fsites%2FR360%2FShared%20Documents%2FAuto%20test%2FGom%20python%20plugin%20cases%2FCase2%2FRelease    
    
[/] 17:42 2020/12/02 BB2726 Gom python plugin case2 「九宮格自動擬合」 需要一個獨立的 script 用來算出 
    bounding box 的 寬：長 比例 e.g. 1:0.543  <-- BB2726 canceled already
	: sorted-xyz // ( -- ['x','z','y'] ) Sorted xyz of bounding box bigest to smallest
		part <py>
		part = pop() # 'Part'
		bb = gom.app.project.parts[part].nominal.bounding_box	 # bounding box
		dim = bb.max - bb.min
		dim = {'x':dim.x, 'y':dim.y, 'z':dim.z}
		xyz = sorted(dim, key=dim.get, reverse=True)  # xyz is a sorted list like ['x', 'z', 'y'] where [0] is the biggest
		push(xyz)
		</py> ;
		/// 用來看出 project 的軸向，最小的就是 core side, cavity side, 中間的就是朝上、朝下。
[X] 10:51 2020/12/04 試解 BB1247_04
    如何正確參考到對的 inspection['Surface_comparison_#1'] 的問題....
        py> gom.app.project.inspection count --> 1 (<class 'int'>)
        py> gom.app.project.inspection[0] --> gom.app.project.inspection['Surface_comparison_#1'] (<class 'gom.Item'>)
    [X] 08:16 2020/12/07 若有失敗的，我用 len(gom.app.project.inspection)-1 應該還是對的
        #彩圖上Elements Front View
        gom.script.view.adjust_view_to_element_by_front_view (
            element=gom.app.project.inspection[len(gom.app.project.inspection)-1]
[ ] 13:46 2020/12/07 peforth v1.26 release 上 pypi 
[ ] 13:46 2020/12/07 v104 two problems --> fp 17:19 2020/12/07
    [X] 17:21 2020/12/07 check list for a release
        [X] remove or disable import peforth and import peforth_gom_port 
        [X] remove or disable all debug breakpoints that probably have 'peforth' in the line 
        [X] 結束的 workspace, view angle 的切換
        [X] 一開始清除所有的東西，一切重來。僅限 'Part' 下。[ ] 若有多 part 則提出警告然後停止執行。
        [X] 最後不要自動 save 
        [X] 一開始的 workspace, standard view angle 要切換好
        [X] 附上最新版的 setup.py 
        [X] 檢查 source code 頭尾的版號
        [X] 檢查 email subject and body 版號    
        [X] 檔名版號、zip 檔版號
        [ ] update 相關 UTS TR     
[X] 16:43 2020/12/17 我的 log 有點亂。此後本檔用來記錄 peforth gom port 相關的筆記。
    Tasks 在 ~\GitHub\Gom\GOM_python_notebook.py 
[X] 13:49 2021/01/25 終於發現如何給 project-k kernel 增添 functions 以及 variables
    以前以為 jeforth peforth 無法在 runtime 給 kernel 增添東西。現在剛想通辦法。以 peforth 為例，就像這樣：
    peforth.push(bp).dictate("py: vm.bp=pop()")
    也就是要用到 dictate() 從裡面去改才行。            
    
[X] peforth GOM port 教材 --> c:\Users\8304018\Documents\GitHub\gomforth\gomforth教材.txt 

    Forth 基本常識
    ===============
    
    - data stack
    - Postfix notation 
    - FORTH 八家將 drop dropall dup swap over 
      + - * / % AND OR NOT and or not 
      variable constant value to 
      ( stack diagram -- ) words help bye stop : ; count space ."
    - Scope of __main__ and peforth kernel 

    進階 
    =====
    
    - Add a colon word
    - <py> ... </py>  
    - <py> ... </pyV>  
    - py> py: py>~  py:~ 
    - debug 
    
        Example low level breakpoint: ( High level simply *debug* <prompt> )
        
            peforth.bp(22,locals())
            
        Breakpoint commands:  bl  be  bd  be*  bd*  (try " help bl " )
        'exit' or ESC leaves the breakpoint and continue running.
        'bye' to totally stop the script session.
        
    常用的 words 
    =============
        
    \ // /// ( 
    bye stop words help 
    : ; 
    <py> </py> </pyV> py: py> py:~ py>~ :: :> ::~ :>~ 
    swap drop nip dup over depth pick roll rot -rot 
    bool and or not AND OR NOT XOR true false 
    "" [] {} none 0< + * - / % 1+ 2+ 1- 2- >> << 0= 0> 0<> 0<= 0>= = == > < != >= <= <> 
    invert negate within abs max min sign trim count 
    if then else for begin until again repeat while 
    ?stop ?dup 
    constant value to variable ! @ ? 
    . cr space chars spaces --> .( ." .' s" s' s` <text> </text> 
    int float type list dict str set tuple dict>keys dir keys 
    dropall .s see cd 
    *debug* bl bd be bd* be* 


1
1
1
1
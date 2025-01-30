bwTh(3).
hwTh(1).

node(n0, [python, mySQL, gcc], (arm64, 736), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [piCamera2]).
node(n10, [ubuntu, mySQL, python, js, gcc], (arm64, 384), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n1, [ubuntu, mySQL, python, js, gcc], (arm64, 416), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n12, [ubuntu, js, mySQL, python], (arm64, 800), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n15, [ubuntu], (x86, 704), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n3, [python], (x86, 384), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [piCamera1]).
node(n2, [mySQL, js, gcc], (x86, 448), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [cam21]).
node(n13, [python, ubuntu, mySQL, gcc], (arm64, 544), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n5, [gcc, mySQL], (x86, 544), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [nutrient, cam22, water]).
node(n8, [js], (arm64, 544), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam11]).
node(n11, [js, python, ubuntu], (x86, 704), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n7, [ubuntu, python], (arm64, 448), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [energy, iphoneXS]).
node(n6, [ubuntu, gcc], (arm64, 448), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [echoDot]).
node(n9, [python, ubuntu, gcc], (arm64, 576), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [cam12, heat]).
node(n4, [python, ubuntu], (arm64, 704), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [soil, arViewer]).
node(n14, [gcc, js], (arm64, 576), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).

link(n3, n9, 39.0, 162).
link(n9, n3, 39.0, 162).
link(n3, n14, 41.0, 60).
link(n14, n3, 41.0, 60).
link(n4, n13, 10, 493).
link(n13, n4, 10, 493).
link(n2, n9, 23.0, 340).
link(n9, n2, 23.0, 340).
link(n0, n10, 3, 350).
link(n10, n0, 3, 350).
link(n4, n6, 16.0, 417).
link(n6, n4, 16.0, 417).
link(n1, n11, 22.0, 213).
link(n11, n1, 22.0, 213).
link(n2, n14, 25.0, 71).
link(n14, n2, 25.0, 71).
link(n12, n14, 17.0, 34).
link(n14, n12, 17.0, 34).
link(n8, n14, 11.0, 424).
link(n14, n8, 11.0, 424).
link(n2, n13, 13.0, 83).
link(n13, n2, 13.0, 83).
link(n9, n11, 29.0, 204).
link(n11, n9, 29.0, 204).
link(n13, n13, 0.0, inf).
link(n2, n10, 40.0, 369).
link(n10, n2, 40.0, 369).
link(n9, n12, 11.0, 300).
link(n12, n9, 11.0, 300).
link(n3, n5, inf, 122).
link(n5, n3, inf, 122).
link(n0, n15, 29.0, 432).
link(n15, n0, 29.0, 432).
link(n10, n14, 39.0, 348).
link(n14, n10, 39.0, 348).
link(n10, n13, 27.0, 206).
link(n13, n10, 27.0, 206).
link(n5, n11, inf, 24).
link(n11, n5, inf, 24).
link(n2, n3, 42.0, 365).
link(n3, n2, 42.0, 365).
link(n4, n12, 21.0, 114).
link(n12, n4, 21.0, 114).
link(n3, n10, 18.0, 32).
link(n10, n3, 18.0, 32).
link(n0, n0, 0.0, inf).
link(n4, n10, 37.0, 90).
link(n10, n4, 37.0, 90).
link(n5, n9, inf, 49).
link(n9, n5, inf, 49).
link(n4, n11, 29.0, 161).
link(n11, n4, 29.0, 161).
link(n8, n9, 5, 244).
link(n9, n8, 5, 244).
link(n0, n1, 30.0, 82).
link(n1, n0, 30.0, 82).
link(n2, n5, inf, 162).
link(n5, n2, inf, 162).
link(n7, n7, 0.0, inf).
link(n3, n8, 34.0, 348).
link(n8, n3, 34.0, 348).
link(n0, n12, 35.0, 201).
link(n12, n0, 35.0, 201).
link(n4, n4, 0.0, inf).
link(n1, n10, 30.0, 248).
link(n10, n1, 30.0, 248).
link(n8, n8, 0.0, inf).
link(n2, n2, 0.0, inf).
link(n9, n13, 10.0, 77).
link(n13, n9, 10.0, 77).
link(n1, n14, 9, 117).
link(n14, n1, 9, 117).
link(n5, n8, inf, 303).
link(n8, n5, inf, 303).
link(n9, n14, 16.0, 378).
link(n14, n9, 16.0, 378).
link(n2, n12, 24.0, 423).
link(n12, n2, 24.0, 423).
link(n3, n3, 0.0, inf).
link(n7, n15, 15.0, 235).
link(n15, n7, 15.0, 235).
link(n12, n12, 0.0, inf).
link(n7, n12, 21.0, 212).
link(n12, n7, 21.0, 212).
link(n4, n9, 20.0, 338).
link(n9, n4, 20.0, 338).
link(n0, n6, 33.0, 298).
link(n6, n0, 33.0, 298).
link(n4, n14, 22.0, 439).
link(n14, n4, 22.0, 439).
link(n6, n13, 6, 427).
link(n13, n6, 6, 427).
link(n6, n15, 21.0, 490).
link(n15, n6, 21.0, 490).
link(n7, n10, 17.0, 27).
link(n10, n7, 17.0, 27).
link(n4, n8, 15.0, 297).
link(n8, n4, 15.0, 297).
link(n2, n11, 32.0, 336).
link(n11, n2, 32.0, 336).
link(n7, n11, 22.0, 444).
link(n11, n7, 22.0, 444).
link(n5, n15, inf, 233).
link(n15, n5, inf, 233).
link(n2, n7, 33.0, 131).
link(n7, n2, 33.0, 131).
link(n5, n5, 0.0, inf).
link(n9, n10, 27.0, 391).
link(n10, n9, 27.0, 391).
link(n1, n6, 9.0, 469).
link(n6, n1, 9.0, 469).
link(n7, n9, 10, 264).
link(n9, n7, 10, 264).
link(n3, n11, 10, 24).
link(n11, n3, 10, 24).
link(n3, n6, 35.0, 149).
link(n6, n3, 35.0, 149).
link(n1, n4, 13.0, 127).
link(n4, n1, 13.0, 127).
link(n7, n14, 26.0, 251).
link(n14, n7, 26.0, 251).
link(n1, n2, 16.0, 387).
link(n2, n1, 16.0, 387).
link(n0, n2, 40.0, 231).
link(n2, n0, 40.0, 231).
link(n12, n15, 16.0, 434).
link(n15, n12, 16.0, 434).
link(n3, n4, 39.0, 430).
link(n4, n3, 39.0, 430).
link(n5, n10, inf, 102).
link(n10, n5, inf, 102).
link(n10, n10, 0.0, inf).
link(n6, n11, 25.0, 404).
link(n11, n6, 25.0, 404).
link(n1, n1, 0.0, inf).
link(n8, n12, 6, 198).
link(n12, n8, 6, 198).
link(n1, n5, inf, 235).
link(n5, n1, inf, 235).
link(n6, n10, 33.0, 27).
link(n10, n6, 33.0, 27).
link(n6, n14, 18.0, 57).
link(n14, n6, 18.0, 57).
link(n10, n15, 32.0, 382).
link(n15, n10, 32.0, 382).
link(n0, n3, 18.0, 303).
link(n3, n0, 18.0, 303).
link(n11, n13, 19, 379).
link(n13, n11, 19, 379).
link(n3, n15, 44.0, 482).
link(n15, n3, 44.0, 482).
link(n8, n13, 5.0, 435).
link(n13, n8, 5.0, 435).
link(n3, n13, 29.0, 257).
link(n13, n3, 29.0, 257).
link(n1, n9, 7.0, 439).
link(n9, n1, 7.0, 439).
link(n11, n12, 30.0, 111).
link(n12, n11, 30.0, 111).
link(n14, n15, 21.0, 340).
link(n15, n14, 21.0, 340).
link(n8, n11, 24.0, 62).
link(n11, n8, 24.0, 62).
link(n5, n14, inf, 116).
link(n14, n5, inf, 116).
link(n4, n5, inf, 334).
link(n5, n4, inf, 334).
link(n11, n11, 0.0, inf).
link(n9, n15, 5, 84).
link(n15, n9, 5, 84).
link(n1, n13, 3, 29).
link(n13, n1, 3, 29).
link(n2, n8, 18.0, 388).
link(n8, n2, 18.0, 388).
link(n11, n14, 31.0, 279).
link(n14, n11, 31.0, 279).
link(n5, n7, inf, 94).
link(n7, n5, inf, 94).
link(n4, n15, 25.0, 360).
link(n15, n4, 25.0, 360).
link(n0, n13, 27.0, 430).
link(n13, n0, 27.0, 430).
link(n6, n8, 11.0, 189).
link(n8, n6, 11.0, 189).
link(n7, n8, 15.0, 244).
link(n8, n7, 15.0, 244).
link(n11, n15, 34.0, 72).
link(n15, n11, 34.0, 72).
link(n4, n7, 30.0, 211).
link(n7, n4, 30.0, 211).
link(n2, n6, 7, 124).
link(n6, n2, 7, 124).
link(n0, n8, 29.0, 184).
link(n8, n0, 29.0, 184).
link(n0, n7, 14, 320).
link(n7, n0, 14, 320).
link(n6, n6, 0.0, inf).
link(n0, n11, 8, 67).
link(n11, n0, 8, 67).
link(n5, n6, inf, 258).
link(n6, n5, inf, 258).
link(n9, n9, 0.0, inf).
link(n12, n13, 11.0, 109).
link(n13, n12, 11.0, 109).
link(n1, n15, 12.0, 126).
link(n15, n1, 12.0, 126).
link(n8, n10, 32.0, 334).
link(n10, n8, 32.0, 334).
link(n1, n12, 8.0, 205).
link(n12, n1, 8.0, 205).
link(n10, n12, 38.0, 60).
link(n12, n10, 38.0, 60).
link(n14, n14, 0.0, inf).
link(n5, n13, inf, 318).
link(n13, n5, inf, 318).
link(n3, n7, 32.0, 313).
link(n7, n3, 32.0, 313).
link(n6, n9, 16.0, 316).
link(n9, n6, 16.0, 316).
link(n3, n12, 40.0, 435).
link(n12, n3, 40.0, 435).
link(n2, n15, 28.0, 469).
link(n15, n2, 28.0, 469).
link(n0, n14, 39.0, 126).
link(n14, n0, 39.0, 126).
link(n0, n5, inf, 497).
link(n5, n0, inf, 497).
link(n0, n9, 24.0, 260).
link(n9, n0, 24.0, 260).
link(n0, n4, 37.0, 264).
link(n4, n0, 37.0, 264).
link(n8, n15, 10.0, 43).
link(n15, n8, 10.0, 43).
link(n15, n15, 0.0, inf).
link(n13, n14, 12.0, 496).
link(n14, n13, 12.0, 496).
link(n6, n7, 26.0, 379).
link(n7, n6, 26.0, 379).
link(n10, n11, 8, 288).
link(n11, n10, 8, 288).
link(n13, n15, 15.0, 228).
link(n15, n13, 15.0, 228).
link(n2, n4, 23.0, 362).
link(n4, n2, 23.0, 362).
link(n7, n13, 20.0, 284).
link(n13, n7, 20.0, 284).
link(n1, n3, 32.0, 184).
link(n3, n1, 32.0, 184).
link(n5, n12, inf, 487).
link(n12, n5, inf, 487).
link(n1, n7, 17.0, 78).
link(n7, n1, 17.0, 78).
link(n1, n8, 2, 394).
link(n8, n1, 2, 394).
link(n6, n12, 17.0, 338).
link(n12, n6, 17.0, 338).

nodeType(n0, edge).
nodeType(n1, cloud).
nodeType(n2, edge).
nodeType(n3, thing).
nodeType(n4, edge).
nodeType(n5, thing).
nodeType(n6, thing).
nodeType(n7, thing).
nodeType(n8, thing).
nodeType(n9, edge).
nodeType(n10, cloud).
nodeType(n11, thing).
nodeType(n12, edge).
nodeType(n13, edge).
nodeType(n14, thing).
nodeType(n15, thing).

location(n0, it).
location(n1, es).
location(n2, it).
location(n3, it).
location(n4, es).
location(n5, it).
location(n6, it).
location(n7, de).
location(n8, it).
location(n9, de).
location(n10, de).
location(n11, it).
location(n12, it).
location(n13, es).
location(n14, it).
location(n15, de).

provider(n0, aws).
provider(n1, aws).
provider(n2, ibm).
provider(n3, ibm).
provider(n4, ibm).
provider(n5, ibm).
provider(n6, ibm).
provider(n7, ibm).
provider(n8, aws).
provider(n9, aws).
provider(n10, aws).
provider(n11, ibm).
provider(n12, azure).
provider(n13, ibm).
provider(n14, aws).
provider(n15, azure).

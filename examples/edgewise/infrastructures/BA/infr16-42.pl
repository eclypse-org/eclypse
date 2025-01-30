bwTh(3).
hwTh(1).

node(n10, [js, ubuntu, mySQL], (arm64, 160), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [nutrient, energy]).
node(n0, [ubuntu, mySQL], (x86, 448), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [cam22, iphoneXS]).
node(n9, [ubuntu, mySQL, python, js, gcc], (arm64, 608), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n13, [mySQL], (arm64, 384), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n8, [mySQL, js, gcc], (x86, 544), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam21]).
node(n1, [ubuntu, mySQL, gcc], (x86, 800), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [cam11, water]).
node(n4, [gcc, python], (x86, 352), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [arViewer, cam12]).
node(n11, [js, ubuntu], (arm64, 832), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n7, [mySQL, js], (arm64, 704), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [soil]).
node(n15, [ubuntu], (x86, 352), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n2, [python, gcc, ubuntu], (arm64, 608), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [heat, echoDot]).
node(n14, [ubuntu, mySQL, python, js, gcc], (arm64, 352), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n12, [gcc, python, ubuntu], (arm64, 672), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n5, [ubuntu, python, js, gcc], (x86, 352), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [piCamera1, piCamera2]).
node(n3, [ubuntu, mySQL, python, js, gcc], (x86, 544), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n6, [ubuntu, mySQL, python, js, gcc], (x86, 256), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).

link(n1, n2, 10.0, 118).
link(n2, n1, 10.0, 118).
link(n5, n14, 2, 466).
link(n14, n5, 2, 466).
link(n8, n12, 17, 189).
link(n12, n8, 17, 189).
link(n9, n15, 2, 120).
link(n15, n9, 2, 120).
link(n0, n5, 10, 421).
link(n5, n0, 10, 421).
link(n0, n14, 10.0, 111).
link(n14, n0, 10.0, 111).
link(n1, n4, 22.0, 94).
link(n4, n1, 22.0, 94).
link(n3, n13, 18, 332).
link(n13, n3, 18, 332).
link(n1, n11, 14.0, 379).
link(n11, n1, 14.0, 379).
link(n0, n13, 2, 32).
link(n13, n0, 2, 32).
link(n7, n13, 6, 340).
link(n13, n7, 6, 340).
link(n3, n6, 13, 411).
link(n6, n3, 13, 411).
link(n6, n12, 10.0, 58).
link(n12, n6, 10.0, 58).
link(n10, n12, 12.0, 45).
link(n12, n10, 12.0, 45).
link(n2, n11, 13.0, 193).
link(n11, n2, 13.0, 193).
link(n2, n15, 10.0, 324).
link(n15, n2, 10.0, 324).
link(n1, n12, 14.0, 436).
link(n12, n1, 14.0, 436).
link(n4, n5, 18, 213).
link(n5, n4, 18, 213).
link(n5, n7, 3, 384).
link(n7, n5, 3, 384).
link(n8, n13, 7.0, 283).
link(n13, n8, 7.0, 283).
link(n3, n10, 4, 488).
link(n10, n3, 4, 488).
link(n5, n11, 3, 307).
link(n11, n5, 3, 307).
link(n11, n15, 12.0, 72).
link(n15, n11, 12.0, 72).
link(n0, n4, 14, 135).
link(n4, n0, 14, 135).
link(n2, n8, 7.0, 467).
link(n8, n2, 7.0, 467).
link(n1, n14, 13.0, 373).
link(n14, n1, 13.0, 373).
link(n4, n15, 20.0, 189).
link(n15, n4, 20.0, 189).
link(n1, n5, 11, 403).
link(n5, n1, 11, 403).
link(n1, n9, 15.0, 65).
link(n9, n1, 15.0, 65).
link(n2, n6, 16, 403).
link(n6, n2, 16, 403).
link(n5, n9, 11.0, 399).
link(n9, n5, 11.0, 399).
link(n3, n12, 8.0, 318).
link(n12, n3, 8.0, 318).
link(n0, n10, 10, 135).
link(n10, n0, 10, 135).
link(n5, n8, 11.0, 323).
link(n8, n5, 11.0, 323).
link(n0, n6, 4, 323).
link(n6, n0, 4, 323).
link(n5, n15, 9.0, 345).
link(n15, n5, 9.0, 345).
link(n7, n14, 3, 70).
link(n14, n7, 3, 70).
link(n3, n11, 13.0, 299).
link(n11, n3, 13.0, 299).
link(n2, n12, 18, 412).
link(n12, n2, 18, 412).
link(n7, n10, 18, 275).
link(n10, n7, 18, 275).
link(n0, n7, 8, 41).
link(n7, n0, 8, 41).
link(n8, n9, 5.0, 299).
link(n9, n8, 5.0, 299).
link(n1, n1, 0.0, inf).
link(n6, n8, 2, 166).
link(n8, n6, 2, 166).
link(n4, n11, 21.0, 133).
link(n11, n4, 21.0, 133).
link(n5, n5, 0.0, inf).
link(n3, n3, 0.0, inf).
link(n1, n15, 16.0, 361).
link(n15, n1, 16.0, 361).
link(n4, n4, 0.0, inf).
link(n0, n12, 6, 123).
link(n12, n0, 6, 123).
link(n7, n12, 7, 496).
link(n12, n7, 7, 496).
link(n2, n14, 12.0, 341).
link(n14, n2, 12.0, 341).
link(n8, n15, 7.0, 463).
link(n15, n8, 7.0, 463).
link(n5, n13, 6, 192).
link(n13, n5, 6, 192).
link(n2, n10, 8.0, 272).
link(n10, n2, 8.0, 272).
link(n9, n14, 17, 205).
link(n14, n9, 17, 205).
link(n13, n13, 0.0, inf).
link(n0, n2, 2, 317).
link(n2, n0, 2, 317).
link(n4, n13, 16.0, 55).
link(n13, n4, 16.0, 55).
link(n2, n7, 10.0, 177).
link(n7, n2, 10.0, 177).
link(n2, n13, 4.0, 410).
link(n13, n2, 4.0, 410).
link(n7, n15, 10.0, 73).
link(n15, n7, 10.0, 73).
link(n15, n15, 0.0, inf).
link(n4, n10, 20.0, 435).
link(n10, n4, 20.0, 435).
link(n6, n11, 13, 450).
link(n11, n6, 13, 450).
link(n2, n5, 10.0, 385).
link(n5, n2, 10.0, 385).
link(n3, n7, 8, 57).
link(n7, n3, 8, 57).
link(n11, n14, 5.0, 209).
link(n14, n11, 5.0, 209).
link(n5, n6, 18, 214).
link(n6, n5, 18, 214).
link(n2, n2, 0.0, inf).
link(n0, n1, 8, 436).
link(n1, n0, 8, 436).
link(n1, n8, 13.0, 386).
link(n8, n1, 13.0, 386).
link(n10, n10, 0.0, inf).
link(n0, n3, 2, 56).
link(n3, n0, 2, 56).
link(n6, n6, 0.0, inf).
link(n9, n13, 9.0, 419).
link(n13, n9, 9.0, 419).
link(n11, n11, 0.0, inf).
link(n14, n14, 0.0, inf).
link(n6, n7, 10.0, 70).
link(n7, n6, 10.0, 70).
link(n3, n9, 8.0, 25).
link(n9, n3, 8.0, 25).
link(n10, n13, 8.0, 161).
link(n13, n10, 8.0, 161).
link(n6, n15, 5, 290).
link(n15, n6, 5, 290).
link(n0, n9, 9, 496).
link(n9, n0, 9, 496).
link(n12, n13, 8.0, 390).
link(n13, n12, 8.0, 390).
link(n2, n3, 4.0, 28).
link(n3, n2, 4.0, 28).
link(n2, n9, 10, 392).
link(n9, n2, 10, 392).
link(n6, n9, 3, 252).
link(n9, n6, 3, 252).
link(n11, n13, 9.0, 479).
link(n13, n11, 9.0, 479).
link(n8, n8, 0.0, inf).
link(n9, n10, 12.0, 147).
link(n10, n9, 12.0, 147).
link(n7, n9, 12.0, 56).
link(n9, n7, 12.0, 56).
link(n12, n14, 10.0, 144).
link(n14, n12, 10.0, 144).
link(n3, n4, 16.0, 475).
link(n4, n3, 16.0, 475).
link(n8, n14, 9.0, 172).
link(n14, n8, 9.0, 172).
link(n13, n15, 10.0, 127).
link(n15, n13, 10.0, 127).
link(n5, n12, 10.0, 195).
link(n12, n5, 10.0, 195).
link(n1, n13, 10.0, 335).
link(n13, n1, 10.0, 335).
link(n3, n14, 11.0, 307).
link(n14, n3, 11.0, 307).
link(n6, n10, 9.0, 180).
link(n10, n6, 9.0, 180).
link(n3, n8, 3, 472).
link(n8, n3, 3, 472).
link(n9, n12, 13.0, 266).
link(n12, n9, 13.0, 266).
link(n1, n10, 14.0, 210).
link(n10, n1, 14.0, 210).
link(n5, n10, 13.0, 490).
link(n10, n5, 13.0, 490).
link(n4, n12, 20.0, 265).
link(n12, n4, 20.0, 265).
link(n7, n8, 12, 23).
link(n8, n7, 12, 23).
link(n1, n6, 12.0, 423).
link(n6, n1, 12.0, 423).
link(n4, n14, 20.0, 234).
link(n14, n4, 20.0, 234).
link(n14, n15, 7, 24).
link(n15, n14, 7, 24).
link(n4, n9, 18, 118).
link(n9, n4, 18, 118).
link(n8, n10, 7, 342).
link(n10, n8, 7, 342).
link(n4, n6, 18.0, 154).
link(n6, n4, 18.0, 154).
link(n0, n15, 8.0, 77).
link(n15, n0, 8.0, 77).
link(n10, n15, 10.0, 283).
link(n15, n10, 10.0, 283).
link(n9, n9, 0.0, inf).
link(n8, n11, 12, 170).
link(n11, n8, 12, 170).
link(n6, n13, 6.0, 39).
link(n13, n6, 6.0, 39).
link(n3, n5, 18, 357).
link(n5, n3, 18, 357).
link(n7, n11, 6.0, 361).
link(n11, n7, 6.0, 361).
link(n2, n4, 16.0, 132).
link(n4, n2, 16.0, 132).
link(n9, n11, 14.0, 469).
link(n11, n9, 14.0, 469).
link(n11, n12, 13.0, 374).
link(n12, n11, 13.0, 374).
link(n13, n14, 8.0, 169).
link(n14, n13, 8.0, 169).
link(n0, n0, 0.0, inf).
link(n12, n15, 14.0, 79).
link(n15, n12, 14.0, 79).
link(n0, n11, 11.0, 342).
link(n11, n0, 11.0, 342).
link(n0, n8, 7, 303).
link(n8, n0, 7, 303).
link(n12, n12, 0.0, inf).
link(n1, n7, 13, 257).
link(n7, n1, 13, 257).
link(n4, n7, 21.0, 249).
link(n7, n4, 21.0, 249).
link(n10, n11, 10, 146).
link(n11, n10, 10, 146).
link(n6, n14, 7, 361).
link(n14, n6, 7, 361).
link(n3, n15, 6, 199).
link(n15, n3, 6, 199).
link(n7, n7, 0.0, inf).
link(n1, n3, 10.0, 179).
link(n3, n1, 10.0, 179).
link(n4, n8, 19.0, 336).
link(n8, n4, 19.0, 336).
link(n10, n14, 15.0, 82).
link(n14, n10, 15.0, 82).

nodeType(n0, edge).
nodeType(n1, edge).
nodeType(n2, thing).
nodeType(n3, cloud).
nodeType(n4, thing).
nodeType(n5, edge).
nodeType(n6, cloud).
nodeType(n7, edge).
nodeType(n8, thing).
nodeType(n9, cloud).
nodeType(n10, thing).
nodeType(n11, edge).
nodeType(n12, edge).
nodeType(n13, thing).
nodeType(n14, cloud).
nodeType(n15, thing).

location(n0, de).
location(n1, es).
location(n2, de).
location(n3, it).
location(n4, it).
location(n5, es).
location(n6, de).
location(n7, es).
location(n8, de).
location(n9, es).
location(n10, es).
location(n11, es).
location(n12, it).
location(n13, de).
location(n14, it).
location(n15, de).

provider(n0, aws).
provider(n1, ibm).
provider(n2, aws).
provider(n3, ibm).
provider(n4, ibm).
provider(n5, aws).
provider(n6, aws).
provider(n7, aws).
provider(n8, ibm).
provider(n9, aws).
provider(n10, aws).
provider(n11, ibm).
provider(n12, ibm).
provider(n13, azure).
provider(n14, azure).
provider(n15, azure).
